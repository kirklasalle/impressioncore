import sqlite3
import time
from pathlib import Path

from src.knowledge.gcide_parser import GCIDEParser


class DictionaryIndex:
    """
    SQLite-based index for the Dictionary Knowledge Base.
    """

    def __init__(self, db_path: str = "data/knowledge/dictionary.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                pos TEXT,
                definition TEXT,
                raw_entry TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON dictionary(word)')
        conn.commit()
        conn.close()

    def build_index(self, gcide_path: str):
        """Rebuild the index from GCIDE source files."""
        print(f"Building dictionary index from {gcide_path}...")
        parser = GCIDEParser(gcide_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing
        cursor.execute('DELETE FROM dictionary')

        count = 0
        start_time = time.time()

        # Batch insert
        batch = []
        BATCH_SIZE = 1000

        for entry in parser.parse_all():
            batch.append((
                entry['word'].lower(), # Index lowercase for search
                entry['pos'],
                entry['definition'],
                entry['raw']
            ))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    'INSERT INTO dictionary (word, pos, definition, raw_entry) VALUES (?, ?, ?, ?)',
                    batch
                )
                batch = []
                count += BATCH_SIZE
                if count % 10000 == 0:
                    print(f"Indexed {count} entries...")

        # Final batch
        if batch:
            cursor.executemany(
                'INSERT INTO dictionary (word, pos, definition, raw_entry) VALUES (?, ?, ?, ?)',
                batch
            )
            count += len(batch)

        conn.commit()
        conn.close()
        print(f"Dictionary index built! {count} entries in {time.time() - start_time:.2f}s")

    def lookup(self, word: str) -> list[dict[str, str]]:
        """Find definition(s) for a word."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Exact match (case insensitive)
        cursor.execute('SELECT word, pos, definition FROM dictionary WHERE word = ?', (word.lower(),))
        results = []
        for row in cursor.fetchall():
            results.append({
                "word": row[0],
                "pos": row[1],
                "definition": row[2]
            })

        conn.close()
        return results

if __name__ == "__main__":
    # Test/Build script
    import sys
    if len(sys.argv) > 1:
        gcide_path = sys.argv[1]
        indexer = DictionaryIndex()
        indexer.build_index(gcide_path)
    else:
        print("Usage: python dictionary_index.py <path_to_gcide>")
