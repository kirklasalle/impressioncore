"""
Segments chat.txt into fine-grained messages and sections for embedding, using:
- Markdown headers (#, ##, ###, etc.)
- List/quote markers (*, -, >)
- Role markers (user, assistant)
- Multiple consecutive empty lines (carriage returns)

Outputs:
- chat_segments.json: List of dicts with segment type, content, and line numbers.
- chat_segments.txt: Each segment separated by a delimiter for review.

Usage:
    python segment_chat_txt.py --input <chat.txt> --output_dir <output_dir>
"""
import argparse
import json
import os
import re


def segment_chat_txt(input_path, output_dir):
    with open(input_path, encoding='utf-8') as f:
        lines = f.readlines()

    segments = []
    current = []
    seg_type = None
    start_line = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect section/session headers
        if re.match(r'^(#{1,6}|\*|\-|>)', line.strip()):
            if current:
                segments.append({'type': seg_type or 'text', 'content': ''.join(current).strip(), 'start': start_line, 'end': i-1})
                current = []
            seg_type = 'header' if line.strip().startswith('#') else 'list_or_quote'
            start_line = i
            current.append(line)
        # Detect role markers
        elif re.match(r'^(user|assistant|ai|system)\s*$', line.strip(), re.I):
            if current:
                segments.append({'type': seg_type or 'text', 'content': ''.join(current).strip(), 'start': start_line, 'end': i-1})
                current = []
            seg_type = 'role_marker'
            start_line = i
            current.append(line)
        # Detect multiple empty lines (session break)
        elif line.strip() == '' and i+1 < len(lines) and lines[i+1].strip() == '':
            if current:
                segments.append({'type': seg_type or 'text', 'content': ''.join(current).strip(), 'start': start_line, 'end': i-1})
                current = []
            seg_type = 'session_break'
            start_line = i
            current.append(line)
            # Skip all consecutive empty lines
            while i+1 < len(lines) and lines[i+1].strip() == '':
                i += 1
                current.append(lines[i])
        else:
            if not current:
                start_line = i
            current.append(line)
        i += 1
    if current:
        segments.append({'type': seg_type or 'text', 'content': ''.join(current).strip(), 'start': start_line, 'end': len(lines)-1})

    # Write JSON
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, 'chat_segments.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    # Write TXT
    txt_path = os.path.join(output_dir, 'chat_segments.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"--- SEGMENT [{seg['type']}] (lines {seg['start']}-{seg['end']}) ---\n")
            f.write(seg['content'] + '\n\n')
    print(f"Segmentation complete. JSON: {json_path}, TXT: {txt_path}")

def main():
    parser = argparse.ArgumentParser(description='Segment chat.txt for fine-grained embedding.')
    parser.add_argument('--input', required=True, help='Path to chat.txt')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    args = parser.parse_args()
    segment_chat_txt(args.input, args.output_dir)

if __name__ == '__main__':
    main()
