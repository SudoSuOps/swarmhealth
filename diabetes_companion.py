"""
Diabetes Companion AI - Inference Module

Built by someone who lives it. For those who need it.
"""

import torch
from pathlib import Path
from typing import Optional


class DiabetesCompanion:
    """
    A compassionate AI companion for people living with diabetes.

    Usage:
        companion = DiabetesCompanion()
        response = companion.chat("I'm struggling with my blood sugar today")
        print(response)
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        base_model: str = "mistralai/Mistral-7B-Instruct-v0.3",
        use_4bit: bool = True,
        device: str = "auto",
    ):
        """
        Initialize the Diabetes Companion.

        Args:
            model_path: Path to LoRA adapter (default: models/diabetes-companion-lora)
            base_model: Base model to use
            use_4bit: Use 4-bit quantization for lower memory usage
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel

        # Find model path
        if model_path is None:
            model_path = Path(__file__).parent / "models" / "diabetes-companion-lora"
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please download the model or specify the correct path."
            )

        print(f"Loading Diabetes Companion from {model_path}...")

        # Load system prompt
        system_prompt_path = model_path / "system_prompt.txt"
        if system_prompt_path.exists():
            self.system_prompt = system_prompt_path.read_text().strip()
        else:
            self.system_prompt = (
                "You are a compassionate Diabetes Companion AI. "
                "You understand the daily challenges of living with diabetes."
            )

        # Quantization config
        if use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
        else:
            bnb_config = None

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map=device,
            torch_dtype=torch.float16,
        )

        # Load LoRA adapter
        self.model = PeftModel.from_pretrained(self.model, model_path)
        self.model.eval()

        # Conversation history
        self.history = []

        print("Diabetes Companion ready.")

    def chat(
        self,
        message: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Send a message and get a response.

        Args:
            message: Your message to the companion
            max_new_tokens: Maximum length of response
            temperature: Creativity (0.0-1.0, higher = more creative)
            top_p: Nucleus sampling parameter

        Returns:
            The companion's response
        """
        # Build conversation
        self.history.append({"role": "user", "content": message})

        # Format for Mistral
        if len(self.history) == 1:
            # First message includes system prompt
            input_text = f"<s>[INST] {self.system_prompt}\n\n{message} [/INST] "
        else:
            # Continuing conversation
            input_text = "<s>"
            for i, turn in enumerate(self.history):
                if turn["role"] == "user":
                    if i == 0:
                        input_text += f"[INST] {self.system_prompt}\n\n{turn['content']} [/INST] "
                    else:
                        input_text += f"[INST] {turn['content']} [/INST] "
                else:
                    input_text += f"{turn['content']}</s>"

            # Remove trailing </s> if present and add space for new response
            if input_text.endswith("</s>"):
                input_text = input_text[:-4] + " "

        # Tokenize
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the new response
        if "[/INST]" in full_response:
            response = full_response.split("[/INST]")[-1].strip()
        else:
            response = full_response

        # Clean up any remaining special tokens
        response = response.replace("</s>", "").strip()

        # Add to history
        self.history.append({"role": "assistant", "content": response})

        return response

    def clear_history(self):
        """Clear conversation history to start fresh."""
        self.history = []
        print("Conversation cleared.")

    def get_history(self) -> list:
        """Get the full conversation history."""
        return self.history.copy()


def main():
    """Interactive chat demo."""
    print("=" * 60)
    print("Diabetes Companion AI")
    print("Built by someone who lives it. For those who need it.")
    print("=" * 60)
    print()
    print("Type your message and press Enter.")
    print("Type 'quit' to exit, 'clear' to start a new conversation.")
    print()

    companion = DiabetesCompanion()
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("\nTake care of yourself. You're doing great.")
                break

            if user_input.lower() == 'clear':
                companion.clear_history()
                print()
                continue

            response = companion.chat(user_input)
            print(f"\nCompanion: {response}\n")

        except KeyboardInterrupt:
            print("\n\nTake care of yourself. You're doing great.")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
