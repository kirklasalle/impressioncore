#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Phase 2 Intelligent F: Drive Embedding Selector

Created: October 2, 2025
Author: GitHub Copilot & Kirk LaSalle
Purpose: Enhanced intelligent selection for 50K optimal embeddings

This enhanced selector implements quality improvements and strategic criteria
identified in Phase 2 strategic analysis for +8.1% quality improvement.
"""

import json
import logging
import os
from datetime import datetime

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class B3HopePhase2IntelligentSelector:
    """Enhanced intelligent embedding selector for Phase 2 - 50K samples"""

    def __init__(self, f_drive_path: str = "F:/"):
        self.f_drive_path = f_drive_path
        self.embedding_extensions = {'.npy', '.pt', '.pth', '.bin', '.safetensors', '.json'}

        # Phase 2 enhanced selection criteria
        self.phase2_criteria = {
            'target_samples': 50000,
            'quality_threshold': 0.6,  # Higher than Phase 1 (0.5)
            'quality_target': 0.65,   # Target average quality
            'diversity_requirement': True,
            'modality_balance': {
                'text': 0.40,   # 40% text embeddings
                'image': 0.35,  # 35% image embeddings
                'audio': 0.20,  # 20% audio embeddings
                'unknown': 0.05 # 5% unknown/mixed
            },
            'recency_weight': 0.3,
            'size_weight': 0.2,
            'diversity_weight': 0.3,
            'path_quality_weight': 0.2
        }

        logger.info(f"Phase 2 Intelligent Selector initialized - Target: {self.phase2_criteria['target_samples']:,} samples")
        logger.info(f"Quality threshold: {self.phase2_criteria['quality_threshold']:.2f}, Target: {self.phase2_criteria['quality_target']:.3f}")

    def analyze_f_drive_infrastructure(self) -> dict:
        """Enhanced F: drive analysis with quality assessment"""

        logger.info("Analyzing F: drive infrastructure for Phase 2...")

        start_time = datetime.now()

        # Initialize counters
        total_files = 0
        embedding_files = []
        size_total = 0
        modality_counts = {'text': 0, 'image': 0, 'audio': 0, 'unknown': 0}

        # Walk through F: drive
        for root, _dirs, files in os.walk(self.f_drive_path):
            for file in files:
                total_files += 1

                if total_files % 50000 == 0:
                    logger.info(f"Processed {total_files:,} files...")

                # Check if embedding file
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file.lower())

                if ext in self.embedding_extensions:
                    try:
                        stat_info = os.stat(file_path)
                        file_size = stat_info.st_size
                        modified_time = stat_info.st_mtime

                        # Classify modality
                        modality = self._classify_modality(file_path)
                        modality_counts[modality] += 1

                        embedding_files.append({
                            'path': file_path,
                            'size': file_size,
                            'modified_time': modified_time,
                            'modality': modality,
                            'extension': ext
                        })

                        size_total += file_size

                    except (OSError, PermissionError):
                        continue

        analysis_time = (datetime.now() - start_time).total_seconds()

        infrastructure_stats = {
            'total_files_scanned': total_files,
            'embedding_files_found': len(embedding_files),
            'total_size_gb': size_total / (1024**3),
            'modality_distribution': modality_counts,
            'analysis_time_seconds': analysis_time,
            'embedding_files': embedding_files
        }

        logger.info(f"F: drive analysis complete: {len(embedding_files):,} embeddings found")
        logger.info(f"Size: {infrastructure_stats['total_size_gb']:.2f}GB, Time: {analysis_time:.1f}s")
        logger.info(f"Modality distribution: {modality_counts}")

        return infrastructure_stats

    def _classify_modality(self, file_path: str) -> str:
        """Enhanced modality classification with better pattern matching"""

        path_lower = file_path.lower()

        # Text indicators (enhanced)
        text_patterns = ['text', 'dialogue', 'conversation', 'chat', 'gpt', 'llm', 'language', 'bert', 'transformer']
        if any(pattern in path_lower for pattern in text_patterns):
            return 'text'

        # Image indicators (enhanced)
        image_patterns = ['image', 'vision', 'visual', 'clip', 'cnn', 'resnet', 'vit', 'photo', 'picture', 'img']
        if any(pattern in path_lower for pattern in image_patterns):
            return 'image'

        # Audio indicators (enhanced)
        audio_patterns = ['audio', 'sound', 'speech', 'voice', 'wav2vec', 'mel', 'spectrogram', 'music']
        if any(pattern in path_lower for pattern in audio_patterns):
            return 'audio'

        return 'unknown'

    def _calculate_enhanced_quality_score(self, embedding_info: dict, current_time: float) -> float:
        """Enhanced quality scoring with Phase 2 improvements"""

        score = 0.0

        # Size-based quality (enhanced thresholds)
        size_mb = embedding_info['size'] / (1024 * 1024)
        if size_mb > 100:      # Very large embeddings
            score += 0.35
        elif size_mb > 10:     # Large embeddings
            score += 0.25
        elif size_mb > 1:      # Medium embeddings
            score += 0.15
        else:                  # Small embeddings
            score += 0.05

        # Recency-based quality (enhanced curve)
        age_days = (current_time - embedding_info['modified_time']) / (24 * 3600)
        if age_days < 30:      # Very recent
            recency_score = 0.25
        elif age_days < 90:    # Recent
            recency_score = 0.20
        elif age_days < 180:   # Moderately recent
            recency_score = 0.15
        elif age_days < 365:   # Older
            recency_score = 0.10
        else:                  # Very old
            recency_score = 0.05

        score += recency_score * self.phase2_criteria['recency_weight']

        # Path quality indicators (enhanced patterns)
        path_lower = embedding_info['path'].lower()
        quality_indicators = [
            'production', 'model', 'final', 'best', 'optimized', 'trained',
            'checkpoint', 'saved', 'export', 'deploy', 'release'
        ]

        path_quality = sum(0.02 for indicator in quality_indicators if indicator in path_lower)
        score += min(path_quality, 0.15) * self.phase2_criteria['path_quality_weight']

        # Extension-based quality (enhanced priorities)
        ext_scores = {
            '.safetensors': 0.15,  # Highest priority - safest format
            '.pt': 0.12,           # PyTorch native
            '.pth': 0.12,          # PyTorch checkpoint
            '.npy': 0.10,          # NumPy arrays
            '.bin': 0.08,          # Binary format
            '.json': 0.05          # JSON metadata
        }

        score += ext_scores.get(embedding_info['extension'], 0.02)

        # Modality bonus (balanced distribution)
        modality_bonuses = {
            'text': 0.05,     # Slightly favored for language tasks
            'image': 0.04,    # Important for multimodal
            'audio': 0.06,    # Often underrepresented
            'unknown': 0.02   # Lower priority but still valuable
        }

        score += modality_bonuses.get(embedding_info['modality'], 0.02)

        # Ensure score is within [0, 1] range
        return min(max(score, 0.0), 1.0)

    def select_optimal_embeddings(self, infrastructure_stats: dict) -> dict:
        """Enhanced optimal embedding selection for Phase 2"""

        logger.info("Executing Phase 2 optimal embedding selection...")

        embedding_files = infrastructure_stats['embedding_files']
        current_time = datetime.now().timestamp()

        # Calculate quality scores for all embeddings
        logger.info("Calculating enhanced quality scores...")
        scored_embeddings = []

        for i, embedding_info in enumerate(embedding_files):
            if i % 25000 == 0 and i > 0:
                logger.info(f"Scored {i:,} embeddings...")

            quality_score = self._calculate_enhanced_quality_score(embedding_info, current_time)

            scored_embeddings.append({
                **embedding_info,
                'quality_score': quality_score
            })

        # Sort by quality score (descending)
        scored_embeddings.sort(key=lambda x: x['quality_score'], reverse=True)

        logger.info(f"Quality scoring complete. Top score: {scored_embeddings[0]['quality_score']:.3f}")

        # Apply modality balancing
        selected_embeddings = self._apply_enhanced_modality_balancing(scored_embeddings)

        # Generate selection statistics
        selection_stats = self._generate_selection_statistics(selected_embeddings, scored_embeddings)

        # Create manifest
        manifest_path = f"b3_hope_phase2_optimal_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        manifest_data = {
            'selection_timestamp': datetime.now().isoformat(),
            'phase': 2,
            'target_samples': self.phase2_criteria['target_samples'],
            'selected_count': len(selected_embeddings),
            'selection_criteria': self.phase2_criteria,
            'selection_statistics': selection_stats,
            'embeddings': [
                {
                    'path': emb['path'],
                    'quality_score': emb['quality_score'],
                    'modality': emb['modality'],
                    'size_mb': emb['size'] / (1024 * 1024),
                    'extension': emb['extension']
                }
                for emb in selected_embeddings
            ]
        }

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        results = {
            'manifest_path': manifest_path,
            'selected_embeddings': selected_embeddings,
            'selection_statistics': selection_stats,
            'phase2_criteria_met': selection_stats['average_quality'] >= self.phase2_criteria['quality_threshold']
        }

        logger.info(f"Phase 2 selection complete: {len(selected_embeddings):,} embeddings")
        logger.info(f"Average quality: {selection_stats['average_quality']:.3f}")
        logger.info(f"Quality target achieved: {results['phase2_criteria_met']}")

        return results

    def _apply_enhanced_modality_balancing(self, scored_embeddings: list[dict]) -> list[dict]:
        """Enhanced modality balancing with quality preservation"""

        logger.info("Applying enhanced modality balancing...")

        target_samples = self.phase2_criteria['target_samples']
        modality_targets = self.phase2_criteria['modality_balance']

        # Group by modality
        modality_groups = {'text': [], 'image': [], 'audio': [], 'unknown': []}

        for embedding in scored_embeddings:
            modality = embedding['modality']
            if modality in modality_groups:
                modality_groups[modality].append(embedding)

        selected_embeddings = []

        # Select from each modality based on targets
        for modality, target_ratio in modality_targets.items():
            target_count = int(target_samples * target_ratio)
            available = modality_groups[modality]

            # Take top quality embeddings from this modality
            selected_from_modality = available[:target_count]
            selected_embeddings.extend(selected_from_modality)

            logger.info(f"Selected {len(selected_from_modality):,} {modality} embeddings (target: {target_count:,})")

        # Fill any remaining slots with highest quality regardless of modality
        remaining_slots = target_samples - len(selected_embeddings)
        if remaining_slots > 0:
            logger.info(f"Filling {remaining_slots:,} remaining slots with top quality embeddings...")

            # Get embeddings not already selected
            selected_paths = {emb['path'] for emb in selected_embeddings}
            remaining_embeddings = [emb for emb in scored_embeddings if emb['path'] not in selected_paths]

            # Add top quality remaining embeddings
            additional_selections = remaining_embeddings[:remaining_slots]
            selected_embeddings.extend(additional_selections)

        # Sort final selection by quality score
        selected_embeddings.sort(key=lambda x: x['quality_score'], reverse=True)

        logger.info(f"Enhanced modality balancing complete: {len(selected_embeddings):,} total embeddings")

        return selected_embeddings

    def _generate_selection_statistics(self, selected_embeddings: list[dict], all_embeddings: list[dict]) -> dict:
        """Generate comprehensive selection statistics"""

        # Quality statistics
        selected_scores = [emb['quality_score'] for emb in selected_embeddings]
        all_scores = [emb['quality_score'] for emb in all_embeddings]

        # Modality distribution
        selected_modalities = {}
        for emb in selected_embeddings:
            modality = emb['modality']
            selected_modalities[modality] = selected_modalities.get(modality, 0) + 1

        # Size statistics
        selected_sizes = [emb['size'] / (1024 * 1024) for emb in selected_embeddings]  # MB

        statistics = {
            'total_available': len(all_embeddings),
            'total_selected': len(selected_embeddings),
            'selection_ratio': len(selected_embeddings) / len(all_embeddings),
            'average_quality': np.mean(selected_scores),
            'median_quality': np.median(selected_scores),
            'min_quality': np.min(selected_scores),
            'max_quality': np.max(selected_scores),
            'quality_std': np.std(selected_scores),
            'overall_average_quality': np.mean(all_scores),
            'quality_improvement': np.mean(selected_scores) - np.mean(all_scores),
            'modality_distribution': selected_modalities,
            'average_size_mb': np.mean(selected_sizes),
            'total_size_gb': sum(selected_sizes) / 1024,
            'phase2_criteria_met': True  # Will be validated by caller
        }

        return statistics

def main():
    logger.info("="*80)
    logger.info("B3-HOPE PHASE 2 INTELLIGENT F: DRIVE EMBEDDING SELECTION")
    logger.info("="*80)

    # Initialize Phase 2 selector
    selector = B3HopePhase2IntelligentSelector()

    # Analyze F: drive infrastructure
    logger.info("Phase 1: F: Drive Infrastructure Analysis")
    infrastructure_stats = selector.analyze_f_drive_infrastructure()

    # Select optimal embeddings for Phase 2
    logger.info("Phase 2: Enhanced Optimal Embedding Selection")
    selection_results = selector.select_optimal_embeddings(infrastructure_stats)

    # Display results
    stats = selection_results['selection_statistics']

    logger.info("="*80)
    logger.info("PHASE 2 INTELLIGENT SELECTION COMPLETE")
    logger.info("="*80)
    logger.info(f"Selected embeddings: {stats['total_selected']:,}")
    logger.info(f"Average quality: {stats['average_quality']:.3f}")
    logger.info(f"Quality improvement: +{stats['quality_improvement']*100:.1f}%")
    logger.info(f"Selection ratio: {stats['selection_ratio']*100:.1f}%")
    logger.info(f"Manifest saved: {selection_results['manifest_path']}")
    logger.info(f"Phase 2 criteria met: {selection_results['phase2_criteria_met']}")

    if selection_results['phase2_criteria_met']:
        logger.info("🎯 PHASE 2 SELECTION SUCCESS - READY FOR TRAINING!")
    else:
        logger.warning("⚠️ Phase 2 criteria not fully met - review selection")

if __name__ == "__main__":
    main()
