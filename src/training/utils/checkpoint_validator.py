"""
Checkpoint Quality Validation System
=====================================

Created: October 1, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Automated quality testing for model checkpoints to detect corruption early

This system validates checkpoints by testing text generation quality and comparing
against known good baselines to prevent training on corrupted weights.
"""

import sys
from pathlib import Path

import torch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

import logging

from src.core.tokenizers.unified_tokenizer_system import UnifiedTokenizerSystem
from src.training.scripts.train_unified_sweet_spot import UnifiedSweetSpotTrainer


class CheckpointValidator:
    """Validates checkpoint quality through text generation testing."""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.quality_thresholds = {
            'min_unique_words': 10,  # Minimum unique recognizable words
            'max_gibberish_ratio': 0.7,  # Maximum ratio of non-words
            'min_avg_word_length': 2.0,  # Minimum average word length
            'max_special_char_ratio': 0.3  # Maximum special character ratio
        }

        # Known good baseline: recovery_step_4000.pth results
        self.baseline_samples = [
            "separate children gotta Pokemon tein mainly Position",
            "Sas Shiite opioid mental modeled diabetes Topics",
            "reminding Lady node ReGb rocked Pizza Ign accessibility"
        ]

    def validate_checkpoint(self, checkpoint_path: str) -> dict:
        """
        Validate a checkpoint by testing text generation quality.

        Args:
            checkpoint_path: Path to checkpoint file

        Returns:
            dict: Validation results with quality metrics and pass/fail status
        """
        results = {
            'checkpoint_path': checkpoint_path,
            'is_valid': False,
            'error': None,
            'metrics': {},
            'sample_outputs': [],
            'quality_score': 0.0
        }

        try:
            # Test checkpoint loading and generation
            sample_outputs = self._test_generation(checkpoint_path)
            results['sample_outputs'] = sample_outputs

            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(sample_outputs)
            results['metrics'] = metrics

            # Determine if checkpoint passes quality thresholds
            is_valid = self._evaluate_quality(metrics)
            results['is_valid'] = is_valid

            # Calculate overall quality score (0-100)
            results['quality_score'] = self._calculate_quality_score(metrics)

            logging.info(f"Checkpoint validation complete: {checkpoint_path}")
            logging.info(f"Quality Score: {results['quality_score']:.1f}/100")
            logging.info(f"Status: {'PASS' if is_valid else 'FAIL'}")

        except Exception as e:
            results['error'] = str(e)
            logging.error(f"Checkpoint validation failed: {e}")

        return results

    def _test_generation(self, checkpoint_path: str) -> list:
        """Test text generation with standard prompts."""

        # Initialize trainer and load checkpoint
        trainer = UnifiedSweetSpotTrainer(device=self.device)
        trainer.load_checkpoint(checkpoint_path)

        # Initialize tokenizer
        tokenizer = UnifiedTokenizerSystem(device=self.device)

        test_prompts = [
            "Hello, how are you?",
            "What is artificial intelligence?",
            "Tell me about yourself.",
            "Complete this sentence: The future of AI is"
        ]

        outputs = []
        for prompt in test_prompts:
            try:
                # Generate response
                response = self._simple_generate(trainer.model, tokenizer, prompt)
                outputs.append({
                    'prompt': prompt,
                    'response': response,
                    'length': len(response.split())
                })
            except Exception as e:
                outputs.append({
                    'prompt': prompt,
                    'response': f"GENERATION_ERROR: {e}",
                    'length': 0
                })

        return outputs

    def _simple_generate(self, model, tokenizer, prompt: str, max_length: int = 50) -> str:
        """Simple text generation function."""

        model.eval()
        with torch.no_grad():
            # Encode prompt
            input_ids = tokenizer.encode_input(prompt)

            # Generate tokens
            generated = []
            current_ids = input_ids

            for _ in range(max_length):
                # Forward pass
                outputs = model(current_ids)
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs

                # Sample next token
                next_token_logits = logits[0, -1, :]
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                generated.append(next_token.item())

                # Update input for next iteration
                current_ids = torch.cat([current_ids, next_token.unsqueeze(0)], dim=1)

                # Check for end token
                if next_token.item() in [tokenizer.output_tokenizer.eos_token_id]:
                    break

            # Decode generated tokens
            generated_text = tokenizer.decode_output(generated)
            return generated_text.strip()

    def _calculate_quality_metrics(self, sample_outputs: list) -> dict:
        """Calculate quality metrics from sample outputs."""

        all_text = " ".join([output['response'] for output in sample_outputs])
        words = all_text.split()

        # Basic metrics
        total_chars = len(all_text)
        total_words = len(words)

        if total_words == 0:
            return {
                'unique_words': 0,
                'gibberish_ratio': 1.0,
                'avg_word_length': 0.0,
                'special_char_ratio': 1.0,
                'total_words': 0,
                'recognizable_words': 0
            }

        # Count recognizable words (basic heuristic)
        recognizable_words = []
        gibberish_words = []
        special_chars = 0

        for word in words:
            # Clean word of punctuation
            clean_word = ''.join(c for c in word if c.isalpha())

            if len(clean_word) >= 2 and clean_word.isalpha():
                # Simple heuristic: words with reasonable vowel/consonant distribution
                vowels = sum(1 for c in clean_word.lower() if c in 'aeiou')
                consonants = len(clean_word) - vowels

                if vowels > 0 and consonants > 0 and len(clean_word) <= 15:
                    recognizable_words.append(clean_word)
                else:
                    gibberish_words.append(word)
            else:
                gibberish_words.append(word)

            # Count special characters
            special_chars += sum(1 for c in word if not c.isalnum())

        unique_words = len(set(recognizable_words))
        gibberish_ratio = len(gibberish_words) / total_words if total_words > 0 else 1.0
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0.0
        special_char_ratio = special_chars / total_chars if total_chars > 0 else 0.0

        return {
            'unique_words': unique_words,
            'gibberish_ratio': gibberish_ratio,
            'avg_word_length': avg_word_length,
            'special_char_ratio': special_char_ratio,
            'total_words': total_words,
            'recognizable_words': len(recognizable_words)
        }

    def _evaluate_quality(self, metrics: dict) -> bool:
        """Evaluate if metrics meet quality thresholds."""

        checks = [
            metrics['unique_words'] >= self.quality_thresholds['min_unique_words'],
            metrics['gibberish_ratio'] <= self.quality_thresholds['max_gibberish_ratio'],
            metrics['avg_word_length'] >= self.quality_thresholds['min_avg_word_length'],
            metrics['special_char_ratio'] <= self.quality_thresholds['max_special_char_ratio']
        ]

        return all(checks)

    def _calculate_quality_score(self, metrics: dict) -> float:
        """Calculate overall quality score 0-100."""

        # Weighted scoring
        scores = []

        # Unique words score (0-25 points)
        unique_score = min(25, (metrics['unique_words'] / 20) * 25)
        scores.append(unique_score)

        # Gibberish ratio score (0-25 points)
        gibberish_score = max(0, 25 - (metrics['gibberish_ratio'] * 25))
        scores.append(gibberish_score)

        # Word length score (0-25 points)
        length_score = min(25, (metrics['avg_word_length'] / 6) * 25)
        scores.append(length_score)

        # Special char score (0-25 points)
        special_score = max(0, 25 - (metrics['special_char_ratio'] * 25))
        scores.append(special_score)

        return sum(scores)

def validate_checkpoint_cli(checkpoint_path: str):
    """CLI interface for checkpoint validation."""

    print(f"🔍 Validating checkpoint: {checkpoint_path}")
    print("=" * 60)

    validator = CheckpointValidator()
    results = validator.validate_checkpoint(checkpoint_path)

    if results['error']:
        print(f"❌ VALIDATION FAILED: {results['error']}")
        return False

    print(f"📊 Quality Score: {results['quality_score']:.1f}/100")
    print(f"🎯 Status: {'✅ PASS' if results['is_valid'] else '❌ FAIL'}")
    print()

    print("📈 Metrics:")
    for key, value in results['metrics'].items():
        print(f"  {key}: {value}")
    print()

    print("🎭 Sample Outputs:")
    for i, output in enumerate(results['sample_outputs'][:2], 1):
        print(f"  {i}. Prompt: {output['prompt']}")
        print(f"     Response: {output['response'][:100]}...")
        print()

    return results['is_valid']

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python checkpoint_validator.py <checkpoint_path>")
        sys.exit(1)

    checkpoint_path = sys.argv[1]
    is_valid = validate_checkpoint_cli(checkpoint_path)
    sys.exit(0 if is_valid else 1)
