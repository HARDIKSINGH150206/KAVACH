import os
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from .database import engine, get_db
from . import models
from .auth import get_current_user

load_dotenv()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediChain API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"))

class ChatRequest(BaseModel):
    session_id: str
    symptoms: str

class ChatResponse(BaseModel):
    message: str
    severity_level: int
    recommended_action: str

class SyncSessionData(BaseModel):
    session_id: str
    symptoms: str
    ai_response: str
    severity_level: int
    recommended_action: str

class SyncRequest(BaseModel):
    sessions: List[SyncSessionData]

SYSTEM_PROMPT = """You are a highly capable medical triage AI for 'MediChain', serving rural patients in India.
Your job is to analyze the patient's symptoms (which may be in English or Hindi) and determine the severity of the condition.
Look for red-flag symptoms (e.g., severe chest pain, prolonged high fever, difficulty breathing).

You MUST return a raw JSON response exactly in this format:
{
  "message": "A compassionate, clear response to the user in the language they used.",
  "severity_level": 1-5, // (1=Safe/Mild, 3=Monitor, 5=Emergency)
  "recommended_action": "Clear actionable step like 'Rest at home', 'Visit PHC tomorrow', or 'Call 108 immediately'"
}
Do not include markdown blocks, just the JSON string.
"""

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Call OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Symptoms: {req.symptoms}"}
            ],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        
        response_text = completion.choices[0].message.content
        ai_data = json.loads(response_text)
        
        # Save to database
        db_session = models.PatientSession(
            session_id=req.session_id,
            symptoms=req.symptoms,
            ai_response=ai_data.get("message", ""),
            severity_level=ai_data.get("severity_level", 1),
            recommended_action=ai_data.get("recommended_action", "")
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        return ChatResponse(
            message=ai_data.get("message", "We processed your symptoms."),
            severity_level=ai_data.get("severity_level", 1),
            recommended_action=ai_data.get("recommended_action", "Consult a doctor if symptoms persist.")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
def get_high_severity_sessions(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Doctor portal route to get critical cases."""
    # Fetch severity 4 and 5
    sessions = db.query(models.PatientSession).filter(models.PatientSession.severity_level >= 4).order_by(models.PatientSession.timestamp.desc()).all()
    return sessions

@app.post("/api/sync")
def sync_offline_sessions(req: SyncRequest, db: Session = Depends(get_db)):
    """Endpoint for the PWA to bulk sync offline triage data when internet is restored."""
    synced_count = 0
    for session_data in req.sessions:
        # Check if already exists to ensure idempotency
        existing = db.query(models.PatientSession).filter(models.PatientSession.session_id == session_data.session_id).first()
        if not existing:
            new_session = models.PatientSession(
                session_id=session_data.session_id,
                symptoms=session_data.symptoms,
                ai_response=session_data.ai_response,
                severity_level=session_data.severity_level,
                recommended_action=session_data.recommended_action
            )
            db.add(new_session)
            synced_count += 1
            
    db.commit()
    return {"status": "success", "synced_count": synced_count}

# For testing auth, you might want a simple token generation endpoint here, omitted for brevity.
