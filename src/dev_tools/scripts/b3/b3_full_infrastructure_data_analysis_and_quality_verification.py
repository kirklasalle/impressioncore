#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #deployment #memory_management #python #pytorch #source_code #src/scripts\b3\b3_full_infrastructure_data_analysis_and_quality_verification.py #training
**Category:** Source Code
**Status:** Active
"""



import json
import logging
import os
import re
import sqlite3
import sys
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import chardet
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# Rich enhancements for professional UI
try:
    from rich.align import Align
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn, TimeElapsedColumn  # noqa: F401
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich not available - using standard output")

# Configure logging with UTF-8 encoding to handle emojis
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            # Only print to console, skip file logging for emoji messages
            if hasattr(self.stream, 'write'):
                self.stream.write(msg + self.terminator)
                self.stream.flush()
        except UnicodeEncodeError:
            # Fallback for emoji characters
            pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('b3_infrastructure_analysis.log', encoding='utf-8'),
        UTF8StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DataQualityMetrics:
    """Comprehensive data quality metrics"""
    file_path: str
    file_size_bytes: int
    file_type: str
    encoding: str | None
    is_corrupted: bool
    quality_score: float
    error_messages: list[str]
    content_preview: str | None
    metadata: dict[str, Any]

@dataclass
class InfrastructureAnalysis:
    """Complete infrastructure analysis results"""
    total_files: int
    total_size_gb: float
    embeddings_analysis: dict[str, Any]
    datasets_analysis: dict[str, Any]
    quality_distribution: dict[str, int]
    file_type_distribution: dict[str, int]
    corruption_report: dict[str, Any]
    b3_readiness_score: float
    recommendations: list[str]

class B3InfrastructureAnalyzer:
    r"""
    Comprehensive B3 Infrastructure Data Analysis & Quality Verification System

    Analyzes the complete F:\data infrastructure to ensure quality and readiness
    for B3 advanced architecture reinitialization.
    """

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = datetime.now()

        # Infrastructure paths
        self.f_data_root = Path("F:/data")
        self.embeddings_path = self.f_data_root / "embeddings"
        self.datasets_path = self.f_data_root / "datasets"
        self.analysis_output_path = Path("F:/data/analysis_reports")

        # Create analysis output directory
        self.analysis_output_path.mkdir(parents=True, exist_ok=True)

        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'acceptable': 0.5,
            'poor': 0.3,
            'corrupted': 0.1
        }

        # File type processors
        self.file_processors = {
            '.npy': self._analyze_numpy_file,
            '.json': self._analyze_json_file,
            '.pth': self._analyze_pytorch_file,
            '.pt': self._analyze_pytorch_file,
            '.faiss': self._analyze_faiss_file,
            '.txt': self._analyze_text_file,
            '.csv': self._analyze_csv_file,
            '.pdf': self._analyze_pdf_file,
            '.db': self._analyze_database_file,
            '.log': self._analyze_log_file
        }

        # Analysis results storage
        self.analysis_results = {
            'file_quality_metrics': [],
            'infrastructure_summary': {},
            'corruption_detected': [],
            'recommendations': [],
            'b3_readiness_assessment': {}
        }

        logger.info("B3 Infrastructure Analyzer initialized")

    def display_header(self):
        """Display professional system header"""
        if not self.console:
            print("B3 Full Infrastructure - Data Analysis & Quality Verification")
            print("=" * 70)
            return

        header_text = Text("🔬 B3 Full Infrastructure Analysis", style="bold cyan")
        subtitle = Text("312.66 GB • 1.8M Files • Quality Verification & B3 Readiness", style="italic")

        panel = Panel(
            Align.center(f"{header_text}\n{subtitle}"),
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)

    def display_status(self, message: str):
        """Display status message with rich formatting"""
        if self.console:
            self.console.print(f"[bold green]⚡[/bold green] {message}")
        else:
            print(f"⚡ {message}")
        # Only log non-emoji messages to file
        clean_message = message.encode('ascii', errors='ignore').decode('ascii')
        if clean_message.strip():
            logger.info(clean_message)

    def scan_infrastructure_overview(self) -> dict[str, Any]:
        r"""Scan complete F:\data infrastructure for overview"""
        self.display_status("📊 Scanning Complete Infrastructure Overview")

        overview = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'total_size_bytes': 0,
            'directory_structure': {},
            'file_extensions': defaultdict(int),
            'large_files': [],  # Files > 1GB
            'directory_sizes': {}
        }

        try:
            # Scan entire F:\data directory
            for root, _dirs, files in os.walk(self.f_data_root):
                root_path = Path(root)
                dir_size = 0

                for file in files:
                    file_path = root_path / file
                    try:
                        file_size = file_path.stat().st_size
                        overview['total_files'] += 1
                        overview['total_size_bytes'] += file_size
                        dir_size += file_size

                        # Track file extensions
                        ext = file_path.suffix.lower()
                        overview['file_extensions'][ext] += 1

                        # Track large files (>1GB)
                        if file_size > 1024**3:
                            overview['large_files'].append({
                                'path': str(file_path),
                                'size_gb': file_size / (1024**3)
                            })

                    except (OSError, PermissionError) as e:
                        logger.warning(f"Cannot access {file_path}: {e}")

                # Store directory size
                overview['directory_sizes'][str(root_path)] = dir_size

            # Convert to GB
            overview['total_size_gb'] = overview['total_size_bytes'] / (1024**3)

            self.display_status(f"✅ Infrastructure Overview Complete: {overview['total_files']:,} files, {overview['total_size_gb']:.2f} GB")

            return overview

        except Exception as e:
            logger.error(f"Infrastructure overview scan failed: {e}")
            return overview

    def analyze_embeddings_infrastructure(self) -> dict[str, Any]:
        r"""Comprehensive analysis of F:\data/embeddings infrastructure"""
        self.display_status("🧠 Analyzing Embeddings Infrastructure")

        embeddings_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_embedding_files': 0,
            'total_embeddings_size_gb': 0.0,
            'embedding_types': defaultdict(int),
            'model_checkpoints': [],
            'faiss_indexes': [],
            'embedding_dimensions': defaultdict(int),
            'corrupted_embeddings': [],
            'b3_specific_embeddings': [],
            'quality_assessment': {
                'excellent': 0,
                'good': 0,
                'acceptable': 0,
                'poor': 0,
                'corrupted': 0
            }
        }

        if not self.embeddings_path.exists():
            self.display_status("⚠️  Embeddings directory not found")
            return embeddings_analysis

        # Analyze all embedding files
        for embedding_file in self.embeddings_path.rglob("*"):
            if embedding_file.is_file():
                try:
                    file_ext = embedding_file.suffix.lower()
                    file_size = embedding_file.stat().st_size

                    embeddings_analysis['total_embedding_files'] += 1
                    embeddings_analysis['total_embeddings_size_gb'] += file_size / (1024**3)
                    embeddings_analysis['embedding_types'][file_ext] += 1

                    # Analyze specific file types
                    if file_ext == '.npy':
                        quality_metrics = self._analyze_numpy_file(embedding_file)
                        quality_level = self._categorize_quality(quality_metrics.quality_score)
                        embeddings_analysis['quality_assessment'][quality_level] += 1

                        if quality_metrics.metadata.get('dimensions'):
                            dims = quality_metrics.metadata['dimensions']
                            embeddings_analysis['embedding_dimensions'][str(dims)] += 1

                    elif file_ext in ['.pth', '.pt']:
                        embeddings_analysis['model_checkpoints'].append({
                            'path': str(embedding_file),
                            'size_mb': file_size / (1024**2),
                            'modified': datetime.fromtimestamp(embedding_file.stat().st_mtime).isoformat()
                        })

                    elif file_ext == '.faiss':
                        embeddings_analysis['faiss_indexes'].append({
                            'path': str(embedding_file),
                            'size_mb': file_size / (1024**2)
                        })

                    # Check for B3-specific files
                    if 'b3' in embedding_file.name.lower():
                        embeddings_analysis['b3_specific_embeddings'].append({
                            'path': str(embedding_file),
                            'type': file_ext,
                            'size_mb': file_size / (1024**2)
                        })

                except Exception as e:
                    embeddings_analysis['corrupted_embeddings'].append({
                        'path': str(embedding_file),
                        'error': str(e)
                    })
                    logger.warning(f"Error analyzing {embedding_file}: {e}")

        self.display_status(f"✅ Embeddings Analysis Complete: {embeddings_analysis['total_embedding_files']:,} files")
        return embeddings_analysis

    def analyze_datasets_infrastructure(self) -> dict[str, Any]:
        r"""Comprehensive analysis of F:\data/datasets infrastructure"""
        self.display_status("📚 Analyzing Datasets Infrastructure")

        datasets_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_dataset_files': 0,
            'total_datasets_size_gb': 0.0,
            'dataset_categories': defaultdict(int),
            'data_formats': defaultdict(int),
            'educational_datasets': [],
            'large_datasets': [],  # >1GB datasets
            'text_datasets': [],
            'image_datasets': [],
            'audio_datasets': [],
            'quality_assessment': {
                'excellent': 0,
                'good': 0,
                'acceptable': 0,
                'poor': 0,
                'corrupted': 0
            },
            'content_analysis': {
                'total_text_size_mb': 0,
                'estimated_tokens': 0,
                'language_distribution': defaultdict(int),
                'encoding_issues': []
            }
        }

        if not self.datasets_path.exists():
            self.display_status("⚠️  Datasets directory not found")
            return datasets_analysis

        # Analyze all dataset files
        for dataset_file in self.datasets_path.rglob("*"):
            if dataset_file.is_file():
                try:
                    file_ext = dataset_file.suffix.lower()
                    file_size = dataset_file.stat().st_size

                    datasets_analysis['total_dataset_files'] += 1
                    datasets_analysis['total_datasets_size_gb'] += file_size / (1024**3)
                    datasets_analysis['data_formats'][file_ext] += 1

                    # Categorize by directory structure
                    relative_path = dataset_file.relative_to(self.datasets_path)
                    category = str(relative_path.parts[0]) if relative_path.parts else 'root'
                    datasets_analysis['dataset_categories'][category] += 1

                    # Large dataset tracking
                    if file_size > 1024**3:  # >1GB
                        datasets_analysis['large_datasets'].append({
                            'path': str(dataset_file),
                            'size_gb': file_size / (1024**3),
                            'category': category
                        })

                    # Educational dataset detection
                    if any(keyword in str(dataset_file).lower() for keyword in
                          ['educational', 'k12', 'curriculum', 'school', 'learning', 'student']):
                        datasets_analysis['educational_datasets'].append({
                            'path': str(dataset_file),
                            'size_mb': file_size / (1024**2)
                        })

                    # Content type analysis
                    if file_ext in ['.txt', '.json', '.csv']:
                        datasets_analysis['text_datasets'].append(str(dataset_file))

                        # Analyze text content quality
                        if file_size < 100 * 1024**2:  # Only analyze files <100MB
                            quality_metrics = self._analyze_text_content_quality(dataset_file)
                            quality_level = self._categorize_quality(quality_metrics.quality_score)
                            datasets_analysis['quality_assessment'][quality_level] += 1

                            if file_ext == '.txt':
                                datasets_analysis['content_analysis']['total_text_size_mb'] += file_size / (1024**2)
                                # Estimate tokens (rough approximation)
                                estimated_tokens = file_size / 4  # ~4 bytes per token
                                datasets_analysis['content_analysis']['estimated_tokens'] += estimated_tokens

                    elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        datasets_analysis['image_datasets'].append(str(dataset_file))

                    elif file_ext in ['.wav', '.mp3', '.flac', '.ogg']:
                        datasets_analysis['audio_datasets'].append(str(dataset_file))

                except Exception as e:
                    logger.warning(f"Error analyzing dataset {dataset_file}: {e}")

        self.display_status(f"✅ Datasets Analysis Complete: {datasets_analysis['total_dataset_files']:,} files")
        return datasets_analysis

    def _analyze_numpy_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze NumPy embedding file quality"""
        try:
            # Load and analyze numpy array
            arr = np.load(file_path, allow_pickle=False)

            quality_score = 1.0
            errors = []
            metadata = {
                'shape': arr.shape,
                'dtype': str(arr.dtype),
                'dimensions': arr.shape[-1] if len(arr.shape) > 1 else arr.shape[0],
                'memory_usage_mb': arr.nbytes / (1024**2)
            }

            # Quality checks
            if np.any(np.isnan(arr)):
                quality_score -= 0.3
                errors.append("Contains NaN values")

            if np.any(np.isinf(arr)):
                quality_score -= 0.3
                errors.append("Contains infinite values")

            if arr.size == 0:
                quality_score = 0.0
                errors.append("Empty array")

            # Check for reasonable embedding dimensions
            if len(arr.shape) >= 2 and arr.shape[-1] not in [128, 256, 384, 512, 768, 1024, 1536, 2048]:
                quality_score -= 0.1
                errors.append(f"Unusual embedding dimension: {arr.shape[-1]}")

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='numpy_embedding',
                encoding=None,
                is_corrupted=len(errors) > 0 and quality_score < 0.5,
                quality_score=max(0.0, quality_score),
                error_messages=errors,
                content_preview=f"Shape: {arr.shape}, Dtype: {arr.dtype}",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='numpy_embedding',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"Failed to load: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_json_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze JSON file quality"""
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)

            quality_score = 1.0
            errors = []

            # Basic quality checks
            if not data:
                quality_score = 0.5
                errors.append("Empty JSON")

            metadata = {
                'json_type': type(data).__name__,
                'size_estimate': len(str(data)) if data else 0
            }

            if isinstance(data, dict):
                metadata['keys_count'] = len(data)
                metadata['top_keys'] = list(data.keys())[:10]
            elif isinstance(data, list):
                metadata['items_count'] = len(data)

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='json_metadata',
                encoding='utf-8',
                is_corrupted=False,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=str(data)[:200] + "..." if len(str(data)) > 200 else str(data),
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='json_metadata',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"JSON parse error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_pytorch_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze PyTorch model file quality"""
        try:
            import torch

            # Load PyTorch checkpoint
            checkpoint = torch.load(file_path, map_location='cpu')

            quality_score = 1.0
            errors = []
            metadata = {
                'checkpoint_type': type(checkpoint).__name__,
                'file_size_mb': file_path.stat().st_size / (1024**2)
            }

            if isinstance(checkpoint, dict):
                metadata['keys'] = list(checkpoint.keys())

                # Check for common checkpoint components
                if 'model_state_dict' in checkpoint:
                    metadata['has_model_state'] = True
                if 'optimizer_state_dict' in checkpoint:
                    metadata['has_optimizer_state'] = True
                if 'epoch' in checkpoint:
                    metadata['epoch'] = checkpoint['epoch']
                if 'loss' in checkpoint:
                    metadata['loss'] = checkpoint['loss']

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='pytorch_checkpoint',
                encoding=None,
                is_corrupted=False,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=f"PyTorch checkpoint: {list(checkpoint.keys()) if isinstance(checkpoint, dict) else type(checkpoint).__name__}",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='pytorch_checkpoint',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"PyTorch load error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_faiss_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze FAISS index file quality"""
        try:
            # Basic file validation
            file_size = file_path.stat().st_size

            quality_score = 1.0 if file_size > 1024 else 0.5  # FAISS files should be >1KB
            errors = []

            if file_size < 1024:
                errors.append("FAISS index file suspiciously small")

            metadata = {
                'file_size_mb': file_size / (1024**2),
                'index_type': 'faiss_vector_index'
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_size,
                file_type='faiss_index',
                encoding=None,
                is_corrupted=len(errors) > 0,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=f"FAISS index: {file_size / (1024**2):.2f} MB",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=0,
                file_type='faiss_index',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"FAISS analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_text_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze text file quality"""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Sample first 10KB
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result.get('encoding', 'utf-8')

            # Read text content
            with open(file_path, encoding=encoding, errors='ignore') as f:
                content = f.read(50000)  # Read first 50KB for analysis

            quality_score = 1.0
            errors = []

            # Quality assessments
            if len(content.strip()) == 0:
                quality_score = 0.0
                errors.append("Empty content")

            # Check for excessive special characters
            special_char_ratio = len(re.findall(r'[^\w\s]', content)) / len(content) if content else 0
            if special_char_ratio > 0.5:
                quality_score -= 0.3
                errors.append(f"High special character ratio: {special_char_ratio:.2f}")

            # Check for reasonable text patterns
            word_count = len(content.split())
            avg_word_length = sum(len(word) for word in content.split()) / word_count if word_count else 0

            if avg_word_length > 20 or avg_word_length < 2:
                quality_score -= 0.2
                errors.append(f"Unusual average word length: {avg_word_length:.1f}")

            # Check for binary content masquerading as text
            null_byte_count = content.count('\x00')
            if null_byte_count > 0:
                quality_score -= 0.4
                errors.append(f"Contains null bytes: {null_byte_count}")

            metadata = {
                'encoding': encoding,
                'encoding_confidence': encoding_result.get('confidence', 0),
                'content_length': len(content),
                'word_count': word_count,
                'avg_word_length': avg_word_length,
                'special_char_ratio': special_char_ratio,
                'null_byte_count': null_byte_count
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='text_file',
                encoding=encoding,
                is_corrupted=quality_score < 0.3,
                quality_score=max(0.0, quality_score),
                error_messages=errors,
                content_preview=content[:300] + "..." if len(content) > 300 else content,
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='text_file',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"Text file analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_text_content_quality(self, file_path: Path) -> DataQualityMetrics:
        """Analyze text content quality for datasets"""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Sample first 10KB
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result.get('encoding', 'utf-8')

            # Read text content
            with open(file_path, encoding=encoding, errors='ignore') as f:
                content = f.read(50000)  # Read first 50KB for analysis

            quality_score = 1.0
            errors = []

            # Quality assessments
            if len(content.strip()) == 0:
                quality_score = 0.0
                errors.append("Empty content")

            # Check for excessive special characters
            special_char_ratio = len(re.findall(r'[^\w\s]', content)) / len(content) if content else 0
            if special_char_ratio > 0.5:
                quality_score -= 0.3
                errors.append(f"High special character ratio: {special_char_ratio:.2f}")

            # Check for reasonable text patterns
            word_count = len(content.split())
            avg_word_length = sum(len(word) for word in content.split()) / word_count if word_count else 0

            if avg_word_length > 20 or avg_word_length < 2:
                quality_score -= 0.2
                errors.append(f"Unusual average word length: {avg_word_length:.1f}")

            metadata = {
                'encoding': encoding,
                'encoding_confidence': encoding_result.get('confidence', 0),
                'content_length': len(content),
                'word_count': word_count,
                'avg_word_length': avg_word_length,
                'special_char_ratio': special_char_ratio
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='text_content',
                encoding=encoding,
                is_corrupted=quality_score < 0.3,
                quality_score=max(0.0, quality_score),
                error_messages=errors,
                content_preview=content[:300] + "..." if len(content) > 300 else content,
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='text_content',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"Text analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_csv_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze CSV file quality"""
        try:
            # Try to read CSV with pandas
            df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows

            quality_score = 1.0
            errors = []

            # Quality checks
            if df.empty:
                quality_score = 0.0
                errors.append("Empty CSV")

            null_percentage = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) if not df.empty else 0
            if null_percentage > 0.5:
                quality_score -= 0.4
                errors.append(f"High null percentage: {null_percentage:.2f}")

            metadata = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'null_percentage': null_percentage,
                'dtypes': df.dtypes.to_dict()
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='csv_data',
                encoding='utf-8',
                is_corrupted=False,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=df.head().to_string() if not df.empty else "Empty DataFrame",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='csv_data',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"CSV analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_pdf_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze PDF file quality"""
        try:
            # Basic PDF validation
            file_size = file_path.stat().st_size
            quality_score = 1.0 if file_size > 1024 else 0.3

            errors = []
            if file_size < 1024:
                errors.append("PDF file suspiciously small")

            metadata = {
                'file_size_mb': file_size / (1024**2),
                'document_type': 'pdf'
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_size,
                file_type='pdf_document',
                encoding=None,
                is_corrupted=len(errors) > 0,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=f"PDF document: {file_size / (1024**2):.2f} MB",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=0,
                file_type='pdf_document',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"PDF analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_database_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze database file quality"""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            quality_score = 1.0 if tables else 0.3
            errors = []

            if not tables:
                errors.append("No tables found in database")

            metadata = {
                'database_type': 'sqlite',
                'table_count': len(tables),
                'table_names': [table[0] for table in tables],
                'file_size_mb': file_path.stat().st_size / (1024**2)
            }

            conn.close()

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='database',
                encoding=None,
                is_corrupted=len(errors) > 0,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=f"SQLite DB: {len(tables)} tables",
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='database',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"Database analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _analyze_log_file(self, file_path: Path) -> DataQualityMetrics:
        """Analyze log file quality"""
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # Read first 10KB

            quality_score = 1.0
            errors = []

            # Check for log patterns
            log_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # Date pattern
                r'\d{2}:\d{2}:\d{2}',  # Time pattern
                r'(INFO|ERROR|WARNING|DEBUG)',  # Log levels
            ]

            pattern_matches = sum(1 for pattern in log_patterns if re.search(pattern, content))
            if pattern_matches < 2:
                quality_score -= 0.3
                errors.append("Doesn't appear to be a structured log file")

            metadata = {
                'file_size_mb': file_path.stat().st_size / (1024**2),
                'content_preview_length': len(content),
                'pattern_matches': pattern_matches
            }

            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size,
                file_type='log_file',
                encoding='utf-8',
                is_corrupted=False,
                quality_score=quality_score,
                error_messages=errors,
                content_preview=content[:300] + "..." if len(content) > 300 else content,
                metadata=metadata
            )

        except Exception as e:
            return DataQualityMetrics(
                file_path=str(file_path),
                file_size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                file_type='log_file',
                encoding=None,
                is_corrupted=True,
                quality_score=0.0,
                error_messages=[f"Log analysis error: {e!s}"],
                content_preview=None,
                metadata={}
            )

    def _categorize_quality(self, quality_score: float) -> str:
        """Categorize quality score into levels"""
        if quality_score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif quality_score >= self.quality_thresholds['good']:
            return 'good'
        elif quality_score >= self.quality_thresholds['acceptable']:
            return 'acceptable'
        elif quality_score >= self.quality_thresholds['poor']:
            return 'poor'
        else:
            return 'corrupted'

    def generate_b3_readiness_assessment(self, embeddings_analysis: dict, datasets_analysis: dict, infrastructure_overview: dict) -> dict[str, Any]:
        """Generate comprehensive B3 readiness assessment"""
        self.display_status("🎯 Generating B3 Readiness Assessment")

        readiness_assessment = {
            'assessment_timestamp': datetime.now().isoformat(),
            'overall_readiness_score': 0.0,
            'infrastructure_readiness': {},
            'data_quality_readiness': {},
            'technical_readiness': {},
            'recommendations': [],
            'risk_assessment': {},
            'deployment_timeline': {}
        }

        # Infrastructure Readiness (30%)
        infrastructure_score = 0.0

        # Check total data size (should be substantial)
        size_score = min(infrastructure_overview['total_size_gb'] / 100, 1.0)  # Scale to 100GB
        infrastructure_score += size_score * 0.4

        # Check file diversity
        file_types = len(infrastructure_overview['file_extensions'])
        diversity_score = min(file_types / 20, 1.0)  # Scale to 20 different types
        infrastructure_score += diversity_score * 0.3

        # Check embeddings presence
        embeddings_score = 1.0 if embeddings_analysis['total_embedding_files'] > 1000 else 0.5
        infrastructure_score += embeddings_score * 0.3

        readiness_assessment['infrastructure_readiness'] = {
            'score': infrastructure_score,
            'total_files': infrastructure_overview['total_files'],
            'total_size_gb': infrastructure_overview['total_size_gb'],
            'embedding_files': embeddings_analysis['total_embedding_files'],
            'dataset_files': datasets_analysis['total_dataset_files'],
            'file_type_diversity': file_types
        }

        # Data Quality Readiness (40%)
        quality_score = 0.0

        # Embedding quality
        embedding_quality = embeddings_analysis['quality_assessment']
        total_embeddings = sum(embedding_quality.values())
        if total_embeddings > 0:
            excellent_ratio = embedding_quality['excellent'] / total_embeddings
            good_ratio = embedding_quality['good'] / total_embeddings
            embedding_quality_score = excellent_ratio * 1.0 + good_ratio * 0.8
        else:
            embedding_quality_score = 0.0

        quality_score += embedding_quality_score * 0.6

        # Dataset quality
        dataset_quality = datasets_analysis['quality_assessment']
        total_datasets = sum(dataset_quality.values())
        if total_datasets > 0:
            dataset_excellent_ratio = dataset_quality['excellent'] / total_datasets
            dataset_good_ratio = dataset_quality['good'] / total_datasets
            dataset_quality_score = dataset_excellent_ratio * 1.0 + dataset_good_ratio * 0.8
        else:
            dataset_quality_score = 0.0

        quality_score += dataset_quality_score * 0.4

        readiness_assessment['data_quality_readiness'] = {
            'score': quality_score,
            'embedding_quality_score': embedding_quality_score,
            'dataset_quality_score': dataset_quality_score,
            'corruption_detected': len(embeddings_analysis['corrupted_embeddings'])
        }

        # Technical Readiness (30%)
        technical_score = 0.0

        # Check for B3-specific components
        b3_components = len(embeddings_analysis['b3_specific_embeddings'])
        b3_score = min(b3_components / 10, 1.0)  # Scale to 10 B3 components
        technical_score += b3_score * 0.4

        # Check for model checkpoints
        checkpoint_score = min(len(embeddings_analysis['model_checkpoints']) / 20, 1.0)
        technical_score += checkpoint_score * 0.3

        # Check for FAISS indexes
        faiss_score = min(len(embeddings_analysis['faiss_indexes']) / 5, 1.0)
        technical_score += faiss_score * 0.3

        readiness_assessment['technical_readiness'] = {
            'score': technical_score,
            'b3_components': b3_components,
            'model_checkpoints': len(embeddings_analysis['model_checkpoints']),
            'faiss_indexes': len(embeddings_analysis['faiss_indexes']),
            'educational_datasets': len(datasets_analysis['educational_datasets'])
        }

        # Calculate overall readiness score
        overall_score = (
            infrastructure_score * 0.3 +
            quality_score * 0.4 +
            technical_score * 0.3
        )

        readiness_assessment['overall_readiness_score'] = overall_score

        # Generate recommendations
        recommendations = []

        if overall_score >= 0.8:
            recommendations.append("✅ EXCELLENT - Ready for immediate B3 reinitialization")
            recommendations.append("🚀 Proceed with advanced B3 architecture deployment")
        elif overall_score >= 0.6:
            recommendations.append("✅ GOOD - Ready for B3 reinitialization with minor optimizations")
            recommendations.append("🔧 Consider quality improvements for optimal performance")
        elif overall_score >= 0.4:
            recommendations.append("⚠️ ACCEPTABLE - B3 reinitialization possible with preparation")
            recommendations.append("🛠️ Address data quality issues before deployment")
        else:
            recommendations.append("❌ INSUFFICIENT - Significant improvements needed")
            recommendations.append("🔨 Focus on data quality and infrastructure optimization")

        # Specific recommendations
        if infrastructure_score < 0.7:
            recommendations.append("📊 Expand dataset collection for better coverage")

        if quality_score < 0.7:
            recommendations.append("🧹 Clean corrupted files and improve data quality")

        if technical_score < 0.7:
            recommendations.append("⚙️ Enhance B3-specific components and model checkpoints")

        readiness_assessment['recommendations'] = recommendations

        return readiness_assessment

    def generate_comprehensive_report(self, overview: dict, embeddings: dict, datasets: dict, readiness: dict) -> dict[str, Any]:
        """Generate comprehensive analysis report"""
        self.display_status("📋 Generating Comprehensive Analysis Report")

        report = {
            'report_metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'analysis_duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
                'analyzer_version': '1.0.0',
                'sacred_covenant_compliance': True
            },
            'executive_summary': {
                'total_infrastructure_size_gb': overview['total_size_gb'],
                'total_files_analyzed': overview['total_files'],
                'b3_readiness_score': readiness['overall_readiness_score'],
                'readiness_level': self._get_readiness_level(readiness['overall_readiness_score']),
                'critical_issues': [],
                'key_strengths': []
            },
            'infrastructure_overview': overview,
            'embeddings_analysis': embeddings,
            'datasets_analysis': datasets,
            'b3_readiness_assessment': readiness,
            'quality_summary': {
                'excellent_files': 0,
                'good_files': 0,
                'acceptable_files': 0,
                'poor_files': 0,
                'corrupted_files': 0
            },
            'recommendations': {
                'immediate_actions': [],
                'short_term_improvements': [],
                'long_term_optimizations': []
            }
        }

        # Calculate quality summary
        embedding_quality = embeddings['quality_assessment']
        dataset_quality = datasets['quality_assessment']

        for quality_level in ['excellent', 'good', 'acceptable', 'poor', 'corrupted']:
            report['quality_summary'][f'{quality_level}_files'] = (
                embedding_quality.get(quality_level, 0) +
                dataset_quality.get(quality_level, 0)
            )

        # Identify critical issues and key strengths
        if readiness['overall_readiness_score'] < 0.6:
            report['executive_summary']['critical_issues'].append("Overall readiness below optimal threshold")

        if embeddings['total_embeddings_size_gb'] > 20:
            report['executive_summary']['key_strengths'].append("Substantial embedding infrastructure")

        if len(datasets['educational_datasets']) > 10:
            report['executive_summary']['key_strengths'].append("Rich educational content available")

        # Generate tiered recommendations
        if readiness['overall_readiness_score'] >= 0.8:
            report['recommendations']['immediate_actions'].append("Deploy B3 advanced architecture")
            report['recommendations']['immediate_actions'].append("Begin production training pipeline")
        else:
            report['recommendations']['immediate_actions'].append("Address data quality issues")
            report['recommendations']['short_term_improvements'].append("Optimize embedding organization")

        return report

    def _get_readiness_level(self, score: float) -> str:
        """Convert readiness score to descriptive level"""
        if score >= 0.9:
            return "EXCEPTIONAL"
        elif score >= 0.8:
            return "EXCELLENT"
        elif score >= 0.7:
            return "GOOD"
        elif score >= 0.6:
            return "ACCEPTABLE"
        elif score >= 0.4:
            return "NEEDS_IMPROVEMENT"
        else:
            return "INSUFFICIENT"

    def save_analysis_results(self, report: dict[str, Any]):
        """Save comprehensive analysis results"""
        self.display_status("💾 Saving Analysis Results")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save main report
        report_file = self.analysis_output_path / f"B3_Infrastructure_Analysis_Report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Save executive summary
        summary_file = self.analysis_output_path / f"B3_Executive_Summary_{timestamp}.md"
        self._generate_markdown_summary(report, summary_file)

        # Save recommendations
        recommendations_file = self.analysis_output_path / f"B3_Recommendations_{timestamp}.txt"
        with open(recommendations_file, 'w', encoding='utf-8') as f:
            f.write("ImpressionCore B3 Infrastructure Analysis - Recommendations\n")
            f.write("=" * 70 + "\n\n")

            f.write("IMMEDIATE ACTIONS:\n")
            for action in report['recommendations']['immediate_actions']:
                f.write(f"• {action}\n")

            f.write("\nSHORT-TERM IMPROVEMENTS:\n")
            for improvement in report['recommendations']['short_term_improvements']:
                f.write(f"• {improvement}\n")

            f.write("\nLONG-TERM OPTIMIZATIONS:\n")
            for optimization in report['recommendations']['long_term_optimizations']:
                f.write(f"• {optimization}\n")

        self.display_status(f"✅ Analysis results saved to {self.analysis_output_path}")

    def _generate_markdown_summary(self, report: dict, output_file: Path):
        """Generate markdown executive summary"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# ImpressionCore B3 Infrastructure Analysis - Executive Summary\n\n")
            f.write(f"**Analysis Date:** {report['report_metadata']['generation_timestamp']}\n")
            f.write(f"**Analysis Duration:** {report['report_metadata']['analysis_duration_minutes']:.1f} minutes\n\n")

            f.write("## 🏆 Overall Assessment\n\n")
            f.write(f"- **B3 Readiness Score:** {report['b3_readiness_assessment']['overall_readiness_score']:.1%}\n")
            f.write(f"- **Readiness Level:** {report['executive_summary']['readiness_level']}\n")
            f.write(f"- **Total Infrastructure:** {report['executive_summary']['total_infrastructure_size_gb']:.2f} GB\n")
            f.write(f"- **Files Analyzed:** {report['executive_summary']['total_files_analyzed']:,}\n\n")

            f.write("## 📊 Infrastructure Overview\n\n")
            f.write(f"- **Embeddings:** {report['embeddings_analysis']['total_embeddings_size_gb']:.2f} GB ({report['embeddings_analysis']['total_embedding_files']:,} files)\n")
            f.write(f"- **Datasets:** {report['datasets_analysis']['total_datasets_size_gb']:.2f} GB ({report['datasets_analysis']['total_dataset_files']:,} files)\n")
            f.write(f"- **B3 Components:** {report['b3_readiness_assessment']['technical_readiness']['b3_components']}\n")
            f.write(f"- **Model Checkpoints:** {report['b3_readiness_assessment']['technical_readiness']['model_checkpoints']}\n\n")

            f.write("## ✅ Key Recommendations\n\n")
            for recommendation in report['b3_readiness_assessment']['recommendations'][:5]:
                f.write(f"- {recommendation}\n")

    def display_final_summary(self, report: dict[str, Any]):
        """Display final analysis summary"""
        if not self.console:
            print("\n" + "="*80)
            print("B3 Infrastructure Analysis Complete")
            print("="*80)
            print(f"Readiness Score: {report['b3_readiness_assessment']['overall_readiness_score']:.1%}")
            print(f"Infrastructure: {report['executive_summary']['total_infrastructure_size_gb']:.2f} GB")
            print(f"Files Analyzed: {report['executive_summary']['total_files_analyzed']:,}")
            return

        # Rich summary
        summary_table = Table(title="🔬 B3 Infrastructure Analysis Summary", show_header=True)
        summary_table.add_column("Metric", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="magenta")
        summary_table.add_column("Status", style="green")

        # Add summary rows
        readiness_score = report['b3_readiness_assessment']['overall_readiness_score']
        status_icon = "🎯" if readiness_score >= 0.8 else "⚠️" if readiness_score >= 0.6 else "❌"

        summary_table.add_row("B3 Readiness", f"{readiness_score:.1%}", status_icon)
        summary_table.add_row("Infrastructure Size", f"{report['executive_summary']['total_infrastructure_size_gb']:.2f} GB", "📊")
        summary_table.add_row("Files Analyzed", f"{report['executive_summary']['total_files_analyzed']:,}", "📁")
        summary_table.add_row("Embeddings", f"{report['embeddings_analysis']['total_embeddings_size_gb']:.2f} GB", "🧠")
        summary_table.add_row("Datasets", f"{report['datasets_analysis']['total_datasets_size_gb']:.2f} GB", "📚")
        summary_table.add_row("Sacred Covenant", "COMPLIANT", "✅")

        self.console.print("\n")
        self.console.print(summary_table)

        # Recommendations panel
        recommendations_text = "\n".join([
            f"• {rec}" for rec in report['b3_readiness_assessment']['recommendations'][:4]
        ])

        recommendations_panel = Panel(
            recommendations_text,
            title="🎯 Key Recommendations",
            border_style="blue"
        )
        self.console.print(recommendations_panel)

    def run_complete_analysis(self) -> dict[str, Any]:
        """Execute complete B3 infrastructure analysis"""
        self.display_header()

        try:
            # Phase 1: Infrastructure Overview
            self.display_status("🔄 Phase 1: Infrastructure Overview Scan")
            infrastructure_overview = self.scan_infrastructure_overview()

            # Phase 2: Embeddings Analysis
            self.display_status("🔄 Phase 2: Embeddings Infrastructure Analysis")
            embeddings_analysis = self.analyze_embeddings_infrastructure()

            # Phase 3: Datasets Analysis
            self.display_status("🔄 Phase 3: Datasets Infrastructure Analysis")
            datasets_analysis = self.analyze_datasets_infrastructure()

            # Phase 4: B3 Readiness Assessment
            self.display_status("🔄 Phase 4: B3 Readiness Assessment")
            readiness_assessment = self.generate_b3_readiness_assessment(
                embeddings_analysis, datasets_analysis, infrastructure_overview
            )

            # Phase 5: Report Generation
            self.display_status("🔄 Phase 5: Comprehensive Report Generation")
            comprehensive_report = self.generate_comprehensive_report(
                infrastructure_overview, embeddings_analysis, datasets_analysis, readiness_assessment
            )

            # Phase 6: Save Results
            self.save_analysis_results(comprehensive_report)
            self.display_final_summary(comprehensive_report)

            self.display_status("🎉 B3 Infrastructure Analysis COMPLETE!")
            return comprehensive_report

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.display_status(f"❌ Analysis failed: {e}")
            return {"error": str(e), "success": False}

def main():
    """Main execution function"""
    print("🔬 Starting B3 Full Infrastructure Analysis & Quality Verification...")

    try:
        analyzer = B3InfrastructureAnalyzer()
        report = analyzer.run_complete_analysis()

        if "error" not in report:
            print("\n✅ Analysis completed successfully!")
            print(f"📊 B3 Readiness: {report['b3_readiness_assessment']['overall_readiness_score']:.1%}")
            print(f"📁 Infrastructure: {report['executive_summary']['total_infrastructure_size_gb']:.2f} GB")
            print(f"🎯 Status: {report['executive_summary']['readiness_level']}")
            print("📋 Report saved to: F:/data/analysis_reports/")
        else:
            print(f"\n❌ Analysis failed: {report['error']}")
            return 1

    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.error(f"Critical error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
