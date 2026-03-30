#!/usr/bin/env python3
"""
Efficient Checkpoint Audit & Cleanup System
Preserves best B1 and B3 models, removes all others
Prepares for optimized B3 architecture transition

Created: October 1, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import os
import time
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import torch
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class EfficientCheckpointAuditor:
    def __init__(self):
        self.checkpoints_root = Path("F:/models/checkpoints")
        self.archive_dir = Path("F:/models/archives/pre_cleanup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.preserved_dir = Path("F:/models/checkpoints/preserved_best")

        # Results storage
        self.test_results: List[Dict] = []
        self.best_b1: Optional[Dict] = None
        self.best_b3: Optional[Dict] = None

        # Known tested checkpoints to skip
        self.tested_checkpoints = {
            'recovery_step_4000.pth': {'architecture': 'B3', 'quality_score': 37.5, 'status': 'BASELINE'},
            'b2_fixed_epoch_2.pth': {'architecture': 'B2', 'quality_score': 15.0, 'status': 'INCOMPATIBLE'},
            'b1_working_checkpoint_epoch_015_quality_0.00_1.pth': {'architecture': 'B1', 'quality_score': 25.0, 'status': 'CORRUPTED'},
            'impressioncore_b1_flagship_1.pth': {'architecture': 'B1', 'quality_score': 20.0, 'status': 'LOAD_ERROR'},
            'distillation_checkpoint_epoch_75_quality_0.00_1.pth': {'architecture': 'B1', 'quality_score': 22.0, 'status': 'ARCHITECTURE_MISMATCH'},
            'unified_final_step_2000.pth': {'architecture': 'B3', 'quality_score': 5.0, 'status': 'SEVERELY_CORRUPTED'},
            'b3_ollama_enhanced_final_step_1500.pth': {'architecture': 'B3', 'quality_score': 12.0, 'status': 'DEGRADED'},
            'best_val_loss_step_400.pth': {'architecture': 'B3', 'quality_score': 8.0, 'status': 'CORRUPTED'}
        }

    def discover_untested_checkpoints(self) -> List[Path]:
        """Efficiently discover untested checkpoint files"""
        logger.info("🔍 Discovering untested checkpoints...")

        all_checkpoints = []
        for pattern in ["*.pth", "*.pt", "*.ckpt"]:
            all_checkpoints.extend(self.checkpoints_root.rglob(pattern))

        # Filter out tested, artifacts, and temporary files
        untested = []
        for cp in all_checkpoints:
            # Skip known tested checkpoints
            if cp.name in self.tested_checkpoints:
                continue

            # Skip artifacts and temporary files
            path_str = str(cp).lower()
            if any(skip in path_str for skip in ['artifacts', 'tmp', 'temp', '__pycache__']):
                continue

            # Skip very small files (likely corrupted)
            if cp.stat().st_size < 1024 * 1024:  # Less than 1MB
                continue

            untested.append(cp)

        logger.info(f"Found {len(untested)} untested checkpoints to evaluate")
        return sorted(untested, key=lambda p: p.stat().st_mtime, reverse=True)  # Newest first

    def quick_quality_assessment(self, checkpoint_path: Path) -> Dict:
        """Fast quality assessment using lightweight tests"""
        result = {
            'path': checkpoint_path,
            'name': checkpoint_path.name,
            'size_mb': checkpoint_path.stat().st_size / (1024**2),
            'modified': datetime.fromtimestamp(checkpoint_path.stat().st_mtime),
            'architecture': self._detect_architecture(checkpoint_path),
            'loadable': False,
            'quality_score': 0.0,
            'param_count': 0,
            'error': None,
            'has_valid_weights': False
        }

        try:
            # Quick load test
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            # Load with timeout protection
            checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
            result['loadable'] = True

            # Extract basic info
            if isinstance(checkpoint, dict):
                if 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                elif 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                else:
                    state_dict = checkpoint

                # Count parameters
                param_count = 0
                valid_weights = 0

                for key, tensor in state_dict.items():
                    if isinstance(tensor, torch.Tensor):
                        param_count += tensor.numel()
                        # Check for reasonable weight values (not NaN/Inf/extreme values)
                        if torch.isfinite(tensor).all() and tensor.abs().max() < 100:
                            valid_weights += 1

                result['param_count'] = param_count
                result['has_valid_weights'] = valid_weights > len(state_dict) * 0.8  # 80% valid

                # Quick quality heuristic based on architecture and weights
                if result['architecture'] == 'B3' and result['has_valid_weights']:
                    result['quality_score'] = min(35.0, param_count / 20_000_000 * 35)  # Heuristic
                elif result['architecture'] == 'B1' and result['has_valid_weights']:
                    result['quality_score'] = min(30.0, param_count / 15_000_000 * 30)  # Heuristic
                else:
                    result['quality_score'] = 5.0 if result['has_valid_weights'] else 0.0

        except Exception as e:
            result['error'] = str(e)
            logger.warning(f"Failed to assess {checkpoint_path.name}: {e}")

        return result

    def _detect_architecture(self, checkpoint_path: Path) -> str:
        """Detect model architecture from path and naming"""
        name_lower = checkpoint_path.name.lower()
        path_str = str(checkpoint_path).lower()

        # Check path structure and naming patterns
        if 'b3' in name_lower or '/b3/' in path_str:
            return 'B3'
        elif 'b2' in name_lower or '/b2/' in path_str:
            return 'B2'
        elif 'b1' in name_lower or '/b1/' in path_str:
            return 'B1'
        elif 'impressioncore' in name_lower and 'flagship' in name_lower:
            return 'B1'  # Legacy flagship models
        elif 'unified' in name_lower or 'sweet_spot' in name_lower:
            return 'B3'  # Recent unified models
        else:
            return 'Unknown'

    def run_efficient_audit(self) -> Dict:
        """Run the efficient audit process"""
        logger.info("🚀 Starting efficient checkpoint audit...")

        # Add known good checkpoints first
        for name, info in self.tested_checkpoints.items():
            checkpoint_path = None

            # Try to find the actual file
            for cp in self.checkpoints_root.rglob(name):
                checkpoint_path = cp
                break

            if checkpoint_path and checkpoint_path.exists():
                result = {
                    'path': checkpoint_path,
                    'name': name,
                    'architecture': info['architecture'],
                    'quality_score': info['quality_score'],
                    'loadable': info['status'] not in ['LOAD_ERROR', 'CORRUPTED', 'SEVERELY_CORRUPTED'],
                    'status': info['status']
                }
                self.test_results.append(result)

                # Update best trackers
                if info['architecture'] == 'B1' and info['quality_score'] > 0:
                    if self.best_b1 is None or info['quality_score'] > self.best_b1['quality_score']:
                        self.best_b1 = result

                elif info['architecture'] == 'B3' and info['quality_score'] > 0:
                    if self.best_b3 is None or info['quality_score'] > self.best_b3['quality_score']:
                        self.best_b3 = result

        # Discover and test untested checkpoints
        untested_checkpoints = self.discover_untested_checkpoints()

        for i, cp in enumerate(untested_checkpoints):
            logger.info(f"Assessing {i+1}/{len(untested_checkpoints)}: {cp.name}")

            result = self.quick_quality_assessment(cp)
            self.test_results.append(result)

            # Update best trackers for loadable checkpoints
            if result['loadable'] and result['quality_score'] > 0:
                if result['architecture'] == 'B1':
                    if self.best_b1 is None or result['quality_score'] > self.best_b1['quality_score']:
                        self.best_b1 = result

                elif result['architecture'] == 'B3':
                    if self.best_b3 is None or result['quality_score'] > self.best_b3['quality_score']:
                        self.best_b3 = result

        return self._finalize_audit_results()

    def _finalize_audit_results(self) -> Dict:
        """Finalize audit results and prepare for cleanup"""
        logger.info("\n📊 AUDIT RESULTS SUMMARY:")
        logger.info("=" * 50)

        if self.best_b1:
            logger.info(f"🏆 Best B1: {self.best_b1['name']}")
            logger.info(f"   Quality: {self.best_b1['quality_score']:.1f}/100")
            logger.info(f"   Size: {self.best_b1.get('size_mb', 0):.1f}MB")

        if self.best_b3:
            logger.info(f"🏆 Best B3: {self.best_b3['name']}")
            logger.info(f"   Quality: {self.best_b3['quality_score']:.1f}/100")
            logger.info(f"   Size: {self.best_b3.get('size_mb', 0):.1f}MB")

        # Preserve best models
        preserved_count = self._preserve_best_models()

        # Calculate cleanup metrics
        total_checkpoints = len(self.test_results)
        preserve_names = set()
        if self.best_b1:
            preserve_names.add(self.best_b1['name'])
        if self.best_b3:
            preserve_names.add(self.best_b3['name'])

        cleanup_candidates = [r for r in self.test_results if r['name'] not in preserve_names]

        logger.info(f"\n📈 AUDIT STATISTICS:")
        logger.info(f"   Total checkpoints evaluated: {total_checkpoints}")
        logger.info(f"   Models preserved: {preserved_count}")
        logger.info(f"   Cleanup candidates: {len(cleanup_candidates)}")

        return {
            'b1_best': self.best_b1,
            'b3_best': self.best_b3,
            'total_evaluated': total_checkpoints,
            'preserved_count': preserved_count,
            'cleanup_count': len(cleanup_candidates),
            'cleanup_candidates': cleanup_candidates
        }

    def _preserve_best_models(self) -> int:
        """Preserve the best B1 and B3 models"""
        self.preserved_dir.mkdir(parents=True, exist_ok=True)
        preserved_count = 0

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.best_b1 and self.best_b1['path'].exists():
            dest = self.preserved_dir / f"best_b1_{timestamp}_{self.best_b1['name']}"
            try:
                shutil.copy2(self.best_b1['path'], dest)
                logger.info(f"✅ Preserved best B1: {dest.name}")
                preserved_count += 1
            except Exception as e:
                logger.error(f"Failed to preserve B1: {e}")

        if self.best_b3 and self.best_b3['path'].exists():
            dest = self.preserved_dir / f"best_b3_{timestamp}_{self.best_b3['name']}"
            try:
                shutil.copy2(self.best_b3['path'], dest)
                logger.info(f"✅ Preserved best B3: {dest.name}")
                preserved_count += 1
            except Exception as e:
                logger.error(f"Failed to preserve B3: {e}")

        return preserved_count

    def execute_cleanup(self, dry_run: bool = True) -> Dict:
        """Execute cleanup with safety measures"""
        if dry_run:
            logger.info("🔍 DRY RUN - No files will be moved")
        else:
            logger.info("🗑️ EXECUTING CLEANUP - Files will be archived")
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        preserve_names = set()
        if self.best_b1:
            preserve_names.add(self.best_b1['name'])
        if self.best_b3:
            preserve_names.add(self.best_b3['name'])

        # Always preserve recovery baseline
        preserve_names.add('recovery_step_4000.pth')

        cleanup_results = {
            'preserved': [],
            'archived': [],
            'errors': []
        }

        for result in self.test_results:
            if result['name'] in preserve_names:
                cleanup_results['preserved'].append(result['name'])
                logger.info(f"🛡️ PRESERVE: {result['name']}")
            else:
                if dry_run:
                    cleanup_results['archived'].append(result['name'])
                    logger.info(f"🗑️ WOULD ARCHIVE: {result['name']}")
                else:
                    try:
                        if result['path'].exists():
                            archive_path = self.archive_dir / result['name']
                            shutil.move(str(result['path']), str(archive_path))
                            cleanup_results['archived'].append(result['name'])
                            logger.info(f"🗑️ ARCHIVED: {result['name']}")
                    except Exception as e:
                        cleanup_results['errors'].append(f"{result['name']}: {e}")
                        logger.error(f"❌ FAILED to archive {result['name']}: {e}")

        return cleanup_results

def main():
    """Main execution"""
    print("🔍 EFFICIENT CHECKPOINT AUDIT SYSTEM")
    print("=" * 60)

    auditor = EfficientCheckpointAuditor()

    # Run audit
    results = auditor.run_efficient_audit()

    # Display results
    print(f"\n🎯 AUDIT COMPLETE")
    print("=" * 30)

    if results['b1_best']:
        print(f"🏆 Best B1: {results['b1_best']['name']}")
        print(f"   Quality: {results['b1_best']['quality_score']:.1f}/100")

    if results['b3_best']:
        print(f"🏆 Best B3: {results['b3_best']['name']}")
        print(f"   Quality: {results['b3_best']['quality_score']:.1f}/100")

    print(f"\n📊 METRICS:")
    print(f"   Evaluated: {results['total_evaluated']} checkpoints")
    print(f"   Preserved: {results['preserved_count']} models")
    print(f"   Cleanup candidates: {results['cleanup_count']} files")

    # Ask about cleanup
    if results['cleanup_count'] > 0:
        print(f"\n⚠️ CLEANUP OPTIONS:")
        print("1. Dry run (show what would be cleaned)")
        print("2. Execute cleanup (archive non-essential checkpoints)")
        print("3. Skip cleanup")

        choice = input("\nChoose option (1-3): ").strip()

        if choice == '1':
            cleanup_results = auditor.execute_cleanup(dry_run=True)
            print(f"\n📋 DRY RUN RESULTS:")
            print(f"   Would preserve: {len(cleanup_results['preserved'])} files")
            print(f"   Would archive: {len(cleanup_results['archived'])} files")

        elif choice == '2':
            confirm = input("⚠️ Confirm archive operation? (yes/no): ").strip().lower()
            if confirm == 'yes':
                cleanup_results = auditor.execute_cleanup(dry_run=False)
                print(f"\n✅ CLEANUP COMPLETE:")
                print(f"   Preserved: {len(cleanup_results['preserved'])} files")
                print(f"   Archived: {len(cleanup_results['archived'])} files")
                print(f"   Errors: {len(cleanup_results['errors'])} files")
            else:
                print("Cleanup cancelled")
        else:
            print("Cleanup skipped")

    print(f"\n🚀 Ready to proceed with optimized B3 architecture!")
    return results

if __name__ == "__main__":
    main()