"""
main.py
=======
八卦推演 — FastAPI application entry point.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8888 --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from api.bazi          import router as bazi_router
from api.liuyao        import router as liuyao_router
from api.qimen         import router as qimen_router
from api.fengshui      import router as fengshui_router
from api.date_selection import router as date_router
from api.knowledge     import router as knowledge_router
from api.agent         import router as agent_router
from api.models        import router as models_router
from api.ziwei         import router as ziwei_router

# ─────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="八卦推演 API",
    description=(
        "中国传统命理系统后端 API\n\n"
        "涵盖：八字 | 六爻 | 奇门遁甲 | 风水 | 择日 | 知识库"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────

# CORS — allow all origins so local dev always works regardless of how
# the .env was written (JSON array, comma-separated, or missing entirely).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────

app.include_router(bazi_router,       prefix="/api/v1")
app.include_router(liuyao_router,     prefix="/api/v1")
app.include_router(qimen_router,      prefix="/api/v1")
app.include_router(fengshui_router,   prefix="/api/v1")
app.include_router(date_router,       prefix="/api/v1")
app.include_router(knowledge_router,  prefix="/api/v1")
app.include_router(agent_router,      prefix="/api/v1")
app.include_router(models_router,     prefix="/api/v1")
app.include_router(ziwei_router,      prefix="/api/v1")

# ─────────────────────────────────────────────────────────────
# Root + health check
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["系统"])
async def root():
    return {
        "name":    "八卦推演 API",
        "version": "2.0.0",
        "status":  "running",
        "docs":    "/docs",
        "modules": ["八字", "六爻", "奇门遁甲", "风水", "择日", "知识库", "AI命理顾问"],
    }


@app.get("/health", tags=["系统"])
async def health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": "2.1.0",
            "modules": ["bazi", "liuyao", "qimen", "fengshui", "date_selection", "knowledge"],
            "port": settings.app_port,
        },
        "message": "运行正常",
    }


# ─────────────────────────────────────────────────────────────
# Global error handler
# ─────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": str(exc), "data": None},
    )


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
