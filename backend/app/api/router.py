from fastapi import APIRouter

from app.ai.skills import list_skills
from app.api.v1 import aftermarket, agent, auth, claims, documents, health, vehicles

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(vehicles.router)
api_router.include_router(documents.router)
api_router.include_router(claims.router)
api_router.include_router(aftermarket.router)
api_router.include_router(agent.router)


@api_router.get("/ai/skills", tags=["ai"])
def ai_skills() -> dict:
    return {"skills": list_skills()}
