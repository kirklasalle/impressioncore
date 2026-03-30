# SRC Relocation Plan (Generated August 23, 2025)

Purpose: Track movement of loose top-level scripts into structured packages.

| Original File | Target Package | New Path | Status |
|---------------|----------------|----------|--------|
| generate_openai_embeddings.py | tools/cli | tools/cli/generate_openai_embeddings.py | done |
| impressioncore_b1_cli.py | archive/interfaces/cli | archive/interfaces/cli/impressioncore_b1_cli.py | archived |
| build_kd_dataset.py | training/distillation/datasets | training/distillation/datasets/build_kd_dataset.py | done |
| build_openai_faiss_index.py | data/embeddings/index | data/embeddings/index/build_openai_faiss_index.py | done |
| chunk_large_text.py | core/utils | core/utils/chunk_large_text.py | done |
| convert_teacher_outputs.py | training/distillation/processing | training/distillation/processing/convert_teacher_outputs.py | done |
| demo_gpu_knowledge_distillation_revolution.py | training/distillation/demos | training/distillation/demos/gpu_kd_demo.py | done |
| launch_gpu_knowledge_distillation_revolution.py | training/launch | training/launch/launch_gpu_kd_revolution.py | done |
| production_inference.py | inference/runtime | inference/runtime/production_inference.py | done |
| reorganize_media_to_raw_pipeline.py | training/pipelines/media | training/pipelines/media/reorganize_media_to_raw_pipeline.py | done |
| verify_pipeline_readiness.py | training/pipelines/validation | training/pipelines/validation/verify_pipeline_readiness.py | done |
| b1_enhanced_training_executor.py | archive/training | archive/training/b1_enhanced_training_executor.py | archived |
| b2_multimodal_model.py | archive/models/b2_multimodal/core | archive/models/b2_multimodal/core/b2_multimodal_model.py | archived |
| filters.py | training/distillation/processing | training/distillation/processing/filters.py | done |
| metrics.py | evaluation/metrics | evaluation/metrics/best_model_tracker.py | done |
| b3_streaming_dataset.py | dev_tools/data_generation | dev_tools/data_generation/b3_streaming_dataset.py | done |
| b3_streaming_training.py | training | training/b3_streaming_training.py | done |
| b3_embeddings_analysis.csv | data/reports | data/reports/b3_embeddings_analysis.csv | done (relocated August 24, 2025) |
<!-- Duplicate rows removed above during normalization -->

Policy (updated): Perform direct physical moves only. No deprecation shims. Update imports in codebase as encountered.

This file is auto-maintained by organizational tasks; edit with care.
| eval | . | evaluation | done | batch move August 23, 2025 - merge eval into evaluation (module consolidation) |
| config | core | core\config | done | batch move August 23, 2025 - centralize configuration |
| management | core | core\management | done | batch move August 23, 2025 - centralize management utilities |
| integrity | core | core\integrity | done | batch move August 23, 2025 - centralize integrity checks |
| tokenization | core | core\tokenization | done | batch move August 23, 2025 - shared tokenization components |
| brainsim | core | core\brainsim | done | batch move August 23, 2025 - brain simulation under core |
| curriculum | training | training\curriculum | done | batch move August 23, 2025 - training curriculum organization |
| distillation | training | training\distillation | done | batch move August 23, 2025 - distillation processes |
| pipelines | training | training\pipelines | done | batch move August 23, 2025 - training oriented pipelines |
| processors | data | data\processors | done | batch move August 23, 2025 - dataset-focused processors |
| embeddings | data | data\embeddings | done | batch move August 23, 2025 - embedding assets |
| model_analysis | evaluation | evaluation\model_analysis | done | batch move August 23, 2025 - model analysis relocation |
| modules | core | core\modules | done | batch move August 23, 2025 - generic building blocks |
| analysis | evaluation | evaluation\analysis | done | batch move August 23, 2025 - evaluation analysis components |
| scripts | dev_tools | dev_tools\scripts | done | batch move August 23, 2025 - developer scripts |
| examples | . | examples | done | batch move August 23, 2025 - examples kept at top-level |
| educational_materials_inventory.txt | docs\reports | docs\reports\educational_materials_inventory.txt | done | batch move August 23, 2025 - report relocation |
| F_DRIVE_CAMPAIGN_SUMMARY_20250731_165527.txt | docs\reports | docs\reports\F_DRIVE_CAMPAIGN_SUMMARY_20250731_165527.txt | done | batch move August 23, 2025 - report relocation |
| f_drive_current_structure.txt | docs\reports | docs\reports\f_drive_current_structure.txt | done | batch move August 23, 2025 - report relocation |
| f_drive_data_structure.txt | docs\reports | docs\reports\f_drive_data_structure.txt | done | batch move August 23, 2025 - report relocation |
| f_drive_detailed_analysis.txt | docs\reports | docs\reports\f_drive_detailed_analysis.txt | done | batch move August 23, 2025 - report relocation |
| f_drive_directories.txt | docs\reports | docs\reports\f_drive_directories.txt | done | batch move August 23, 2025 - report relocation |
| kd_dataset.jsonl | data\datasets\metadata | data\datasets\metadata\kd_dataset.jsonl | done | batch move August 23, 2025 - dataset metadata relocation |
| sample_teachers.jsonl | data\datasets\metadata | data\datasets\metadata\sample_teachers.jsonl | done | batch move August 23, 2025 - dataset metadata relocation |
| smart_acquisition_readable.txt | data\reports | data\reports\smart_acquisition_readable.txt | done | batch move August 23, 2025 - data acquisition reference |
| ollama_generate.py | training/distillation/teachers | training/distillation/teachers/ollama_generate.py | done |
