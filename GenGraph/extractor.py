import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class NERExtractor:
    def __init__(self):
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.api_key = os.environ['KEY']
        
    def extract_entities_and_relationships(self, text):
        prompt = (
            f"Extract entities and relationships from the given text and format the response "
            f"as a valid JSON object containing 'entities' (list of names) and 'relationships' "
            f"(list of objects with 'source', 'relationship', and 'target'). Ensure the response is in "
            f"pure JSON format without additional explanations.\n\nText: {text}"
        )

        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": "You are an NLP model that extracts entities and relationships from text. Respond only with a JSON object."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            try:
                content = result["choices"][0]["message"]["content"].strip()
                
                content = content.split("```json")[-1].split("```")[0].strip()
                parsed_data = json.loads(content)
                return parsed_data
            except (KeyError, json.JSONDecodeError) as e:
                return {"error": "Unexpected response format", "raw": result, "exception": str(e)}
        else:
            return {"error": "Failed to fetch data", "status_code": response.status_code, "details": response.text}

if __name__ == "__main__":
    text = "Naruto Uzumaki is the son of Minato Namikaze. Sasuke Uchiha is Naruto's rival."
    ner = NERExtractor()
    results = ner.extract_entities_and_relationships(text)
    print(json.dumps(results, indent=4))
