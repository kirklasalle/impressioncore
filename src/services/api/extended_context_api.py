"""
Extended Context API for 256k Token Processing
Enhanced ImpressionCore API with production-ready 256k context window support

This module provides comprehensive API endpoints for processing extremely long
sequences with advanced memory optimization, real-time monitoring, and
streaming capabilities optimized for GTX 1050 Ti hardware constraints.

Author: ImpressionCore Development Team
Created: 2025-01-30
Hardware Target: GTX 1050 Ti (4GB VRAM)
Context Length: Up to 256k tokens
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, AsyncGenerator, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path

import torch
import torch.nn.functional as F
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our optimized components
from ..core.memory_manager.ultra_efficient_manager import UltraEfficientMemoryManager
from ..models.layers.production_sparse_attention import ProductionSparseAttention
from ..core.kernels.fused_operations import FusedOperations
from ..core.pipeline.parallel_processor import ParallelProcessor
from ..core.reliability.production_error_handler import ProductionErrorHandler
from ..core.monitoring.performance_telemetry import PerformanceTelemetry
from ..core.quality.quality_assurance import QualityAssuranceSystem
from ..core.utils.rich_enhancements import create_enhanced_console
from ..core.utils.rich_logging import setup_rich_logging


class ProcessingMode(str, Enum):
    """
    Processing mode for extended context operations.
    
    Defines different optimization strategies for processing long sequences:
    - QUALITY_FIRST: Prioritize output quality over speed
    - SPEED_FIRST: Prioritize processing speed over quality
    - BALANCED: Balance between quality and speed (recommended)
    - MEMORY_OPTIMIZED: Minimize memory usage for constrained hardware
    """
    QUALITY_FIRST = "quality_first"      # High quality, slower processing
    SPEED_FIRST = "speed_first"          # Fast processing, lower quality
    BALANCED = "balanced"                # Optimal balance for most use cases
    MEMORY_OPTIMIZED = "memory_optimized"  # Minimal memory footprint


class ProgressStatus(str, Enum):
    """Progress status for long-running operations."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    STREAMING = "streaming"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingConfig:
    """Configuration for extended context processing."""
    max_tokens: int = 256_000
    chunk_size: int = 8_192
    overlap_size: int = 512
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    enable_streaming: bool = True
    enable_monitoring: bool = True
    enable_quality_checks: bool = True
    memory_budget_gb: float = 3.8
    target_latency_ms: float = 200.0
    quality_threshold: float = 0.98


class ExtendedContextRequest(BaseModel):
    """Request model for extended context processing."""
    text: str = Field(..., description="Input text to process")
    max_tokens: Optional[int] = Field(256_000, description="Maximum tokens to process")
    processing_mode: ProcessingMode = Field(ProcessingMode.BALANCED, description="Processing mode")
    enable_streaming: bool = Field(True, description="Enable streaming response")
    enable_monitoring: bool = Field(True, description="Enable performance monitoring")
    session_id: Optional[str] = Field(None, description="Session ID for persistence")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration")


class SessionRequest(BaseModel):
    """Request model for creating processing sessions."""
    max_tokens: Optional[int] = Field(256_000, description="Maximum tokens for this session")
    processing_mode: ProcessingMode = Field(ProcessingMode.BALANCED, description="Default processing mode")
    memory_budget_gb: Optional[float] = Field(3.8, description="Memory budget for this session")
    quality_threshold: Optional[float] = Field(0.98, description="Quality threshold for processing")
    enable_monitoring: bool = Field(True, description="Enable session monitoring")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")


class ProcessingProgress(BaseModel):
    """Progress information for extended context processing."""
    session_id: str
    status: ProgressStatus
    progress_percent: float
    tokens_processed: int
    total_tokens: int
    estimated_time_remaining: Optional[float]
    current_chunk: int
    total_chunks: int
    memory_usage_gb: float
    latency_ms: float
    quality_score: Optional[float]
    error_message: Optional[str]


class ProcessingResult(BaseModel):
    """Result of extended context processing."""
    session_id: str
    status: ProgressStatus
    result: Optional[str]
    tokens_processed: int
    processing_time_ms: float
    memory_peak_gb: float
    quality_metrics: Optional[Dict[str, float]]
    performance_metrics: Optional[Dict[str, Any]]
    error_details: Optional[Dict[str, Any]]


