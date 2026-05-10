from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.routes import router as claims_router

app = FastAPI(title="ChargePoint Claims Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims_router)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
