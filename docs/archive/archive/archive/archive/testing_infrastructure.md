# ⚠️ ARCHIVED FILE

**Created:** March 06, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\archive\archive\archive\testing_infrastructure.md #attention_mechanism #cuda #docs\archive\testing_infrastructure.md #documentation #gpu_optimization #inference #memory_management #performance #testing #training [2025, reference, testing]  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

# Testing Infrastructure

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #attention_mechanism #cuda #docs\archive\testing_infrastructure.md #documentation #gpu_optimization #inference #memory_management #performance #testing #training  
**Category:** Archive  
**Status:** Archived

---
tags: [2025, reference, testing]
---

# Testing Infrastructure Implementation Plan

## Current Issues

After reviewing the codebase, I've identified several issues with the current testing approach:

1. **Limited Test Coverage**: Many components lack comprehensive tests.
2. **Inconsistent Testing Approaches**: Different parts of the codebase use different testing approaches.
3. **Missing Integration Tests**: There are few tests that verify component interactions.
4. **No Continuous Integration**: There's no automated testing as part of a CI/CD pipeline.
5. **Lack of Test Documentation**: Tests are poorly documented, making it difficult to understand their purpose.

## Testing Goals

1. Establish a comprehensive testing strategy
2. Implement consistent testing approaches across the codebase
3. Achieve high test coverage for critical components
4. Automate testing as part of development workflow
5. Ensure tests are well-documented and maintainable

## Testing Strategy

### 1. Test Pyramid Approach

Implement a test pyramid with:

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test interactions between components
3. **System Tests**: Test end-to-end functionality
4. **Performance Tests**: Test system performance under various conditions

### 2. Test Coverage Targets

Set the following test coverage targets:

| Component Type | Coverage Target |
|----------------|-----------------|
| Core Components | 90% |
| Model Components | 80% |
| Utility Functions | 85% |
| Integration Points | 75% |
| UI Components | 70% |

### 3. Testing Tools

Use the following testing tools:

1. **Unit Testing**: pytest
2. **Integration Testing**: pytest with fixtures
3. **System Testing**: pytest with custom test runners
4. **Performance Testing**: pytest-benchmark
5. **Coverage Analysis**: pytest-cov
6. **Mocking**: pytest-mock and unittest.mock
7. **Property-Based Testing**: hypothesis

## Test Implementation Plan

### Phase 1: Unit Testing Framework (1-2 weeks)

#### 1.1. Test Directory Structure

``` text
tests/
├── unit/                     # Unit tests
│   ├── core/                 # Tests for core components
│   ├── knowledge/            # Tests for knowledge components
│   ├── models/               # Tests for model components
│   └── utils/                # Tests for utility functions
├── integration/              # Integration tests
│   ├── core_knowledge/       # Tests for core-knowledge integration
│   ├── knowledge_models/     # Tests for knowledge-models integration
│   └── models_utils/         # Tests for models-utils integration
├── system/                   # System tests
│   ├── training/             # Tests for training workflow
│   ├── inference/            # Tests for inference workflow
│   └── knowledge/            # Tests for knowledge workflow
├── performance/              # Performance tests
│   ├── models/               # Performance tests for models
│   ├── knowledge/            # Performance tests for knowledge store
│   └── memory/               # Performance tests for memory usage
└── conftest.py               # Shared test fixtures
```

#### 1.2. Base Test Classes

