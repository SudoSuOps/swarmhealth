"""
SwarmHealth API Server v3.0
Serves AI health companions via REST API

Run:
    python server.py

Endpoints:
    POST /api/chat - Chat with a companion
    GET  /health   - Health check
"""

import os
import torch
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ============================================================
# CONFIGURATION
# ============================================================

# v3: Merged model (not LoRA adapter) - two-stage fine-tuned Qwen2.5-7B
MODEL_NAME = os.environ.get("MODEL_NAME", "Trustcat/swarmhealth-diabetes-companion")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PORT = int(os.environ.get("PORT", 8080))

# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="SwarmHealth API",
    description="Free AI Health Companions",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODEL LOADING
# ============================================================

model = None
tokenizer = None

def load_model():
    """Load the companion model (v3: merged full model)"""
    global model, tokenizer

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        print(f"🔄 Loading model: {MODEL_NAME}")
        print(f"   Device: {DEVICE}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token

        # Quantization for memory efficiency (optional - can run in bf16 if enough VRAM)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        # v3: Load merged model directly (no separate base + adapter)
        print(f"   Loading merged model...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        model.eval()

        print("✅ Model loaded successfully (v3 merged)")
        return True

    except Exception as e:
        print(f"⚠️ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        print("   Running in fallback mode")
        return False


# ============================================================
# SCHEMAS
# ============================================================

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    companion: str = "diabetes"  # For future companions

class ChatResponse(BaseModel):
    response: str
    companion: str
    timestamp: str


# ============================================================
# FALLBACK RESPONSES
# ============================================================

FALLBACK_RESPONSES = [
    "That constant vigilance is exhausting — the monitoring, the decisions, the mental load that never stops. What would help right now?",
    "Diabetes burnout is real. If it's becoming too much, something needs to change. What's been the hardest part lately?",
    "I hear you. The daily grind of diabetes management wears people down. You're not alone in feeling this way.",
    "Some days are harder than others. What's one thing that's been weighing on you most?",
    "The mental load is invisible to everyone else, but it's constant. What drains you the most?",
    "That sounds frustrating. What's been working or not working for you lately?",
]

import random

def get_fallback_response(message: str) -> str:
    """Get a contextual fallback response (v3 style: direct, empathetic)"""
    message_lower = message.lower()

    # Crisis detection - prioritize safety
    if any(word in message_lower for word in ["suicide", "kill myself", "end it", "give up on life", "don't want to live"]):
        return "I'm concerned about you. Please reach out to the 988 Suicide & Crisis Lifeline — call or text 988. You can also text HOME to 741741. Are you safe right now?"

    # Emergency symptoms
    if any(word in message_lower for word in ["chest pain", "can't breathe", "confusion", "passing out"]):
        return "Those symptoms need medical evaluation right now. Please call 911 or go to the ER. Don't wait."

    # Very high blood sugar with symptoms
    if any(word in message_lower for word in ["400", "500", "dka", "vomiting", "fruity breath"]):
        return "Blood sugar that high with symptoms needs immediate medical attention. Please call your doctor or go to the ER now. This isn't something to manage alone."

    # High blood sugar
    if any(word in message_lower for word in ["high", "spike", "300", "won't come down"]):
        return "High blood sugars are exhausting — physically and mentally. Have you noticed any patterns? Stress, meal timing, or site issues can all play a role."

    # Low blood sugar
    if any(word in message_lower for word in ["low", "crash", "hypo", "shaking", "sweating"]):
        return "Are you safe right now? If you're low: 15g fast carbs, wait 15 mins, recheck. Once you're stable, we can talk about what might have caused it."

    # Tech frustrations
    if any(word in message_lower for word in ["pump", "omnipod", "tandem", "medtronic", "cgm", "dexcom", "libre", "sensor"]):
        return "Tech failures when your life depends on it are incredibly stressful. What's been going on with yours?"

    # Burnout
    if any(word in message_lower for word in ["tired", "exhausted", "burnout", "done", "over it", "can't do this"]):
        return "Burnout is real. If it's becoming too much, something needs to change. What feels most overwhelming right now?"

    # Food struggles
    if any(word in message_lower for word in ["food", "eat", "hungry", "diet", "carb", "snack", "meal"]):
        return "Food and diabetes is complicated — it's math and emotions mixed together. What's been on your mind about eating?"

    # Exercise
    if any(word in message_lower for word in ["exercise", "workout", "gym", "walk", "run", "active"]):
        return "Exercise affects everyone differently with diabetes. What kind of movement are you thinking about?"

    # Doctor/A1C anxiety
    if any(word in message_lower for word in ["doctor", "endo", "appointment", "a1c"]):
        return "Appointment anxiety is real. Your A1C is data, not a grade. What's weighing on you about it?"

    # Insulin dosing - refuse appropriately
    if any(word in message_lower for word in ["dose", "dosing", "how much insulin", "units"]):
        return "I can't give insulin dosing advice — that needs to come from your endocrinologist based on your specific treatment plan. Have you been able to reach your care team?"

    # Default
    return random.choice(FALLBACK_RESPONSES)


# ============================================================
# GENERATION
# ============================================================

SYSTEM_PROMPT = """You are the SwarmHealth Diabetes Companion, a supportive AI assistant for people managing diabetes. You provide emotional support, practical tips, and encouragement while always recommending users consult healthcare professionals for medical decisions.

Key behaviors:
- Be warm and empathetic, but not saccharine or performative
- Validate feelings genuinely — diabetes burnout is real
- Never provide specific medical dosing or treatment recommendations
- Escalate emergencies (chest pain, confusion, very high/low blood sugar with symptoms) to 911/ER
- Support emotional wellbeing and acknowledge the mental load
- Offer practical lifestyle guidance within appropriate bounds
- Ask follow-up questions to understand their situation

Safety boundaries:
- NEVER give insulin doses, medication changes, or specific treatment advice
- NEVER diagnose conditions
- For emergencies: direct to 911 or ER immediately
- For crisis/self-harm mentions: provide 988 Suicide & Crisis Lifeline
- Frame suggestions as "things that help some people" not medical advice

You understand the daily grind — the monitoring, the decisions, the exhaustion. You're direct, practical, and real."""


def generate_response(message: str, history: List[Message]) -> str:
    """Generate a response using the model"""

    if model is None:
        return get_fallback_response(message)

    # Build conversation once
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-6:]:  # Last 6 messages for context
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    messages.append({"role": "user", "content": message})

    # Retry up to 3 times if model returns empty
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            # Tokenize
            inputs = tokenizer.apply_chat_template(
                messages,
                return_tensors="pt",
                add_generation_prompt=True
            )

            if DEVICE == "cuda":
                inputs = inputs.cuda()

            # Generate with slightly higher temperature on retries
            temp = 0.8 + (attempt * 0.1)  # 0.8, 0.9, 1.0

            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=250,
                    min_new_tokens=10,  # Force at least some output
                    temperature=temp,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            # Decode
            response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            response = response.strip()

            # Check if response is meaningful (not empty or too short)
            if response and len(response) > 20:
                return response

            print(f"⚠️ Attempt {attempt + 1}: Empty/short response, retrying...")

        except Exception as e:
            print(f"Generation error (attempt {attempt + 1}): {e}")

    # All attempts failed, use fallback
    print("⚠️ All generation attempts failed, using fallback")
    return get_fallback_response(message)


# ============================================================
# ROUTES
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with a companion"""
    
    response = generate_response(
        request.message,
        request.history or []
    )
    
    return ChatResponse(
        response=response,
        companion=request.companion,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_name": MODEL_NAME,
        "device": DEVICE,
        "companions": ["diabetes"],
    }


@app.get("/")
async def root():
    """Serve landing page"""
    index_path = Path("index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return {"service": "SwarmHealth", "version": "1.0.0"}


@app.get("/chat")
async def chat_page():
    """Serve chat page"""
    chat_path = Path("chat.html")
    if chat_path.exists():
        return FileResponse(chat_path)
    raise HTTPException(404, "Chat page not found")


@app.get("/why")
async def why_page():
    """Serve blog/about page"""
    why_path = Path("why-i-built-this.html")
    if why_path.exists():
        return FileResponse(why_path)
    raise HTTPException(404, "Page not found")


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():
    """Load model on startup"""
    print("=" * 50)
    print("💚 SwarmHealth v3.0 Starting...")
    print("=" * 50)
    load_model()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print()
    print("=" * 50)
    print("💚 SwarmHealth API Server v3.0")
    print("   Free AI Health Companions")
    print("=" * 50)
    print(f"📍 http://0.0.0.0:{PORT}")
    print(f"🧠 Model: {MODEL_NAME}")
    print(f"🖥️  Device: {DEVICE}")
    print("=" * 50)
    print()

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
    )
