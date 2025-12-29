"""
Diabetes Companion AI - Training Script

Fine-tunes Mistral-7B (or larger) for compassionate diabetes guidance.
Uses QLoRA for memory-efficient training.

Built by someone who lives it. For those who need it.

Usage:
    python train_diabetes_llm.py --action train
    python train_diabetes_llm.py --action test
"""

import argparse
import json
import torch
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class TrainingConfig:
    """Training configuration"""
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    data_dir: Path = Path("data")
    output_dir: Path = Path("models/diabetes-companion-lora")

    # LoRA config
    lora_r: int = 32  # Higher rank for more complex task
    lora_alpha: int = 64
    lora_dropout: float = 0.1
    target_modules: tuple = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")

    # Training config
    num_epochs: int = 3
    batch_size: int = 2
    gradient_accumulation_steps: int = 8  # Effective batch size = 16
    learning_rate: float = 2e-4
    max_seq_length: int = 2048
    warmup_ratio: float = 0.03

    # Quantization
    use_4bit: bool = True


def load_training_data(data_dir: Path):
    """Load training and validation data."""

    train_path = data_dir / "train.json"
    val_path = data_dir / "val.json"

    if not train_path.exists():
        raise FileNotFoundError(f"Training data not found: {train_path}")

    with open(train_path) as f:
        train_data = json.load(f)

    val_data = None
    if val_path.exists():
        with open(val_path) as f:
            val_data = json.load(f)

    return train_data, val_data


def format_conversation(sample: dict) -> str:
    """Format a conversation sample for training."""

    system = sample.get("system", "")
    conversations = sample.get("conversations", [])

    # Mistral format
    text = f"<s>[INST] {system}\n\n"

    for i, turn in enumerate(conversations):
        role = turn["role"]
        content = turn["content"]

        if role == "user":
            if i > 0:
                text += f" [INST] {content} [/INST] "
            else:
                text += f"{content} [/INST] "
        else:
            text += f"{content}</s>"

    return text


def train(config: TrainingConfig):
    """Main training function."""

    print("=" * 60)
    print("🧠 Diabetes Companion AI - Training")
    print("=" * 60)
    print(f"Base model: {config.base_model}")
    print(f"Output: {config.output_dir}")
    print(f"LoRA rank: {config.lora_r}")
    print(f"4-bit: {config.use_4bit}")
    print("=" * 60)

    # Load data
    print("\n📊 Loading training data...")
    train_data, val_data = load_training_data(config.data_dir)
    print(f"   Training samples: {len(train_data)}")
    print(f"   Validation samples: {len(val_data) if val_data else 0}")

    # Import training libraries
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling,
        BitsAndBytesConfig,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset

    # Tokenizer
    print("\n🔤 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Quantization config
    if config.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    else:
        bnb_config = None

    # Load model
    print("\n🤖 Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )

    if config.use_4bit:
        model = prepare_model_for_kbit_training(model)

    # LoRA config
    print("\n🔧 Applying LoRA...")
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=list(config.target_modules),
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Trainable: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")

    # Prepare dataset
    print("\n📦 Preparing dataset...")

    def tokenize_sample(sample):
        text = format_conversation(sample)
        tokens = tokenizer(
            text,
            truncation=True,
            max_length=config.max_seq_length,
            padding="max_length",
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    train_texts = [format_conversation(s) for s in train_data]
    train_dataset = Dataset.from_dict({"text": train_texts})
    train_dataset = train_dataset.map(
        lambda x: tokenizer(x["text"], truncation=True, max_length=config.max_seq_length, padding="max_length"),
        remove_columns=["text"],
    )
    train_dataset = train_dataset.map(lambda x: {"labels": x["input_ids"]})

    val_dataset = None
    if val_data:
        val_texts = [format_conversation(s) for s in val_data]
        val_dataset = Dataset.from_dict({"text": val_texts})
        val_dataset = val_dataset.map(
            lambda x: tokenizer(x["text"], truncation=True, max_length=config.max_seq_length, padding="max_length"),
            remove_columns=["text"],
        )
        val_dataset = val_dataset.map(lambda x: {"labels": x["input_ids"]})

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(config.output_dir),
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=10,
        save_steps=100,
        eval_strategy="steps" if val_dataset else "no",
        eval_steps=100 if val_dataset else None,
        save_total_limit=2,
        fp16=True,
        optim="paged_adamw_8bit",
        report_to="none",
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    # Trainer
    print("\n🚀 Starting training...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # Train
    trainer.train()

    # Save
    print("\n💾 Saving model...")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)

    # Save system prompt
    system_prompt_path = Path(config.data_dir) / "system_prompt.txt"
    if system_prompt_path.exists():
        import shutil
        shutil.copy(system_prompt_path, config.output_dir / "system_prompt.txt")

    print(f"\n✅ Training complete! Model saved to {config.output_dir}")


def test(config: TrainingConfig):
    """Test the trained model."""

    print("=" * 60)
    print("🧠 Diabetes Companion AI - Testing")
    print("=" * 60)

    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel

    # Load system prompt
    system_prompt_path = config.output_dir / "system_prompt.txt"
    if system_prompt_path.exists():
        system_prompt = system_prompt_path.read_text()
    else:
        system_prompt = "You are a compassionate Diabetes Companion AI."

    print(f"Loading from {config.output_dir}...")

    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    tokenizer.pad_token = tokenizer.eos_token

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    # Load LoRA
    model = PeftModel.from_pretrained(model, config.output_dir)
    model.eval()

    print("✅ Model loaded\n")

    # Test conversations
    test_prompts = [
        "I'm so tired of managing diabetes every single day. It never ends.",
        "My blood sugar has been running high for a week. What should I do?",
        "Can you explain why brain fog happens with diabetes?",
        "I noticed a small cut on my foot and I'm worried.",
        "I have Type 1 diabetes and Addison's disease. Some days I can barely function.",
    ]

    for prompt in test_prompts:
        print("=" * 60)
        print(f"USER: {prompt}")
        print("-" * 60)

        # Format input
        input_text = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST] "
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract response after [/INST]
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()

        print(f"AI: {response}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Diabetes Companion AI Training")
    parser.add_argument("--action", choices=["train", "test"], default="train")
    parser.add_argument("--base-model", default="mistralai/Mistral-7B-Instruct-v0.3")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("models/diabetes-companion-lora"))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lora-r", type=int, default=32)

    args = parser.parse_args()

    config = TrainingConfig(
        base_model=args.base_model,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
    )

    if args.action == "train":
        train(config)
    else:
        test(config)


if __name__ == "__main__":
    main()