```python
# tests/unit/base_test.py
import unittest
import pytest
from typing import Any, Dict, List, Optional, Union

class BaseTest(unittest.TestCase):
    """Base class for all unit tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Common setup code
        pass
    
    def tearDown(self):
        """Clean up test environment."""
        # Common cleanup code
        pass
    
    def assert_dict_equal(self, expected: Dict[str, Any], actual: Dict[str, Any], 
                          msg: Optional[str] = None):
        """Assert that two dictionaries are equal, with better error messages."""
        # Check keys
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())
        
        missing_keys = expected_keys - actual_keys
        extra_keys = actual_keys - expected_keys
        
        if missing_keys:
            self.fail(f"{msg or 'Dictionaries differ'}: Missing keys: {missing_keys}")
        
        if extra_keys:
            self.fail(f"{msg or 'Dictionaries differ'}: Extra keys: {extra_keys}")
        
        # Check values
        for key in expected_keys:
            expected_value = expected[key]
            actual_value = actual[key]
            
            if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                self.assert_dict_equal(expected_value, actual_value, 
                                      msg=f"{msg or 'Dictionaries differ'} at key '{key}'")
            else:
                self.assertEqual(expected_value, actual_value, 
                                msg=f"{msg or 'Dictionaries differ'} at key '{key}'")
    
    def assert_model_equal(self, expected_model, actual_model, msg: Optional[str] = None):
        """Assert that two models have the same architecture and parameters."""
        # Check model class
        self.assertEqual(expected_model.__class__, actual_model.__class__, 
                        msg=f"{msg or 'Models differ'}: Different classes")
        
        # Check model parameters
        expected_params = dict(expected_model.named_parameters())
        actual_params = dict(actual_model.named_parameters())
        
        # Check parameter names
        expected_param_names = set(expected_params.keys())
        actual_param_names = set(actual_params.keys())
        
        missing_params = expected_param_names - actual_param_names
        extra_params = actual_param_names - expected_param_names
        
        if missing_params:
            self.fail(f"{msg or 'Models differ'}: Missing parameters: {missing_params}")
        
        if extra_params:
            self.fail(f"{msg or 'Models differ'}: Extra parameters: {extra_params}")
        
        # Check parameter shapes
        for name in expected_param_names:
            expected_shape = expected_params[name].shape
            actual_shape = actual_params[name].shape
            
            self.assertEqual(expected_shape, actual_shape, 
                            msg=f"{msg or 'Models differ'}: Shape mismatch for parameter '{name}'")
```

#### 1.3. Test Fixtures

```python
# tests/conftest.py
import pytest
import torch
import os
import tempfile
from typing import Dict, Any, List, Optional, Union

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def small_model_config():
    """Create a small model configuration for testing."""
    return {
        "vocab_size": 1000,
        "hidden_size": 64,
        "num_hidden_layers": 2,
        "num_attention_heads": 2,
        "intermediate_size": 128,
        "max_position_embeddings": 128,
        "layer_norm_eps": 1e-12,
        "dropout": 0.1,
        "initializer_range": 0.02,
        "model_type": "impressioncore-test"
    }

@pytest.fixture
def small_model(small_model_config):
    """Create a small model for testing."""
    from impressioncore.model import ImpressionCoreModel, ModelConfig
    
    config = ModelConfig.from_dict(small_model_config)
    model = ImpressionCoreModel(config)
    
    return model

@pytest.fixture
def sample_knowledge_store():
    """Create a sample knowledge store for testing."""
    from src.knowledge.uks import UniversalKnowledgeStore
    from src.knowledge.node import KnowledgeNode
    
    # Create store
    uks = UniversalKnowledgeStore()
    
    # Create nodes
    mars = KnowledgeNode("Mars")
    mars.set_attribute("type", "planet")
    mars.set_attribute("color", "red")
    
    earth = KnowledgeNode("Earth")
    earth.set_attribute("type", "planet")
    earth.set_attribute("color", "blue")
    
    # Add nodes to store
    uks.add_node(mars)
    uks.add_node(earth)
    
    # Create relationships
    uks.add_relation(mars, "orbits", "Sun")
    uks.add_relation(earth, "orbits", "Sun")
    
    return uks

@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    import torch
    from torch.utils.data import Dataset
    
    class SampleDataset(Dataset):
        def __init__(self, size=100):
            self.size = size
            
        def __len__(self):
            return self.size
            
        def __getitem__(self, idx):
            # Create a sample item with input_ids, attention_mask, and labels
            return {
                "input_ids": torch.randint(0, 1000, (32,)),
                "attention_mask": torch.ones(32),
                "labels": torch.randint(0, 1000, (32,))
            }
    
    return SampleDataset()

@pytest.fixture
def mock_gpu_environment(monkeypatch):
    """Mock GPU environment for testing."""
    # Mock torch.cuda.is_available
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    
    # Mock torch.cuda.device_count
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 1)
    
    # Mock torch.cuda.current_device
    monkeypatch.setattr(torch.cuda, "current_device", lambda: 0)
    
    # Mock torch.cuda.get_device_name
    monkeypatch.setattr(torch.cuda, "get_device_name", lambda device: "Test GPU")
    
    # Mock torch.cuda.get_device_properties
    class MockDeviceProperties:
        def __init__(self):
            self.name = "Test GPU"
            self.total_memory = 4 * 1024 * 1024 * 1024  # 4 GB
            self.major = 7
            self.minor = 0
            self.multi_processor_count = 10
            self.max_threads_per_block = 1024
            self.max_threads_per_multi_processor = 2048
    
    monkeypatch.setattr(torch.cuda, "get_device_properties", 
                       lambda device: MockDeviceProperties())
    
    # Mock torch.cuda.memory_allocated
    monkeypatch.setattr(torch.cuda, "memory_allocated", 
                       lambda device=None: 1 * 1024 * 1024 * 1024)  # 1 GB
    
    # Mock torch.cuda.memory_reserved
    monkeypatch.setattr(torch.cuda, "memory_reserved", 
                       lambda device=None: 2 * 1024 * 1024 * 1024)  # 2 GB
    
    # Mock torch.cuda.empty_cache
    monkeypatch.setattr(torch.cuda, "empty_cache", lambda: None)
```