class ExtendedContextAPI:
    """
    Production API for 256k context processing with advanced optimizations.
    
    Features:
    - Streaming processing for real-time feedback
    - Adaptive memory management
    - Quality-preserving optimizations
    - Real-time performance monitoring
    - Graceful error handling and recovery
    """
    
    def __init__(self, device: str = "cuda", config: Optional[ProcessingConfig] = None):
        """Initialize the Extended Context API."""
        self.device = device
        self.config = config or ProcessingConfig()
        self.console = create_enhanced_console()
        self.logger = setup_rich_logging(
            "extended_context_api",
            log_level="INFO",
            console=self.console
        )
        
        # Active sessions tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_counter = 0
        
        # Initialize core components
        self._initialize_components()
        
        # FastAPI app
        self.app = FastAPI(
            title="ImpressionCore Extended Context API",
            description="Production API for 256k token context processing",
            version="1.0.0"
        )
        self._setup_routes()
        
        self.logger.info("Extended Context API initialized successfully")
    
    def _initialize_components(self):
        """Initialize all core processing components."""
        try:
            # Memory manager
            self.memory_manager = UltraEfficientMemoryManager(
                device=self.device,
                max_memory_gb=self.config.memory_budget_gb
            )
            
            # Error handler
            self.error_handler = ProductionErrorHandler(
                device=self.device,
                memory_budget_gb=self.config.memory_budget_gb
            )
            
            # Performance monitoring
            self.telemetry = PerformanceTelemetry(
                target_latency_ms=self.config.target_latency_ms,
                memory_budget_gb=self.config.memory_budget_gb
            )
            
            # Quality assurance
            self.quality_system = QualityAssuranceSystem(
                device=self.device,
                quality_threshold=self.config.quality_threshold
            )
            
            # Parallel processor
            self.parallel_processor = ParallelProcessor(
                device=self.device,
                chunk_size=self.config.chunk_size,
                overlap_size=self.config.overlap_size
            )
            
            # Fused operations
            self.fused_ops = FusedOperations(device=self.device)
            
            self.logger.info("All core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise RuntimeError(f"Component initialization failed: {e}")
    
    def _setup_routes(self):
        """Set up FastAPI routes."""
        
        @self.app.post("/process", response_model=ProcessingResult)
        async def process_text(
            request: ExtendedContextRequest,
            background_tasks: BackgroundTasks
        ):
            """Process text with extended context support."""
            return await self.process_extended_context(request, background_tasks)
        
        @self.app.get("/stream/{session_id}")
        async def stream_processing(session_id: str):
            """Stream processing results in real-time."""
            return StreamingResponse(
                self.stream_processing_results(session_id),
                media_type="text/plain"
            )
        
        @self.app.websocket("/ws/{session_id}")
        async def websocket_progress(websocket: WebSocket, session_id: str):
            """WebSocket endpoint for real-time progress updates."""
            await self.handle_websocket_progress(websocket, session_id)
        
        @self.app.get("/progress/{session_id}", response_model=ProcessingProgress)
        async def get_progress(session_id: str):
            """Get current processing progress."""
            return await self.get_processing_progress(session_id)
        
        @self.app.delete("/session/{session_id}")
        async def cancel_session(session_id: str):
            """Cancel an active processing session."""
            return await self.cancel_processing_session(session_id)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return await self.get_health_status()
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Get current system metrics."""
            return await self.get_system_metrics()
    
    async def process_extended_context(
        self,
        request: ExtendedContextRequest,
        background_tasks: BackgroundTasks
    ) -> ProcessingResult:
        """
        Process text with extended context window support.
        
        Args:
            request: Processing request with configuration
            background_tasks: Background task manager
            
        Returns:
            Processing result with metrics and status
        """
        # Generate session ID
        session_id = request.session_id or f"session_{self.session_counter}"
        self.session_counter += 1
        
        # Initialize session
        session_info = {
            "session_id": session_id,
            "request": request,
            "status": ProgressStatus.PENDING,
            "start_time": time.time(),
            "progress": 0.0,
            "result": None,
            "error": None
        }
        self.active_sessions[session_id] = session_info
        
        try:
            # Start background processing
            if request.enable_streaming:
                background_tasks.add_task(
                    self._process_with_streaming,
                    session_id,
                    request
                )
                
                return ProcessingResult(
                    session_id=session_id,
                    status=ProgressStatus.INITIALIZING,
                    result=None,
                    tokens_processed=0,
                    processing_time_ms=0.0,
                    memory_peak_gb=0.0
                )
            else:
                # Synchronous processing
                return await self._process_synchronous(session_id, request)
                
        except Exception as e:
            session_info["status"] = ProgressStatus.FAILED
            session_info["error"] = str(e)
            
            self.logger.error(f"Processing failed for session {session_id}: {e}")
            
            return ProcessingResult(
                session_id=session_id,
                status=ProgressStatus.FAILED,
                result=None,
                tokens_processed=0,
                processing_time_ms=0.0,
                memory_peak_gb=0.0,
                error_details={"error": str(e)}
            )
    
    async def _process_with_streaming(self, session_id: str, request: ExtendedContextRequest):
        """Process text with streaming updates."""
        session_info = self.active_sessions[session_id]
        
        try:
            session_info["status"] = ProgressStatus.INITIALIZING
            
            # Tokenize input
            tokens = self._tokenize_text(request.text)
            total_tokens = len(tokens)
            
            if total_tokens > request.max_tokens:
                tokens = tokens[:request.max_tokens]
                total_tokens = request.max_tokens
            
            # Calculate chunks
            chunk_size = self.config.chunk_size
            overlap_size = self.config.overlap_size
            chunks = self._create_chunks(tokens, chunk_size, overlap_size)
            total_chunks = len(chunks)
            
            session_info["total_tokens"] = total_tokens
            session_info["total_chunks"] = total_chunks
            session_info["status"] = ProgressStatus.PROCESSING
            
            # Process chunks with monitoring
            processed_results = []
            
            with self.telemetry.monitored_operation("extended_context_processing"):
                with self.error_handler.error_recovery_context():
                    
                    for i, chunk in enumerate(chunks):
                        # Update progress
                        progress = (i / total_chunks) * 100
                        session_info["progress"] = progress
                        session_info["current_chunk"] = i + 1
                        
                        # Process chunk
                        chunk_result = await self._process_chunk(
                            chunk, request.processing_mode
                        )
                        processed_results.append(chunk_result)
                        
                        # Quality check
                        if request.enable_monitoring and self.config.enable_quality_checks:
                            quality_score = await self._check_chunk_quality(chunk_result)
                            session_info["quality_score"] = quality_score
                        
                        # Memory and performance metrics
                        memory_usage = self.memory_manager.get_current_usage()
                        session_info["memory_usage_gb"] = memory_usage
                        
                        # Allow other tasks to run
                        await asyncio.sleep(0.001)
            
            # Combine results
            final_result = self._combine_chunk_results(processed_results)
            
            # Update session
            session_info["status"] = ProgressStatus.COMPLETED
            session_info["result"] = final_result
            session_info["progress"] = 100.0
            session_info["end_time"] = time.time()
            
            self.logger.info(f"Processing completed for session {session_id}")
            
        except Exception as e:
            session_info["status"] = ProgressStatus.FAILED
            session_info["error"] = str(e)
            self.logger.error(f"Streaming processing failed for session {session_id}: {e}")
    
    async def _process_synchronous(
        self, 
        session_id: str, 
        request: ExtendedContextRequest
    ) -> ProcessingResult:
        """Process text synchronously without streaming."""
        start_time = time.time()
        session_info = self.active_sessions[session_id]
        
        try:
            session_info["status"] = ProgressStatus.PROCESSING
            
            # Process the text
            with self.telemetry.monitored_operation("synchronous_processing"):
                with self.error_handler.error_recovery_context():
                    result = await self._process_full_text(request.text, request.processing_mode)
            
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000
            memory_peak = self.memory_manager.get_peak_usage()
            tokens_processed = len(self._tokenize_text(request.text))
            
            # Update session
            session_info["status"] = ProgressStatus.COMPLETED
            session_info["result"] = result
            session_info["end_time"] = time.time()
            
            return ProcessingResult(
                session_id=session_id,
                status=ProgressStatus.COMPLETED,
                result=result,
                tokens_processed=tokens_processed,
                processing_time_ms=processing_time,
                memory_peak_gb=memory_peak,
                quality_metrics=self.telemetry.get_quality_metrics(),
                performance_metrics=self.telemetry.get_performance_summary()
            )
            
        except Exception as e:
            session_info["status"] = ProgressStatus.FAILED
            session_info["error"] = str(e)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResult(
                session_id=session_id,
                status=ProgressStatus.FAILED,
                result=None,
                tokens_processed=0,
                processing_time_ms=processing_time,
                memory_peak_gb=self.memory_manager.get_peak_usage(),
                error_details={"error": str(e)}
            )
    
    async def stream_processing_results(self, session_id: str) -> AsyncGenerator[str, None]:
        """Stream processing results as they become available."""
        if session_id not in self.active_sessions:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
        
        session_info = self.active_sessions[session_id]
        last_progress = -1
        
        while True:
            current_progress = session_info.get("progress", 0)
            status = session_info.get("status", ProgressStatus.PENDING)
            
            # Send update if progress changed
            if current_progress != last_progress or status in [
                ProgressStatus.COMPLETED, 
                ProgressStatus.FAILED, 
                ProgressStatus.CANCELLED
            ]:
                progress_data = {
                    "session_id": session_id,
                    "status": status.value,
                    "progress": current_progress,
                    "timestamp": time.time()
                }
                
                if "result" in session_info and session_info["result"]:
                    progress_data["partial_result"] = session_info["result"]
                
                if "error" in session_info and session_info["error"]:
                    progress_data["error"] = session_info["error"]
                
                yield f"data: {json.dumps(progress_data)}\n\n"
                last_progress = current_progress
            
            # Exit conditions
            if status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED]:
                break
            
            await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
    
    async def handle_websocket_progress(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection for real-time progress updates."""
        await websocket.accept()
        
        if session_id not in self.active_sessions:
            await websocket.send_json({"error": "Session not found"})
            await websocket.close()
            return
        
        session_info = self.active_sessions[session_id]
        
        try:
            while True:
                progress_data = await self.get_processing_progress(session_id)
                await websocket.send_json(progress_data.dict())
                
                if progress_data.status in [
                    ProgressStatus.COMPLETED, 
                    ProgressStatus.FAILED, 
                    ProgressStatus.CANCELLED
                ]:
                    break
                
                await asyncio.sleep(0.5)  # Update every 500ms
                
        except Exception as e:
            self.logger.error(f"WebSocket error for session {session_id}: {e}")
        finally:
            await websocket.close()
    
    async def get_processing_progress(self, session_id: str) -> ProcessingProgress:
        """Get current processing progress for a session."""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_info = self.active_sessions[session_id]
        
        # Calculate estimated time remaining
        estimated_time = None
        if session_info.get("progress", 0) > 0:
            elapsed = time.time() - session_info.get("start_time", time.time())
            remaining_progress = 100 - session_info.get("progress", 0)
            if remaining_progress > 0:
                estimated_time = (elapsed / session_info.get("progress", 1)) * remaining_progress
        
        return ProcessingProgress(
            session_id=session_id,
            status=session_info.get("status", ProgressStatus.PENDING),
            progress_percent=session_info.get("progress", 0.0),
            tokens_processed=session_info.get("tokens_processed", 0),
            total_tokens=session_info.get("total_tokens", 0),
            estimated_time_remaining=estimated_time,
            current_chunk=session_info.get("current_chunk", 0),
            total_chunks=session_info.get("total_chunks", 0),
            memory_usage_gb=session_info.get("memory_usage_gb", 0.0),
            latency_ms=session_info.get("latency_ms", 0.0),
            quality_score=session_info.get("quality_score"),
            error_message=session_info.get("error")
        )
    
    async def cancel_processing_session(self, session_id: str) -> Dict[str, str]:
        """Cancel an active processing session."""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_info = self.active_sessions[session_id]
        session_info["status"] = ProgressStatus.CANCELLED
        
        self.logger.info(f"Session {session_id} cancelled")
        
        return {"message": f"Session {session_id} cancelled successfully"}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get API health status."""
        try:
            memory_status = self.memory_manager.get_health_status()
            telemetry_status = self.telemetry.get_health_metrics()
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "active_sessions": len(self.active_sessions),
                "memory_status": memory_status,
                "performance_status": telemetry_status,
                "device": self.device,
                "max_context_length": self.config.max_tokens
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        return {
            "memory_metrics": self.memory_manager.get_detailed_metrics(),
            "performance_metrics": self.telemetry.get_performance_summary(),
            "quality_metrics": self.quality_system.get_quality_report(),
            "active_sessions": {
                session_id: {
                    "status": info.get("status"),
                    "progress": info.get("progress", 0),
                    "start_time": info.get("start_time")
                }
                for session_id, info in self.active_sessions.items()
            }
        }
    
    # Helper methods
    def _tokenize_text(self, text: str) -> List[int]:
        """Tokenize input text. Placeholder implementation."""
        # This would be replaced with actual tokenizer
        return list(range(len(text.split())))
    
    def _create_chunks(self, tokens: List[int], chunk_size: int, overlap_size: int) -> List[List[int]]:
        """Create overlapping chunks from tokens."""
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunks.append(tokens[start:end])
            
            if end >= len(tokens):
                break
                
            start = end - overlap_size
        
        return chunks
    
    async def _process_chunk(self, chunk: List[int], mode: ProcessingMode) -> str:
        """Process a single chunk. Placeholder implementation."""
        # This would be replaced with actual model processing
        await asyncio.sleep(0.01)  # Simulate processing time
        return f"processed_chunk_{len(chunk)}_tokens"
    
    async def _process_full_text(self, text: str, mode: ProcessingMode) -> str:
        """Process full text. Placeholder implementation."""
        # This would be replaced with actual model processing
        await asyncio.sleep(0.1)  # Simulate processing time
        return f"processed_full_text_{len(text)}_chars"
    
    def _combine_chunk_results(self, results: List[str]) -> str:
        """Combine chunk processing results."""
        return " ".join(results)
    
    async def _check_chunk_quality(self, result: str) -> float:
        """Check quality of chunk processing result."""
        # This would be replaced with actual quality assessment
        return 0.95  # Placeholder quality score
    
    def cleanup_session(self, session_id: str):
        """Clean up session resources."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up session {session_id}")
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI server."""
        self.logger.info(f"Starting Extended Context API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, **kwargs)


# Factory function for easy deployment
def create_extended_context_api(
    device: str = "cuda",
    max_tokens: int = 256_000,
    memory_budget_gb: float = 3.8,
    target_latency_ms: float = 200.0
) -> ExtendedContextAPI:
    """
    Factory function to create an Extended Context API instance.
    
    Args:
        device: Computing device ("cuda" or "cpu")
        max_tokens: Maximum tokens to process
        memory_budget_gb: Memory budget in GB
        target_latency_ms: Target latency in milliseconds
        
    Returns:
        Configured ExtendedContextAPI instance
    """
    config = ProcessingConfig(
        max_tokens=max_tokens,
        memory_budget_gb=memory_budget_gb,
        target_latency_ms=target_latency_ms
    )
    
    return ExtendedContextAPI(device=device, config=config)

def create_extended_context_app(
    device: str = "cuda",
    max_tokens: int = 256000,
    memory_budget_gb: float = 3.5,
    target_latency_ms: int = 200
) -> FastAPI:
    """
    Factory function to create a FastAPI application with Extended Context API.
    
    This function creates and configures a complete FastAPI application with
    all necessary endpoints for extended context processing.
    
    Args:
        device: Computing device ("cuda" or "cpu")
        max_tokens: Maximum tokens to process
        memory_budget_gb: Memory budget in GB
        target_latency_ms: Target latency in milliseconds
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="ImpressionCore Extended Context API",
        description="Production-ready 256k context window processing API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Create API instance
    api = create_extended_context_api(
        device=device,
        max_tokens=max_tokens,
        memory_budget_gb=memory_budget_gb,
        target_latency_ms=target_latency_ms
    )
    
    # Add middleware for performance monitoring
    @app.middleware("http")
    async def performance_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": time.time()}
    
    # Main processing endpoint
    @app.post("/process")
    async def process_extended_context(request: ExtendedContextRequest):
        return await api.process_extended_context(request.dict())
    
    # Streaming endpoint
    @app.post("/stream")
    async def stream_extended_context(request: ExtendedContextRequest):
        async def generate():
            async for chunk in api.stream_process(request.dict()):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    # Session management endpoints
    @app.post("/session")
    async def create_session(request: SessionRequest):
        return await api.create_processing_session(request.dict())
    
    @app.get("/session/{session_id}")
    async def get_session(session_id: str):
        return await api.get_session_status(session_id)
    
    @app.delete("/session/{session_id}")
    async def cancel_session(session_id: str):
        return await api.cancel_session(session_id)
    
    # Metrics endpoint
    @app.get("/metrics")
    async def get_metrics():
        return await api.get_system_metrics()
    
    # WebSocket endpoint for real-time updates
    @app.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        await websocket.accept()
        try:
            while True:
                # Send periodic updates about session progress
                status = await api.get_session_status(session_id)
                await websocket.send_json(status)
                await asyncio.sleep(1)
        except Exception:
            pass  # Client disconnected
    
    return app

if __name__ == "__main__":
    # Example usage
    api = create_extended_context_api(device="cuda")
    api.run_server(host="0.0.0.0", port=8000)
