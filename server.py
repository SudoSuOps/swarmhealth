"""
SwarmHealth API Server
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

MODEL_NAME = os.environ.get("MODEL_NAME", "swarmhealth/diabetes-companion")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PORT = int(os.environ.get("PORT", 8080))

# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="SwarmHealth API",
    description="Free AI Health Companions",
    version="1.0.0",
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
    """Load the companion model"""
    global model, tokenizer
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print(f"🔄 Loading model: {MODEL_NAME}")
        print(f"   Device: {DEVICE}")
        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto" if DEVICE == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        model.eval()
        
        print("✅ Model loaded successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to load model: {e}")
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
    "I hear you. Managing diabetes is a constant job, and it's okay to feel exhausted by it sometimes. What's been weighing on you the most?",
    "That sounds really frustrating. The ups and downs of blood sugar can be so unpredictable. How are you taking care of yourself today?",
    "Thank you for sharing that with me. You're not alone in feeling this way—diabetes burnout is real. What would help you feel a little better right now?",
    "I understand. Some days are harder than others with diabetes. Remember that you're doing your best, even when it doesn't feel like it. What's one small win you've had recently?",
    "It sounds like you're going through a tough time. The mental load of diabetes is often invisible to others, but it's very real. Would you like to talk more about what's happening?",
    "I'm sorry you're dealing with this. Diabetes can feel relentless sometimes. Is there anything specific I can help you think through?",
    "That makes total sense. The constant monitoring and adjustments can be overwhelming. How long have you been feeling this way?",
    "I get it. Some days diabetes just... wins. And that's okay. Tomorrow is a new day. What usually helps you reset?",
]

import random

def get_fallback_response(message: str) -> str:
    """Get a contextual fallback response"""
    message_lower = message.lower()
    
    # Context-specific responses
    if any(word in message_lower for word in ["high", "spike", "300", "400"]):
        return "High blood sugars are so frustrating, especially when you can't figure out why. Have you been able to identify any patterns, or does it feel random?"
    
    if any(word in message_lower for word in ["low", "crash", "hypo", "shaking"]):
        return "Lows are scary. That shaky, urgent feeling is the worst. Are you okay right now? Make sure you've treated it if you haven't already. 💚"
    
    if any(word in message_lower for word in ["pump", "omnipod", "tandem", "medtronic"]):
        return "Pump issues can be so frustrating—when your lifeline doesn't work right, it's stressful. What's been going on with it?"
    
    if any(word in message_lower for word in ["cgm", "dexcom", "libre", "sensor"]):
        return "CGM problems are the worst, especially when you're relying on it to keep you safe. Is it a sensor issue or something else?"
    
    if any(word in message_lower for word in ["tired", "exhausted", "burnout", "done"]):
        return "Diabetes burnout is real, and it's okay to acknowledge when you're running on empty. You've been doing this 24/7 with no days off. What would taking a mental break look like for you?"
    
    if any(word in message_lower for word in ["doctor", "endo", "appointment", "a1c"]):
        return "Medical appointments can bring up a lot of emotions—anxiety about numbers, feeling judged, or just the exhaustion of explaining everything again. How are you feeling about it?"
    
    # Default to random supportive response
    return random.choice(FALLBACK_RESPONSES)


# ============================================================
# GENERATION
# ============================================================

SYSTEM_PROMPT = """You are a supportive companion for someone living with diabetes. You understand the daily challenges—the blood sugar swings, the constant monitoring, the technology frustrations, the mental load, and the burnout.

Your role is to:
- Listen with empathy and understanding
- Validate their feelings and experiences
- Offer emotional support
- Share that they're not alone

You must NEVER:
- Give medical advice
- Suggest insulin doses or medication changes
- Diagnose conditions
- Replace their healthcare team

Always be warm, supportive, and understanding. Use a conversational tone like talking to a friend who gets it."""


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


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():
    """Load model on startup"""
    print("=" * 50)
    print("💚 SwarmHealth Starting...")
    print("=" * 50)
    load_model()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print()
    print("=" * 50)
    print("💚 SwarmHealth API Server")
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
