from openai import OpenAI
import base64
import os

def encode_image(image_object):
    image_bytes = image_object.read()
    return base64.b64encode(image_bytes).decode("utf-8")

    
def analyze_image(image_path):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": "You are a helpful assistant which will help student with their query."},
            {"role": "user", "content": [
                {"type": "text", "text": "help solve the Question in this image and Do not use Markdown."},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{image_path}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content


def get_image_analysis(image_path):
    image_data = encode_image(image_path)
    return analyze_image(image_data)