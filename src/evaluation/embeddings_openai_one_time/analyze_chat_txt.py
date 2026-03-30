"""
Analyzes a large chat.txt file to determine session/message boundaries, structure, and optimal embedding segmentation.
- Prints summary statistics and sample boundaries.
- Outputs a report with detected session/message delimiters and recommendations.

Usage:
    python analyze_chat_txt.py --input <path_to_chat.txt> --output <report.json>
"""
import argparse
import json
import re


def analyze_chat_txt(input_path, output_path):
    with open(input_path, encoding='utf-8') as f:
        lines = f.readlines()

    # Heuristics for boundaries
    session_pattern = re.compile(r'^(Session|Topic|Title|#|\[.*\])', re.I)
    role_pattern = re.compile(r'^(User|Assistant|AI|System|\(user\)|\(assistant\))', re.I)
    empty_lines = 0
    session_lines = []
    role_lines = []
    for i, line in enumerate(lines):
        if session_pattern.match(line):
            session_lines.append(i)
        if role_pattern.match(line):
            role_lines.append(i)
        if line.strip() == '':
            empty_lines += 1

    # Sample boundaries
    session_samples = [lines[i][:200] for i in session_lines[:5]]
    role_samples = [lines[i][:200] for i in role_lines[:5]]

    # Stats
    stats = {
        'total_lines': len(lines),
        'empty_lines': empty_lines,
        'session_delimiter_count': len(session_lines),
        'role_delimiter_count': len(role_lines),
        'session_samples': session_samples,
        'role_samples': role_samples,
    }

    # Recommendations
    if len(session_lines) > 10:
        recommendation = 'Likely session/topic boundaries detected. Use these for chunking.'
    elif len(role_lines) > 1000:
        recommendation = 'Likely per-message boundaries detected. Use these for fine-grained chunking.'
    else:
        recommendation = 'No clear boundaries detected. Consider manual inspection or chunk by size.'
    stats['recommendation'] = recommendation

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"Analysis complete. See {output_path}")
    print(json.dumps(stats, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Analyze chat.txt for structure and boundaries.')
    parser.add_argument('--input', required=True, help='Path to chat.txt')
    parser.add_argument('--output', required=True, help='Path to output report.json')
    args = parser.parse_args()
    analyze_chat_txt(args.input, args.output)

if __name__ == '__main__':
    main()