#### 1.4. Sample Unit Tests

```python
# tests/unit/models/test_impressioncore_model.py
import pytest
import torch
import os
from typing import Dict, Any

from src.model import ImpressionCoreModel, ModelConfig

class TestImpressionCoreModel:
    """Tests for the ImpressionCoreModel class."""
    
    def test_init(self, small_model_config):
        """Test model initialization."""
        # Create model
        config = ModelConfig.from_dict(small_model_config)
        model = ImpressionCoreModel(config)  # Updated to use ImpressionCoreModel
        
        # Check model attributes
        assert model.config.vocab_size == small_model_config["vocab_size"]
        assert model.config.hidden_size == small_model_config["hidden_size"]
        assert model.config.num_hidden_layers == small_model_config["num_hidden_layers"]
        assert model.config.num_attention_heads == small_model_config["num_attention_heads"]
        
        # Check model structure
        assert len(model.layers) == small_model_config["num_hidden_layers"]
        assert isinstance(model.token_embeddings, torch.nn.Embedding)
        assert isinstance(model.position_embeddings, torch.nn.Embedding)
        assert isinstance(model.output, torch.nn.Linear)
    
    def test_forward(self, small_model):
        """Test model forward pass."""
        # Create input
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        attention_mask = torch.ones((batch_size, seq_length))
        
        # Forward pass
        outputs = small_model(input_ids=input_ids, attention_mask=attention_mask)
        
        # Check outputs
        assert "logits" in outputs
        assert outputs["logits"].shape == (batch_size, seq_length, small_model.config.vocab_size)
    
    def test_forward_with_labels(self, small_model):
        """Test model forward pass with labels."""
        # Create input
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        attention_mask = torch.ones((batch_size, seq_length))
        labels = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        
        # Forward pass
        outputs = small_model(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            labels=labels
        )
        
        # Check outputs
        assert "logits" in outputs
        assert "loss" in outputs
        assert outputs["logits"].shape == (batch_size, seq_length, small_model.config.vocab_size)
        assert outputs["loss"].shape == ()  # Scalar
    
    def test_generate(self, small_model):
        """Test model text generation."""
        # Create input
        batch_size = 2
        seq_length = 5
        input_ids = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        
        # Generate text
        max_length = 10
        generated_ids = small_model.generate(
            input_ids=input_ids,
            max_length=max_length
        )
        
        # Check output
        assert generated_ids.shape[0] == batch_size
        assert generated_ids.shape[1] <= max_length + seq_length
        
        # Check that the original input is preserved
        assert torch.all(generated_ids[:, :seq_length] == input_ids)
    
    def test_save_load(self, small_model, temp_dir):
        """Test model saving and loading."""
        # Save model
        save_path = os.path.join(temp_dir, "model")
        os.makedirs(save_path, exist_ok=True)
        
        # Save config
        config_path = os.path.join(save_path, "config.json")
        with open(config_path, "w") as f:
            import json
            json.dump(small_model.config.__dict__, f)
        
        # Save weights
        model_path = os.path.join(save_path, "model.pt")
        torch.save(small_model.state_dict(), model_path)
        
        # Load model
        loaded_model = ImpressionCoreModel.from_pretrained(save_path)  # Updated to use ImpressionCoreModel
        
        # Check model attributes
        assert loaded_model.config.vocab_size == small_model.config.vocab_size
        assert loaded_model.config.hidden_size == small_model.config.hidden_size
        assert loaded_model.config.num_hidden_layers == small_model.config.num_hidden_layers
        assert loaded_model.config.num_attention_heads == small_model.config.num_attention_heads
        
        # Check model parameters
        for p1, p2 in zip(small_model.parameters(), loaded_model.parameters()):
            assert torch.all(p1 == p2)
```

