# Refactoring Plan v2

**Created:** July 23, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\process\refactor_plan_v2.md #api #command_line #deployment #documentation #inference #multimodal #testing #training #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This plan outlines a more robust and verifiable process for reorganizing the project's root directory.

## 1. Directory Creation

First, we will ensure all necessary destination dire### Batch 8: External Drive Files

```shell
move b3_f_drive_scan_20250710_171354.json F:\ImpressionCore_Training\scans\
move embedding_dir_listing.txt F:\ImpressionCore_Training\listings\
move Fdatasets_dir_listing.txt F:\ImpressionCore_Training\listings\
```

### Batch 9: F: Drive Root Cleanup (Completed 2025-07-24)

**F: Drive Permanent Directory Structure:**

- `F:\backup\` - All backups
- `F:\datasets\` - All data, RAW, embeddings, related training data  
- `F:\downloads\` - All downloads
- `F:\models\` - All models and checkpoints

**Files moved from F:\ root to F:\datasets\:**

```shell
move datasets_dir_listing.txt F:\datasets\
move embedding_label_mapping.csv F:\datasets\
move comprehensive_dataset_collection_report.json F:\datasets\
move enhanced_educational_dataset.json F:\datasets\
move lfw_allnames.csv F:\datasets\
move lfw_readme.csv F:\datasets\
move matchpairsDevTest.csv F:\datasets\
move matchpairsDevTrain.csv F:\datasets\
move mismatchpairsDevTest.csv F:\datasets\
move mismatchpairsDevTrain.csv F:\datasets\
move knowledge_store.db F:\datasets\
move aggregate_data_for_embedding.py F:\datasets\
move dataset_manager.py F:\datasets\
move dataset_manager_simplified.py F:\datasets\
move real_world_dataset_manager.py F:\datasets\
move simple_dataset_loader.py F:\datasets\
move complete_multimodal_data_manager.py F:\datasets\
move universal_multimodal_embedder.py F:\datasets\
move ImpressionCore_B1_Dataset_Manager.py F:\datasets\
move ImpressionCore_B1_Dataset_Manager_Fixed.py F:\datasets\
move ImpressionCore_Dataset_Analyzer_Reorganizer.py F:\datasets\
move ImpressionCore_Dataset_Verification_Agent.py F:\datasets\
move ImpressionCore_Enhanced_Dataset_Filler.py F:\datasets\
move ImpressionCore_Multimodal_Dataset_Collector.py F:\datasets\
move great_data_scraping_manager.py F:\datasets\
move great_embedding_system.py F:\datasets\
move f_drive_embedding_analyzer.py F:\datasets\
move F_Drive_Complete_Analysis_Report_20250621_173812.json F:\datasets\
move F_Drive_Complete_Multimodal_Analyzer.py F:\datasets\
move F_Drive_Embedding_Ready_Files_20250621_173812.json F:\datasets\
move ImpressionCore_Mission_Complete.py F:\datasets\
move __init__.py F:\datasets\
Remove-Item __pycache__ -Recurse -Force
```

## 3. Final Verification

After all batches are complete, we will run `list_files` on the root directory one last time to confirm that only the expected files and directories remain.

**Status Update - 2025-07-24:**

- ✅ Project root directory cleanup: COMPLETED
- ✅ F: drive root cleanup: COMPLETED  
- ✅ All loose files organized into appropriate permanent directories
- ✅ F: drive now contains only the 4 permanent directories: backup, datasets, downloads, modelsst.

```shell
mkdir src\dev_tools\analysis
mkdir src\dev_tools\data_generation
mkdir src\dev_tools\examples
mkdir src\dev_tools\fixes
mkdir src\dev_tools\migration
mkdir src\dev_tools\misc
mkdir src\dev_tools\monitoring
mkdir src\dev_tools\reporting
mkdir src\dev_tools\validation
mkdir src\scripts
mkdir src\tests
mkdir src\training
mkdir docs\reports
mkdir docs\developer
mkdir docs\technical
mkdir docs\process
mkdir docs\reference
mkdir logs\training
mkdir logs\validation
mkdir models
mkdir data
mkdir F:\ImpressionCore_Training\scans
mkdir F:\ImpressionCore_Training\listings
```

## 2. File Migration (in Batches)

We will move files in logical batches to ensure we can track progress and verify each step.

### Batch 1: Development & Analysis Scripts

```shell
move 4_phase_methodology_analysis.py src\dev_tools\analysis\
move analyze_checkpoint.py src\dev_tools\analysis\
move b3_advanced_sota_analyzer.py src\dev_tools\analysis\
move b3_comprehensive_data_analysis.py src\dev_tools\analysis\
move b3_crash_recovery_analysis.py src\dev_tools\analysis\
move f_drive_comprehensive_analyzer.py src\dev_tools\analysis\
```

### Batch 2: Data Generation Scripts

```shell
move b3_advanced_data_scraper.py src\dev_tools\data_generation\
move b3_massive_embedding_generation_final.py src\dev_tools\data_generation\
move b3_massive_embedding_generator.py src\dev_tools\data_generation\
move b3_research_driven_embedding_generator.py src\dev_tools\data_generation\
move b3_robust_resumable_generator.py src\dev_tools\data_generation\
move b3_streaming_dataset.py src\dev_tools\data_generation\
move prepare_raw_data.py src\dev_tools\data_generation\
```

### Batch 3: Example Scripts

```shell
move b1_distilled_chat_inference_proper.py src\dev_tools\examples\
move b1_distilled_chat_inference.py src\dev_tools\examples\
move b1_gpt2_chat_inference.py src\dev_tools\examples\
move b1_native_chat_inference.py src\dev_tools\examples\
move b1_simple_working_chat.py src\dev_tools\examples\
move b2_simple_chat.py src\dev_tools\examples\
move b3_model_demo.py src\dev_tools\examples\
move demo_embedding_discovery.py src\dev_tools\examples\
```

### Batch 4: Miscellaneous `dev_tools` Scripts

```shell
move classification_fix_explanation.py src\dev_tools\fixes\
move b3_b2_migration_system.py src\dev_tools\migration\
move celebrate_completion.py src\dev_tools\misc\
move b3_generation_monitor.py src\dev_tools\monitoring\
move monitor_b2_distillation_training.py src\dev_tools\monitoring\
move b3_completion_report.py src\dev_tools\reporting\
move b3_comprehensive_status_report.py src\dev_tools\reporting\
move b3_enterprise_completion_final.py src\dev_tools\reporting\
move generate_b2_status_report.py src\dev_tools\reporting\
move generate_phase1_completion_report.py src\dev_tools\reporting\
move b3_comprehensive_status_check.py src\dev_tools\validation\
move b3_critical_success_final.py src\dev_tools\validation\
move b3_embedding_verification_system.py src\dev_tools\validation\
move b3_final_verification_system.py src\dev_tools\validation\
move b3_phase1_deployment_verification.py src\dev_tools\validation\
move b3_phase2_readiness_verification.py src\dev_tools\validation\
move b3_validation_system.py src\dev_tools\validation\
move post_restart_b3_validator.py src\dev_tools\validation\
move b3_f_drive_scanner.py src\dev_tools\
move b3_implementation_manager.py src\dev_tools\
move b3_precision_enhancement_system.py src\dev_tools\
move b3_sota_enhancement_system.py src\dev_tools\
move mock_api_server.py src\dev_tools\
move prepare_b2_phase2.py src\dev_tools\
move update_phase_structure.py src\dev_tools\
```

### Batch 5: Interface, Training, Test, and Deployment Scripts

```shell
move b2_enhanced_chat_interface.py src\interfaces\cli\
move impressioncore_b2_chat_interface.py src\interfaces\cli\
move impressioncore_b2_enhanced_chat.py src\interfaces\cli\
move b3_full_embedded_initialization.py src\training\
move b3_full_embedding_training.py src\training\
move b3_phase1_enhanced.py src\training\
move b3_phase1_full_embedding_integration.py src\training\
move b3_real_implementation.py src\training\
move b3_streaming_training.py src\training\
move execute_distillation_training.py src\training\
move execute_enhanced_training.py src\training\
move execute_training_pipeline.py src\training\
move launch_enhanced_b2_training.py src\training\
move launch_enhanced_training.py src\training\
move launch_phase4_training.py src\training\
move phase1_b3_training_launcher.py src\training\
move phase1_embedding_system.py src\training\
move phase1_enhanced_embedding_system.py src\training\
move phase3_local_distillation.py src\training\
move phase4_production_trainer.py src\training\
move phase4_remote_api_distillation.py src\training\
move phase4_simplified.py src\training\
move quickstart_enhanced_training.py src\training\
move setup_b2_fixed_training.py src\training\
move setup_b2_scaled_training.py src\training\
move setup_raw_data_training_corrupted_20250708_170555.py src\training\
move setup_raw_data_training_simple.py src\training\
move setup_raw_data_training_with_timeouts.py src\training\
move setup_raw_data_training.py src\training\
move setup_ultra_lightweight_training.py src\training\
move train_b2_enhanced_optimized.py src\training\
move test_and_deploy_b1_distilled.py src\tests\
move test_b2_fixed_inference.py src\tests\
move test_b3_final.py src\tests\
move test_b3_initialization.py src\tests\
move test_b3_streaming_system.py src\tests\
move test_dataloader.py src\tests\
move test_enhanced_b2.py src\tests\
move test_enhanced_model_loading.py src\tests\
move test_imports.py src\tests\
move test_optimizations.py src\tests\
move test_phase_update.py src\tests\
move test_safetensors_fix.py src\tests\
move test_ultra_lightweight_inference.py src\tests\
move test_vrgc_system.py src\tests\
move convert_to_production_model.py src\deployment\
move create_deployment_package.py src\deployment\
move deploy_impressioncore_b2_fixed.py src\deployment\
move deploy_impressioncore_b2.py src\deployment\
move deployment_summary.py src\deployment\
move phase4_production_api_setup.py src\deployment\
move validate_deployment.py src\deployment\
```

### Batch 6: Shell Scripts, Documentation, and Log Files

```shell
move run_b2_enhanced_training.sh src\scripts\
move run_b3_full_training.py src\scripts\
move run_b3_phase1_full.py src\scripts\
move run_b3_phase1_part2_enhanced_training.py src\scripts\
move run_b3_phase1b_gap_analysis.py src\scripts\
move run_embedding_and_training_pipeline.py src\scripts\
move run_phase1_automation.py src\scripts\
move run_phase1_init.py src\scripts\
move run_phase1_optimize.py src\scripts\
move B2_DISTILLATION_IMPLEMENTATION_SUMMARY.md docs\reports\
move B3_ARCHITECTURE_ANALYSIS_REPORT.md docs\reports\
move B3_FINAL_IMPLEMENTATION_SUMMARY.md docs\reports\
move B3_REAL_IMPLEMENTATION_SUMMARY.md docs\reports\
move B3_SCALABILITY_ANALYSIS_REPORT.md docs\reports\
move B3_SCALABILITY_ANALYSIS_REVISED.md docs\reports\
move comprehensive_analysis_b3.md docs\reports\
move DEPLOYMENT_SUMMARY.md docs\reports\
move FINAL_COMPLETION_SUMMARY.md docs\reports\
move IMPRESSIONCORE_B2_COMPLETION_REPORT.md docs\reports\
move PROJECT_COMPLETION_REPORT.md docs\reports\
move B3_FINAL_LAUNCH_COMMANDS.md docs\developer\
move B3_FULL_EMBEDDING_TRAINING_STRATEGY.md docs\technical\
move B3_STREAMING_ENHANCEMENT_PLAN.md docs\technical\
move B3_IMPLEMENTATION_ROADMAP.md docs\process\
move B3_Update_Implementation_Roadmap.md docs\process\
move Google_Search_Operators.md docs\reference\
move b3_full_embedded_run.log logs\training\
move b3_full_embedding_training.log logs\training\
move b3_real_training.log logs\training\
move b3_validation.log logs\validation\
move ids_maintenance.log logs\
move web_search_mcp.log logs\
```

### Batch 7: Model, Data, and Config Files

```shell
move b2_phase1_init_config.yaml configs\
move impressioncore_b2_production_20250709_132629.zip deployment\
move dummy.txt data\
move dummy.vocab data\
move streaming_test_results.json data\
move training_metadata.json data\
move vector_database.db data\
move verify_results.txt data\
```

### Batch 8: External Drive Files

```shell
move b3_f_drive_scan_20250710_171354.json F:\ImpressionCore_Training\scans\
move embedding_dir_listing.txt F:\ImpressionCore_Training\listings\
move Fdatasets_dir_listing.txt F:\ImpressionCore_Training\listings\
```

## 3. Final Verification

After all batches are complete, we will run `list_files` on the root directory one last time to confirm that only the expected files and directories remain.
