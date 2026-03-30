# Project TODO List

**Created:** May 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\project_todos.md #api #attention_mechanism #documentation #memory_management #tokenization #training #web_interface  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Generated: 2025-05-25 09:43:49
Last updated: 2025-05-31
Responsible: @GitHubCopilot

This list is automatically extracted from TODO comments in the codebase.

## High Priority

- **Fix this bug**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 269

## Medium Priority

- **Implement API connection logic**
  - `File`: src\core\integration\brainsim_adapter.py
  - `Line`: 135

- **Implement embedded mode logic**
  - `File`: src\core\integration\brainsim_adapter.py
  - `Line`: 140

- **Implement API call logic**
  - `File`: src\core\integration\brainsim_adapter.py
  - `Line`: 197

- **Implement embedded call logic**
  - `File`: src\core\integration\brainsim_adapter.py
  - `Line`: 202

- **Add code to save or visualize the generated_samples tensor**
  - `File`: src\diffusion\generator.py
  - `Line`: 309

- **Implement node removal in UKS**
  - `File`: src\knowledge\document_store.py
  - `Line`: 236

- **Integrate xFormers or custom efficient attention**
  - `File`: src\models\architectures\impressioncore_b1.py
  - `Line`: 75

- **detect_low_vram_system and log_memory_usage are not defined in hardware_detection.py**
  - `File`: src\models\memory_controller.py
  - `Line`: 65

- **Implement feature**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 270

- **Auto-detect or allow manual input**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 348

- **Add a brief description of this file's purpose.**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 352

- **Add design philosophy if applicable.**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 355

- **Document any specific memory considerations for this file.**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 358

- **Provide usage examples if applicable.**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 361

- **Add any relevant notes.**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 364

- **Add docstring enhancement logic here**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 446

- **More detailed stats for functions/classes**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 531

- **Add function/class level docstring stats if _find_missing_docstrings is used to populate more detailed stats**
  - `File`: src\scripts\documentation\enhance_code_docs.py
  - `Line`: 594

- **Replace with actual dataset loading (e.g., images, text embeddings)**
  - `File`: src\training\train_diffusion.py
  - `Line`: 115

- **Save settings to user's configuration**
  - `File`: src\user_data\web\server.py
  - `Line`: 1280

- **Load user's settings**
  - `File`: src\user_data\web\server.py
  - `Line`: 1283

- **Fetch user's API keys from database**
  - `File`: src\user_data\web\server.py
  - `Line`: 1606

- **Save API key to database**
  - `File`: src\user_data\web\server.py
  - `Line`: 1633

- **Remove API key from database**
  - `File`: src\user_data\web\server.py
  - `Line`: 1660

- **Implement activity log page**
  - `File`: src\user_data\web\server.py
  - `Line`: 1707

- **Implement actual model creation logic**
  - `File`: src\user_data\web\server.py
  - `Line`: 1844

- **Replace with actual architecture retrieval logic**
  - `File`: src\user_data\web\server.py
  - `Line`: 2010

- **Get list of uploaded files relevant to this training session**
  - `File`: src\user_data\web\server.py
  - `Line`: 2230

- **Implement secure download logic**
  - `File`: src\user_data\web\server.py
  - `Line`: 2336

- **Save settings to user's configuration**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\user_data\web\server2.py
  - `Line`: 1603

- **Save settings to user's configuration**
  - `File`: src\user_data\web\server_bak.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\user_data\web\server_bak.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\user_data\web\server_bak.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\user_data\web\server_bak.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\user_data\web\server_bak.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\web\server_bak.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\web\server_bak.py
  - `Line`: 1603

- **Implement detailed module graph creation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 272

- **Implement memory profile estimation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 358

- **Implement memory profile visualization**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 493

- **Implement model-specific attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 196

- **Implement model-specific all-layer attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 231

- **Implement attention flow visualization logic**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 288

- **Implement proper cross-attention visualization**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 313

- **Implement model-specific hook registration based on model type**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 252

- **Implement layer activation extraction**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 284

- **Implement model graph creation**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 299

- **Implement proper layout and styling for the graph plot**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 364

- **Replace with actual data collection from models**
  - `File`: src\web\routes\metrics.py
  - `Line`: 71

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 216

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 294

- **Save settings to user's configuration**
  - `File`: src\web\server.py
  - `Line`: 1505

- **Load user's settings**
  - `File`: src\web\server.py
  - `Line`: 1508

- **Fetch user's API keys from database**
  - `File`: src\web\server.py
  - `Line`: 1831

