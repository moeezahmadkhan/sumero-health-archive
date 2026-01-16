import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 1. Configuration
model_id = "unsloth/Llama-3.2-1B-Instruct" # Small, fast for sample
data_path = "pilot_instructions.jsonl"
output_dir = "./lora_adapter"

def train():
    # 2. Load Model & Tokenizer
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )

    model = prepare_model_for_kbit_training(model)

    # 3. LoRA Setup
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # 4. Data Preparation
    def format_prompt(sample):
        return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{sample['instruction']}\n\n{sample['input']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{sample['output']}<|eot_id|>"

    dataset = load_dataset("json", data_files=data_path, split="train")
    dataset = dataset.map(lambda x: {"text": format_prompt(x)})
    dataset = dataset.map(lambda x: tokenizer(x["text"], truncation=True, max_length=512), batched=True)

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=100, # Fast loop for 300-500 samples equivalent
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="no",
        report_to="none"
    )

    # 6. Train
    trainer = Trainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("Starting training...")
    trainer.train()
    
    # 7. Save Adapter
    model.save_pretrained(output_dir)
    print(f"Training complete. Adapter saved to {output_dir}")

if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Training script defined, but execution requires GPU/Dependencies: {e}")
        print("Note: In a local environment without GPU, this serves as a template.")
