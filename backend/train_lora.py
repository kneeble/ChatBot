import os
import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType

#  Path 
json_path = os.path.join(os.path.dirname(__file__), "training_data.jsonl")
base_model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
output_dir = "lora-output"

#  Load .jsonl manually 
with open(json_path, "r", encoding="utf-8") as f:
    data = [json.loads(line.strip()) for line in f if line.strip()]

#  Convert to HF Dataset 
dataset = Dataset.from_list(data)

#  Format for instruction tuning 
def format_example(example):
    prompt = example["instruction"]
    if example.get("input"):
        prompt += f"\n\n{example['input']}"
    return {
        "text": f"### Instruction:\n{prompt}\n\n### Response:\n{example['output']}"
    }

formatted = dataset.map(format_example)

#  Load tokenizer and model 
tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    trust_remote_code=True,
    torch_dtype=torch.float32,  # safer for macOS/MPS
    device_map="auto"
)

#  Tokenize and add labels 
def tokenize(example):
    tokenized = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=256
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized = formatted.map(tokenize, batched=True)

#  Apply LoRA config 
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, lora_config)

#  Training args (safe for macOS) 
training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=1,
    logging_steps=5,
    save_strategy="epoch",
    save_total_limit=1,
    report_to="none",
    fp16=False,
    bf16=False
)

#  Trainer 
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    tokenizer=tokenizer
)

#  Train 
trainer.train()

#  Save adapter 
model.save_pretrained(os.path.join(output_dir, "adapter"))
print("Training complete. Adapter saved to:", os.path.join(output_dir, "adapter"))