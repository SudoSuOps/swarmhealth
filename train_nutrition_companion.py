"""
SwarmHealth Diabetes Companion - Nutrition Focus Training
Train LoRA adapter on Qwen2.5-7B-Instruct for actionable diabetes guidance

Focus areas:
- Nutrition and food swaps
- Exercise recommendations
- Blood sugar management
- Foot care and neuropathy
- Vitamins and supplements
- Daily routines and scheduling
"""

import os
import json
import torch
from pathlib import Path
from datetime import datetime

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import Dataset

# ============================================================
# CONFIGURATION
# ============================================================

BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"  # Strong instruction-tuned base
TRAINING_DATA = "/home/ai/Desktop/quantum-rails/diabetes-ai/training_data_nutrition_v2.jsonl"
OUTPUT_DIR = "/home/ai/Desktop/quantum-rails/diabetes-ai/models/nutrition-companion-v2"

# LoRA config - higher rank for more capacity
LORA_R = 64
LORA_ALPHA = 128
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

# Training hyperparameters
EPOCHS = 5
BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 8
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 2048
WARMUP_RATIO = 0.1

# ============================================================
# LOAD DATA
# ============================================================

def load_training_data():
    """Load JSONL training data"""
    examples = []

    with open(TRAINING_DATA, 'r') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} training examples")
    return examples


def format_for_training(examples, tokenizer):
    """Format messages into training format"""
    formatted = []

    for ex in examples:
        messages = ex.get("messages", [])

        # Apply chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        formatted.append({"text": text})

    return Dataset.from_list(formatted)


# ============================================================
# TRAINING
# ============================================================

def main():
    print("=" * 60)
    print("SwarmHealth Nutrition Companion Training")
    print(f"Base model: {BASE_MODEL}")
    print(f"Training data: {TRAINING_DATA}")
    print("=" * 60)

    # Load tokenizer
    print("\n📦 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Quantization config for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load model
    print("\n🧠 Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    print("\n⚡ Applying LoRA adapter...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load and format data
    print("\n📊 Loading training data...")
    examples = load_training_data()
    dataset = format_for_training(examples, tokenizer)

    # Training config (SFTConfig combines TrainingArguments + SFT-specific params)
    training_config = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        bf16=True,
        logging_steps=5,
        save_strategy="epoch",
        save_total_limit=2,
        optim="adamw_8bit",
        max_grad_norm=0.3,
        report_to="none",
        seed=42,
        # SFT-specific
        max_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
        packing=False,
    )

    # Trainer
    print("\n🚀 Starting training...")
    trainer = SFTTrainer(
        model=model,
        args=training_config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )

    # Train
    start_time = datetime.now()
    trainer.train()

    # Save
    print("\n💾 Saving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Training complete
    duration = datetime.now() - start_time
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"   Duration: {duration}")
    print(f"   Model saved to: {OUTPUT_DIR}")
    print("=" * 60)

    # Create model card
    with open(f"{OUTPUT_DIR}/README.md", "w") as f:
        f.write(f"""# SwarmHealth Diabetes Nutrition Companion v2

## Model Details
- **Base Model:** {BASE_MODEL}
- **Training Examples:** {len(examples)}
- **LoRA Rank:** {LORA_R}
- **Training Epochs:** {EPOCHS}
- **Trained:** {datetime.now().strftime("%Y-%m-%d")}

## Focus Areas
- Nutrition and food swaps (fries → sweet potatoes, etc.)
- Blood sugar friendly foods
- Exercise recommendations
- Foot care and neuropathy prevention
- Vitamins and supplements
- Daily routines and scheduling
- Mental health and motivation

## Usage
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("{BASE_MODEL}")
model = PeftModel.from_pretrained(base, "{OUTPUT_DIR}")
tokenizer = AutoTokenizer.from_pretrained("{OUTPUT_DIR}")
```

## License
Free for personal use. Not medical advice.
""")


if __name__ == "__main__":
    main()
