# README — Fine-Tuning DeepSeek-R1 with LoRA & Serving via Flask- Oscar Sanchez Huezca

This project demonstrates how to fine-tune the `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` language model using the LoRA method and deploy it through a Flask backend for custom chatbot applications.

> **macOS-focused:** This setup is specifically tailored for macOS users utilizing the MPS (Metal Performance Shaders) backend. However, it can be adapted for Windows or Linux with appropriate GPU (CUDA) support and library adjustments. (I have a Mac so it made things feasible)

---

## Key Components

### 1. `train_lora.py` — Fine-Tuning with LoRA

This script fine-tunes the base model using `LoRA` (Low-Rank Adaptation), which enables efficient and lightweight training without modifying the base weights.

#### What It Does:

* Loads training data from a `training_data.jsonl` file
* Prepares it for instruction tuning (formatting inputs/outputs)
* Loads the tokenizer and base model from Hugging Face
* Applies a LoRA configuration (adapter method)
* Trains the model on macOS/MPS-friendly settings (no FP16)
* Saves the trained LoRA adapter to `lora-output/adapter`

#### Why LoRA?

LoRA allows fast and memory-efficient fine-tuning by injecting trainable layers into frozen pre-trained weights. Ideal for:

* macOS with limited GPU support (MPS)
* Customizing large language models with minimal compute

---

### 2. `app.py` — Flask API to Serve the Fine-Tuned Model

A simple backend that loads the LoRA-adapted model and serves it via a `/generate` endpoint.

#### Key Changes from a Basic App:

* Loads both the **base model** and **LoRA adapter**
* Uses `"### Instruction:\n...\n\n### Response:\n"` formatting to follow instruction-tuning pattern
* Cleans incoming prompts to reduce token bloat
* Uses `.generate()` to infer responses with top-k/p sampling
* Handles streaming output with Flask `Response`

#### Endpoints:

* `GET /` — Basic check if backend is live
* `POST /generate` — Accepts `{"prompt": "..."}` and returns streamed response

---

### 3. `run_test_questions.py` — Test Questions via CLI

Instead of Python-based HTTP, this script uses shell `curl` commands for each question to emulate real terminal API testing.

#### How It Works:

* Loads questions from `test_questions.txt`
* Sends each via `curl -X POST http://localhost:8080/generate`
* Captures and saves results into `model_responses.txt`

#### Why?

* Mirrors how a REST client like Postman or terminal user might test
* Avoids Python HTTP quirks with streaming endpoints

---

## Requirements & Installation

### Python Dependencies

Install all required libraries with:

```bash
pip install -r requirements.txt
```

#### `requirements.txt` Example:

```
torch>=2.0.0
transformers>=4.36.0
datasets
peft
accelerate
flask
flask-cors
```

> **macOS Users** : Ensure your PyTorch installation includes MPS support. Avoid `fp16` or CUDA settings unless you're on a different platform with a supported GPU.

> **Windows/Linux Users** : You can enable `fp16=True` in `TrainingArguments` and switch device mapping to CUDA if you have a compatible NVIDIA GPU.

### Node.js (if frontend is used)

If you're using a React or Vite frontend:

```bash
npm install
npm run dev
```

Otherwise, Node is not required for backend + model functionality alone.

---

## Do I Need Ollama?

Once the model is downloaded and fine-tuned from Hugging Face,  **Ollama is no longer necessary** . This project loads and serves the model using `transformers` and `torch` only.

---

## File Structure

```bash
ChatBot/
├── training_data.jsonl       # Fine-tuning data (prompt-completion pairs)
├── test_questions.txt        # List of test prompts
├── model_responses.txt       # Output log of model answers
├── train_lora.py             # Script to fine-tune model using LoRA
├── app.py                    # Flask API serving the fine-tuned model
├──run_test_questions.py          # Script to test model using curl
└── requirements.txt          # Python dependencies
```

---

## Usage Guide

### 1. Fine-Tune the Model

```bash
python train_lora.py
```

> Output: `lora-output/adapter/`

### 2. Run Flask Server

```bash
python app.py
```

> Access: `http://localhost:8080`

### 3. Test Model with Questions (In the usage case where you need to test)

```bash
python run_test_questions.py
```

> Output saved in: `model_responses.txt`

---


## Usage Guide

### Test Model with Questions from txt file

```bash
python run_test_questions.py
```

Once the questions are parsed and sent though the terminal with the curl function, the result is a text file with both the full question and answer (Included in the repo)

This was to verify that the training of the model had been done correctly and was actually effectve in its training, especially when it was focusing on Philosophy-based questions, but it even outperformed expectations with more general knowledge questions. That being said, there was only word-based questions, no mathematic or arithmetic questions involved and nothing that required too much logical processing because the model had not been fine-tuned to do so. The main focus was getting the model to process Philosophy questions correctly and concisely. There was also no testing that asked for added detail, which is something that was included in the training data itself. 

---



## Licenses

This project builds upon open-source tools released under various licenses:

* **DeepSeek-R1 Model** — MIT License ([https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B]())
* **Transformers & Datasets** — Apache 2.0 License ([https://github.com/huggingface/transformers]())
* **PEFT (LoRA)** — Apache 2.0 License ([https://github.com/huggingface/peft]())
* **Flask & Flask-Cors** — BSD License
* **Accelerate** — Apache 2.0 License
