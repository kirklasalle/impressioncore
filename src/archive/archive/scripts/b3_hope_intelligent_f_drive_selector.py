#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Intelligent F: Drive Embedding Selector

Created: October 2, 2025
Author: GitHub Copilot & Kirk LaSalle
Purpose: Intelligent selection and optimization of F: drive embeddings for maximum B3-Hope training effectiveness

This system analyzes the 507,939 available F: drive embeddings and implements smart selection
strategies to maximize training quality and efficiency.
"""

import os
import sys
import json
import logging
import argparse
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import torch
import pickle
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'b3_hope_intelligent_selector_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingInfo:
    """Information about a single embedding file"""
    file_path: str
    file_size: int
    last_modified: float
    embedding_type: str  # 'numpy', 'pytorch', 'text', 'image', 'audio'
    quality_score: float = 0.0
    dimensions: Optional[int] = None
    sample_count: Optional[int] = None

@dataclass
class SelectionCriteria:
    """Criteria for intelligent embedding selection"""
    target_samples: int = 50000
    quality_threshold: float = 0.5
    diversity_factor: float = 0.3
    recency_factor: float = 0.2
    size_preference: str = "medium"  # 'small', 'medium', 'large'
    modality_balance: Dict[str, float] = None

    def __post_init__(self):
        if self.modality_balance is None:
            self.modality_balance = {
                'text': 0.4,
                'image': 0.35,
                'audio': 0.25
            }

class B3HopeIntelligentFDriveSelector:
    """Intelligent F: Drive embedding selector for B3-Hope training optimization"""

    def __init__(self, f_data_path: str = "F:/data", f_models_path: str = "F:/models"):
        self.f_data_path = Path(f_data_path)
        self.f_models_path = Path(f_models_path)
        self.embedding_info: List[EmbeddingInfo] = []

        logger.info("Initializing B3-Hope Intelligent F: Drive Selector...")
        logger.info(f"F: data path: {self.f_data_path}")
        logger.info(f"F: models path: {self.f_models_path}")

    def analyze_f_drive_infrastructure(self, force_refresh: bool = False) -> Dict:
        """Analyze F: drive infrastructure with NO CACHING - fresh scan every time"""

        logger.info("Performing fresh F: drive infrastructure analysis (NO CACHE)...")

        # Quick statistics
        stats = {
            'total_files': 0,
            'total_size_gb': 0.0,
            'embedding_files': 0,
            'modality_counts': defaultdict(int),
            'file_type_counts': defaultdict(int),
            'embeddings': []
        }

        # Define embedding file patterns
        embedding_patterns = {
            '.npy': 'numpy',
            '.npz': 'numpy',
            '.pth': 'pytorch',
            '.pt': 'pytorch',
            '.pkl': 'pickle',
            '.json': 'json'
        }

        # Scan F: data directory with robust error handling
        if os.path.exists(str(self.f_data_path)):
            logger.info(f"Scanning F: data directory: {self.f_data_path}")

            try:
                for root, dirs, files in os.walk(str(self.f_data_path)):
                    for file in files:
                        try:
                            # Use string paths to avoid PathLib issues
                            file_path_str = os.path.join(root, file)

                            # Get file stats safely
                            try:
                                file_stat = os.stat(file_path_str)
                                file_size = file_stat.st_size
                                last_modified = file_stat.st_mtime
                            except (OSError, IOError) as e:
                                logger.debug(f"Could not stat {file_path_str}: {e}")
                                continue

                            stats['total_files'] += 1
                            stats['total_size_gb'] += file_size / (1024**3)

                            # Check if it's an embedding file
                            _, suffix = os.path.splitext(file.lower())
                            if suffix in embedding_patterns:
                                stats['embedding_files'] += 1
                                stats['file_type_counts'][suffix] += 1

                                # Determine modality based on path
                                modality = self._infer_modality(file_path_str)
                                stats['modality_counts'][modality] += 1

                                # Create embedding info
                                embedding_info = EmbeddingInfo(
                                    file_path=file_path_str,
                                    file_size=file_size,
                                    last_modified=last_modified,
                                    embedding_type=embedding_patterns[suffix],
                                    quality_score=self._estimate_quality_score_from_string(file_path_str, modality, file_size, last_modified)
                                )

                                stats['embeddings'].append(embedding_info)

                                if len(stats['embeddings']) % 10000 == 0:
                                    logger.info(f"Processed {len(stats['embeddings'])} embeddings...")

                        except Exception as e:
                            logger.debug(f"Error processing file {file}: {e}")
                            continue

            except Exception as e:
                logger.error(f"Error scanning F: data directory: {e}")

        # Scan F: models directory
        if os.path.exists(str(self.f_models_path)):
            logger.info(f"Scanning F: models directory: {self.f_models_path}")

            try:
                for root, dirs, files in os.walk(str(self.f_models_path)):
                    for file in files:
                        try:
                            file_path_str = os.path.join(root, file)

                            try:
                                file_stat = os.stat(file_path_str)
                                file_size = file_stat.st_size
                            except (OSError, IOError):
                                continue

                            stats['total_files'] += 1
                            stats['total_size_gb'] += file_size / (1024**3)

                            _, suffix = os.path.splitext(file.lower())
                            stats['file_type_counts'][suffix] += 1

                        except Exception as e:
                            logger.debug(f"Error processing model file {file}: {e}")
                            continue

            except Exception as e:
                logger.error(f"Error scanning F: models directory: {e}")

        logger.info(f"Analysis complete: {stats['total_files']} total files, {stats['embedding_files']} embeddings")
        logger.info(f"Total size: {stats['total_size_gb']:.1f}GB")
        logger.info(f"Modality distribution: {dict(stats['modality_counts'])}")

        return stats

    def _infer_modality(self, file_path: str) -> str:
        """Infer the modality of an embedding based on file path"""
        path_lower = file_path.lower()

        if any(keyword in path_lower for keyword in ['text', 'nlp', 'language', 'bert', 'gpt']):
            return 'text'
        elif any(keyword in path_lower for keyword in ['image', 'vision', 'visual', 'clip', 'resnet']):
            return 'image'
        elif any(keyword in path_lower for keyword in ['audio', 'speech', 'sound', 'wav2vec', 'audio']):
            return 'audio'
        else:
            return 'unknown'

    def _estimate_quality_score_from_string(self, file_path_str: str, modality: str, file_size: int, last_modified: float) -> float:
        """Estimate quality score for an embedding file using string path"""
        score = 0.5  # Base score

        # Size-based scoring (assuming larger files often contain more information)
        size_mb = file_size / (1024**2)
        if 1 <= size_mb <= 100:  # Sweet spot for embedding files
            score += 0.2
        elif size_mb > 100:
            score += 0.1

        # Recency scoring (newer files might be better processed)
        age_days = (datetime.now().timestamp() - last_modified) / 86400
        if age_days < 30:
            score += 0.2
        elif age_days < 90:
            score += 0.1

        # Path-based quality hints
        path_lower = file_path_str.lower()
        if 'processed' in path_lower or 'clean' in path_lower:
            score += 0.1
        if 'embeddings' in path_lower:
            score += 0.1
        if 'high_quality' in path_lower or 'best' in path_lower:
            score += 0.2

        return min(score, 1.0)

    def select_optimal_embeddings(self, criteria: SelectionCriteria) -> List[EmbeddingInfo]:
        """Select optimal embeddings based on intelligent criteria"""

        logger.info("Starting intelligent embedding selection...")
        logger.info(f"Target samples: {criteria.target_samples}")
        logger.info(f"Quality threshold: {criteria.quality_threshold}")

        # Load analysis
        analysis = self.analyze_f_drive_infrastructure()
        all_embeddings = analysis['embeddings']

        logger.info(f"Total available embeddings: {len(all_embeddings)}")

        # Filter by quality threshold
        quality_embeddings = [emb for emb in all_embeddings if emb.quality_score >= criteria.quality_threshold]
        logger.info(f"Embeddings meeting quality threshold: {len(quality_embeddings)}")

        # Group by modality
        modality_groups = defaultdict(list)
        for emb in quality_embeddings:
            modality = self._infer_modality(emb.file_path)
            modality_groups[modality].append(emb)

        logger.info(f"Modality distribution: {[(k, len(v)) for k, v in modality_groups.items()]}")

        # Select balanced samples from each modality
        selected_embeddings = []

        for modality, target_ratio in criteria.modality_balance.items():
            available = modality_groups.get(modality, [])
            target_count = int(criteria.target_samples * target_ratio)

            if len(available) == 0:
                logger.warning(f"No {modality} embeddings available")
                continue

            # Sort by quality score (descending)
            available.sort(key=lambda x: x.quality_score, reverse=True)

            # Select top quality embeddings up to target count
            selected = available[:min(target_count, len(available))]
            selected_embeddings.extend(selected)

            logger.info(f"Selected {len(selected)} {modality} embeddings (target: {target_count})")

        # If we haven't reached target, add best remaining embeddings
        if len(selected_embeddings) < criteria.target_samples:
            remaining_needed = criteria.target_samples - len(selected_embeddings)
            selected_paths = {emb.file_path for emb in selected_embeddings}

            remaining_embeddings = [emb for emb in quality_embeddings if emb.file_path not in selected_paths]
            remaining_embeddings.sort(key=lambda x: x.quality_score, reverse=True)

            additional = remaining_embeddings[:remaining_needed]
            selected_embeddings.extend(additional)

            logger.info(f"Added {len(additional)} additional high-quality embeddings")

        logger.info(f"Final selection: {len(selected_embeddings)} embeddings")

        # Calculate selection statistics
        avg_quality = sum(emb.quality_score for emb in selected_embeddings) / len(selected_embeddings)
        total_size_gb = sum(emb.file_size for emb in selected_embeddings) / (1024**3)

        logger.info(f"Average quality score: {avg_quality:.3f}")
        logger.info(f"Total selected size: {total_size_gb:.2f}GB")

        return selected_embeddings

    def save_selection_manifest(self, selected_embeddings: List[EmbeddingInfo], output_path: str = "b3_hope_optimal_embeddings.json"):
        """Save selection manifest for training use"""

        manifest = {
            'creation_date': datetime.now().isoformat(),
            'total_embeddings': len(selected_embeddings),
            'selection_criteria': 'intelligent_quality_based',
            'embeddings': []
        }

        for emb in selected_embeddings:
            manifest['embeddings'].append({
                'file_path': emb.file_path,
                'file_size': emb.file_size,
                'quality_score': emb.quality_score,
                'embedding_type': emb.embedding_type,
                'modality': self._infer_modality(emb.file_path)
            })

        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Selection manifest saved to {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="B3-Hope Intelligent F: Drive Embedding Selector")
    parser.add_argument("--target_samples", type=int, default=50000, help="Target number of embeddings to select")
    parser.add_argument("--quality_threshold", type=float, default=0.5, help="Minimum quality score threshold")
    parser.add_argument("--force_refresh", action="store_true", help="Force refresh of F: drive analysis cache")
    parser.add_argument("--output_manifest", type=str, default="b3_hope_optimal_embeddings.json", help="Output manifest file")

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("B3-HOPE INTELLIGENT F: DRIVE EMBEDDING SELECTOR")
    logger.info("="*80)

    # Initialize selector
    selector = B3HopeIntelligentFDriveSelector()

    # Create selection criteria
    criteria = SelectionCriteria(
        target_samples=args.target_samples,
        quality_threshold=args.quality_threshold
    )

    # Perform intelligent selection
    selected_embeddings = selector.select_optimal_embeddings(criteria)

    # Save manifest
    manifest_path = selector.save_selection_manifest(selected_embeddings, args.output_manifest)

    logger.info("="*80)
    logger.info("INTELLIGENT SELECTION COMPLETE")
    logger.info("="*80)
    logger.info(f"Selected {len(selected_embeddings)} optimal embeddings")
    logger.info(f"Manifest saved to: {manifest_path}")
    logger.info("Ready for B3-Hope production training!")

if __name__ == "__main__":
    main()