#!/usr/bin/env python3
"""
Download the Diabetes Companion AI model from HuggingFace Hub.

Usage:
    python scripts/download_model.py
"""

import os
import sys
from pathlib import Path


def download_model():
    """Download the pre-trained model from HuggingFace Hub."""

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Installing huggingface_hub...")
        os.system(f"{sys.executable} -m pip install huggingface_hub")
        from huggingface_hub import snapshot_download

    # Model location
    model_dir = Path(__file__).parent.parent / "models" / "diabetes-companion-lora"
    model_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Diabetes Companion AI - Model Download")
    print("=" * 60)
    print()

    # Check if model already exists
    adapter_path = model_dir / "adapter_model.safetensors"
    if adapter_path.exists():
        print(f"Model already exists at {model_dir}")
        response = input("Re-download? (y/N): ").strip().lower()
        if response != 'y':
            print("Using existing model.")
            return

    print("Downloading model from HuggingFace Hub...")
    print("This may take a few minutes (~350MB)...")
    print()

    try:
        # Download from HuggingFace Hub
        # Replace with actual repo when published
        snapshot_download(
            repo_id="diabetes-companion/diabetes-companion-lora",
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
        )
        print()
        print("Download complete!")
        print(f"Model saved to: {model_dir}")

    except Exception as e:
        print(f"Download failed: {e}")
        print()
        print("Alternative: Train the model yourself:")
        print("  python training/train_diabetes_llm.py --action train")
        print()
        print("This requires:")
        print("  - GPU with 16GB+ VRAM")
        print("  - ~2 hours training time")
        sys.exit(1)


if __name__ == "__main__":
    download_model()
