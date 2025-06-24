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

RESPONSE FORMAT:
Provide your response as valid JSON with these fields:
- "answer": A clear, direct answer to the question
- "explanation": A detailed explanation of the reasoning and concepts
- "key_concepts": An array of important concepts or terms covered
- "next_steps": Suggestions for further learning or practice (optional)

EXAMPLE:
Question: "What is the derivative of x²?"
{
    "answer": "The derivative of x² is 2x",
    "explanation": "Using the power rule for differentiation: when we have x^n, the derivative is n×x^(n-1). For x², n=2, so we get 2×x^(2-1) = 2×x^1 = 2x. This represents the instantaneous rate of change of the function at any point.",
    "key_concepts": ["power rule", "derivative", "rate of change"],
    "next_steps": "Try practicing with other polynomial functions like x³ or 3x⁴"
}

Question: """ + question + """
            """
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

    "max_tokens": 800
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
            if 'key_concepts' not in response_dict:
                response_dict['key_concepts'] = []
            return response_dict
        except json.JSONDecodeError:
            return {
                "error": "Failed to decode response as JSON", 
                "content": structured_response,
                "answer": "Error in response format",
                "explanation": "The AI response could not be parsed properly. Raw content available in 'content' field.",
                "key_concepts": []
            }
    else:
        return {
            "error": "No valid response from model",
            "answer": "No response received",
            "explanation": "The AI model did not provide a valid response.",
            "key_concepts": []
        }