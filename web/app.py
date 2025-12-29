"""
SwarmHealth - Diabetes Companion Web Interface

Built by someone who lives it. For those who need it. FREE.

Run locally:
    python web/app.py

Deploy:
    Set environment variable CUDA_VISIBLE_DEVICES=0 (or appropriate GPU)
"""

import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr

# Global companion instance
companion = None


def load_model():
    """Load the model on first use."""
    global companion
    if companion is None:
        print("Loading Diabetes Companion AI...")
        from diabetes_companion import DiabetesCompanion
        companion = DiabetesCompanion()
        print("Model ready!")
    return companion


def chat(message: str, history: list) -> str:
    """Handle chat messages."""
    if not message.strip():
        return ""

    comp = load_model()

    # Clear history if this is a new conversation
    if not history:
        comp.clear_history()

    response = comp.chat(message)
    return response


def create_interface():
    """Create the Gradio interface."""

    # Build interface
    with gr.Blocks(
        title="SwarmHealth - Diabetes Companion",
    ) as demo:

        # Header
        gr.Markdown("""
        # 🩺 SwarmHealth - Diabetes Companion

        **Built by someone who lives it. For those who need it. FREE.**

        A compassionate AI companion that understands the daily challenges of living with diabetes.

        ---

        ⚠️ **Important:** This is NOT medical advice. Always consult your healthcare provider.
        In emergencies, call 911 or go to the ER.

        ---
        """)

        # Chat interface
        chatbot = gr.ChatInterface(
            fn=chat,
            examples=[
                "I'm so tired of managing diabetes every single day. It never ends.",
                "My blood sugar has been running high for a week. What should I do?",
                "Can you explain why brain fog happens with diabetes?",
                "I noticed a small cut on my foot and I'm worried.",
                "I have Type 1 diabetes and Addison's disease. Some days I can barely function.",
                "How does stress affect blood sugar?",
                "What should I know about diabetic eye exams?",
            ],
        )

        # Footer
        gr.Markdown("""
        ---

        ### About SwarmHealth

        SwarmHealth provides free, open-source AI companions for people living with chronic conditions.

        - 🔗 [GitHub](https://github.com/swarmhealth)
        - 🤗 [Model on HuggingFace](https://huggingface.co/Trustcat/swarmhealth-diabetes-companion)
        - 📜 MIT License - Use it, share it, help people

        ---

        *"This person is someone's parent, someone's child, someone's love. Treat them that way."*
        """)

    return demo


if __name__ == "__main__":
    # Pre-load model
    print("=" * 60)
    print("SwarmHealth - Diabetes Companion")
    print("Built by someone who lives it. For those who need it.")
    print("=" * 60)

    demo = create_interface()

    # Get port from environment or default
    port = int(os.environ.get("PORT", 7860))

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
    )