```python
# tests/unit/knowledge/test_uks.py
import pytest
import os
from typing import Dict, Any

from src.knowledge.uks import UniversalKnowledgeStore
from src.knowledge.node import KnowledgeNode

class TestUniversalKnowledgeStore:
    """Tests for the UniversalKnowledgeStore class."""
    
    def test_init(self):
        """Test store initialization."""
        # Create store
        uks = UniversalKnowledgeStore()
        
        # Check store attributes
        assert len(uks.nodes) == 0
    
    def test_add_node(self):
        """Test adding nodes to the store."""
        # Create store
        uks = UniversalKnowledgeStore()
        
        # Create node
        node = KnowledgeNode("Test")
        node.set_attribute("type", "test")
        
        # Add node to store
        uks.add_node(node)
        
        # Check store
        assert len(uks.nodes) == 1
        assert node.id in uks.nodes
        assert uks.nodes[node.id] == node
    
    def test_add_relation(self):
        """Test adding relations between nodes."""
        # Create store
        uks = UniversalKnowledgeStore()
        
        # Create nodes
        node1 = KnowledgeNode("Node1")
        node2 = KnowledgeNode("Node2")
        
        # Add nodes to store
        uks.add_node(node1)
        uks.add_node(node2)
        
        # Add relation
        uks.add_relation(node1, "test_relation", node2)
        
        # Check relation
        assert len(node1.relations) == 1
        assert node1.relations[0]["type"] == "test_relation"
        assert node1.relations[0]["target_id"] == node2.id
    
    def test_query(self):
        """Test querying the store."""
        # Create store
        uks = UniversalKnowledgeStore()
        
        # Create nodes
        node1 = KnowledgeNode("Node1")
        node1.set_attribute("type", "test")
        node1.set_attribute("value", 1)
        
        node2 = KnowledgeNode("Node2")
        node2.set_attribute("type", "test")
        node2.set_attribute("value", 2)
        
        node3 = KnowledgeNode("Node3")
        node3.set_attribute("type", "other")
        node3.set_attribute("value", 3)
        
        # Add nodes to store
        uks.add_node(node1)
        uks.add_node(node2)
        uks.add_node(node3)
        
        # Query by type
        results = uks.query(filters={"type": "test"})
        assert len(results) == 2
        assert node1 in results
        assert node2 in results
        assert node3 not in results
        
        # Query by value
        results = uks.query(filters={"value": 2})
        assert len(results) == 1
        assert node2 in results
    
    def test_export_import(self, temp_dir):
        """Test exporting and importing the store."""
        # Create store
        uks = UniversalKnowledgeStore()
        
        # Create nodes
        node1 = KnowledgeNode("Node1")
        node1.set_attribute("type", "test")
        
        node2 = KnowledgeNode("Node2")
        node2.set_attribute("type", "test")
        
        # Add nodes to store
        uks.add_node(node1)
        uks.add_node(node2)
        
        # Add relation
        uks.add_relation(node1, "test_relation", node2)
        
        # Export store
        export_path = os.path.join(temp_dir, "uks.json")
        uks.export(export_path)
        
        # Import store
        imported_uks = UniversalKnowledgeStore.import_from(export_path)
        
        # Check imported store
        assert len(imported_uks.nodes) == len(uks.nodes)
        
        # Check nodes
        for node_id, node in uks.nodes.items():
            assert node_id in imported_uks.nodes
            imported_node = imported_uks.nodes[node_id]
            
            # Check attributes
            assert imported_node.name == node.name
            assert imported_node.attributes == node.attributes
            
            # Check relations
            assert len(imported_node.relations) == len(node.relations)
            for i, relation in enumerate(node.relations):
                assert imported_node.relations[i]["type"] == relation["type"]
                assert imported_node.relations[i]["target_id"] == relation["target_id"]
```

