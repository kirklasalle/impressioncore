#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #memory_management #python #source_code #src/brainsim/memory/test_brainsim3_adapter_functional.py #testing
**Category:** Source Code
**Status:** Active
"""









# Test suite for the functional BrainSim3 adapter

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #api #memory_management #python #source_code #src\\brainsim\\memory\\test_brainsim3_adapter_functional.py #testing
# Category:** Source Code
# Status:** Active

import logging
import os
import shutil
import sys
import tempfile
import unittest

# Add project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.core.brain import brainsim_adapter_functional as bsa_functional
from src.core.utils.rich_status_animation import StatusAnimation

# Configure logging once for the entire test suite
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BrainSimFunctionalAdapterIntegrationTest")

class MockUKS:
    """A mock UKS for testing purposes."""
    def __init__(self):
        self.nodes = {}
        self.relationships = {}
        self._node_id_counter = 0
        self._rel_id_counter = 0
        logger.info("MockUKS instantiated.")

    def create_node(self, node_type, attributes):
        self._node_id_counter += 1
        node_id = self._node_id_counter
        self.nodes[node_id] = {'type': node_type, **attributes}
        logger.info(f"MockUKS: Created node {node_id} with data {self.nodes[node_id]}")
        return node_id

    def add_relationship(self, source_id, target_id, relationship_type, data=None):
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node does not exist.")
        self._rel_id_counter += 1
        rel_id = self._rel_id_counter
        self.relationships[rel_id] = {
            'source': source_id,
            'target': target_id,
            'type': relationship_type,
            'data': data or {}
        }
        logger.info(f"MockUKS: Created relationship {rel_id} with data {self.relationships[rel_id]}")
        return rel_id

    def query(self, query_string):
        logger.info(f"MockUKS: Received query '{query_string}'")
        # Simple mock query, returns all nodes for verification.
        return list(self.nodes.values())

    def get_node(self, node_id):
        return self.nodes.get(node_id)

class TestBrainSimFunctionalAdapterIntegration(unittest.TestCase):
    """
    Test suite for the functional BrainSimAdapter.
    """

    @classmethod
    def setUpClass(cls):
        """Set up a temporary directory and resources for the entire test class."""
        logger.info("Setting up TestBrainSimFunctionalAdapterIntegration suite.")
        cls.uks_output_dir = tempfile.mkdtemp(prefix="impressioncore-test-functional-")
        logger.info(f"Created temporary directory for test outputs: {cls.uks_output_dir}")
        cls.uks_path = os.path.join(cls.uks_output_dir, "uks_db.pkl")

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory after all tests have run."""
        logger.info("--- Tearing down TestBrainSimFunctionalAdapterIntegration suite ---")

        status_animation = StatusAnimation(total_steps=1, description="Cleaning up test artifacts")
        status_animation.update(step=0)

        if os.path.exists(cls.uks_output_dir):
            try:
                shutil.rmtree(cls.uks_output_dir)
                logger.info(f"  - Successfully deleted directory and all its contents: {cls.uks_output_dir}")
            except OSError as e:
                logger.warning(f"  - Error deleting directory {cls.uks_output_dir}: {e}")
        else:
            logger.info(f"  - Directory not found, skipping cleanup: {cls.uks_output_dir}")

        status_animation.complete(message="Cleanup complete")
        logger.info("--- Cleanup Complete ---")

    def test_01_mock_uks_integration(self):
        """
        Runs a simple integration test with a mock, in-memory UKS.
        """
        logger.info("--- Running Test 1: Mock UKS Integration (Functional) ---")

        mock_uks = MockUKS()

        logger.info("Testing Node Creation...")
        france_id = bsa_functional.add_node(mock_uks, "Country", {"name": "France", "continent": "Europe"})
        paris_id = bsa_functional.add_node(mock_uks, "City", {"name": "Paris"})
        eiffel_tower_id = bsa_functional.add_node(mock_uks, "Landmark", {"name": "Eiffel Tower", "height_m": 330})
        logger.info(f"Created nodes with IDs: France({france_id}), Paris({paris_id}), Eiffel Tower({eiffel_tower_id})")

        logger.info("Testing Relationship Creation...")
        rel1_id = bsa_functional.add_relationship(mock_uks, paris_id, france_id, "CAPITAL_OF")
        rel2_id = bsa_functional.add_relationship(mock_uks, eiffel_tower_id, paris_id, "LOCATED_IN")
        logger.info(f"Created relationships with IDs: {rel1_id}, {rel2_id}")
        self.assertEqual(len(mock_uks.relationships), 2, "Should have 2 relationships")

        logger.info("Testing Querying...")
        query_results = bsa_functional.query(mock_uks, "all nodes")
        logger.info(f"Query results: {query_results}")

        self.assertEqual(len(query_results), 3, "Should return 3 nodes")
        logger.info("Assertion passed: Query returned 3 nodes as expected.")

        logger.info("Testing specific node retrieval...")
        paris_node = bsa_functional.get_node(mock_uks, paris_id)
        self.assertIsNotNone(paris_node)
        self.assertEqual(paris_node['name'], "Paris")
        logger.info(f"Verified Paris node: {paris_node}")

        eiffel_node = bsa_functional.get_node(mock_uks, eiffel_tower_id)
        self.assertIsNotNone(eiffel_node)
        self.assertEqual(eiffel_node['height_m'], 330)
        logger.info(f"Verified Eiffel Tower node: {eiffel_node}")

        logger.info("--- Mock UKS Integration Test Finished Successfully ---")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBrainSimFunctionalAdapterIntegration))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

