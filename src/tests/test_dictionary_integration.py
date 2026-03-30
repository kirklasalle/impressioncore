import unittest

from src.knowledge.dictionary_index import DictionaryIndex
from src.orchestrator.nexus_interpreter import NexusInterpreter


class TestDictionaryIntegration(unittest.TestCase):
    def setUp(self):
        self.interpreter = NexusInterpreter()

    def test_direct_lookup(self):
        """Test direct index access."""
        idx = DictionaryIndex()
        results = idx.lookup("Abacus")
        self.assertTrue(len(results) > 0)
        print(f"Abacus def: {results[0]['definition'][:50]}...")
        self.assertIn("calculating", results[0]['definition'].lower())

    def test_nexus_command(self):
        """Test NEXUS (DICT-LOOKUP) command."""
        code = '(DICT-LOOKUP "Abacus")'
        result = self.interpreter.execute(code)
        self.assertIsInstance(result, str)
        self.assertIn("calculating", result.lower())

    def test_nexus_def_command(self):
        """Test NEXUS (DICT-DEF) command."""
        code = '(DICT-DEF "Abacus")'
        result = self.interpreter.execute(code)
        self.assertIsInstance(result, str)
        self.assertIn("(n.)", result.lower()) # Check for POS

if __name__ == "__main__":
    unittest.main()
