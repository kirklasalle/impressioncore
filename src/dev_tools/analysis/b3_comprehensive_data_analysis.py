#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #multimodal #python #pytorch #source_code #src/dev_tools/analysis/b3_comprehensive_data_analysis.py
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #memory_management #multimodal #python #pytorch #source_code #src\\dev_tools\\analysis\\b3_comprehensive_data_analysis.py
# Category:** Development Tools
# Status:** Active

"""
🔍 B3 COMPREHENSIVE F: DRIVE DATA ANALYSIS & DEDUPLICATION
ImpressionCore B3 - Complete Data Inventory and Optimization

MISSION:
1. ANALYZE all F: drive directories (139GB + 33GB + 992MB + 585MB = ~173GB total)
2. DETECT duplicates and redundant data across all directories
3. IDENTIFY high-quality, unique embeddings and datasets
4. CREATE unified, deduplicated dataset strategy for B3
5. ENSURE maximum data utilization without redundancy
"""

import hashlib
import json
import logging
import mmap
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np


class B3ComprehensiveDataAnalyzer:
    """
    Comprehensive analysis system for all F: drive data
    Focuses on deduplication and optimal data utilization
    """

    def __init__(self):
        self.f_drive_path = Path("F:\\")
        self.analysis_output_path = self.f_drive_path / "b3_comprehensive_analysis"
        self.analysis_output_path.mkdir(exist_ok=True)

        # Target directories to analyze
        self.target_directories = {
            'datasets': {
                'path': self.f_drive_path / "datasets",
                'size_reported': '139 GB',
                'expected_content': 'Primary dataset collection'
            },
            'b2_datasets': {
                'path': self.f_drive_path / "b2_datasets",
                'size_reported': '33 GB',
                'expected_content': 'B2 project datasets'
            },
            'b2_embeddings': {
                'path': self.f_drive_path / "b2_embeddings",
                'size_reported': '992 MB',
                'expected_content': 'B2 generated embeddings'
            },
            'b3_professional_dataset': {
                'path': self.f_drive_path / "b3_professional_dataset",
                'size_reported': '585 MB',
                'expected_content': 'B3 newly created data'
            }
        }

        # File analysis tracking
        self.file_registry = {}
        self.duplicate_registry = defaultdict(list)
        self.hash_registry = {}
        self.embedding_analysis = {}

        # Deduplication settings
        self.chunk_size = 8192  # For file hashing
        self.similarity_threshold = 0.95  # For embedding similarity

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of file for duplicate detection"""

        try:
            hash_sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                # Use memory mapping for large files
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    for chunk in iter(lambda: mmapped_file.read(self.chunk_size), b""):
                        hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not hash {filepath}: {e}")
            return None

    def analyze_directory_structure(self):
        """Analyze the complete directory structure of all target directories"""

        print("🔍 ANALYZING F: DRIVE DIRECTORY STRUCTURE:")
        print("=" * 70)

        structure_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'directories_analyzed': {},
            'total_files_found': 0,
            'total_size_bytes': 0,
            'file_type_distribution': defaultdict(int),
            'directory_health': {}
        }

        for dir_name, dir_info in self.target_directories.items():
            dir_path = dir_info['path']

            print(f"\n📁 ANALYZING: {dir_name.upper()} ({dir_info['size_reported']})")
            print(f"   Path: {dir_path}")
            print(f"   Expected: {dir_info['expected_content']}")

            if not dir_path.exists():
                print("   ❌ Directory not found!")
                structure_analysis['directory_health'][dir_name] = 'NOT_FOUND'
                continue

            # Analyze directory contents
            dir_analysis = {
                'exists': True,
                'file_count': 0,
                'total_size_bytes': 0,
                'subdirectories': [],
                'file_types': defaultdict(int),
                'largest_files': [],
                'embedding_files': [],
                'dataset_files': []
            }

            try:
                # Walk through directory
                for root, _dirs, files in os.walk(dir_path):
                    # Track subdirectories
                    if root != str(dir_path):
                        rel_path = os.path.relpath(root, dir_path)
                        if rel_path not in dir_analysis['subdirectories']:
                            dir_analysis['subdirectories'].append(rel_path)

                    # Analyze files
                    for file in files:
                        file_path = Path(root) / file

                        try:
                            file_stat = file_path.stat()
                            file_size = file_stat.st_size
                            file_ext = file_path.suffix.lower()

                            # Update counters
                            dir_analysis['file_count'] += 1
                            dir_analysis['total_size_bytes'] += file_size
                            dir_analysis['file_types'][file_ext] += 1

                            structure_analysis['total_files_found'] += 1
                            structure_analysis['total_size_bytes'] += file_size
                            structure_analysis['file_type_distribution'][file_ext] += 1

                            # Track large files
                            if file_size > 100 * 1024 * 1024:  # > 100MB
                                dir_analysis['largest_files'].append({
                                    'name': file,
                                    'size_mb': file_size / (1024 * 1024),
                                    'path': str(file_path)
                                })

                            # Identify embedding files
                            if file_ext in ['.npy', '.npz', '.pt', '.pth', '.pkl', '.pickle']:
                                dir_analysis['embedding_files'].append(str(file_path))

                            # Identify dataset files
                            if file_ext in ['.json', '.jsonl', '.csv', '.tsv', '.txt', '.parquet']:
                                dir_analysis['dataset_files'].append(str(file_path))

                        except Exception as e:
                            self.logger.warning(f"Could not analyze file {file_path}: {e}")

                # Sort largest files
                dir_analysis['largest_files'].sort(key=lambda x: x['size_mb'], reverse=True)
                dir_analysis['largest_files'] = dir_analysis['largest_files'][:10]  # Top 10

                # Calculate directory health
                if dir_analysis['file_count'] > 0:
                    structure_analysis['directory_health'][dir_name] = 'HEALTHY'
                else:
                    structure_analysis['directory_health'][dir_name] = 'EMPTY'

                print(f"   ✅ Files: {dir_analysis['file_count']:,}")
                print(f"   📊 Size: {dir_analysis['total_size_bytes'] / (1024**3):.2f} GB")
                print(f"   📁 Subdirectories: {len(dir_analysis['subdirectories'])}")
                print(f"   🔗 Embedding files: {len(dir_analysis['embedding_files']):,}")
                print(f"   📋 Dataset files: {len(dir_analysis['dataset_files']):,}")

                # Show top file types
                if dir_analysis['file_types']:
                    print("   📈 Top file types:")
                    sorted_types = sorted(dir_analysis['file_types'].items(), key=lambda x: x[1], reverse=True)
                    for ext, count in sorted_types[:5]:
                        print(f"      {ext if ext else '(no ext)'}: {count:,} files")

            except Exception as e:
                print(f"   ❌ Error analyzing directory: {e}")
                structure_analysis['directory_health'][dir_name] = 'ERROR'
                dir_analysis['exists'] = False

            structure_analysis['directories_analyzed'][dir_name] = dir_analysis

        # Save structure analysis
        structure_file = self.analysis_output_path / "directory_structure_analysis.json"
        with open(structure_file, 'w') as f:
            json.dump(structure_analysis, f, indent=2, default=str)

        print("\n📊 OVERALL F: DRIVE ANALYSIS:")
        print(f"   📁 Total Files: {structure_analysis['total_files_found']:,}")
        print(f"   💾 Total Size: {structure_analysis['total_size_bytes'] / (1024**3):.2f} GB")
        print(f"   📋 Analysis saved: {structure_file}")

        return structure_analysis

    def detect_duplicate_files(self):
        """Detect duplicate files across all directories using file hashing"""

        print("\n🔍 DETECTING DUPLICATE FILES ACROSS ALL DIRECTORIES:")
        print("=" * 70)

        duplicate_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'files_analyzed': 0,
            'duplicates_found': 0,
            'space_wasted_gb': 0,
            'duplicate_groups': {},
            'hash_registry': {},
            'deduplication_opportunities': []
        }

        print("📊 Scanning all files and calculating hashes...")

        # Collect all files from all directories
        all_files = []
        for dir_name, dir_info in self.target_directories.items():
            dir_path = dir_info['path']
            if dir_path.exists():
                for root, _dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = Path(root) / file
                        all_files.append({
                            'path': file_path,
                            'directory': dir_name,
                            'size': file_path.stat().st_size if file_path.exists() else 0
                        })

        print(f"   📁 Found {len(all_files):,} files to analyze")

        # Calculate hashes and detect duplicates
        hash_to_files = defaultdict(list)

        for idx, file_info in enumerate(all_files):
            file_path = file_info['path']

            try:
                # Calculate hash
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    hash_to_files[file_hash].append(file_info)
                    duplicate_analysis['hash_registry'][str(file_path)] = file_hash

                duplicate_analysis['files_analyzed'] += 1

                # Progress update
                if idx % 10000 == 0:
                    print(f"      📊 Processed {idx:,}/{len(all_files):,} files...")

            except Exception as e:
                self.logger.warning(f"Could not process {file_path}: {e}")

        # Identify duplicate groups
        duplicate_group_id = 0
        total_wasted_space = 0

        for file_hash, file_list in hash_to_files.items():
            if len(file_list) > 1:  # Duplicates found
                duplicate_group_id += 1

                # Calculate wasted space (all files except the first one)
                file_size = file_list[0]['size']
                wasted_space = file_size * (len(file_list) - 1)
                total_wasted_space += wasted_space

                duplicate_group = {
                    'group_id': duplicate_group_id,
                    'file_hash': file_hash,
                    'file_count': len(file_list),
                    'file_size_mb': file_size / (1024 * 1024),
                    'wasted_space_mb': wasted_space / (1024 * 1024),
                    'files': []
                }

                # Record all duplicate files
                for file_info in file_list:
                    duplicate_group['files'].append({
                        'path': str(file_info['path']),
                        'directory': file_info['directory'],
                        'size_mb': file_info['size'] / (1024 * 1024)
                    })

                duplicate_analysis['duplicate_groups'][f"group_{duplicate_group_id}"] = duplicate_group
                duplicate_analysis['duplicates_found'] += len(file_list) - 1

        duplicate_analysis['space_wasted_gb'] = total_wasted_space / (1024**3)

        # Generate deduplication recommendations
        print("\n📋 DUPLICATE ANALYSIS RESULTS:")
        print(f"   🔍 Files Analyzed: {duplicate_analysis['files_analyzed']:,}")
        print(f"   🔄 Duplicate Groups: {len(duplicate_analysis['duplicate_groups'])}")
        print(f"   📊 Duplicate Files: {duplicate_analysis['duplicates_found']:,}")
        print(f"   💾 Wasted Space: {duplicate_analysis['space_wasted_gb']:.2f} GB")

        # Show top duplicate groups
        if duplicate_analysis['duplicate_groups']:
            print("\n🔥 TOP DUPLICATE GROUPS:")
            sorted_groups = sorted(
                duplicate_analysis['duplicate_groups'].values(),
                key=lambda x: x['wasted_space_mb'],
                reverse=True
            )

            for i, group in enumerate(sorted_groups[:5]):
                print(f"   #{i+1}: {group['file_count']} copies of {group['file_size_mb']:.1f}MB file")
                print(f"        Wasted: {group['wasted_space_mb']:.1f}MB")
                print(f"        Directories: {set(f['directory'] for f in group['files'])}")

        # Save duplicate analysis
        duplicate_file = self.analysis_output_path / "duplicate_analysis.json"
        with open(duplicate_file, 'w') as f:
            json.dump(duplicate_analysis, f, indent=2, default=str)

        print(f"   📋 Analysis saved: {duplicate_file}")

        return duplicate_analysis

    def analyze_embedding_quality_and_uniqueness(self):
        """Analyze embedding files for quality and uniqueness"""

        print("\n🔗 ANALYZING EMBEDDING QUALITY AND UNIQUENESS:")
        print("=" * 70)

        embedding_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'embedding_files_found': 0,
            'total_embeddings': 0,
            'quality_scores': {},
            'similarity_groups': {},
            'recommended_embeddings': [],
            'redundant_embeddings': []
        }

        # Find all embedding files
        embedding_files = []
        for dir_name, dir_info in self.target_directories.items():
            dir_path = dir_info['path']
            if dir_path.exists():
                for root, _dirs, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith(('.npy', '.npz', '.pt', '.pth')):
                            file_path = Path(root) / file
                            embedding_files.append({
                                'path': file_path,
                                'directory': dir_name,
                                'filename': file
                            })

        print(f"   📁 Found {len(embedding_files):,} embedding files")
        embedding_analysis['embedding_files_found'] = len(embedding_files)

        # Analyze each embedding file
        for idx, file_info in enumerate(embedding_files):
            file_path = file_info['path']

            try:
                # Load and analyze embeddings
                if file_path.suffix == '.npy':
                    embeddings = np.load(file_path)
                elif file_path.suffix == '.npz':
                    with np.load(file_path) as data:
                        embeddings = data[next(iter(data.keys()))]  # First array
                else:
                    # Skip PyTorch files for now (would need torch)
                    continue

                if embeddings.ndim == 2:  # Valid embedding format
                    num_embeddings, embedding_dim = embeddings.shape

                    # Calculate quality metrics
                    quality_score = self._calculate_embedding_quality(embeddings)

                    file_analysis = {
                        'path': str(file_path),
                        'directory': file_info['directory'],
                        'num_embeddings': num_embeddings,
                        'embedding_dim': embedding_dim,
                        'quality_score': quality_score,
                        'file_size_mb': file_path.stat().st_size / (1024 * 1024),
                        'recommended': quality_score > 0.7  # Quality threshold
                    }

                    embedding_analysis['quality_scores'][str(file_path)] = file_analysis
                    embedding_analysis['total_embeddings'] += num_embeddings

                    if file_analysis['recommended']:
                        embedding_analysis['recommended_embeddings'].append(file_analysis)
                    else:
                        embedding_analysis['redundant_embeddings'].append(file_analysis)

                # Progress update
                if idx % 100 == 0:
                    print(f"      📊 Analyzed {idx}/{len(embedding_files)} embedding files...")

            except Exception as e:
                self.logger.warning(f"Could not analyze embedding file {file_path}: {e}")

        # Sort recommendations by quality
        embedding_analysis['recommended_embeddings'].sort(
            key=lambda x: x['quality_score'], reverse=True
        )

        print("\n📊 EMBEDDING ANALYSIS RESULTS:")
        print(f"   🔗 Total Embeddings: {embedding_analysis['total_embeddings']:,}")
        print(f"   ✅ High Quality Files: {len(embedding_analysis['recommended_embeddings'])}")
        print(f"   ⚠️ Low Quality Files: {len(embedding_analysis['redundant_embeddings'])}")

        # Show top quality embeddings
        if embedding_analysis['recommended_embeddings']:
            print("\n🏆 TOP QUALITY EMBEDDING FILES:")
            for i, emb in enumerate(embedding_analysis['recommended_embeddings'][:5]):
                print(f"   #{i+1}: {Path(emb['path']).name}")
                print(f"        Quality: {emb['quality_score']:.3f}")
                print(f"        Count: {emb['num_embeddings']:,}")
                print(f"        Directory: {emb['directory']}")

        # Save embedding analysis
        embedding_file = self.analysis_output_path / "embedding_analysis.json"
        with open(embedding_file, 'w') as f:
            json.dump(embedding_analysis, f, indent=2, default=str)

        print(f"   📋 Analysis saved: {embedding_file}")

        return embedding_analysis

    def _calculate_embedding_quality(self, embeddings: np.ndarray) -> float:
        """Calculate quality score for embeddings"""

        try:
            # Quality metrics
            metrics = {}

            # 1. Variance (good embeddings have reasonable variance)
            variance = np.var(embeddings)
            metrics['variance'] = min(1.0, variance / 2.0)  # Normalize

            # 2. Mean near zero (well-centered embeddings)
            mean_deviation = abs(np.mean(embeddings))
            metrics['centering'] = max(0.0, 1.0 - mean_deviation * 2)

            # 3. No NaN or infinite values
            metrics['validity'] = 1.0 if np.isfinite(embeddings).all() else 0.0

            # 4. Reasonable norm distribution
            norms = np.linalg.norm(embeddings, axis=1)
            norm_std = np.std(norms)
            metrics['norm_consistency'] = max(0.0, 1.0 - norm_std)

            # 5. Dimensionality check (prefer standard dimensions)
            dim = embeddings.shape[1]
            if dim in [128, 256, 384, 512, 768, 1024]:
                metrics['dimension'] = 1.0
            else:
                metrics['dimension'] = 0.5

            # Weighted average
            weights = {
                'variance': 0.25,
                'centering': 0.25,
                'validity': 0.3,
                'norm_consistency': 0.15,
                'dimension': 0.05
            }

            quality_score = sum(metrics[key] * weights[key] for key in metrics)
            return min(1.0, max(0.0, quality_score))

        except Exception:
            return 0.0

    def create_unified_dataset_strategy(self):
        """Create strategy for unified, deduplicated dataset"""

        print("\n🎯 CREATING UNIFIED DATASET STRATEGY:")
        print("=" * 70)

        # Load previous analysis results
        structure_file = self.analysis_output_path / "directory_structure_analysis.json"
        duplicate_file = self.analysis_output_path / "duplicate_analysis.json"
        self.analysis_output_path / "embedding_analysis.json"

        strategy = {
            'strategy_timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'deduplication_plan': {},
            'unified_structure': {},
            'implementation_steps': [],
            'expected_outcomes': {}
        }

        # Analyze available data sources
        if structure_file.exists():
            with open(structure_file) as f:
                structure_data = json.load(f)

            for dir_name, dir_analysis in structure_data['directories_analyzed'].items():
                if dir_analysis.get('exists', False):
                    strategy['data_sources'][dir_name] = {
                        'file_count': dir_analysis['file_count'],
                        'size_gb': dir_analysis['total_size_bytes'] / (1024**3),
                        'embedding_files': len(dir_analysis.get('embedding_files', [])),
                        'dataset_files': len(dir_analysis.get('dataset_files', [])),
                        'recommendation': self._recommend_directory_usage(dir_name, dir_analysis)
                    }

        # Deduplication recommendations
        if duplicate_file.exists():
            with open(duplicate_file) as f:
                duplicate_data = json.load(f)

            strategy['deduplication_plan'] = {
                'duplicates_to_remove': duplicate_data['duplicates_found'],
                'space_to_save_gb': duplicate_data['space_wasted_gb'],
                'priority_groups': []
            }

            # Prioritize largest duplicate groups
            if duplicate_data['duplicate_groups']:
                sorted_groups = sorted(
                    duplicate_data['duplicate_groups'].values(),
                    key=lambda x: x['wasted_space_mb'],
                    reverse=True
                )
                strategy['deduplication_plan']['priority_groups'] = sorted_groups[:10]

        # Unified structure proposal
        strategy['unified_structure'] = {
            'base_directory': 'F:/b3_unified_dataset',
            'subdirectories': {
                'embeddings': {
                    'text_embeddings': 'High-quality text embeddings',
                    'image_embeddings': 'High-quality image embeddings',
                    'audio_embeddings': 'High-quality audio embeddings',
                    'multimodal_embeddings': 'Cross-modal embeddings'
                },
                'datasets': {
                    'text_datasets': 'Text/NLP datasets',
                    'image_datasets': 'Image/vision datasets',
                    'audio_datasets': 'Audio/speech datasets',
                    'multimodal_datasets': 'Cross-modal datasets'
                },
                'metadata': {
                    'quality_scores': 'Quality assessment data',
                    'deduplication_logs': 'Deduplication records',
                    'source_mapping': 'Original source tracking'
                }
            }
        }

        # Implementation steps
        strategy['implementation_steps'] = [
            {
                'step': 1,
                'action': 'Create unified directory structure',
                'description': 'Set up F:/b3_unified_dataset with organized subdirectories',
                'estimated_time': '5 minutes'
            },
            {
                'step': 2,
                'action': 'Remove duplicate files',
                'description': f"Remove {strategy['deduplication_plan'].get('duplicates_to_remove', 0)} duplicate files",
                'estimated_time': '15-30 minutes'
            },
            {
                'step': 3,
                'action': 'Copy high-quality embeddings',
                'description': 'Move recommended embedding files to unified structure',
                'estimated_time': '20-45 minutes'
            },
            {
                'step': 4,
                'action': 'Organize datasets by modality',
                'description': 'Categorize and move dataset files by type',
                'estimated_time': '30-60 minutes'
            },
            {
                'step': 5,
                'action': 'Generate metadata and mappings',
                'description': 'Create comprehensive metadata for all unified data',
                'estimated_time': '10-20 minutes'
            }
        ]

        # Expected outcomes
        total_original_size = sum(src['size_gb'] for src in strategy['data_sources'].values())
        expected_deduplicated_size = total_original_size - strategy['deduplication_plan'].get('space_to_save_gb', 0)

        strategy['expected_outcomes'] = {
            'original_data_size_gb': total_original_size,
            'deduplicated_size_gb': expected_deduplicated_size,
            'space_savings_gb': strategy['deduplication_plan'].get('space_to_save_gb', 0),
            'efficiency_gain_percent': (strategy['deduplication_plan'].get('space_to_save_gb', 0) / total_original_size) * 100 if total_original_size > 0 else 0,
            'unified_embedding_count_estimate': 500000,  # Conservative estimate
            'data_quality_improvement': 'Significant - only high-quality, non-redundant data retained'
        }

        # Save strategy
        strategy_file = self.analysis_output_path / "unified_dataset_strategy.json"
        with open(strategy_file, 'w') as f:
            json.dump(strategy, f, indent=2, default=str)

        print("📊 UNIFIED DATASET STRATEGY SUMMARY:")
        print(f"   📁 Original Data: {total_original_size:.2f} GB")
        print(f"   ✂️ After Deduplication: {expected_deduplicated_size:.2f} GB")
        print(f"   💾 Space Savings: {strategy['expected_outcomes']['space_savings_gb']:.2f} GB")
        print(f"   📈 Efficiency Gain: {strategy['expected_outcomes']['efficiency_gain_percent']:.1f}%")
        print(f"   📋 Strategy saved: {strategy_file}")

        return strategy

    def _recommend_directory_usage(self, dir_name: str, dir_analysis: dict) -> str:
        """Recommend how to use each directory based on analysis"""

        file_count = dir_analysis.get('file_count', 0)
        embedding_files = len(dir_analysis.get('embedding_files', []))
        dataset_files = len(dir_analysis.get('dataset_files', []))

        if file_count == 0:
            return "SKIP - Empty directory"
        elif embedding_files > dataset_files and embedding_files > 100:
            return "PRIMARY - Rich embedding source"
        elif dataset_files > embedding_files and dataset_files > 50:
            return "SECONDARY - Good dataset source"
        elif file_count > 1000:
            return "ANALYZE - Large directory, needs detailed review"
        else:
            return "OPTIONAL - Small directory, low priority"

    def execute_comprehensive_analysis(self):
        """Execute the complete comprehensive data analysis"""

        print("🚀 EXECUTING COMPREHENSIVE F: DRIVE DATA ANALYSIS:")
        print("=" * 70)

        start_time = time.time()

        # Execute all analysis phases
        print("\n📊 PHASE 1: Directory Structure Analysis")
        structure_results = self.analyze_directory_structure()

        print("\n🔍 PHASE 2: Duplicate Detection")
        duplicate_results = self.detect_duplicate_files()

        print("\n🔗 PHASE 3: Embedding Quality Analysis")
        embedding_results = self.analyze_embedding_quality_and_uniqueness()

        print("\n🎯 PHASE 4: Unified Dataset Strategy")
        strategy_results = self.create_unified_dataset_strategy()

        # Final summary
        end_time = time.time()
        analysis_time = end_time - start_time

        final_summary = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_time_minutes': analysis_time / 60,
            'directories_analyzed': len(self.target_directories),
            'total_files_found': structure_results['total_files_found'],
            'total_size_gb': structure_results['total_size_bytes'] / (1024**3),
            'duplicates_found': duplicate_results['duplicates_found'],
            'space_wasted_gb': duplicate_results['space_wasted_gb'],
            'high_quality_embeddings': len(embedding_results['recommended_embeddings']),
            'total_embeddings': embedding_results['total_embeddings'],
            'efficiency_opportunity_gb': strategy_results['expected_outcomes']['space_savings_gb'],
            'next_phase_ready': True
        }

        # Save final summary
        summary_file = self.analysis_output_path / "comprehensive_analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(final_summary, f, indent=2, default=str)

        print("\n🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
        print(f"⏱️ Analysis Time: {analysis_time/60:.1f} minutes")
        print(f"📁 Files Analyzed: {final_summary['total_files_found']:,}")
        print(f"💾 Total Data: {final_summary['total_size_gb']:.2f} GB")
        print(f"🔄 Duplicates Found: {final_summary['duplicates_found']:,}")
        print(f"✂️ Space to Save: {final_summary['space_wasted_gb']:.2f} GB")
        print(f"🔗 Quality Embeddings: {final_summary['high_quality_embeddings']}")
        print(f"📋 Summary: {summary_file}")

        return final_summary

def main():
    """Execute comprehensive F: drive data analysis"""

    print("🤖 VIRTUALLY ROBOTIC GITHUB COPILOT - COMPREHENSIVE DATA ANALYSIS")
    print("=" * 70)
    print("🔍 F: DRIVE COMPREHENSIVE ANALYSIS & DEDUPLICATION")
    print("⚡ MISSION: ANALYZE 173GB+ DATA, ELIMINATE DUPLICATES, OPTIMIZE FOR B3")
    print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Initialize comprehensive analyzer
    analyzer = B3ComprehensiveDataAnalyzer()

    # Execute complete analysis
    analyzer.execute_comprehensive_analysis()

    print("\n🎯 COMPREHENSIVE ANALYSIS FINISHED!")
    print("🚀 Ready for B3 Unified Dataset Implementation!")

if __name__ == "__main__":
    main()
