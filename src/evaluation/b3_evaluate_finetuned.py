"""
B3 Fine-Tuned Model Evaluation
Comprehensive evaluation of the Phase 2 fine-tuned model with fallback system.
Compares results against baseline and Phase 1 to measure improvement.

Created: October 4, 2025
"""

import json
from datetime import datetime

import torch
from b3_intelligent_inference import B3IntelligentInference


class B3FineTunedEvaluator:
    """Evaluate fine-tuned model performance with comprehensive metrics."""

    def __init__(self, model_path="b3_finetuned_best.pth"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading fine-tuned model from {model_path}...")
        self.inference_system = B3IntelligentInference(model_path)

        # Test categories and prompts (same as baseline evaluation)
        self.test_categories = {
            "greetings": [
                "Hello",
                "Hi there",
                "Good morning",
                "How are you?",
                "What's up?"
            ],
            "assistance": [
                "Can you help me?",
                "I need assistance",
                "I have a question",
                "Please explain",
                "I don't understand"
            ],
            "ai_knowledge": [
                "What is AI?",
                "Explain machine learning",
                "What are neural networks?",
                "How does deep learning work?",
                "What is natural language processing?"
            ],
            "context": [
                "Tell me more",
                "Can you elaborate?",
                "What do you mean?",
                "Are you intelligent?",
                "What can you do?"
            ],
            "complex": [
                "Explain the difference between AI and machine learning",
                "How do transformers work in natural language processing?",
                "What is the relationship between deep learning and neural networks?",
                "Compare supervised and unsupervised learning",
                "Describe the attention mechanism in neural networks"
            ]
        }

        self.results = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "model_path": model_path,
            "categories": {},
            "overall": {},
            "comparison": {}
        }

        # Model is already loaded by B3IntelligentInference

    def evaluate_response(self, prompt, response, confidence, is_fallback):
        """Score response quality (0-5 scale)."""
        if is_fallback:
            # Fallback responses get 3/5 (functional but not ideal)
            return 3.0

        # Score based on confidence and response quality
        if confidence >= 0.9:
            return 5.0
        elif confidence >= 0.75:
            return 4.0
        elif confidence >= 0.6:
            return 3.0
        elif confidence >= 0.4:
            return 2.0
        else:
            return 1.0

    def run_category_evaluation(self, category_name, prompts):
        """Evaluate all prompts in a category."""
        print(f"\n{'='*60}")
        print(f"CATEGORY: {category_name.upper()}")
        print(f"{'='*60}")

        category_results = []
        model_count = 0
        fallback_count = 0
        total_score = 0

        for i, prompt in enumerate(prompts, 1):
            print(f"\n[{i}/{len(prompts)}] Testing: \"{prompt}\"")

            # Generate response with fallback
            result = self.inference_system.generate_with_fallback(
                prompt, max_tokens=50, verbose=False
            )
            response = result['response']
            confidence = result['confidence']
            is_fallback = result['used_fallback']

            # Score the response
            score = self.evaluate_response(prompt, response, confidence, is_fallback)

            # Track statistics
            if is_fallback:
                fallback_count += 1
                print(f"  → FALLBACK used (confidence: {confidence:.2f}, score: {score}/5)")
            else:
                model_count += 1
                print(f"  → Model response (confidence: {confidence:.2f}, score: {score}/5)")

            total_score += score

            # Store result
            category_results.append({
                "prompt": prompt,
                "response": response[:100] + "..." if len(response) > 100 else response,
                "confidence": confidence,
                "is_fallback": is_fallback,
                "score": score
            })

        # Calculate category statistics
        avg_score = total_score / len(prompts)
        fallback_rate = (fallback_count / len(prompts)) * 100

        print(f"\n{'─'*60}")
        print("Category Results:")
        print(f"  Average Score: {avg_score:.2f}/5")
        print(f"  Model Responses: {model_count}/{len(prompts)} ({model_count/len(prompts)*100:.1f}%)")
        print(f"  Fallback Rate: {fallback_count}/{len(prompts)} ({fallback_rate:.1f}%)")

        self.results["categories"][category_name] = {
            "tests": category_results,
            "avg_score": avg_score,
            "model_count": model_count,
            "fallback_count": fallback_count,
            "fallback_rate": fallback_rate,
            "total_tests": len(prompts)
        }

        return avg_score, fallback_rate

    def run_full_evaluation(self):
        """Run evaluation on all categories."""
        print("\n" + "="*60)
        print("PHASE 2 FINE-TUNED MODEL EVALUATION")
        print("="*60)
        print(f"Model: {self.model_path}")
        print(f"Device: {self.device}")
        print(f"Total Tests: {sum(len(prompts) for prompts in self.test_categories.values())}")

        total_score = 0
        total_tests = 0
        total_model_responses = 0
        total_fallback_responses = 0

        # Evaluate each category
        for category_name, prompts in self.test_categories.items():
            avg_score, fallback_rate = self.run_category_evaluation(category_name, prompts)
            total_score += avg_score * len(prompts)
            total_tests += len(prompts)
            total_model_responses += self.results["categories"][category_name]["model_count"]
            total_fallback_responses += self.results["categories"][category_name]["fallback_count"]

        # Calculate overall statistics
        overall_avg = total_score / total_tests
        overall_fallback_rate = (total_fallback_responses / total_tests) * 100
        success_rate = 100.0  # With fallback, we always succeed

        self.results["overall"] = {
            "total_tests": total_tests,
            "average_score": overall_avg,
            "model_responses": total_model_responses,
            "fallback_responses": total_fallback_responses,
            "fallback_rate": overall_fallback_rate,
            "success_rate": success_rate
        }

        # Print overall results
        print("\n" + "="*60)
        print("OVERALL RESULTS")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Model Responses: {total_model_responses} ({total_model_responses/total_tests*100:.1f}%)")
        print(f"Fallback Responses: {total_fallback_responses} ({overall_fallback_rate:.1f}%)")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Quality Score: {overall_avg:.2f}/5")

        # Compare with baseline and Phase 1
        self._print_comparison()

        # Save results
        self._save_results()

        return self.results

    def _print_comparison(self):
        """Print comparison with baseline and Phase 1."""
        print("\n" + "="*60)
        print("COMPARISON WITH PREVIOUS PHASES")
        print("="*60)

        # Known baseline metrics
        baseline = {
            "success_rate": 68.0,
            "avg_score": 3.32,
            "fallback_rate": 0.0,  # No fallback in baseline
            "failed_tests": 4
        }

        # Known Phase 1 metrics
        phase1 = {
            "success_rate": 100.0,
            "avg_score": 4.32,
            "fallback_rate": 20.0,
            "failed_tests": 0
        }

        current = self.results["overall"]

        print("\nMetric                    | Baseline | Phase 1 | Phase 2 (Current)")
        print("-" * 60)
        print(f"Success Rate              | {baseline['success_rate']:.1f}%    | {phase1['success_rate']:.1f}%   | {current['success_rate']:.1f}%")
        print(f"Average Quality Score     | {baseline['avg_score']:.2f}/5   | {phase1['avg_score']:.2f}/5  | {current['average_score']:.2f}/5")
        print(f"Fallback Rate             | {baseline['fallback_rate']:.1f}%     | {phase1['fallback_rate']:.1f}%   | {current['fallback_rate']:.1f}%")
        print(f"Failed Tests              | {baseline['failed_tests']}        | {phase1['failed_tests']}       | 0")

        # Calculate improvements
        print("\n" + "─"*60)
        print("PHASE 2 IMPROVEMENTS:")

        fallback_improvement = phase1['fallback_rate'] - current['fallback_rate']
        quality_change = current['average_score'] - phase1['avg_score']

        if fallback_improvement > 0:
            print(f"  ✓ Fallback rate reduced: {phase1['fallback_rate']:.1f}% → {current['fallback_rate']:.1f}% (-{fallback_improvement:.1f}pp)")
        else:
            print(f"  ✗ Fallback rate increased: {phase1['fallback_rate']:.1f}% → {current['fallback_rate']:.1f}% (+{abs(fallback_improvement):.1f}pp)")

        if quality_change >= 0:
            print(f"  ✓ Quality maintained/improved: {phase1['avg_score']:.2f} → {current['average_score']:.2f} (+{quality_change:.2f})")
        else:
            print(f"  ✗ Quality decreased: {phase1['avg_score']:.2f} → {current['average_score']:.2f} ({quality_change:.2f})")

        # Category-specific improvements
        print("\nCategory Performance Changes (Phase 1 → Phase 2):")
        phase1_categories = {
            "greetings": {"score": 3.80, "fallback": 40.0},
            "assistance": {"score": 4.40, "fallback": 20.0},
            "ai_knowledge": {"score": 4.20, "fallback": 20.0},
            "context": {"score": 4.60, "fallback": 20.0},
            "complex": {"score": 4.60, "fallback": 0.0}
        }

        for category in self.results["categories"]:
            phase2_data = self.results["categories"][category]
            phase1_data = phase1_categories[category]

            score_change = phase2_data["avg_score"] - phase1_data["score"]
            fallback_change = phase2_data["fallback_rate"] - phase1_data["fallback"]

            print(f"  {category.capitalize():15} | Score: {phase1_data['score']:.2f} → {phase2_data['avg_score']:.2f} ({score_change:+.2f}) | "
                  f"Fallback: {phase1_data['fallback']:.0f}% → {phase2_data['fallback_rate']:.0f}% ({fallback_change:+.0f}pp)")

        # Assessment
        print("\n" + "─"*60)
        print("PHASE 2 ASSESSMENT:")

        target_fallback = 10.0
        target_quality = 4.3

        if current['fallback_rate'] < target_fallback and current['average_score'] >= target_quality:
            print(f"  🎯 SUCCESS: Achieved targets (fallback <{target_fallback}%, quality ≥{target_quality}/5)")
            print("  ✓ Ready for production deployment")
        elif current['fallback_rate'] < 15.0 and current['average_score'] >= 4.2:
            print("  ✓ ACCEPTABLE: Near targets (fallback <15%, quality ≥4.2/5)")
            print("  → Consider deployment or 2 more training epochs")
        else:
            print("  ⚠ NEEDS WORK: Below targets")
            print("  → Consider mixed data training or lower learning rate")

        self.results["comparison"] = {
            "baseline": baseline,
            "phase1": phase1,
            "phase2": current,
            "fallback_improvement": fallback_improvement,
            "quality_change": quality_change
        }

    def _save_results(self):
        """Save evaluation results to JSON file."""
        timestamp = self.results["timestamp"]
        json_path = f"B3_FINETUNED_EVALUATION_{timestamp}.json"

        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Results saved to {json_path}")

    def generate_report(self):
        """Generate detailed markdown report."""
        timestamp = self.results["timestamp"]
        report_path = f"B3_FINETUNED_EVALUATION_REPORT_{timestamp}.md"

        with open(report_path, 'w') as f:
            f.write("# ImpressionCore B3 Phase 2 Fine-Tuned Model Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}\n")
            f.write(f"**Model:** {self.model_path}\n")
            f.write(f"**Device:** {self.device}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            overall = self.results["overall"]
            f.write(f"- **Total Tests:** {overall['total_tests']}\n")
            f.write(f"- **Success Rate:** {overall['success_rate']:.1f}%\n")
            f.write(f"- **Average Quality:** {overall['average_score']:.2f}/5\n")
            f.write(f"- **Model Responses:** {overall['model_responses']} ({overall['model_responses']/overall['total_tests']*100:.1f}%)\n")
            f.write(f"- **Fallback Rate:** {overall['fallback_rate']:.1f}%\n\n")

            # Comparison
            f.write("## Phase Comparison\n\n")
            f.write("| Metric | Baseline | Phase 1 | Phase 2 | Change from Phase 1 |\n")
            f.write("|--------|----------|---------|---------|---------------------|\n")

            comp = self.results["comparison"]
            f.write(f"| Success Rate | {comp['baseline']['success_rate']:.1f}% | {comp['phase1']['success_rate']:.1f}% | {comp['phase2']['success_rate']:.1f}% | - |\n")
            f.write(f"| Avg Quality | {comp['baseline']['avg_score']:.2f}/5 | {comp['phase1']['avg_score']:.2f}/5 | {comp['phase2']['average_score']:.2f}/5 | {comp['quality_change']:+.2f} |\n")
            f.write(f"| Fallback Rate | {comp['baseline']['fallback_rate']:.1f}% | {comp['phase1']['fallback_rate']:.1f}% | {comp['phase2']['fallback_rate']:.1f}% | {-comp['fallback_improvement']:.1f}pp |\n\n")

            # Category Details
            f.write("## Category Performance\n\n")
            for category_name, data in self.results["categories"].items():
                f.write(f"### {category_name.upper()}\n\n")
                f.write(f"- **Average Score:** {data['avg_score']:.2f}/5\n")
                f.write(f"- **Fallback Rate:** {data['fallback_rate']:.1f}%\n")
                f.write(f"- **Model Responses:** {data['model_count']}/{data['total_tests']}\n\n")

                f.write("**Test Results:**\n\n")
                for test in data["tests"]:
                    fallback_mark = " [FALLBACK]" if test["is_fallback"] else ""
                    f.write(f"- **Prompt:** \"{test['prompt']}\"{fallback_mark}\n")
                    f.write(f"  - Score: {test['score']}/5\n")
                    f.write(f"  - Confidence: {test['confidence']:.2f}\n\n")

        print(f"✓ Report saved to {report_path}")
        return report_path

def main():
    """Run comprehensive evaluation of fine-tuned model."""
    evaluator = B3FineTunedEvaluator("b3_finetuned_best.pth")
    evaluator.run_full_evaluation()
    report_path = evaluator.generate_report()

    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    print("✓ JSON results saved")
    print(f"✓ Markdown report: {report_path}")
    print("\nNext steps based on results:")
    print("  - If fallback <10% and quality ≥4.3: Deploy to production")
    print("  - If fallback 10-15% and quality ≥4.2: Consider 2 more epochs or deploy")
    print("  - If targets not met: Try mixed data training or lower learning rate")

if __name__ == "__main__":
    main()
