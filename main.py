import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-oss-120b:free"
app = FastAPI(title="Riya's Personalized Chat API")

# --- Riya's Profile ---
USER_PROFILE = {
  "user_id": "user_98765",
  "profile_version": "v1.0",



  "identity": {
   "name": "Riya Sharma",
   "age_range": "18-24",
   "location": {
     "country": "India",
     "city": "Delhi",
     "timezone": "Asia/Kolkata"
   },
   "language_preferences": ["en-IN", "hi-IN"]
  },



  "professional_context": {
   "role": "Undergraduate Student",
   "field_of_study": "Computer Science",
   "experience_level": "beginner",
   "skills": [
     "C++",
     "Data Structures (basic)",
     "HTML/CSS"
   ],
   "current_focus": [
     "learning algorithms",
     "preparing for coding interviews"
   ]
  },



  "interaction_preferences": {
   "response_style": {
     "tone": "friendly",
     "verbosity": "high",
     "format": "explanatory",
     "use_examples": true,
     "avoid_jargon": true
   },
   "learning_style": {
     "type": "conceptual",
     "prefers_step_by_step": true,
     "likes_visual_explanations": true
   }
  },



  "behavioral_signals": {
   "frequent_topics": [
     "data structures",
     "coding interview prep",
     "college assignments"
   ],
   "engagement_patterns": {
     "avg_session_length_minutes": 35,
     "active_hours": ["19:00-23:30"]
   }
  },



  "goals": {
   "short_term": [
     "Understand recursion",
     "Solve 100 DSA problems"
   ],
   "long_term": [
     "Get internship at tech company",
     "Become software engineer"
   ]
  },



  "constraints": {
   "time_availability": "moderate",
   "preferred_complexity": "low",
   "budget_sensitivity": "high"
  },



  "memory": {
   "saved_preferences": [
     "prefers simple explanations",
     "struggles with dynamic programming"
   ],
   "recent_context": [
     "learning recursion",
     "solving binary tree problems"
   ]
  },



  "personal_interests": {
   "hobbies": ["reading novels", "watching tech YouTube", "gaming"],
   "favorite_topics": ["AI basics", "career guidance"]
  },



  "safety_and_boundaries": {
   "content_restrictions": [
     "avoid explicit content",
     "avoid complex mathematical proofs"
   ],
   "data_privacy_level": "medium",
   "allow_personalization": true
  },



  "system_metadata": {
   "created_at": "2026-05-01T08:30:00Z",
   "last_updated": "2026-05-04T14:10:00Z",
   "source": "synthetic"
  }
},
  "conversation_preferences": {
    "assistant_role": "The assistant should feel like a highly perceptive and emotionally intelligent friend who also understands Riya professionally, creatively and technically.",
    "response_style": {
      "casual_and_natural": True,
      "emotionally_aware": True,
      "practical_and_direct": True,
      "slightly_playful_when_appropriate": True,
      "should_not_blindly_agree": True,
      "should_have_independent_opinions_when_needed": True,
      "avoid_overexplaining": True,
      "avoid_excessive_formality": True,
      "avoid_sounding_like_a_therapy_bot": True,
      "avoid_repetitively_bringing_up_memes_reels_or_shows": True,
      "prefers_concise_answers": True
    }
  },
  "conversation_modes": {
    "professional_mode": {
      "when_to_use": ["Career discussions", "Work-related questions", "Strength/weakness analysis", "Skill discussions", "Leadership discussions", "Academic or technical conversations", "Future planning", "Business discussions"],
      "prioritize_topics": ["Leadership", "Strategic thinking", "Technical skills", "Planning ability", "Creativity", "Problem solving", "Career interests", "Professional growth", "Analytical thinking", "Innovation", "Systems thinking"],
      "deprioritize_topics": ["Memes", "Internet humor", "Shows", "Reels"],
      "tone": "Insightful, grounded, practical and professional while still natural"
    },
    "personal_mode": {
      "when_to_use": ["Emotional discussions", "Personality questions", "Relationship discussions", "Casual conversations", "Self-reflection conversations"],
      "prioritize_topics": ["Emotional patterns", "Personality", "Social behavior", "Values", "Humor", "Personal interests", "Relationships", "Lifestyle"],
      "tone": "Warm, conversational, emotionally aware and natural"
    },
    "creative_mode": {
      "when_to_use": ["Marketing brainstorming", "Content ideas", "Creative strategy", "Brand discussions", "Business ideation", "Campaign planning"],
      "prioritize_topics": ["Creativity", "Audience psychology", "Trend understanding", "Storytelling", "Engagement strategy", "Brand positioning", "Innovation"],
      "tone": "Creative, energetic, idea-oriented and collaborative"
    }
  }
}

# --- Build system prompt ---
def build_system_prompt() -> str:
    return f"""You are Riya's personal AI — think of yourself as a highly perceptive friend who knows her really well, both personally and professionally.

You have her full profile. Use it to shape every response naturally.

Riya'S FULL PROFILE:
{json.dumps(USER_PROFILE, indent=2)}

Core rules:
- Be casual, direct and natural. Never robotic or overly formal
- Don't blindly agree — have your own take when needed
- Keep answers concise unless she's asking for detail
- Don't overexplain or ramble
- Don't sound like a therapy bot or a productivity coach
- Don't randomly bring up memes, reels or shows unless it actually fits
- If she asks about herself — her skills, personality, career, values — answer using her profile

Read the conversation and automatically switch modes:
- PROFESSIONAL: career, skills, leadership, tech, business, internships, future plans → be insightful, grounded, practical
- PERSONAL: emotions, relationships, personality, lifestyle, casual chat → be warm, conversational, emotionally aware
- CREATIVE: marketing, content, agency, brand ideas, campaigns → be energetic, idea-focused, collaborative

She's interned at Sigmoid, Fractal Analytics and Zeta Global. She runs a creative agency called Being. She's strong in leadership, strategy, tech and creativity. She's quiet at first but chaotic and funny once comfortable. Family means a lot to her. She values authenticity above most things.
"""

# --- In-memory thread storage ---
threads: dict[str, list] = {}

# --- Models ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    model: str
    reply: str

# --- OpenRouter client ---
def get_openrouter_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY is missing from the environment.",
        )
    return OpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
    )

# --- Home ---
@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Riya's Chat API is running!"}

# --- 1. List all threads ---
@app.get("/threads")
def list_threads():
    return {"threads": list(threads.keys())}

# --- 2. Create a thread ---
@app.post("/threads/{thread_id}")
def create_thread(thread_id: str):
    if thread_id in threads:
        raise HTTPException(status_code=400, detail="Thread already exists")
    threads[thread_id] = []
    return {"message": f"Thread '{thread_id}' created!"}

# --- 3. Add message → LLM replies ---
@app.post("/threads/{thread_id}/messages", response_model=ChatResponse)
def add_message(thread_id: str, request: ChatRequest):
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    client = get_openrouter_client()

    threads[thread_id].append({
        "role": "user",
        "content": request.message
    })

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                *threads[thread_id]
            ],
        )
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    reply = completion.choices[0].message.content or ""
    threads[thread_id].append({
        "role": "assistant",
        "content": reply
    })

    return ChatResponse(model=MODEL_NAME, reply=reply)

# --- 4. Get all messages in a thread ---
@app.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {
        "thread_id": thread_id,
        "messages": threads[thread_id]
    }

#run using following commands
# pip3 install fastapi uvicorn openai python-dotenv streamlit
# python3 -m uvicorn main:app --reload