- **Save API key to database**
  - `File`: src\web\server.py
  - `Line`: 1858

- **Remove API key from database**
  - `File`: src\web\server.py
  - `Line`: 1885

- **Implement activity log page**
  - `File`: src\web\server.py
  - `Line`: 1932

- **Implement actual model creation logic**
  - `File`: src\web\server.py
  - `Line`: 2069

- **Replace with actual architecture retrieval logic**
  - `File`: src\web\server.py
  - `Line`: 2235

- **Get list of uploaded files relevant to this training session**
  - `File`: src\web\server.py
  - `Line`: 2455

- **Implement secure download logic**
  - `File`: src\web\server.py
  - `Line`: 2561

- **Save settings to user's configuration**
  - `File`: src\web\server2.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\web\server2.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\web\server2.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\web\server2.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\web\server2.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\web\server2.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\web\server2.py
  - `Line`: 1603

- **Save settings to user's configuration**
  - `File`: src\web\server_bak.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\web\server_bak.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\web\server_bak.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\web\server_bak.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\web\server_bak.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\web\server_bak.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\web\server_bak.py
  - `Line`: 1603

- **Implement detailed module graph creation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 272

- **Implement memory profile estimation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 358

- **Implement memory profile visualization**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 493

- **Implement model-specific attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 196

- **Implement model-specific all-layer attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 231

- **Implement attention flow visualization logic**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 288

- **Implement proper cross-attention visualization**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 313

- **Implement model-specific hook registration based on model type**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 252

- **Implement layer activation extraction**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 284

- **Implement model graph creation**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 299

- **Implement proper layout and styling for the graph plot**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 364

- **Replace with actual data collection from models**
  - `File`: src\web\routes\metrics.py
  - `Line`: 71

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 216

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 294

- **Save settings to user's configuration**
  - `File`: src\web\server.py
  - `Line`: 1505

- **Load user's settings**
  - `File`: src\web\server.py
  - `Line`: 1508

- **Fetch user's API keys from database**
  - `File`: src\web\server.py
  - `Line`: 1831

- **Save API key to database**
  - `File`: src\web\server.py
  - `Line`: 1858

- **Remove API key from database**
  - `File`: src\web\server.py
  - `Line`: 1885

- **Implement activity log page**
  - `File`: src\web\server.py
  - `Line`: 1932

- **Implement actual model creation logic**
  - `File`: src\web\server.py
  - `Line`: 2069

- **Replace with actual architecture retrieval logic**
  - `File`: src\web\server.py
  - `Line`: 2235

- **Get list of uploaded files relevant to this training session**
  - `File`: src\web\server.py
  - `Line`: 2455

- **Implement secure download logic**
  - `File`: src\web\server.py
  - `Line`: 2561

- **Save settings to user's configuration**
  - `File`: src\web\server2.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\web\server2.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\web\server2.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\web\server2.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\web\server2.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\web\server2.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\web\server2.py
  - `Line`: 1603

- **Save settings to user's configuration**
  - `File`: src\web\server_bak.py
  - `Line`: 1146

- **Load user's settings**
  - `File`: src\web\server_bak.py
  - `Line`: 1149

- **Fetch user's API keys from database**
  - `File`: src\web\server_bak.py
  - `Line`: 1364

- **Save API key to database**
  - `File`: src\web\server_bak.py
  - `Line`: 1391

- **Remove API key from database**
  - `File`: src\web\server_bak.py
  - `Line`: 1418

- **Implement activity log page**
  - `File`: src\web\server_bak.py
  - `Line`: 1465

- **Implement actual model creation logic**
  - `File`: src\web\server_bak.py
  - `Line`: 1603

- **Implement detailed module graph creation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 272

- **Implement memory profile estimation**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 358

- **Implement memory profile visualization**
  - `File`: src\visualization\architecture_graph.py
  - `Line`: 493

- **Implement model-specific attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 196

- **Implement model-specific all-layer attention extraction**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 231

- **Implement attention flow visualization logic**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 288

- **Implement proper cross-attention visualization**
  - `File`: src\visualization\attention_patterns.py
  - `Line`: 313

- **Implement model-specific hook registration based on model type**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 252

- **Implement layer activation extraction**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 284

- **Implement model graph creation**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 299

- **Implement proper layout and styling for the graph plot**
  - `File`: src\visualization\model_visualizer.py
  - `Line`: 364

- **Replace with actual data collection from models**
  - `File`: src\web\routes\metrics.py
  - `Line`: 71

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 216

- **Implement tokenizer loading**
  - `File`: src\web\routes\model_visualization.py
  - `Line`: 294
