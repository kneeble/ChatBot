from typing import Iterator
from flask import Flask, request, Response, stream_with_context, jsonify
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch


base_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
adapter_path = "lora-output/adapter"

tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token 

model = AutoModelForCausalLM.from_pretrained(base_model, trust_remote_code=True)
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)

# Flask setup 
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "Backend is running with DeepSeek-R1 + LoRA adapter"

@app.route("/generate", methods=["POST"])
def generate() -> Response:
    def stream_gen():
        try:
            data = request.json
            prompt = data.get("prompt", "")
            if not prompt:
                yield "Error: No prompt provided."
                return

            # Clean and structure prompt
            cleaned_prompt = prompt.strip().replace("\n", " ").replace("  ", " ")[:800]
            formatted_prompt = f"### Instruction:\n{cleaned_prompt}\n\n### Response:\n"

            # Tokenize
            inputs = tokenizer(formatted_prompt, return_tensors="pt", padding=True).to(device)

            # Generate
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id
            )

            generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
            decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            yield decoded

        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(stream_with_context(stream_gen()), content_type="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    app.run(host="0.0.0.0", port=8080)
