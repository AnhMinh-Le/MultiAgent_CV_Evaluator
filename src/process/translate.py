import requests
from app import load_huggingface_api_key


api_token = load_huggingface_api_key()

def translate_vi_to_en(text, api_token):
    url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-vi-en"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result[0]['translation_text']
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def translate_en_to_vi(text, api_token):
    url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-vi"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result[0]['translation_text']
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")