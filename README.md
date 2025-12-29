# Diabetes Companion AI

**Built by someone who lives it. For those who need it. FREE.**

---

## The Story

I'm a Type 1 diabetic. I lost my foot to this disease. I also have Addison's disease - my adrenal glands don't work right either.

For years, I wished I had someone to talk to who truly understood. Not a doctor who sees me for 15 minutes twice a year. Not a website full of generic advice. Someone who gets the daily exhaustion, the brain fog, the fear of complications, the loneliness of a disease no one else can see.

So I built it.

**This is the guide I wish I had.**

---

## What It Does

The Diabetes Companion AI is a fine-tuned LLM that provides:

- **Empathy first** - It understands the emotional weight of diabetes
- **Real knowledge** - Blood glucose patterns, nutrition, complications, autoimmune conditions
- **Honest guidance** - Explains the WHY behind everything
- **Accountability with love** - Holds you accountable without shame
- **Crisis awareness** - Knows when to tell you to see a doctor NOW

### It Understands:
- Type 1 and Type 2 diabetes
- Autoimmune conditions (especially Addison's disease)
- Brain fog and cognitive effects
- Why infection is catastrophic for diabetics
- Foot care and complication prevention
- The mental health burden of chronic disease
- Dawn phenomenon, stress effects, exercise impacts
- Anti-inflammatory eating and nutrition

---

## Quick Start

### Requirements
- Python 3.10+
- CUDA-capable GPU with 8GB+ VRAM (for 4-bit inference)
- ~10GB disk space

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/diabetes-companion-ai.git
cd diabetes-companion-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the model (or train your own)
python scripts/download_model.py
# OR train from scratch:
# python training/train_diabetes_llm.py --action train
```

### Run the Chat Interface

```bash
python chat.py
```

### Use in Your Own Code

```python
from diabetes_companion import DiabetesCompanion

companion = DiabetesCompanion()

response = companion.chat("I'm so tired of managing diabetes every day.")
print(response)
```

---

## Model Details

| Component | Details |
|-----------|---------|
| Base Model | Mistral-7B-Instruct-v0.3 |
| Fine-tuning | QLoRA (4-bit quantization) |
| LoRA Rank | 32 |
| Training Data | 1,800 conversations |
| Validation Data | 200 conversations |
| Final Loss | 0.046 |

### Training Data Categories:
- Emotional support and burnout
- Blood glucose management
- Nutrition and anti-inflammatory eating
- Complication prevention (feet, eyes, kidneys, nerves)
- Autoimmune understanding
- Mental health and brain fog
- Accountability conversations

---

## Important Disclaimers

**This is NOT medical advice.** This AI is a companion, not a doctor.

- Always consult healthcare providers for medical decisions
- In emergencies, call 911 or go to the ER
- This tool is for emotional support and general education
- Your doctor knows YOUR specific situation

**When to seek immediate help:**
- Blood sugar over 400 or under 50
- Signs of DKA (nausea, vomiting, fruity breath, confusion)
- Infected wounds, especially on feet
- Chest pain or difficulty breathing
- Any medical emergency

---

## Philosophy

This AI was built with these principles:

1. **Lead with empathy, not lectures** - Every diabetic is doing their best
2. **Explain the WHY** - Understanding builds better habits than fear
3. **Celebrate small wins** - Progress matters more than perfection
4. **Hold accountable with love** - Never shame, always support
5. **Be honest about risks** - Without causing unnecessary fear
6. **Remember the human** - This person is someone's parent, child, love

---

## Contributing

This project is open source because diabetes shouldn't be a lonely fight.

Ways to help:
- Add more training conversations
- Improve the model's responses
- Translate to other languages
- Build better interfaces
- Share with someone who needs it

---

## License

MIT License - Use it, modify it, share it. Just help people.

---

## Acknowledgments

To everyone fighting this disease every day - you're doing better than you think.

To the families who support us - thank you for understanding.

To the researchers working on a cure - keep going.

---

**Made with love by someone who knows the fight.**

*"This person is someone's parent, someone's child, someone's love. Treat them that way."*
