"""
Quick Checkpoint Quality Test
============================

Created: October 1, 2025
Purpose: Test the recovery_step_4000.pth baseline quality
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

def test_recovery_baseline():
    """Test the recovery checkpoint quality using existing inference system."""

    print("🔍 Testing Recovery Baseline Checkpoint Quality")
    print("=" * 60)

    # Use the existing test_inference.py script
    import subprocess

    try:
        result = subprocess.run([
            sys.executable, "test_inference.py"
        ], capture_output=True, text=True, cwd=project_root)

        if result.returncode == 0:
            output = result.stdout

            # Extract responses from output
            responses = []
            lines = output.split('\n')
            for line in lines:
                if "🤖 Response:" in line:
                    response = line.split("🤖 Response:")[1].strip()
                    responses.append(response)

            # Basic quality analysis
            total_words = 0
            recognizable_words = 0

            for response in responses:
                words = response.split()
                total_words += len(words)

                for word in words:
                    # Simple heuristic for recognizable words
                    clean_word = ''.join(c for c in word if c.isalpha())
                    if len(clean_word) >= 3 and clean_word.isalpha():
                        vowels = sum(1 for c in clean_word.lower() if c in 'aeiou')
                        if vowels > 0:
                            recognizable_words += 1

            quality_ratio = recognizable_words / total_words if total_words > 0 else 0
            quality_score = quality_ratio * 100

            print(f"📊 Recovery Baseline Quality Analysis:")
            print(f"   Total Words: {total_words}")
            print(f"   Recognizable Words: {recognizable_words}")
            print(f"   Quality Ratio: {quality_ratio:.2f}")
            print(f"   Quality Score: {quality_score:.1f}/100")
            print()

            print(f"🎯 Baseline Status: {'✅ ACCEPTABLE' if quality_score > 30 else '❌ POOR'}")
            print()

            if responses:
                print("📝 Sample Responses:")
                for i, response in enumerate(responses[:2], 1):
                    print(f"   {i}. {response[:80]}...")

            return quality_score > 30

        else:
            print(f"❌ Error running inference test: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing baseline: {e}")
        return False

if __name__ == "__main__":
    success = test_recovery_baseline()
    sys.exit(0 if success else 1)