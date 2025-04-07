from typing import Iterator
import requests
import json
from flask import Flask, request, Response, stream_with_context, jsonify

app = Flask(__name__)

OLLAMA_API_BASE = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_API_BASE}/api/generate"
MODEL = "deepseek-r1:1.5b"

@app.route("/generate", methods=["POST"])
def gen_stream() -> Iterator[str]:
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
 
    def stream_gen():
        response = requests.post(
            OLLAMA_GENERATE_URL, 
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True
                },
                stream=True
            )
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    yield json_response['response']
                if json_response.get('done', False):
                    break

    return Response(stream_with_context(stream_gen()), content_type="text/plain")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)