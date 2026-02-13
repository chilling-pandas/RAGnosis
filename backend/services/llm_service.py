import requests
import os

class LLMService:
    def __init__(self):
        self.mode = os.getenv("LLM_MODE", "local")

        # Local Ollama
        self.local_url = "http://localhost:11434/api/generate"
        self.local_model = "qwen2.5:3b-instruct-q4_K_M"

        # Hosted HuggingFace inference
        self.hf_api_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
        self.hf_token = os.getenv("HF_TOKEN")

    def generate(self, prompt: str):

        if self.mode == "local":
            payload = {
                "model": self.local_model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(self.local_url, json=payload)
            return response.json().get("response", "")

        elif self.mode == "cloud":
            headers = {
                "Authorization": f"Bearer {self.hf_token}"
            }

            payload = {
                "inputs": prompt
            }

            response = requests.post(self.hf_api_url, headers=headers, json=payload)

            if response.status_code != 200:
                return "LLM cloud error."

            return response.json()[0]["generated_text"]

        else:
            return "Invalid LLM mode."

