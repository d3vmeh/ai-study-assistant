import requests
import base64
import json
import os

api_key = os.getenv("OPENAI_API_KEY")

def encode_image(path):
    image = open(path, "rb")
    return base64.b64encode(image.read()).decode('utf8')



def get_llm_response(question,image_path):
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
            "text": """
            
            You are a a teaching assistant for a class the user is taking. You are responsible for answering questions and helping the user understand the material.
           

            An image may be provided to help you answer the question.


            Respond in a structured format (e.g., JSON) with the following fields:
            - answer: your answer to the question.
            - explanation: your explanation for your answer.

            Example question and response:
            Question: "What is the derivative of x²?"
            Response: {
                "answer": "The derivative of x² is 2x.",
                "explanation": "Using the power rule for differentiation, when we have x^n, the derivative is n*x^(n-1). For x², n=2, so the derivative is 2*x^(2-1) = 2x."
            }
            

            Here is the user's question: """+question+"""
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

    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        structured_response = response_data['choices'][0]['message']['content']
        cleaned_response = structured_response.strip('```json\n').strip('```').strip()
        try:
            response_dict = json.loads(cleaned_response)
            return response_dict
        except json.JSONDecodeError:
            return {"error": "Failed to decode response as JSON", "content": structured_response}
    else:
        return {"error": "No valid response from model"}