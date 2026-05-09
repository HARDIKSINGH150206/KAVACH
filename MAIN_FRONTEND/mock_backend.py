from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "demo", "model_readiness": True}

@app.get("/config")
async def config():
    return {"audio_weight": 0.55, "sms_weight": 0.45, "audio_source_mode": "live"}

@app.websocket("/ws/threat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # 1. Send normal state first
        await websocket.send_text(json.dumps({
            "type": "audio", "gan_artifact_detected": False, "score": 0.12
        }))
        await websocket.send_text(json.dumps({
            "type": "fusion", "threat_score": 0.15
        }))
        
        await asyncio.sleep(5)
        
        # 2. Trigger the "2-Minute Wow" critical threat demo!
        await websocket.send_text(json.dumps({
            "type": "audio", 
            "gan_artifact_detected": True, 
            "score": 0.81
        }))
        
        await websocket.send_text(json.dumps({
            "type": "sms",
            "riskScore": 0.82,
            "text": "Aapka account block ho jayega! Turant kyc update karein http://sco.in/kyc",
            "highlights": [
                {"word": "block", "score": "+0.18"},
                {"word": "Turant", "score": "+0.18"},
                {"word": "http://sco.in", "score": "+0.22"}
            ],
            "entropy": 4.2,
            "tld": ".co.in",
            "spoofedSender": "AxisBank"
        }))
        
        await websocket.send_text(json.dumps({
            "type": "fusion", 
            "threat_score": 0.87
        }))
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