### Phase 2: Integration Testing Framework (1-2 weeks)

#### 2.1. Integration Test Base Class

```python
# tests/integration/base_integration_test.py
import unittest
import pytest
import os
import tempfile
from typing import Dict, Any, List, Optional, Union

class BaseIntegrationTest(unittest.TestCase):
    """Base class for all integration tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Set up common test resources
        self._setup_resources()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def _setup_resources(self):
        """Set up common test resources."""
        # Override in subclasses to set up specific resources
        pass
    
    def assert_integration_works(self, component1, component2, input_data, expected_output):
        """Assert that two components integrate correctly."""
        # Process input through component1
        intermediate_output = component1(input_data)
        
        # Process intermediate output through component2
        final_output = component2(intermediate_output)
        
        # Check final output
        self.assertEqual(expected_output, final_output)
```

#### 2.2. Sample Integration Tests

```python
# tests/integration/knowledge_models/test_knowledge_integration.py
import pytest
import torch
import os
from typing import Dict, Any

from src.model import ImpressionCoreModel, ModelConfig
from src.knowledge.uks import UniversalKnowledgeStore
from src.integration.knowledge_integration import KnowledgeIntegration

class TestKnowledgeIntegration:
    """Tests for the integration between knowledge store and models."""
    
    def test_knowledge_augmentation(self, small_model, sample_knowledge_store):
        """Test knowledge augmentation during inference."""
        # Create knowledge integration
        integration = KnowledgeIntegration(
            model=small_model,
            knowledge_store=sample_knowledge_store
        )
        
        # Create input
        input_text = "Tell me about Mars."
        input_ids = torch.tensor([[1, 2, 3, 4, 5]])  # Dummy input IDs
        attention_mask = torch.ones((1, 5))
        
        # Augment input with knowledge
        augmented_input_ids, augmented_attention_mask, metadata = integration.augment_input(
            input_ids=input_ids,
            attention_mask=attention_mask,
            input_text=input_text
        )
        
        # Check augmentation
        assert augmented_input_ids.shape[1] > input_ids.shape[1]
        assert augmented_attention_mask.shape[1] > attention_mask.shape[1]
        assert metadata["knowledge_used"] == True
        assert len(metadata["knowledge_facts"]) > 0
        
        # Check that knowledge about Mars was included
        mars_facts = [fact for fact in metadata["knowledge_facts"] 
                     if fact["subject"] == "Mars"]
        assert len(mars_facts) > 0
    
    def test_knowledge_grounded_generation(self, small_model, sample_knowledge_store):
        """Test knowledge-grounded text generation."""
        # Create knowledge integration
        integration = KnowledgeIntegration(
            model=small_model,
            knowledge_store=sample_knowledge_store
        )
        
        # Create input
        input_text = "Tell me about Mars."
        input_ids = torch.tensor([[1, 2, 3, 4, 5]])  # Dummy input IDs
        
        # Generate text with knowledge grounding
        output_ids = integration.generate(
            input_ids=input_ids,
            input_text=input_text,
            max_length=20
        )
        
        # Check output
        assert output_ids.shape[1] > input_ids.shape[1]
        
        # Get generation metadata
        metadata = integration.last_generation_metadata
        
        # Check that knowledge was used
        assert metadata["knowledge_used"] == True
        assert len(metadata["knowledge_facts"]) > 0
        
        # Check that knowledge about Mars was included
        mars_facts = [fact for fact in metadata["knowledge_facts"] 
                     if fact["subject"] == "Mars"]
        assert len(mars_facts) > 0
```

