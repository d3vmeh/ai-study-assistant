import requests
import base64
import json
import os

api_key = os.getenv("OPENAI_API_KEY")

def encode_image(path):
    image = open(path, "rb")
    return base64.b64encode(image.read()).decode('utf8')



def get_assistant_response(question,image_path):
    encoded_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": """You are an expert teaching assistant helping students understand academic material across all subjects. Your role is to provide clear, accurate, and pedagogically sound explanations that promote learning.

CORE PRINCIPLES:
- Break down complex concepts into digestible steps
- Use analogies and examples when helpful
- Encourage critical thinking rather than just providing answers
- Adapt explanations to the apparent level of the question
- Be patient and supportive in your tone

ANALYSIS APPROACH:
1. Carefully examine any provided image for relevant information
2. Identify the subject area and specific concepts involved
3. Determine the appropriate level of explanation needed
4. Consider common misconceptions or difficulties students face with this topic

IMPORTANT: You must respond with ONLY valid JSON. Do not include any text before or after the JSON object.

RESPONSE FORMAT:
{
    "answer": "A clear, direct answer to the question",
    "explanation": "A detailed explanation with formatting. Use <newline><newline> for paragraph breaks, **bold** for emphasis, and $ for LaTeX math",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "next_steps": "Optional suggestions for further learning"
}

For the explanation field:
- Use <newline><newline> (not \\n\\n) for paragraph breaks
- Use **text** for bold subtitles
- Use $equation$ for inline math and $$equation$$ for display math
- Use numbered lists (1. 2. 3.) or bullet points (- item)

Question: """ + question + """

Remember: Respond with ONLY the JSON object, no additional text."""
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
            }
            }
        ]
        }
    ],

    "max_tokens": 1500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        structured_response = response_data['choices'][0]['message']['content']
        cleaned_response = structured_response.strip('```json\n').strip('```').strip()
        try:
            response_dict = json.loads(cleaned_response)
            # Ensure required fields exist
            if 'answer' not in response_dict:
                response_dict['answer'] = "Answer not provided"
            if 'explanation' not in response_dict:
                response_dict['explanation'] = "Explanation not provided"
            else:
                # Replace <newline> tags with actual newlines
                response_dict['explanation'] = response_dict['explanation'].replace('<newline>', '\n')
            if 'key_concepts' not in response_dict:
                response_dict['key_concepts'] = []
            return response_dict
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response if it's embedded in text
            import re
            # More robust regex to handle nested objects and arrays
            json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', structured_response, re.DOTALL)
            if json_match:
                try:
                    response_dict = json.loads(json_match.group())
                    if 'answer' not in response_dict:
                        response_dict['answer'] = "Answer not provided"
                    if 'explanation' not in response_dict:
                        response_dict['explanation'] = "Explanation not provided"
                    else:
                        response_dict['explanation'] = response_dict['explanation'].replace('<newline>', '\n')
                    if 'key_concepts' not in response_dict:
                        response_dict['key_concepts'] = []
                    return response_dict
                except:
                    pass
            
            # If all else fails, return error with debug info
            return {
                "error": f"Failed to decode response as JSON: {str(e)}", 
                "content": structured_response,
                "answer": "Error in response format",
                "explanation": f"The AI response could not be parsed properly. Raw content: {structured_response[:500]}...",
                "key_concepts": []
            }
    else:
        return {
            "error": "No valid response from model",
            "answer": "No response received",
            "explanation": "The AI model did not provide a valid response.",
            "key_concepts": []
        }