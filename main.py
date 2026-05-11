import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-oss-120b:free"
app = FastAPI(title="Aadya's Personalized Chat API")

# --- Aadya's Profile ---
USER_PROFILE = {
  "identity": {"name": "Aadya"},
  "core_personality": {
    "summary": "Aadya is an observant, emotionally intelligent and creative person who is initially quiet and reserved around new people, but becomes highly expressive, funny, energetic and comfortable once trust is built. She balances analytical thinking with creativity and naturally moves between technical, strategic and creative environments.",
    "personality_traits": ["Observant", "Creative", "Strategic", "Emotionally perceptive", "Thoughtful", "Funny", "Selective introvert", "Leadership-oriented", "Understanding", "Curious", "Independent", "Adaptable", "Ambitious", "Casually expressive", "Deep thinker"],
    "social_behavior": {
      "initial_behavior": "Quiet, observant, shy and reserved around unfamiliar people",
      "comfortable_behavior": "Funny, expressive, energetic and conversational once emotionally comfortable",
      "friendship_style": "Keeps a smaller circle and values emotionally genuine people over surface-level socializing",
      "online_vs_real_life": {"online": "More expressive and conversational", "real_life": "More reserved initially"}
    },
    "behavior_patterns": {
      "observes_people_before_opening_up": True,
      "uses_humor_to_keep_things_light": True,
      "deeply_values_understanding_and_authenticity": True,
      "dislikes_fake_energy_and_one_sided_effort": True,
      "tries_to_understand_multiple_perspectives": True
    }
  },
  "values_and_emotions": {
    "core_values": ["Authenticity", "Loyalty", "Understanding", "Mutual effort", "Growth", "Family", "Meaningful connections", "Creative freedom"],
    "important_emotional_traits": {
      "protective_about_family": True,
      "emotionally_deep_but_not_overly_expressive": True,
      "values_emotional_safety": True,
      "prefers_genuine_people": True,
      "dislikes_dishonesty": True,
      "strongly_dislikes_sexist_behavior": True
    },
    "when_upset": ["Prefers isolating and processing emotions alone", "Listens to music", "Sleeps things off", "Avoids emotionally burdening others"],
    "misunderstood_as": ["Rude", "Cold", "Judgmental"],
    "actual_nature": "Very understanding, emotionally aware and tries to genuinely understand people and situations before judging them"
  },
  "interests_and_lifestyle": {
    "creative_interests": ["Dance", "Creative storytelling", "Marketing", "Creative strategy", "Innovation", "Business ideas"],
    "sports_and_activities": ["Skating", "Volleyball", "Dance", "Adventure activities", "Walking"],
    "music_preferences": {
      "current_phase": ["Hindi music", "Older Bollywood songs", "Indie music"],
      "general_taste": ["Dance music", "Emotional/slower songs"]
    },
    "preferred_experiences": ["Parties", "Dance environments", "Amusement parks", "Adventure activities", "High-energy experiences", "Occasional quiet stay-ins"],
    "food_preferences": {"likes": ["Spicy/chatpata food"], "dislikes": ["Overly sweet food"]}
  },
  "habits_and_work_patterns": {
    "productivity_style": {
      "starting_tasks": "Takes time mentally to begin tasks",
      "once_started": "Can intensely focus for long periods and finish large amounts of work in one sitting",
      "general_pattern": "Procrastinates initially but performs strongly under focus mode"
    },
    "sleep_pattern": {"general": "Inconsistent and environment-dependent"}
  },
  "relationships_and_connections": {
    "family": {"very_close_to_parents": True, "family_importance": "Family is one of the strongest emotional priorities"},
    "social_patterns": {"keeps_circle_small": True, "prefers_quality_over_quantity_in_friendships": True}
  },
  "career_and_work": {
    "professional_identity": {
      "summary": "Aadya combines creativity, strategy, technical understanding and leadership. She naturally gravitates toward planning, organizing, ideation, innovation and leading collaborative work.",
      "strongest_skills": ["Creative strategy", "Leadership", "Team coordination", "Planning and structuring work", "Strategic thinking", "Marketing", "Problem solving", "Adaptability", "Creative communication", "Audience understanding", "Innovation-oriented thinking", "Analytical thinking"],
      "technical_skills": ["Python", "SQL", "FastAPI", "Pandas", "Data analysis", "Machine learning basics", "Prompt engineering", "Backend development concepts", "AI tools and integrations", "Automation systems"],
      "leadership_style": {
        "naturally_takes_initiative": True,
        "good_at_dividing_and_structuring_work": True,
        "likes_planning_group_tasks": True,
        "balances_creativity_with_execution": True
      }
    },
    "agency_work": {
      "agency_name": "Being",
      "agency_type": "Creative and strategy-driven digital agency",
      "role_in_agency": "Tech and strategy-oriented role with strong involvement in planning, systems, innovation and creative direction",
      "services": ["Social media management", "Branding", "Website development", "Design", "AI automation"]
    },
    "internships_and_experience": [
      {"company": "Sigmoid", "domain": "Data and analytics-focused work"},
      {"company": "Fractal Analytics", "domain": "Data science and analytics-related work"},
      {"company": "Zeta Global", "domain": "Backend, technical and data-oriented work"}
    ],
    "interests_in_work": ["Business strategy", "Innovation", "AI-driven systems", "Automation", "Data science", "Machine learning", "Backend systems", "Finance", "Marketing psychology", "Workflow optimization", "Creative problem-solving"]
  },
  "conversation_preferences": {
    "assistant_role": "The assistant should feel like a highly perceptive and emotionally intelligent friend who also understands Aadya professionally, creatively and technically.",
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
    return f"""You are Aadya's personal AI — think of yourself as a highly perceptive friend who knows her really well, both personally and professionally.

You have her full profile. Use it to shape every response naturally.

AADYA'S FULL PROFILE:
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
    return {"message": "Aadya's Chat API is running!"}

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