### Phase 3: System Testing Framework (1-2 weeks)

#### 3.1. System Test Base Class

```python
# tests/system/base_system_test.py
import unittest
import pytest
import os
import tempfile
import subprocess
import time
from typing import Dict, Any, List, Optional, Union

class BaseSystemTest(unittest.TestCase):
    """Base class for all system tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Set up common test resources
        self._setup_resources()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def _setup_resources(self):
        """Set up common test resources."""
        # Override in subclasses to set up specific resources
        pass
    
    def run_command(self, command: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        # Run command
        result = subprocess.run(
            command,
            cwd=cwd or self.temp_dir.name,
            capture_output=True,
            text=True
        )
        
        return result
    
    def assert_command_succeeds(self, command: List[str], cwd: Optional[str] = None):
        """Assert that a command succeeds."""
        # Run command
        result = self.run_command(command, cwd)
        
        # Check result
        self.assertEqual(result.returncode, 0, 
                        f"Command failed with error: {result.stderr}")
    
    def assert_file_exists(self, path: str):
        """Assert that a file exists."""
        self.assertTrue(os.path.exists(path), f"File does not exist: {path}")
    
    def assert_file_contains(self, path: str, content: str):
        """Assert that a file contains specific content."""
        with open(path, "r") as f:
            file_content = f.read()
        
        self.assertIn(content, file_content, 
                     f"File does not contain expected content: {content}")
```

#### 3.2. Sample System Tests

```python
# tests/system/training/test_training_workflow.py
import pytest
import os
import json
import torch
from typing import Dict, Any

class TestTrainingWorkflow:
    """Tests for the end-to-end training workflow."""
    
    def test_train_model_script(self, temp_dir):
        """Test the train_model.py script."""
        # Create test data
        data_dir = os.path.join(temp_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a small text file for training
        with open(os.path.join(data_dir, "train.txt"), "w") as f:
            f.write("This is a test document for training.\n" * 100)
        
        # Create a small text file for evaluation
        with open(os.path.join(data_dir, "eval.txt"), "w") as f:
            f.write("This is a test document for evaluation.\n" * 50)
        
        # Create output directory
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create config file
        config_path = os.path.join(temp_dir, "config.json")
        config = {
            "model": {
                "vocab_size": 1000,
                "hidden_size": 64,
                "num_hidden_layers": 2,
                "num_attention_heads": 2,
                "intermediate_size": 128,
                "max_position_embeddings": 128,
                "layer_norm_eps": 1e-12,
                "dropout": 0.1,
                "initializer_range": 0.02,
                "model_type": "impressioncore-test"
            },
            "training": {
                "batch_size": 4,
                "eval_batch_size": 4,
                "learning_rate": 5e-5,
                "num_train_epochs": 1,
                "max_steps": 10,
                "logging_steps": 2,
                "save_steps": 5,
                "output_dir": output_dir
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        # Run training script
        from examples.train_model import main
        
        # Mock command-line arguments
        import sys
        sys.argv = [
            "train_model.py",
            "--config", config_path,
            "--train_file", os.path.join(data_dir, "train.txt"),
            "--eval_file", os.path.join(data_dir, "eval.txt"),
            "--output_dir", output_dir
        ]
        
        # Run main function
        main()
        
        # Check output
        assert os.path.exists(os.path.join(output_dir, "final"))
        assert os.path.exists(os.path.join(output_dir, "final", "model.pt"))
        assert os.path.exists(os.path.join(output_dir, "final", "config.json"))
        
        # Check checkpoints
        assert os.path.exists(os.path.join(output_dir, "checkpoint-5"))
        assert os.path.exists(os.path.join(output_dir, "checkpoint-10"))
        
        # Check that model can be loaded
        from src.model import ImpressionCoreModel
        model = ImpressionCoreModel.from_pretrained(os.path.join(output_dir, "final"))
        
        # Check model attributes
        assert model.config.vocab_size == config["model"]["vocab_size"]
        assert model.config.hidden_size == config["model"]["hidden_size"]
        assert model.config.num_hidden_layers == config["model"]["num_hidden_layers"]
```

