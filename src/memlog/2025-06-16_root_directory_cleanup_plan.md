# Root Directory Cleanup Plan - June 16, 2025

**Date:** June 16, 2025  
**Task:** Root Directory Organization & Cleanup  
**Priority:** HIGH - File Integrity & Project Organization  
**Responsible:** GitHub Copilot  
**Reference:** Documentation Index & IDS System Analysis  

## Current Issues Identified

### Root Directory Problems
- **Scattered Script Files:** Multiple .py files in root that should be in appropriate directories
- **Temporary Analysis Files:** JSON analysis files and logs cluttering root
- **Multiple Backup Directories:** Backup folders mixed with main project files  
- **Version Files:** Orphaned version files (=2.6.0, =3.7.0)
- **Cache Directories:** __pycache__ in root directory

## PROPER ORGANIZATIONAL STRUCTURE (Based on IDS Documentation)

### Established Directory Structure (Per Documentation Index)
```
src/
├── assistant/           # AI assistant functionality
├── benchmarks/          # Performance evaluation
├── core/               # Core system components
├── deployment/         # Deployment and packaging
├── dev_tools/          # Development utilities
├── interfaces/         # User interface components
├── memlog/            # System memory and logging
├── modules/           # Modular components
├── services/          # External service integrations
├── tests/             # Testing infrastructure
├── training/          # Model training and optimization
└── user_data/         # User-specific data and configurations

docs/
├── api/               # API documentation
├── developer/         # Developer documentation
├── process/           # Process documentation and roadmaps
├── reference/         # Technical specifications
├── reports/           # Analysis and status reports
├── strategic/         # Strategic vision documents
├── technical/         # Technical implementation docs
└── user/             # User guides and tutorials
```

## FILES TO ORGANIZE

### Scripts to Move to src/dev_tools/
- analyze_storage.py → src/dev_tools/
- backup_model_loading_fix_files.py → src/dev_tools/
- create_backup.py → src/dev_tools/
- create_comprehensive_dataset.py → src/dev_tools/data_generation/
- demo_high_school_training.py → src/dev_tools/examples/
- enhanced_backup_and_monitor.py → src/dev_tools/
- fix_emojis.py → src/dev_tools/fixes/
- fix_imports.py → src/dev_tools/fixes/
- high_school_graduate_trainer.py → src/dev_tools/training/
- test_clip_fix.py → src/dev_tools/tests/
- test_environment.py → src/dev_tools/tests/
- test_trainer_clip_fix.py → src/dev_tools/tests/
- verify_backup.py → src/dev_tools/

### Data Files to Move to F: Drive Training Storage
- enhanced_high_school_training_data.json → F:\ImpressionCore_Training\datasets\custom\
- high_school_graduate_dataset.json → F:\ImpressionCore_Training\datasets\custom\
- high_school_training_data.json → F:\ImpressionCore_Training\datasets\custom\
- world_class_high_school_dataset.json → F:\ImpressionCore_Training\datasets\custom\

**Note:** F: drive (476GB dedicated ImpressionCore training drive) is the established storage location for all datasets and models per the training storage infrastructure.

### Analysis Files to Move to docs/reports/
- embedding_status_analysis_20250611_185056.json → docs/reports/
- embedding_status_analysis_20250611_191259.json → docs/reports/
- embedding_status_analysis_20250612_082329.json → docs/reports/

### Log Files to Move to src/memlog/
- ids_maintenance.log → src/memlog/
- training_10_quality.log → src/memlog/

### Files to Remove
- =2.6.0 (orphaned version file)
- =3.7.0 (orphaned version file)
- __pycache__/ (should be in .gitignore)

### Backup Directory Consolidation
- Consolidate backup_* directories into backup/ with proper timestamping
- Maintain backup_manifest.md for reference

## Expected Final Root Directory Structure

```
d:\Projects\impressioncore\
├── .git/
├── .github/
├── .mcp/
├── .venv310/
├── .vscode/
├── backup/ (consolidated backup directory)
├── docs/
├── src/
├── CONTRIBUTING.md
├── COPILOT_PRIME_DIRECTIVE.md
├── COPILOT_SACRED_COVENANT.md
├── MODEL_LOADING_FIX_QUICK_REFERENCE.md
├── README.md
├── SYSTEM_STATUS_FINAL.md
├── backup_manifest.md
├── install_sentencepiece.bat
├── main.py (main entry point)
├── mvp_launcher.py (main launcher)
├── refresh_ids.bat
├── requirements.txt
└── setup.py
```

## CLEANUP ACTIONS PLAN

### Phase 1: Verify F: Drive Training Storage Structure
1. Confirm F:\ImpressionCore_Training\datasets\custom\ exists
2. Verify all other directories exist per structure

### Phase 2: Move Files to Proper Locations
1. Move development scripts to src/dev_tools/ subdirectories
2. Move data files to F:\ImpressionCore_Training\datasets\custom\
3. Move analysis files to docs/reports/
4. Move log files to src/memlog/

### Phase 3: Consolidate Backup Directories
1. Review backup directories for essential content
2. Consolidate into single backup/ directory with timestamps
3. Update backup_manifest.md

### Phase 4: Remove Orphaned Files
1. Remove version files (=2.6.0, =3.7.0)
2. Remove __pycache__ directory
3. Update .gitignore if needed

### Phase 5: Validation
1. Update IDS documentation index
2. Run system validation tests
3. Document changes in memlog

This organization follows the established ImpressionCore project structure as documented in the IDS system.
