import os
import re
from collections.abc import Generator
from pathlib import Path


class GCIDEParser:
    """
    Parser for GNU Collaborative International Dictionary of English (GCIDE).
    Handles the specific XML-like format used in CIDE.* files.
    """

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    def parse_all(self) -> Generator[dict[str, str], None, None]:
        """Yields dictionary entries from all CIDE.* files."""
        # CIDE files are typically CIDE.A through CIDE.Z
        # We look for files starting with CIDE. followed by a letter
        files = sorted([f for f in os.listdir(self.data_dir) if f.startswith("CIDE.") and len(f) == 6])

        for filename in files:
            yield from self.parse_file(self.data_dir / filename)

    def parse_file(self, filepath: Path) -> Generator[dict[str, str], None, None]:
        """Parse a single CIDE file line by line."""
        current_entry = []
        in_entry = False

        try:
            with open(filepath, encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("<entry"):
                        in_entry = True
                        current_entry = [line]
                    elif line.startswith("</entry>"):
                        in_entry = False
                        current_entry.append(line)
                        parsed = self._process_entry_block(" ".join(current_entry))
                        if parsed:
                            yield parsed
                        current_entry = []
                    elif in_entry:
                        current_entry.append(line)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    def _process_entry_block(self, raw_xml: str) -> dict[str, str] | None:
        """Extract fields from an <entry> block."""
        try:
            # Simple regex extraction for robustness against malformed XML
            # GCIDE isn't strict XML

            # Extract Headword
            hw_match = re.search(r'<hw>(.*?)</hw>', raw_xml)
            if not hw_match:
                return None
            raw_hw = self._clean_text(hw_match.group(1))
            headword = self._clean_headword(raw_hw)

            # Extract Part of Speech (first one found)
            pos_match = re.search(r'<pos>(.*?)</pos>', raw_xml)
            pos = self._clean_text(pos_match.group(1)) if pos_match else "n."

            # Extract Definition (can be multiple)
            # We'll simplisticly grab all <def> content or text
            # For now, just a plain text extraction of the whole body
            body = self._clean_xml_tags(raw_xml)

            # Refined definition extraction
            defs = re.findall(r'<def>(.*?)</def>', raw_xml)
            cleaned_defs = [self._clean_text(d) for d in defs]
            full_def = "; ".join(cleaned_defs)

            return {
                "word": headword,
                "pos": pos,
                "definition": full_def if full_def else body,
                "raw": raw_xml
            }
        except Exception:
            return None

    def _clean_headword(self, hw: str) -> str:
        """Remove pronunciation markers from GCIDE headwords."""
        # GCIDE uses " for primary accent, * for syllables, ` for secondary, ' sometimes
        return re.sub(r'["*`\']', '', hw).strip()

    def _clean_text(self, text: str) -> str:
        """Remove GCIDE specific internal tags like <xex>, <ets>."""
        # text = re.sub(r'<[^>]+>', '', text) # Naive strip
        # Keep it readable but strip tags
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def _clean_xml_tags(self, text: str) -> str:
        return re.sub(r'<[^>]+>', '', text).strip()
