"""
ImpressionCore Text Generation API
=================================

RESTful API endpoints for text generation service with
real-time monitoring, streaming support, and enterprise features.

Features:
- REST API with FastAPI
- Streaming text generation
- Real-time VRAM monitoring
- Rate limiting and security
- Comprehensive error handling
- OpenAPI documentation

Author: ImpressionCore Team
Date: 2025-01-09
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Union, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

from .service import (
    TextGenerationService,
    GenerationConfig,
    GenerationResult,
    create_text_generation_service
)
from src.core.utils.rich_enhancements import RichUI
from src.core.config.model_config import ModelConfig


# Pydantic models for API requests/responses
class GenerationRequest(BaseModel):
    """Request model for text generation."""
    prompt: str = Field(..., description="Input text prompt", min_length=1, max_length=2048)
    max_length: int = Field(512, description="Maximum generation length", ge=1, le=2048)
    temperature: float = Field(0.8, description="Sampling temperature", ge=0.1, le=2.0)
    top_p: float = Field(0.9, description="Top-p sampling threshold", ge=0.1, le=1.0)
    top_k: int = Field(50, description="Top-k sampling limit", ge=1, le=100)
    repetition_penalty: float = Field(1.1, description="Repetition penalty", ge=1.0, le=2.0)
    do_sample: bool = Field(True, description="Enable sampling")
    num_return_sequences: int = Field(1, description="Number of sequences", ge=1, le=5)
    stream: bool = Field(False, description="Enable streaming response")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class GenerationResponse(BaseModel):
    """Response model for text generation."""
    generated_text: str
    input_text: str
    generation_time: float
    tokens_per_second: float
    memory_used: float
    metadata: Dict[str, Any]


class ServiceStatsResponse(BaseModel):
    """Response model for service statistics."""
    service_stats: Dict[str, Any]
    device_info: Dict[str, Any]
    memory_info: Dict[str, Any]
    model_info: Dict[str, Any]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: float
    version: str
    device: str
    memory_available: bool
    model_loaded: bool


# Global service instance
service: Optional[TextGenerationService] = None
rich_ui = RichUI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global service
    
    # Startup
    rich_ui.print_status("🚀 Starting ImpressionCore Text Generation API...", "info")
    
    try:
        # Initialize service
        service = create_text_generation_service(enable_monitoring=True)
        await service.initialize()
        
        rich_ui.print_status("✅ Text Generation API ready!", "success")
        yield
        
    except Exception as e:
        rich_ui.print_status(f"❌ Failed to start API: {e}", "error")
        raise
    
    # Shutdown
    if service:
        await service.cleanup()
        rich_ui.print_status("✅ API shutdown completed", "success")


# Create FastAPI application
app = FastAPI(
    title="ImpressionCore Text Generation API",
    description="Privacy-first, hardware-optimized text generation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

def get_service() -> TextGenerationService:
    """Dependency to get the service instance."""
    if service is None or not service.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text generation service not available"
        )
    return service


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key using constant-time comparison.

    Reads the expected key from IMPRESSIONCORE_API_KEY environment variable.
    When no env var is set, authentication is bypassed (development mode).
    """
    import hmac
    import os

    expected_key = os.environ.get("IMPRESSIONCORE_API_KEY", "")

    # Development mode: no key configured → skip auth
    if not expected_key:
        if credentials and credentials.credentials:
            return credentials.credentials
        return None

    # Production mode: require valid key with constant-time comparison
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    if not hmac.compare_digest(credentials.credentials, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return credentials.credentials


# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global service
    
    memory_available = True
    model_loaded = False
    device = "unknown"
    
    if service:
        model_loaded = service.is_initialized
        device = str(service.device)
        
        # Check memory availability
        try:
            memory_info = service._get_memory_info()
            if "cuda_memory_free_gb" in memory_info:
                memory_available = memory_info["cuda_memory_free_gb"] > 0.5  # 500MB threshold
        except:
            memory_available = False
    
    return HealthResponse(
        status="healthy" if model_loaded and memory_available else "degraded",
        timestamp=time.time(),
        version="1.0.0",
        device=device,
        memory_available=memory_available,
        model_loaded=model_loaded
    )


@app.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    service: TextGenerationService = Depends(get_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Generate text from a prompt."""
    try:
        # Convert request to GenerationConfig
        config = GenerationConfig(
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repetition_penalty=request.repetition_penalty,
            do_sample=request.do_sample,
            num_return_sequences=request.num_return_sequences
        )
        
        # Generate text
        result = await service.generate_text(
            prompt=request.prompt,
            config=config,
            stream=False
        )
        
        # Convert to response model
        return GenerationResponse(
            generated_text=result.generated_text,
            input_text=result.input_text,
            generation_time=result.generation_time,
            tokens_per_second=result.tokens_per_second,
            memory_used=result.memory_used,
            metadata=result.metadata
        )
        
    except Exception as e:
        logging.error(f"Generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


@app.post("/generate/stream")
async def generate_text_stream(
    request: GenerationRequest,
    service: TextGenerationService = Depends(get_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Generate text with streaming response."""
    try:
        # Convert request to GenerationConfig
        config = GenerationConfig(
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repetition_penalty=request.repetition_penalty,
            do_sample=request.do_sample,
            num_return_sequences=request.num_return_sequences
        )
        
        async def generate_stream():
            """Stream generator for text generation."""
            generator = await service.generate_text(
                prompt=request.prompt,
                config=config,
                stream=True
            )
            
            # Stream the tokens
            for token in generator:
                if isinstance(token, str):
                    yield f"data: {token}\n\n"
                else:
                    # Final result
                    yield f"data: [DONE]\n\n"
                    break
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        logging.error(f"Streaming generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming generation failed: {str(e)}"
        )


@app.get("/stats", response_model=ServiceStatsResponse)
async def get_service_stats(
    service: TextGenerationService = Depends(get_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Get service statistics and monitoring data."""
    try:
        stats = service.get_stats()
        return ServiceStatsResponse(**stats)
        
    except Exception as e:
        logging.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@app.get("/monitoring/memory")
async def get_memory_monitoring(
    service: TextGenerationService = Depends(get_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Get real-time memory monitoring data."""
    try:
        memory_info = service._get_memory_info()
        monitoring_data = service.monitoring_data[-100:]  # Last 100 entries
        
        return {
            "current_memory": memory_info,
            "monitoring_history": monitoring_data,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logging.error(f"Failed to get memory monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve memory monitoring: {str(e)}"
        )


@app.post("/admin/cleanup")
async def cleanup_service(
    background_tasks: BackgroundTasks,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Administrative endpoint to cleanup service memory."""
    global service
    
    try:
        if service:
            await service.cleanup()
            # Reinitialize
            await service.initialize()
        
        return {"status": "cleanup_completed", "timestamp": time.time()}
        
    except Exception as e:
        logging.error(f"Cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": time.time(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": time.time(),
            "path": str(request.url)
        }
    )


# Server configuration
def create_server_config():
    """Create server configuration."""
    return {
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "access_log": True,
        "reload": False,  # Set to True for development
        "workers": 1  # Single worker for GPU memory management
    }


def run_server():
    """Run the API server."""
    config = create_server_config()
    rich_ui.print_status(f"🚀 Starting server on {config['host']}:{config['port']}", "info")
    uvicorn.run(app, **config)


if __name__ == "__main__":
    run_server()
