from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic
import os

router = APIRouter()

class AnalysisRequest(BaseModel):
    prompt: str

class AnalysisResponse(BaseModel):
    analysis: str

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_chart(request: AnalysisRequest):
    """
    Analizza i dati del grafico usando Claude AI
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]
        )
        
        # Estrai il contenuto della risposta
        analysis_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                analysis_text += block.text
        
        return AnalysisResponse(analysis=analysis_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check per l'endpoint AI"""
    return {"status": "online", "service": "ai-analysis"}
