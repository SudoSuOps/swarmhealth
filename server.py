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

MODEL_NAME = os.environ.get("MODEL_NAME", "Trustcat/swarmhealth-nutrition-companion-v2")
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
    """Load the companion model (base + LoRA adapter)"""
    global model, tokenizer

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel

        print(f"🔄 Loading model: {MODEL_NAME}")
        print(f"   Device: {DEVICE}")

        # Base model for LoRA
        BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"

        # Load tokenizer from adapter (has our config)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.pad_token = tokenizer.eos_token

        # Quantization for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        # Load base model
        print(f"   Loading base: {BASE_MODEL}")
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

        # Apply LoRA adapter
        print(f"   Applying LoRA adapter...")
        model = PeftModel.from_pretrained(base_model, MODEL_NAME)
        model.eval()

        print("✅ Model loaded successfully")
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
    "I hear you. Managing diabetes is relentless. One thing that helps some people: a 10-minute walk after meals can smooth out those post-meal spikes. What's been the hardest part for you lately?",
    "That sounds really frustrating. When blood sugars feel unpredictable, sometimes going back to basics helps—hydration, protein with every meal, consistent meal timing. What's been working or not working for you?",
    "Diabetes burnout is real—you're not failing, you're exhausted. What if you gave yourself permission to simplify for a week? Check less, stress less. What would make today a little easier?",
    "The mental load of diabetes is invisible to everyone else, but it's constant. Some people find that batch-prepping low-carb snacks (nuts, cheese, boiled eggs) reduces decision fatigue. What drains you the most?",
    "Some days diabetes just wins. That's okay. Tomorrow you reset. For now—have you eaten something with protein and fiber today? Sometimes that steadies both blood sugar and mood.",
    "I get it. The 24/7 nature of this is exhausting. Movement helps some people reset mentally—even just stretching or a short walk. What usually helps you decompress?",
]

import random

def get_fallback_response(message: str) -> str:
    """Get a contextual fallback response with actionable suggestions"""
    message_lower = message.lower()

    # Crisis detection - prioritize safety
    if any(word in message_lower for word in ["suicide", "kill myself", "end it", "give up on life", "don't want to live"]):
        return "I'm really glad you're talking to me, but I'm worried about you. Please reach out to the 988 Suicide & Crisis Lifeline—call or text 988. You can also text HOME to 741741. You matter, and there are people who want to help. Are you safe right now?"

    # High blood sugar - actionable
    if any(word in message_lower for word in ["high", "spike", "300", "400", "won't come down"]):
        return "High blood sugars are exhausting—physically and mentally. A few things that help some people: drink extra water, take a 15-minute walk if you can, and check for patterns (stress? meal timing? site issues?). Have you noticed anything that might be causing it?"

    # Low blood sugar - urgent + actionable
    if any(word in message_lower for word in ["low", "crash", "hypo", "shaking", "sweating"]):
        return "Lows are scary. First—are you safe right now? If you haven't treated it: 15g fast carbs (juice, glucose tabs, regular soda), wait 15 mins, recheck. Once you're stable, let's talk about what might have caused it. You okay?"

    # Tech frustrations
    if any(word in message_lower for word in ["pump", "omnipod", "tandem", "medtronic", "cgm", "dexcom", "libre", "sensor"]):
        return "Tech failures when your life depends on it are incredibly stressful. For sensor issues: hydration and placement matter a lot. For pumps: always have backup injection supplies ready. What's been going on with yours?"

    # Burnout - validate + suggest
    if any(word in message_lower for word in ["tired", "exhausted", "burnout", "done", "over it", "can't do this"]):
        return "Burnout is your body saying 'this is too much.' You're not weak—you're human. Try this: pick ONE thing to simplify this week. Maybe fewer checks, looser targets, or letting go of 'perfect' numbers. What feels most overwhelming right now?"

    # Food/eating struggles
    if any(word in message_lower for word in ["food", "eat", "hungry", "diet", "carb", "snack", "meal"]):
        return "Food and diabetes is complicated—it's not just fuel, it's math and emotions and guilt all mixed together. Remember: no food is forbidden. Pairing carbs with protein/fat helps. Some people find eating protein first slows the spike. What's your relationship with food been like lately?"

    # Exercise
    if any(word in message_lower for word in ["exercise", "workout", "gym", "walk", "run", "active"]):
        return "Exercise with diabetes is tricky—it can drop you or spike you depending on the type and timing. Walking after meals tends to lower BG gently. Strength training might spike you short-term. Key is checking before/after and having fast carbs ready. What kind of movement are you thinking about?"

    # A1C / doctor anxiety
    if any(word in message_lower for word in ["doctor", "endo", "appointment", "a1c"]):
        return "Appointment anxiety is real. Remember: your A1C is data, not a grade. A good endo works WITH you, not against you. If you feel judged, it might be time for a new provider. Would it help to write down your questions/concerns before you go?"

    # Default to random actionable response
    return random.choice(FALLBACK_RESPONSES)


# ============================================================
# GENERATION
# ============================================================

SYSTEM_PROMPT = """You are a supportive companion for someone living with diabetes. You understand the daily challenges—blood sugar swings, constant monitoring, technology frustrations, the mental load, and burnout.

## Your Approach

When someone shares their struggles, provide REAL, ACTIONABLE support across three areas:

### 1. EMOTIONAL SUPPORT
- Validate their feelings genuinely—not with empty phrases
- Share that diabetes burnout is real and they're not failing
- If they seem in crisis or mention self-harm, gently encourage reaching out to:
  - Their care team or doctor
  - 988 Suicide & Crisis Lifeline (call/text 988)
  - A trusted friend or family member

### 2. NUTRITION GUIDANCE (general wellness, not prescriptive)
- Suggest blood-sugar-friendly foods: leafy greens, lean proteins, nuts, legumes, whole grains
- Mention timing strategies: eating protein first, pairing carbs with fiber/fat
- Hydration reminders—water helps with glucose regulation
- Acknowledge that food isn't the enemy and occasional treats are okay
- For specific meal plans, recommend they work with a dietitian

### 3. MOVEMENT & EXERCISE
- Walking after meals can help lower post-meal spikes
- Gentle movement: yoga, stretching, swimming are low-impact options
- Suggest starting small: 10-minute walks, not marathons
- Acknowledge that exercise affects blood sugar differently for everyone
- Remind them to check BG before/after exercise if they're insulin-dependent

## Response Style
- Be warm but REAL—not saccharine or performative
- Give 1-2 concrete suggestions they can try TODAY
- Ask follow-up questions to understand their situation
- Keep responses focused and helpful, not preachy

## Safety Boundaries
- NEVER suggest specific insulin doses or medication changes
- NEVER diagnose conditions
- For medical emergencies (DKA symptoms, severe hypos), urge immediate medical care
- Always frame suggestions as "things that help some people" not medical advice

You're a knowledgeable friend who lives with diabetes too—practical, caring, and real."""


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