### Phase 4: Performance Testing Framework (1-2 weeks)

#### 4.1. Performance Test Base Class

```python
# tests/performance/base_performance_test.py
import unittest
import pytest
import time
import os
import tempfile
import torch
import psutil
import numpy as np
from typing import Dict, Any, List, Optional, Union, Callable

class BasePerformanceTest(unittest.TestCase):
    """Base class for all performance tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Set up common test resources
        self._setup_resources()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def _setup_resources(self):
        """Set up common test resources."""
        # Override in subclasses to set up specific resources
        pass
    
    def measure_time(self, func: Callable, *args, **kwargs) -> float:
        """Measure the execution time of a function."""
        # Warm up
        func(*args, **kwargs)
        
        # Measure time
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        
        return end_time - start_time
    
    def measure_memory(self, func: Callable, *args, **kwargs) -> Dict[str, float]:
        """Measure the memory usage of a function."""
        # Get initial memory usage
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            initial_gpu_memory = torch.cuda.memory_allocated()
        
        initial_cpu_memory = psutil.Process().memory_info().rss
        
        # Run function
        result = func(*args, **kwargs)
        
        # Get final memory usage
        final_cpu_memory = psutil.Process().memory_info().rss
        
        memory_usage = {
            "cpu_memory_mb": (final_cpu_memory - initial_cpu_memory) / (1024 * 1024)
        }
        
        if torch.cuda.is_available():
            final_gpu_memory = torch.cuda.memory_allocated()
            memory_usage["gpu_memory_mb"] = (final_gpu_memory - initial_gpu_memory) / (1024 * 1024)
        
        return memory_usage
    
    def benchmark(self, func: Callable, *args, repeat: int = 5, **kwargs) -> Dict[str, Any]:
        """Benchmark a function for time and memory usage."""
        # Measure time
        times = []
        for _ in range(repeat):
            times.append(self.measure_time(func, *args, **kwargs))
        
        # Measure memory
        memory_usage = self.measure_memory(func, *args, **kwargs)
        
        # Calculate statistics
        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        return {
            "avg_time": avg_time,
            "std_time": std_time,
            "min_time": min_time,
            "max_time": max_time,
            **memory_usage
        }
    
    def assert_performance(self, benchmark_result: Dict[str, Any], 
                          max_time: Optional[float] = None,
                          max_cpu_memory_mb: Optional[float] = None,
                          max_gpu_memory_mb: Optional[float] = None):
        """Assert that performance meets requirements."""
        if max_time is not None:
            self.assertLessEqual(benchmark_result["avg_time"], max_time, 
                               f"Average time ({benchmark_result['avg_time']:.4f}s) exceeds maximum ({max_time:.4f}s)")
        
        if max_cpu_memory_mb is not None:
            self.assertLessEqual(benchmark_result["cpu_memory_mb"], max_cpu_memory_mb, 
                               f"CPU memory usage ({benchmark_result['cpu_memory_mb']:.2f} MB) exceeds maximum ({max_cpu_memory_mb:.2f} MB)")
        
        if max_gpu_memory_mb is not None and "gpu_memory_mb" in benchmark_result:
            self.assertLessEqual(benchmark_result["gpu_memory_mb"], max_gpu_memory_mb, 
                               f"GPU memory usage ({benchmark_result['gpu_memory_mb']:.2f} MB) exceeds maximum ({max_gpu_memory_mb:.2f} MB)")
```

#### 4.2. Sample Performance Tests

