"""
Path C Checkpoint Progression Tester
Test all 12 checkpoints + baseline to track quality evolution
Created: October 6, 2025
"""

import torch
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.training.b3_constitutional_trainer import ImpressionCoreB3Hope
from src.training.automated_conversation_tester import (
    AutomatedConversationTester,
    create_enhanced_test_queries
)


class CheckpointProgressionTester:
    """Test all Path C checkpoints to track quality progression"""

    def __init__(self):
        self.checkpoint_dir = Path("F:/models/checkpoints/b3/embedding_integration")
        self.baseline_path = Path("F:/models/checkpoints/b3/b3_massive_final.pth")
        self.results_file = Path("docs/analysis/checkpoint_progression_results.md")

        # Define all checkpoints in chronological order
        self.checkpoints = [
            # Baseline (for comparison)
            {
                "name": "Baseline (Pre-Training)",
                "path": self.baseline_path,
                "phase": "baseline",
                "epoch": 0
            },
            # Phase 1: Alignment
            {
                "name": "Phase 1 - Epoch 5",
                "path": self.checkpoint_dir / "b3_embedding_integration_alignment_epoch5.pth",
                "phase": "alignment",
                "epoch": 5
            },
            {
                "name": "Phase 1 - Epoch 10 (Complete)",
                "path": self.checkpoint_dir / "b3_embedding_integration_alignment_epoch10.pth",
                "phase": "alignment",
                "epoch": 10
            },
            # Phase 2: Generation
            {
                "name": "Phase 2 - Epoch 5",
                "path": self.checkpoint_dir / "b3_embedding_integration_generation_epoch5.pth",
                "phase": "generation",
                "epoch": 5
            },
            {
                "name": "Phase 2 - Epoch 10",
                "path": self.checkpoint_dir / "b3_embedding_integration_generation_epoch10.pth",
                "phase": "generation",
                "epoch": 10
            },
            {
                "name": "Phase 2 - Epoch 15",
                "path": self.checkpoint_dir / "b3_embedding_integration_generation_epoch15.pth",
                "phase": "generation",
                "epoch": 15
            },
            {
                "name": "Phase 2 - Epoch 20 (Complete)",
                "path": self.checkpoint_dir / "b3_embedding_integration_generation_epoch20.pth",
                "phase": "generation",
                "epoch": 20
            },
            # Phase 3: Multi-task
            {
                "name": "Phase 3 - Epoch 5",
                "path": self.checkpoint_dir / "b3_embedding_integration_multitask_epoch5.pth",
                "phase": "multitask",
                "epoch": 5
            },
            {
                "name": "Phase 3 - Epoch 10",
                "path": self.checkpoint_dir / "b3_embedding_integration_multitask_epoch10.pth",
                "phase": "multitask",
                "epoch": 10
            },
            {
                "name": "Phase 3 - Epoch 15 (Complete)",
                "path": self.checkpoint_dir / "b3_embedding_integration_multitask_epoch15.pth",
                "phase": "multitask",
                "epoch": 15
            },
            # Phase 4: Fine-tuning
            {
                "name": "Phase 4 - Epoch 5",
                "path": self.checkpoint_dir / "b3_embedding_integration_finetuning_epoch5.pth",
                "phase": "finetuning",
                "epoch": 5
            },
            {
                "name": "Phase 4 - Epoch 10 (Complete)",
                "path": self.checkpoint_dir / "b3_embedding_integration_finetuning_epoch10.pth",
                "phase": "finetuning",
                "epoch": 10
            },
            # Final Model
            {
                "name": "FINAL MODEL (All Phases Complete)",
                "path": Path("F:/models/checkpoints/b3/b3_embedding_integrated_final.pth"),
                "phase": "final",
                "epoch": 55
            }
        ]

    def test_checkpoint(self, checkpoint_info: dict, test_queries: list) -> dict:
        """Test a single checkpoint"""
        print(f"\n{'='*80}")
        print(f"Testing: {checkpoint_info['name']}")
        print(f"Path: {checkpoint_info['path']}")
        print(f"{'='*80}\n")

        if not checkpoint_info['path'].exists():
            print(f"❌ Checkpoint not found: {checkpoint_info['path']}")
            return {
                "status": "not_found",
                "coherence_avg": 0.0,
                "generic_rate": 1.0,
                "error": "Checkpoint file not found"
            }

        try:
            # Initialize tester
            tester = AutomatedConversationTester(
                checkpoint_path=str(checkpoint_info['path']),
                device='cuda'
            )

            # Run tests
            results = tester.run_comprehensive_test(test_queries)

            # Extract key metrics
            coherence_scores = [r['coherence'] for r in results if 'coherence' in r]
            generic_rates = [r['generic_rate'] for r in results if 'generic_rate' in r]

            summary = {
                "status": "success",
                "coherence_avg": sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0,
                "coherence_min": min(coherence_scores) if coherence_scores else 0.0,
                "coherence_max": max(coherence_scores) if coherence_scores else 0.0,
                "generic_rate": sum(generic_rates) / len(generic_rates) if generic_rates else 0.0,
                "num_tests": len(results),
                "detailed_results": results
            }

            print(f"\n✅ Testing Complete!")
            print(f"   Average Coherence: {summary['coherence_avg']:.2f}/10.0")
            print(f"   Generic Rate: {summary['generic_rate']:.2%}")
            print(f"   Tests Run: {summary['num_tests']}")

            return summary

        except Exception as e:
            print(f"\n❌ Error testing checkpoint: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "coherence_avg": 0.0,
                "generic_rate": 1.0,
                "error": str(e)
            }

    def run_full_progression_test(self, priority_only: bool = False):
        """Test all checkpoints (or priority ones only)"""
        print("\n" + "="*80)
        print("PATH C CHECKPOINT PROGRESSION TESTING")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'Priority Checkpoints Only' if priority_only else 'All Checkpoints'}")
        print("="*80 + "\n")

        # Create test queries
        test_queries = create_enhanced_test_queries()
        print(f"📝 Created {len(test_queries)} test queries\n")

        # Priority checkpoints (test these first)
        priority_indices = [0, 12, 2, 6]  # Baseline, Final, Phase1-End, Phase2-End

        if priority_only:
            checkpoints_to_test = [self.checkpoints[i] for i in priority_indices]
            print("🎯 Testing Priority Checkpoints (4 total):\n")
        else:
            checkpoints_to_test = self.checkpoints
            print(f"🎯 Testing All Checkpoints ({len(checkpoints_to_test)} total):\n")

        # Test each checkpoint
        all_results = []
        for idx, checkpoint in enumerate(checkpoints_to_test, 1):
            print(f"\n[{idx}/{len(checkpoints_to_test)}] {checkpoint['name']}")

            result = self.test_checkpoint(checkpoint, test_queries)
            all_results.append({
                "checkpoint": checkpoint,
                "results": result
            })

            # Brief pause between tests
            if idx < len(checkpoints_to_test):
                print("\n⏸️  Pausing 3 seconds before next test...")
                import time
                time.sleep(3)

        # Generate report
        self.generate_progression_report(all_results)

        print("\n" + "="*80)
        print("✅ CHECKPOINT PROGRESSION TESTING COMPLETE!")
        print(f"Results saved to: {self.results_file}")
        print("="*80 + "\n")

        return all_results

    def generate_progression_report(self, all_results: list):
        """Generate comprehensive markdown report"""
        report_lines = [
            "**Created:** October 6, 2025",
            "**Updated:** October 6, 2025",
            "**Author:** Kirk LaSalle; GitHub Copilot",
            "**Tags:** #ids #standardized_header #docs\\analysis\\checkpoint_progression_results.md #testing #path_c",
            "**Category:** Analysis",
            "**Status:** Complete",
            "",
            "# Path C Checkpoint Progression Test Results",
            "",
            f"**Test Date:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",
            f"**Checkpoints Tested:** {len(all_results)}",
            f"**Test Queries:** {all_results[0]['results'].get('num_tests', 0) if all_results else 0}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "This report documents the quality progression across all Path C training checkpoints,",
            "from baseline (pre-training) through final model (55 epochs across 4 phases).",
            "",
            "---",
            "",
            "## Checkpoint Progression Table",
            "",
            "| Checkpoint | Phase | Epoch | Coherence | Generic Rate | Status |",
            "|------------|-------|-------|-----------|--------------|--------|"
        ]

        # Add results table
        for result in all_results:
            checkpoint = result['checkpoint']
            metrics = result['results']

            if metrics['status'] == 'success':
                coherence = f"{metrics['coherence_avg']:.2f}/10.0"
                generic = f"{metrics['generic_rate']:.1%}"
                status = "✅"
            elif metrics['status'] == 'not_found':
                coherence = "N/A"
                generic = "N/A"
                status = "❌ Not Found"
            else:
                coherence = "ERROR"
                generic = "ERROR"
                status = "❌ Error"

            report_lines.append(
                f"| {checkpoint['name']} | {checkpoint['phase']} | {checkpoint['epoch']} | "
                f"{coherence} | {generic} | {status} |"
            )

        # Add detailed results section
        report_lines.extend([
            "",
            "---",
            "",
            "## Detailed Results by Checkpoint",
            ""
        ])

        for result in all_results:
            checkpoint = result['checkpoint']
            metrics = result['results']

            report_lines.extend([
                f"### {checkpoint['name']}",
                "",
                f"**Phase:** {checkpoint['phase']}",
                f"**Total Epoch:** {checkpoint['epoch']}",
                f"**Checkpoint Path:** `{checkpoint['path']}`",
                ""
            ])

            if metrics['status'] == 'success':
                report_lines.extend([
                    "**Quality Metrics:**",
                    "",
                    f"- Average Coherence: {metrics['coherence_avg']:.2f}/10.0",
                    f"- Coherence Range: {metrics['coherence_min']:.2f} - {metrics['coherence_max']:.2f}",
                    f"- Generic Response Rate: {metrics['generic_rate']:.2%}",
                    f"- Tests Completed: {metrics['num_tests']}",
                    ""
                ])

                # Add sample responses if available
                if 'detailed_results' in metrics and metrics['detailed_results']:
                    report_lines.extend([
                        "**Sample Responses:**",
                        ""
                    ])
                    for idx, test in enumerate(metrics['detailed_results'][:3], 1):  # First 3 only
                        report_lines.extend([
                            f"{idx}. **Query:** {test.get('query', 'N/A')}",
                            f"   **Response:** {test.get('response', 'N/A')[:100]}...",
                            f"   **Coherence:** {test.get('coherence', 0):.2f}/10.0",
                            ""
                        ])
            else:
                report_lines.extend([
                    f"**Status:** {metrics['status']}",
                    f"**Error:** {metrics.get('error', 'Unknown error')}",
                    ""
                ])

            report_lines.append("---")
            report_lines.append("")

        # Add analysis section
        report_lines.extend([
            "## Analysis & Conclusions",
            "",
            "### Quality Progression Pattern",
            "",
            "*Analysis will be added after reviewing results*",
            "",
            "### Key Findings",
            "",
            "1. **Baseline vs Final:** [To be filled]",
            "2. **Phase 1 Impact:** [To be filled]",
            "3. **Phase 2-4 Impact:** [To be filled]",
            "4. **Optimal Checkpoint:** [To be filled]",
            "",
            "### Recommendations",
            "",
            "Based on these results, the recommended next steps are:",
            "",
            "*Recommendations will be added after analysis*",
            "",
            "---",
            "",
            f"*Report generated: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}*"
        ])

        # Write report
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        self.results_file.write_text("\n".join(report_lines), encoding='utf-8')
        print(f"\n📄 Report generated: {self.results_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Path C checkpoint progression")
    parser.add_argument(
        '--priority-only',
        action='store_true',
        help='Test only priority checkpoints (baseline, final, phase1-end, phase2-end)'
    )
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='Test a specific checkpoint by name (e.g., "final", "phase1_epoch10")'
    )

    args = parser.parse_args()

    tester = CheckpointProgressionTester()

    if args.checkpoint:
        # Test single checkpoint
        checkpoint_map = {
            'baseline': 0,
            'final': 12,
            'phase1_epoch5': 1,
            'phase1_epoch10': 2,
            'phase2_epoch5': 3,
            'phase2_epoch10': 4,
            'phase2_epoch15': 5,
            'phase2_epoch20': 6,
            'phase3_epoch5': 7,
            'phase3_epoch10': 8,
            'phase3_epoch15': 9,
            'phase4_epoch5': 10,
            'phase4_epoch10': 11
        }

        if args.checkpoint.lower() in checkpoint_map:
            idx = checkpoint_map[args.checkpoint.lower()]
            checkpoint = tester.checkpoints[idx]
            test_queries = create_enhanced_test_queries()
            result = tester.test_checkpoint(checkpoint, test_queries)
            print("\n" + "="*80)
            print(f"Single Checkpoint Test: {checkpoint['name']}")
            print(f"Average Coherence: {result.get('coherence_avg', 0):.2f}/10.0")
            print(f"Generic Rate: {result.get('generic_rate', 0):.2%}")
            print("="*80)
        else:
            print(f"❌ Unknown checkpoint: {args.checkpoint}")
            print(f"Available: {', '.join(checkpoint_map.keys())}")
            return 1
    else:
        # Test all or priority
        tester.run_full_progression_test(priority_only=args.priority_only)

    return 0


if __name__ == "__main__":
    sys.exit(main())
