#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Comprehensive Evaluation Report Generator
================================================================

Evaluates the b3_massive_best.pth model across multiple dimensions:
- Conversational quality
- Technical knowledge accuracy
- Response coherence and grammar
- Context understanding
- Helpfulness and tone

Created: October 4, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import json
from datetime import datetime

import torch
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope
from transformers import AutoTokenizer


class B3HopeEvaluator:
    """Comprehensive evaluation system for B3-Hope model"""

    def __init__(self, checkpoint_path: str = "b3_massive_best.pth"):
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print("\n" + "="*80)
        print("B3-HOPE COMPREHENSIVE EVALUATION SYSTEM")
        print("="*80)

        # Load model
        print(f"\nLoading model: {checkpoint_path}")
        self.config = B3HopeConfig()
        self.model = ImpressionCoreB3Hope(self.config)

        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()

        self.training_loss = checkpoint.get('train_loss', 'unknown')

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"Model Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        print(f"Training Loss: {self.training_loss}")
        print(f"Device: {self.device}")

        # Evaluation results
        self.results = {
            'metadata': {
                'checkpoint': checkpoint_path,
                'parameters': sum(p.numel() for p in self.model.parameters()),
                'training_loss': str(self.training_loss),
                'device': str(self.device),
                'evaluation_date': datetime.now().strftime("%B %d, %Y %H:%M:%S")
            },
            'categories': {}
        }

    def generate_response(self, prompt: str, max_tokens: int = 50) -> str:
        """Generate response for a prompt"""
        inputs = self.tokenizer(prompt, return_tensors='pt', padding=True)
        input_ids = inputs['input_ids'].to(self.device)
        inputs['attention_mask'].to(self.device)

        generated_ids = input_ids.tolist()[0]

        with torch.no_grad():
            for _ in range(max_tokens):
                # Use sliding window if context too long
                context_ids = generated_ids[-512:] if len(generated_ids) > 512 else generated_ids
                input_tensor = torch.tensor([context_ids], device=self.device)

                outputs = self.model(input_tensor)
                next_token_logits = outputs['logits'][0, -1, :]
                next_token = torch.argmax(next_token_logits).item()

                generated_ids.append(next_token)

                # Stop if EOS token
                if next_token == self.tokenizer.eos_token_id:
                    break

        full_response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        # Extract only the response part (after the prompt)
        response = full_response[len(prompt):].strip()
        return response

    def evaluate_category(self, category_name: str, test_cases: list[dict]) -> dict:
        """Evaluate a category of test cases"""
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category_name}")
        print(f"{'='*80}")

        results = []

        for i, test_case in enumerate(test_cases, 1):
            prompt = test_case['prompt']
            expected_qualities = test_case.get('qualities', [])

            print(f"\n[Test {i}/{len(test_cases)}]")
            print(f"Prompt: \"{prompt}\"")

            response = self.generate_response(prompt)
            print(f"Response: \"{response}\"")

            # Evaluate response quality
            evaluation = self.evaluate_response(response, expected_qualities)
            print(f"Quality Score: {evaluation['score']}/5")
            print(f"Assessment: {evaluation['assessment']}")

            results.append({
                'prompt': prompt,
                'response': response,
                'expected_qualities': expected_qualities,
                'evaluation': evaluation
            })

        # Calculate category statistics
        scores = [r['evaluation']['score'] for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        print(f"\n{category_name} Summary:")
        print(f"  Average Score: {avg_score:.2f}/5")
        print(f"  Total Tests: {len(results)}")

        return {
            'test_cases': results,
            'average_score': avg_score,
            'total_tests': len(results)
        }

    def evaluate_response(self, response: str, expected_qualities: list[str]) -> dict:
        """Evaluate a single response"""
        score = 0
        issues = []
        strengths = []

        # Check for empty or very short responses
        if not response or len(response) < 5:
            return {
                'score': 0,
                'assessment': 'Empty or too short response',
                'issues': ['No meaningful content'],
                'strengths': []
            }

        # 1. Coherence (1 point)
        if not self._is_gibberish(response):
            score += 1
            strengths.append('Coherent output')
        else:
            issues.append('Contains gibberish or repetitive patterns')

        # 2. Grammar (1 point)
        if self._has_good_grammar(response):
            score += 1
            strengths.append('Grammatically correct')
        else:
            issues.append('Grammar issues detected')

        # 3. Relevance (1 point)
        if len(response.split()) >= 5:
            score += 1
            strengths.append('Substantive response')
        else:
            issues.append('Response too brief')

        # 4. Expected qualities (1 point)
        if self._has_expected_qualities(response, expected_qualities):
            score += 1
            strengths.append('Contains expected qualities')
        else:
            issues.append('Missing some expected qualities')

        # 5. Natural tone (1 point)
        if self._has_natural_tone(response):
            score += 1
            strengths.append('Natural conversational tone')
        else:
            issues.append('Tone could be more natural')

        # Generate assessment
        if score >= 4:
            assessment = 'Excellent'
        elif score >= 3:
            assessment = 'Good'
        elif score >= 2:
            assessment = 'Fair'
        else:
            assessment = 'Poor'

        return {
            'score': score,
            'assessment': assessment,
            'issues': issues,
            'strengths': strengths
        }

    def _is_gibberish(self, text: str) -> bool:
        """Check if text is gibberish (repetitive or nonsensical)"""
        words = text.lower().split()
        if len(words) < 3:
            return False

        # Check for excessive repetition
        unique_words = len(set(words))
        if unique_words < len(words) * 0.3:  # Less than 30% unique words
            return True

        # Check for very short repeated patterns
        return any(words[i] == words[i + 1] == words[i + 2] for i in range(len(words) - 2))

    def _has_good_grammar(self, text: str) -> bool:
        """Basic grammar check"""
        # Check for capitalization at start
        if text and text[0].islower():
            return False

        # Check for reasonable sentence structure
        return len(text.split()) >= 3

    def _has_expected_qualities(self, response: str, qualities: list[str]) -> bool:
        """Check if response has expected qualities"""
        if not qualities:
            return True

        response_lower = response.lower()
        matched = sum(1 for q in qualities if q.lower() in response_lower)
        return matched >= len(qualities) * 0.5  # At least 50% match

    def _has_natural_tone(self, text: str) -> bool:
        """Check for natural conversational tone"""
        # Check for question marks, exclamations, or common conversational words
        conversational_markers = ['?', '!', 'you', 'I', 'can', 'help', 'please', 'would', 'could']
        return any(marker in text for marker in conversational_markers)

    def run_full_evaluation(self):
        """Run complete evaluation suite"""

        # Category 1: Greetings & Basic Interactions
        self.results['categories']['greetings'] = self.evaluate_category(
            "Greetings & Basic Interactions",
            [
                {'prompt': 'Hello', 'qualities': ['greeting', 'friendly']},
                {'prompt': 'Hi there', 'qualities': ['greeting']},
                {'prompt': 'Good morning', 'qualities': ['greeting']},
                {'prompt': 'How are you?', 'qualities': ['response', 'polite']},
                {'prompt': 'What\'s up?', 'qualities': ['casual', 'friendly']}
            ]
        )

        # Category 2: Help & Assistance Requests
        self.results['categories']['assistance'] = self.evaluate_category(
            "Help & Assistance Requests",
            [
                {'prompt': 'Can you help me?', 'qualities': ['helpful', 'willing']},
                {'prompt': 'I need assistance', 'qualities': ['helpful', 'supportive']},
                {'prompt': 'I have a question', 'qualities': ['ready', 'listening']},
                {'prompt': 'Please explain', 'qualities': ['explanation', 'clarify']},
                {'prompt': 'I don\'t understand', 'qualities': ['patient', 'clarifying']}
            ]
        )

        # Category 3: AI & Technology Questions
        self.results['categories']['ai_knowledge'] = self.evaluate_category(
            "AI & Technology Knowledge",
            [
                {'prompt': 'What is AI?', 'qualities': ['artificial intelligence', 'definition']},
                {'prompt': 'Explain machine learning', 'qualities': ['machine learning', 'data']},
                {'prompt': 'How does deep learning work?', 'qualities': ['deep learning', 'neural']},
                {'prompt': 'What are neural networks?', 'qualities': ['neural', 'network', 'brain']},
                {'prompt': 'Tell me about Python', 'qualities': ['python', 'programming']}
            ]
        )

        # Category 4: Conversational Context
        self.results['categories']['context'] = self.evaluate_category(
            "Conversational Context Understanding",
            [
                {'prompt': 'What is your purpose?', 'qualities': ['assistant', 'help']},
                {'prompt': 'How do you work?', 'qualities': ['AI', 'process']},
                {'prompt': 'What can you do?', 'qualities': ['capabilities', 'help']},
                {'prompt': 'Are you intelligent?', 'qualities': ['AI', 'intelligence']},
                {'prompt': 'How do you learn?', 'qualities': ['learning', 'training']}
            ]
        )

        # Category 5: Complex Requests
        self.results['categories']['complex'] = self.evaluate_category(
            "Complex Requests",
            [
                {'prompt': 'Explain the difference between AI and machine learning', 'qualities': ['AI', 'machine learning', 'difference']},
                {'prompt': 'How does training a neural network work?', 'qualities': ['training', 'neural', 'data']},
                {'prompt': 'What makes a good AI assistant?', 'qualities': ['helpful', 'accurate', 'understanding']},
                {'prompt': 'Could you help me understand overfitting?', 'qualities': ['overfitting', 'model', 'data']},
                {'prompt': 'I want to learn about programming', 'qualities': ['programming', 'learning', 'help']}
            ]
        )

        # Calculate overall statistics
        self._calculate_overall_stats()

        # Generate report
        self._generate_report()

    def _calculate_overall_stats(self):
        """Calculate overall statistics across all categories"""
        all_scores = []
        total_tests = 0
        category_scores = {}

        for cat_name, cat_data in self.results['categories'].items():
            all_scores.extend([tc['evaluation']['score'] for tc in cat_data['test_cases']])
            total_tests += cat_data['total_tests']
            category_scores[cat_name] = cat_data['average_score']

        self.results['overall'] = {
            'total_tests': total_tests,
            'average_score': sum(all_scores) / len(all_scores) if all_scores else 0,
            'category_scores': category_scores,
            'score_distribution': {
                '5_excellent': all_scores.count(5),
                '4_good': all_scores.count(4),
                '3_fair': all_scores.count(3),
                '2_poor': all_scores.count(2),
                '1_very_poor': all_scores.count(1),
                '0_failed': all_scores.count(0)
            }
        }

    def _generate_report(self):
        """Generate markdown report"""
        report_filename = f"B3_HOPE_EVALUATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# ImpressionCore B3-Hope Model Evaluation Report\n\n")
            f.write(f"**Generated:** {self.results['metadata']['evaluation_date']}\n\n")
            f.write(f"**Model:** {self.results['metadata']['checkpoint']}\n\n")
            f.write(f"**Parameters:** {self.results['metadata']['parameters']:,}\n\n")
            f.write(f"**Training Loss:** {self.results['metadata']['training_loss']}\n\n")
            f.write(f"**Device:** {self.results['metadata']['device']}\n\n")

            f.write("---\n\n")
            f.write("## Executive Summary\n\n")
            f.write(f"**Total Tests Conducted:** {self.results['overall']['total_tests']}\n\n")
            f.write(f"**Overall Average Score:** {self.results['overall']['average_score']:.2f}/5.0\n\n")

            f.write("### Score Distribution\n\n")
            dist = self.results['overall']['score_distribution']
            f.write(f"- **Excellent (5/5):** {dist['5_excellent']} tests ({dist['5_excellent']/self.results['overall']['total_tests']*100:.1f}%)\n")
            f.write(f"- **Good (4/5):** {dist['4_good']} tests ({dist['4_good']/self.results['overall']['total_tests']*100:.1f}%)\n")
            f.write(f"- **Fair (3/5):** {dist['3_fair']} tests ({dist['3_fair']/self.results['overall']['total_tests']*100:.1f}%)\n")
            f.write(f"- **Poor (2/5):** {dist['2_poor']} tests ({dist['2_poor']/self.results['overall']['total_tests']*100:.1f}%)\n")
            f.write(f"- **Very Poor (1/5):** {dist['1_very_poor']} tests ({dist['1_very_poor']/self.results['overall']['total_tests']*100:.1f}%)\n")
            f.write(f"- **Failed (0/5):** {dist['0_failed']} tests ({dist['0_failed']/self.results['overall']['total_tests']*100:.1f}%)\n\n")

            f.write("### Category Performance\n\n")
            for cat_name, score in self.results['overall']['category_scores'].items():
                f.write(f"- **{cat_name.replace('_', ' ').title()}:** {score:.2f}/5.0\n")

            f.write("\n---\n\n")
            f.write("## Detailed Results by Category\n\n")

            for cat_name, cat_data in self.results['categories'].items():
                f.write(f"### {cat_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Average Score:** {cat_data['average_score']:.2f}/5.0\n\n")

                for i, test_case in enumerate(cat_data['test_cases'], 1):
                    f.write(f"#### Test {i}: \"{test_case['prompt']}\"\n\n")
                    f.write(f"**Response:** {test_case['response']}\n\n")
                    eval_data = test_case['evaluation']
                    f.write(f"**Score:** {eval_data['score']}/5 ({eval_data['assessment']})\n\n")

                    if eval_data['strengths']:
                        f.write("**Strengths:**\n")
                        for strength in eval_data['strengths']:
                            f.write(f"- {strength}\n")
                        f.write("\n")

                    if eval_data['issues']:
                        f.write("**Issues:**\n")
                        for issue in eval_data['issues']:
                            f.write(f"- {issue}\n")
                        f.write("\n")

                    f.write("---\n\n")

            f.write("## Conclusion\n\n")

            overall_score = self.results['overall']['average_score']
            if overall_score >= 4.0:
                conclusion = "The model demonstrates **excellent** conversational capabilities with strong coherence, grammar, and contextual understanding."
            elif overall_score >= 3.0:
                conclusion = "The model shows **good** conversational abilities with room for improvement in specific areas."
            elif overall_score >= 2.0:
                conclusion = "The model has **fair** performance but requires significant improvements for production use."
            else:
                conclusion = "The model demonstrates **poor** performance and is not ready for production deployment."

            f.write(conclusion + "\n\n")

            f.write("### Key Findings\n\n")
            best_category = max(self.results['overall']['category_scores'].items(), key=lambda x: x[1])
            worst_category = min(self.results['overall']['category_scores'].items(), key=lambda x: x[1])

            f.write(f"- **Strongest Area:** {best_category[0].replace('_', ' ').title()} ({best_category[1]:.2f}/5.0)\n")
            f.write(f"- **Weakest Area:** {worst_category[0].replace('_', ' ').title()} ({worst_category[1]:.2f}/5.0)\n")
            f.write(f"- **Success Rate:** {(dist['5_excellent'] + dist['4_good'])/self.results['overall']['total_tests']*100:.1f}% (scores 4+)\n\n")

            f.write("### Recommendations\n\n")
            if overall_score >= 4.0:
                f.write("- **Production Ready:** Model is suitable for deployment\n")
                f.write("- **Monitoring:** Continue monitoring for edge cases\n")
                f.write("- **Enhancement:** Consider fine-tuning for specific use cases\n")
            elif overall_score >= 3.0:
                f.write("- **Additional Training:** Focus on weaker categories\n")
                f.write("- **Quality Assurance:** Implement strict output filtering\n")
                f.write("- **User Testing:** Conduct beta testing before full deployment\n")
            else:
                f.write("- **Significant Retraining:** Model requires substantial improvement\n")
                f.write("- **Architecture Review:** Consider model architecture changes\n")
                f.write("- **Not Production Ready:** Do not deploy in current state\n")

        print(f"\n{'='*80}")
        print(f"REPORT GENERATED: {report_filename}")
        print(f"{'='*80}")

        # Also save JSON results
        json_filename = f"B3_HOPE_EVALUATION_RESULTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"JSON DATA: {json_filename}")

        return report_filename

def main():
    """Main execution"""
    evaluator = B3HopeEvaluator("b3_massive_best.pth")
    evaluator.run_full_evaluation()

    print("\n" + "="*80)
    print("EVALUATION COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()