```python
# tests/performance/models/test_model_performance.py
import pytest
import torch
import os
from typing import Dict, Any

from src.model import ImpressionCoreModel, ModelConfig

class TestModelPerformance:
    """Performance tests for the ImpressionCoreModel."""
    
    def test_forward_performance(self, small_model):
        """Test forward pass performance."""
        # Create input
        batch_size = 4
        seq_length = 128
        input_ids = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        attention_mask = torch.ones((batch_size, seq_length))
        
        # Define forward function
        def forward_func():
            with torch.no_grad():
                outputs = small_model(input_ids=input_ids, attention_mask=attention_mask)
                return outputs
        
        # Benchmark forward pass
        import time
        
        # Warm up
        forward_func()
        
        # Measure time
        times = []
        for _ in range(10):
            start_time = time.time()
            forward_func()
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Calculate statistics
        import numpy as np
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        # Check performance
        assert avg_time < 1.0, f"Forward pass too slow: {avg_time:.4f}s"
        
        # Measure memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated()
            forward_func()
            final_memory = torch.cuda.memory_allocated()
            memory_usage = (final_memory - initial_memory) / (1024 * 1024)  # MB
            
            # Check memory usage
            assert memory_usage < 100, f"Forward pass uses too much memory: {memory_usage:.2f} MB"
    
    def test_generate_performance(self, small_model):
        """Test text generation performance."""
        # Create input
        batch_size = 2
        seq_length = 5
        input_ids = torch.randint(0, small_model.config.vocab_size, (batch_size, seq_length))
        
        # Define generation function
        def generate_func():
            with torch.no_grad():
                generated_ids = small_model.generate(
                    input_ids=input_ids,
                    max_length=20
                )
                return generated_ids
        
        # Benchmark generation
        import time
        
        # Warm up
        generate_func()
        
        # Measure time
        times = []
        for _ in range(5):
            start_time = time.time()
            generate_func()
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Calculate statistics
        import numpy as np
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        # Check performance
        assert avg_time < 2.0, f"Generation too slow: {avg_time:.4f}s"
        
        # Measure memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated()
            generate_func()
            final_memory = torch.cuda.memory_allocated()
            memory_usage = (final_memory - initial_memory) / (1024 * 1024)  # MB
            
            # Check memory usage
            assert memory_usage < 200, f"Generation uses too much memory: {memory_usage:.2f} MB"
```

### Phase 5: Continuous Integration Setup (1 week)

#### 5.1. GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install -e .
    
    - name: Run unit tests
      run: |
        pytest tests/unit -v --cov=src --cov=core
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v
    
    - name: Run system tests
      run: |
        pytest tests/system -v
    
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
```

#### 5.2. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-requests]

-   repo: local
    hooks:
    -   id: pytest-check
        name: pytest-check
        entry: pytest tests/unit
        language: system
        pass_filenames: false
        always_run: true
```

## Implementation Plan

I'll implement this testing infrastructure in a phased approach:

### Phase 1: Unit Testing Framework (1-2 weeks)

1. Create the test directory structure
2. Implement base test classes
3. Create test fixtures
4. Implement unit tests for core components

### Phase 2: Integration Testing Framework (1-2 weeks)

1. Implement base integration test class
2. Create integration test fixtures
3. Implement integration tests for component interactions

### Phase 3: System Testing Framework (1-2 weeks)

1. Implement base system test class
2. Create system test fixtures
3. Implement system tests for end-to-end workflows

### Phase 4: Performance Testing Framework (1-2 weeks)

1. Implement base performance test class
2. Create performance test fixtures
3. Implement performance tests for critical components

### Phase 5: Continuous Integration Setup (1 week)

1. Set up GitHub Actions workflow
2. Configure pre-commit hooks
3. Set up code coverage reporting

## Success Criteria

The testing infrastructure will be considered successful when:

1. **Test Coverage**: Achieve the target test coverage for each component type
2. **Test Reliability**: Tests are reliable and do not produce false positives or negatives
3. **Test Performance**: Tests run quickly enough to be part of the development workflow
4. **Test Maintainability**: Tests are well-documented and easy to maintain
5. **Continuous Integration**: Tests are automatically run as part of the CI/CD pipeline

## Conclusion

By implementing this comprehensive testing infrastructure, we will ensure that the ImpressionCore system is reliable, maintainable, and performs as expected. This will improve the developer experience, reduce the risk of regressions, and make it easier to add new features and fix bugs.


> Deprecated and moved to archive on 2025-06-01.


> Deprecated and moved to archive on 2025-06-01.


> Deprecated and moved to archive on 2025-06-01.


> Deprecated and moved to archive on 2025-06-01.
