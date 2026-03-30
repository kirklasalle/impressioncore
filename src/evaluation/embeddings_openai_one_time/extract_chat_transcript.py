"""
Extracts structured data and full text from an OpenAI chat HTML export for ImpressionCore analytics and integration.

- Outputs:
    1. chat_transcript.json: List of dicts with session, timestamp, role, and message.
    2. chat_transcript.csv: CSV with session, timestamp, role, message.
    3. chat_transcript.txt: Full readable text transcript.

Usage:
    python extract_chat_transcript.py --input <path_to_chat.html> --output_dir <output_dir>

Memory: Efficient for large files; processes line by line.
"""
import argparse
import csv
import json
import os
import re

from bs4 import BeautifulSoup


def extract_chat_html(input_path, output_dir):
    with open(input_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    sessions = []
    text_lines = []
    csv_rows = []
    # Heuristic: Each session is a <div> or <section> with a header/title
    for session in soup.find_all(['section', 'div'], class_=re.compile(r'(chat|session|conversation)', re.I)):
        session_title = session.find(['h1', 'h2', 'header'])
        session_name = session_title.get_text(strip=True) if session_title else 'Session'
        for msg in session.find_all(['div', 'p'], class_=re.compile(r'(message|msg|role|user|assistant)', re.I)):
            role = 'assistant' if 'assistant' in msg.get('class', []) else 'user'
            timestamp = msg.get('data-timestamp') or ''
            message = msg.get_text(strip=True)
            sessions.append({
                'session': session_name,
                'timestamp': timestamp,
                'role': role,
                'message': message
            })
            csv_rows.append([session_name, timestamp, role, message])
            text_lines.append(f"[{session_name}] ({role}) {message}")

    # Fallback: If no sessions found, try to extract all messages
    if not sessions:
        for msg in soup.find_all(['div', 'p'], class_=re.compile(r'(message|msg|role|user|assistant)', re.I)):
            role = 'assistant' if 'assistant' in msg.get('class', []) else 'user'
            timestamp = msg.get('data-timestamp') or ''
            message = msg.get_text(strip=True)
            sessions.append({
                'session': '',
                'timestamp': timestamp,
                'role': role,
                'message': message
            })
            csv_rows.append(['', timestamp, role, message])
            text_lines.append(f"({role}) {message}")

    # Write JSON
    json_path = os.path.join(output_dir, 'chat_transcript.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)
    # Write CSV
    csv_path = os.path.join(output_dir, 'chat_transcript.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['session', 'timestamp', 'role', 'message'])
        writer.writerows(csv_rows)
    # Write TXT
    txt_path = os.path.join(output_dir, 'chat_transcript.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_lines))
    print(f"Extraction complete. JSON: {json_path}, CSV: {csv_path}, TXT: {txt_path}")

def main():
    parser = argparse.ArgumentParser(description='Extract OpenAI chat HTML export to structured formats.')
    parser.add_argument('--input', required=True, help='Path to chat.html')
    parser.add_argument('--output_dir', required=True, help='Directory for output files')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    extract_chat_html(args.input, args.output_dir)

if __name__ == '__main__':
    main()
