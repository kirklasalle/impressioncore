# ##########################################################################

# ##########################################################################

GitHub Copilot: # ImpressionCore Workspace Analysis ESSENTIALS

## Directory Structure Overview - ESSENTIALS

### docs Directory

- **Purpose**: Project documentation
- **Contents**:
  - `prd.md`: Product Requirements Document (general app specification)
  - `development_roadmap.md`: Development timeline with phases and milestones
  - `modal-engine.md`: Technical specifications for the Modal Engine architecture
  - `training-pipeline.md`: Documentation on the training process
  - third-party-libraries.md: External dependencies documentation

### brainsim3 Directory

- **Purpose**: BrainSimulator III integration and UKS implementation
- **Contents**:
  - `BrainSimulator/`: Core simulation engine
    - `Modules/`: Functional components
      - `ModuleUKS.cs` and related files (Query, Statement, File)
      - ModuleUKSDlg.xaml.cs: User interface for UKS
      - `Relationship.cs`: Relationship implementation for knowledge graph
      - `Thing.cs`: Node implementation for knowledge graph
    - Utils.cs: Common utility functions
    - Doxyfile: Documentation generation configuration
  - `UKS/`: Universal Knowledge Store implementation
    - `UKS.File.cs`: File handling for knowledge store
    - `Documentation/`: Generated code documentation (HTML)
    - Doxyfile: UKS documentation configuration

### src Directory

- **Purpose**: Main source code for ImpressionCore
- **Contents**:
  - `pipeline/`: Processing pipelines
    - `main.py`: Entry point for modal engine
  - models: Model implementations
    - `model.py`: Transformer model architecture
  - `preprocessing/`: Data preparation modules
    - `text_processor.py`: Text input processing
    - `image_processor.py`: Image input processing
    - `audio_processor.py`: Audio input processing
    - `multimodal_aligner.py`: Cross-modal data alignment

### core Directory

- **Purpose**: Core ImpressionCore framework
- **Contents**:
  - `model.py`: Core model implementation with transformer architecture
  - `config.py`: Configuration system for model parameters and resources

### Root Directory Files

- .gitignore: Source control exclusions
- README.md: Project overview and setup instructions
- Example files: Demonstration code including advanced_feature_demo.py

## Project Status

The project is currently in Phase 2 (Advanced Features) of development according to the roadmap, with completed milestones for UKS and BrainSimIII integration. Current focus is on enhancing multimodal processing capabilities and implementing transformer-based feature extraction.

- Additionally, the token rate control module (src/token_rate_control.ts) is active to ensure requests adhere to the 35,000 tokens/minute limit.

# ##########################################################################

# ##########################################################################

# ##########################################################################

GitHub Copilot: # ImpressionCore Workspace Analysis - Complete Directory Structure

## Root Directory Structure Overview

### docs Directory

- **Purpose**: Project documentation
- **Key Files**: `prd.md`, `development_roadmap.md`, `modal-engine.md`, `training-pipeline.md`

### src Directory

- **Purpose**: Main source code
- **Subdirectories**: `pipeline`, models, `preprocessing`

### core Directory  

- **Purpose**: Core framework implementation
- **Key Files**: `model.py`, `config.py`

### brainsim3 Directory

- **Purpose**: BrainSimulator III integration
- **Subdirectories**: `BrainSimulator`, `UKS`

### examples Directory

- **Purpose**: Example implementations and demos
- **Key Files**: `advanced_feature_demo.py`

### tests Directory

- **Purpose**: Unit and integration tests
- **Subdirectories**: Test modules for different components

### data Directory

- **Purpose**: Training and evaluation datasets
- **Subdirectories**: Organized by data type/domain

### `/tools` Directory

- **Purpose**: Utility scripts and development tools
- **Key Files**: Helper scripts for development workflows

### `/configs` Directory

- **Purpose**: Configuration files
- **Key Files**: Model configurations, training parameters

### models Directory

- **Purpose**: Pretrained model checkpoints
- **Subdirectories**: Organized by model version/type

### `/notebooks` Directory

- **Purpose**: Jupyter notebooks for experiments
- **Key Files**: Research and development notebooks

### scripts Directory

- **Purpose**: Automation scripts
- **Key Files**: Training, evaluation, and deployment scripts

### `/api` Directory

- **Purpose**: API implementation
- **Key Files**: Endpoints and service definitions

### `/utils` Directory

- **Purpose**: Shared utility functions
- **Key Files**: Common helper functions

### `/ui` Directory

- **Purpose**: User interface components
- **Subdirectories**: Web, desktop interfaces

### `/deployment` Directory

- **Purpose**: Deployment configurations
- **Key Files**: Docker, cloud configurations

### `/logs` Directory

- **Purpose**: Application and training logs
- **Organization**: Date-based log storage

### `/third_party` Directory

- **Purpose**: External dependencies
- **Subdirectories**: Organized by library/framework

### `/evaluation` Directory

- **Purpose**: Evaluation metrics and tools
- **Key Files**: Benchmarking scripts, evaluation datasets

### `/research` Directory

- **Purpose**: Research experiments and papers
- **Key Files**: Experimental implementations, research notes

### `/docs-api` Directory

- **Purpose**: API documentation
- **Key Files**: Generated API references

### Additional Root-Level Files

- README.md: Project overview
- `.gitignore`: Source control exclusion patterns
- requirements.txt: Python dependencies
- setup.py: Package installation configuration
- `LICENSE`: Project license information
- `CONTRIBUTING.md`: Contribution guidelines

Note: This is a comprehensive mapping of the directory structure based on the project's architecture. The specific content and organization may vary within each directory.
