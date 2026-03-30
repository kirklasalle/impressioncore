# Code Organization Refactoring Plan

## Current Structure Issues

After analyzing the current project structure, I've identified several inconsistencies between the actual implementation and the documented architecture:

1. **Multiple Code Bases**: Code is spread across `src/`, `core/`, `impressioncore/`, and `brainsim/` directories, creating confusion about the primary codebase.

2. **Inconsistent Module Locations**:
   - UKS implementation exists in both `src/knowledge/uks.py` and `impressioncore/knowledge/uks.py`
   - BrainSim exists in both `brainsim/` and `src/core/brainsim/`
   - Model implementations are in both `src/models/` and `core/`

3. **Mixed Language Implementation**: The project contains both Python (`.py`) and TypeScript (`.ts`) files without clear separation.

4. **Duplicated Functionality**: Similar functionality appears to be implemented in multiple places (e.g., model training in both `src/training/` and `core/trainer.py`).

## Refactoring Goals

1. Establish a clear, consistent project structure
2. Eliminate duplication and consolidate related functionality
3. Ensure imports and references work correctly
4. Maintain backward compatibility where possible
5. Improve discoverability and maintainability

## Proposed Directory Structure

Based on the README and the actual implementation, I propose the following consolidated structure:

```
impressioncore/
├── src/                           # Main source code
│   ├── core/                      # Core components
│   │   ├── modal_engine.py        # Central processing engine
│   │   ├── brainsim/              # BrainSim integration
│   │   ├── cognitive/             # Cognitive architecture
│   │   └── multimodal/            # Multimodal processing
│   ├── knowledge/                 # Knowledge representation
│   │   ├── uks.py                 # Universal Knowledge Store
│   │   ├── node.py                # Knowledge node implementation
│   │   ├── rule_engine.py         # Rule-based reasoning
│   │   └── visualization.py       # Knowledge visualization
│   ├── models/                    # Model implementations
│   │   ├── transformer/           # Transformer model implementation
│   │   ├── diffusion/             # Diffusion model for image generation
│   │   └── dual_shadow.py         # Dual shadow model framework
│   ├── training/                  # Training components
│   │   ├── trainer.py             # Main trainer implementation
│   │   ├── experience_replay.py   # Experience replay for continuous learning
│   │   └── metrics/               # Training metrics
│   ├── utils/                     # Utility functions
│   │   ├── gpu_utils.py           # GPU memory management
│   │   ├── checkpoint_utils.py    # Checkpoint handling
│   │   └── config.py              # Configuration management
│   └── api/                       # API endpoints
├── tests/                         # Test suite
├── examples/                      # Example scripts
├── docs/                          # Documentation
├── scripts/                       # Utility scripts
└── memlog/                        # Logging and persistence
    ├── state/                     # System state logs
    ├── tasks/                     # Task tracking
    ├── persistence/               # Persistent data storage
    └── changelogs/                # System changes
```

## Migration Plan

### Phase 1: Consolidate Core Components

1. **Create Unified Structure**:
   - Create the directory structure outlined above
   - Ensure all directories have proper `__init__.py` files

2. **Migrate Universal Knowledge Store**:
   - Consolidate `src/knowledge/uks.py` and `impressioncore/knowledge/uks.py`
   - Update imports in all files referencing UKS
   - Ensure all functionality is preserved

3. **Consolidate BrainSim Integration**:
   - Move `brainsim/` core files to `src/core/brainsim/`
   - Update imports and references
   - Maintain backward compatibility with existing code

### Phase 2: Consolidate Model and Training Code

1. **Unify Model Implementation**:
   - Consolidate model code from `core/model.py` and `src/models/`
   - Ensure all model variants and configurations are preserved
   - Update imports and references

2. **Unify Training Implementation**:
   - Consolidate training code from `core/trainer.py` and `src/training/`
   - Preserve all training options and configurations
   - Update imports and references

### Phase 3: Address Language Inconsistencies

1. **TypeScript Components**:
   - Move TypeScript files to a dedicated `web/` or `frontend/` directory
   - Ensure clear separation between Python backend and TypeScript frontend
   - Update build scripts and configuration

2. **Create Language Bridges**:
   - Implement clear API boundaries between Python and TypeScript code
   - Document interaction patterns between different language components

### Phase 4: Update Documentation and Tests

1. **Update Documentation**:
   - Revise README to reflect the new structure
   - Update import examples and code snippets
   - Create architecture diagrams showing component relationships

2. **Update Tests**:
   - Ensure all tests work with the new structure
   - Add tests for previously untested components
   - Implement continuous integration to verify structure integrity

## Implementation Approach

### Step 1: Create Structure Mapping

Create a detailed mapping of current files to their new locations:

```python
STRUCTURE_MAPPING = {
    "src/knowledge/uks.py": "impressioncore/src/knowledge/uks.py",
    "impressioncore/knowledge/uks.py": "impressioncore/src/knowledge/uks.py",
    "core/model.py": "impressioncore/src/models/transformer/model.py",
    # ... additional mappings
}
```

### Step 2: Create Migration Script

Develop a migration script that:

1. Creates the new directory structure
2. Copies files to their new locations
3. Updates imports in all files
4. Verifies that the new structure works correctly

### Step 3: Implement Backward Compatibility

Create compatibility layers to ensure existing code continues to work:

1. Add import redirects in old locations
2. Create compatibility modules that re-export from new locations
3. Document deprecation timelines for old import paths

### Step 4: Testing Strategy

1. Create a comprehensive test suite that verifies:
   - All modules can be imported correctly
   - All functionality works as expected
   - Examples run successfully with the new structure

2. Run tests in both the old and new structures to ensure compatibility

## Risk Mitigation

1. **Backup**: Create a complete backup of the current codebase before starting
2. **Incremental Approach**: Implement changes in small, testable increments
3. **Version Control**: Use feature branches and pull requests for each phase
4. **Continuous Testing**: Run tests after each significant change
5. **Documentation**: Document all changes and provide migration guides for users

## Timeline

- **Phase 1 (Consolidate Core Components)**: 1 week
- **Phase 2 (Consolidate Model and Training Code)**: 1 week
- **Phase 3 (Address Language Inconsistencies)**: 3 days
- **Phase 4 (Update Documentation and Tests)**: 3 days

Total estimated time: 2.5 weeks

## Success Criteria

The refactoring will be considered successful when:

1. All code is organized according to the proposed structure
2. All tests pass in the new structure
3. All examples run successfully
4. Documentation accurately reflects the new structure
5. No functionality is lost or broken
6. The codebase is more maintainable and easier to navigate
