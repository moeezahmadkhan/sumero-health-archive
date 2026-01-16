import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os

# 1. Configuration
model_id = "unsloth/Llama-3.2-1B-Instruct"
adapter_dir = "./lora_adapter"

def run_inference(prompt_text):
    # Check if adapter exists
    if not os.path.exists(adapter_dir):
        print(f"Warning: Adapter not found at {adapter_dir}. Running base model instead.")
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
    else:
        # Load Quantized Base Model
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto"
        )
        # Load Adapter
        model = PeftModel.from_pretrained(base_model, adapter_dir)

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Format input
    full_prompt = (
        f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        f"Analyze my health data and provide insights.\n\n"
        f"{prompt_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return response

if __name__ == "__main__":
    # Example manual tests from the prompt
    test_cases = [
        "Why is my recovery low? (Sleep: 5.8h, Heart Rate: 78, Stress: 8)",
        "What should I do today? (Sleep: 8h, Stress: 3, Activity: 75)",
        "Is this dangerous? (Heart Rate: 85, Sleep: 4h)"
    ]
    
    print("\n--- Running AI Health Platform Inference ---")
    for tc in test_cases:
        print(f"\nUser Query: {tc}")
        # Note: In the real app, we extract variables and format them as the model expects
        # Here we just pass the text for demonstration
        print(f"AI Response: [SIMULATED - requires model loading]\n")
        # To actually run, uncomment below (requires GPU/Deps)
        # print(f"AI Response:\n{run_inference(tc)}\n")
