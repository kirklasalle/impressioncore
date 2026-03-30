# User Guide Tools

**Created:** April 17, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\user\user_guide_tools.md #api #command_line #documentation #memory_management #pytorch #testing #tokenization #web_interface  
**Category:** User Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Tools User Guide

## Enhanced Markdown Viewer & IDS UI/UX (2025-06-05)

- **Raw/Rendered Preview Toggle:** Switch between raw HTML and fully rendered (with diagrams) preview modes in the documentation editor.
- **Live Diagram Rendering:** Mermaid diagrams and other JS-based diagrams are now rendered in the preview (requires PyQtWebEngine).
- **Directory Tree Navigation:** The directory tree now supports expandable directories and file selection for easier navigation.
- **Global Theme Support:** The entire application supports dark/light mode, not just the editor.
- **Formatting Toolbar:** Added for markdown editing.
- **Synchronized Scrolling:** Editor and preview panes scroll together.
- **Multi-Tab Editing:** Edit multiple documents at once, with recent files tracking.
- **Tag-Based Filtering & Advanced Search:** Integrated with IDS tagging system for efficient document search and navigation.
- **IDS Integration:** Editor launchable from IDS menu; subprocess launch now sets PYTHONPATH for import reliability.
- **Requirements Updated:** PyQtWebEngine added to requirements.txt and doc_viewer/requirements.txt.
- **Verification:** Full system operation verified in both interactive and automated modes.

See the [Developer Guide](../developer/developer_guide.md) for technical details and [memlog entry](../../src/memlog/ids_uiux_diagram_theme_enhancement_2025-06-05.md) for changelog and verification.

---

## Cheat Sheet: Tool List & Usage

| Tool Name                       | How to Initiate / Use                                                                 | Example Usage                                                                                 |
|----------------------------------|--------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| dbcode-get-connections           | Retrieve all available DB connections                                                | dbcode-get-connections()                                                                     |
| dbcode-get-databases             | Get databases for a connection                                                       | dbcode-get-databases({connectionId, connectionName})                                         |
| dbcode-get-schemas               | Get schema names for a database                                                      | dbcode-get-schemas({connectionId, connectionName, databaseName})                             |
| dbcode-get-tables                | Get tables, columns, keys for a database                                             | dbcode-get-tables({connectionId, connectionName, databaseName, schemaName})                  |
| dbcode-execute-query             | Execute a SQL query                                                                  | dbcode-execute-query({connectionId, connectionName, databaseName, query, schemaName})        |
| search_codebase                  | Search codebase for relevant code                                                    | search_codebase()                                                                            |
| semantic_search                  | Semantic search for code or comments                                                 | semantic_search({query: 'tokenizer'})                                                        |
| list_code_usages                 | List all usages of a symbol                                                          | list_code_usages({symbolName: 'generate_diagram'})                                           |
| get_vscode_api                   | Get VS Code API references                                                           | get_vscode_api({query: 'webview'})                                                           |
| file_search                      | Search for files by glob pattern                                                     | file_search({query: '**/*.py'})                                                              |
| grep_search                      | Text search in workspace                                                             | grep_search({query: 'def ', includePattern: '**/*.py'})                                      |
| read_file                        | Read file contents by line range                                                     | read_file({filePath, startLineNumberBaseZero: 0, endLineNumberBaseZero: 20})                 |
| list_dir                         | List directory contents                                                              | list_dir({path: '/src'})                                                                     |
| run_in_terminal                  | Run shell commands in terminal                                                       | run_in_terminal({command: 'ls -l', explanation: 'List files', isBackground: false})          |
| get_terminal_output              | Get output of a previous terminal command                                            | get_terminal_output({id: 'terminal-1'})                                                      |
| get_errors                       | Get compile/lint errors in a file                                                    | get_errors({filePaths: ['/src/main.py']})                                                    |
| get_changed_files                | Get git diffs of current file changes                                                | get_changed_files({repositoryPath: '.', sourceControlState: ['unstaged']})                   |
| test_failure                     | Get test failure information                                                         | test_failure()                                                                               |
| get_terminal_selection           | Get current selection in terminal                                                    | get_terminal_selection()                                                                     |
| get_terminal_last_command        | Get last command in terminal                                                         | get_terminal_last_command()                                                                  |
| create_new_workspace             | Steps to create a new project                                                        | create_new_workspace({query: 'Create a Next.js app'})                                        |
| get_project_setup_info           | Get setup info for a project type                                                    | get_project_setup_info({language: 'python', projectType: 'basic'})                           |
| install_extension                | Install a VS Code extension                                                          | install_extension({id: 'ms-python.python', name: 'Python'})                                  |
| create_new_jupyter_notebook      | Create a new Jupyter Notebook                                                        | create_new_jupyter_notebook({query: 'Data analysis'})                                        |
| insert_edit_into_file            | Edit an existing file                                                                | insert_edit_into_file({code, explanation, filePath})                                         |
| create_file                      | Create a new file                                                                    | create_file({content, filePath})                                                             |
| fetch_webpage                    | Fetch content from a web page                                                        | fetch_webpage({query: 'API docs', urls: ['https://example.com']})                            |
| test_search                      | Find test file for a source file or vice versa                                       | test_search({filePaths: ['/src/foo.py']})                                                    |
| get_doc_info                     | Get documentation info for a symbol                                                  | get_doc_info({filePaths: ['/src/foo.py']})                                                   |
| github_repo                      | Search a GitHub repo for code snippets                                               | github_repo({query: 'tokenizer', repo: 'owner/repo'})                                        |
| python_environment_tool          | Get Python environment info                                                          | python_environment_tool({resourcePath: '/src'})                                              |
| python_install_package_tool      | Install Python packages                                                              | python_install_package_tool({packageList: ['torch'], workspacePath: '/src'})                 |
| vscode-websearchforcopilot_webSearch | Search the web for info                                                          | vscode-websearchforcopilot_webSearch({query: 'PyTorch memory optimization'})                 |
| vscode_searchExtensions_internal | Search for VS Code extensions                                                        | vscode_searchExtensions_internal({category: 'AI', keywords: ['chat']})                       |
| bb7_click_element                | Click an element in browser automation                                               | bb7_click_element({index: 2})                                                                |
| bb7_close_browser                | Close the current browser instance                                                   | bb7_close_browser()                                                                          |
| bb7_done                         | Complete a browser automation task                                                   | bb7_done({success: true, text: 'Done'})                                                      |
| bb7_get_dropdown_options         | Get dropdown options from a browser element                                          | bb7_get_dropdown_options({index: 1})                                                         |
| bb7_go_back                      | Go back to previous page in browser                                                  | bb7_go_back()                                                                                |
| bb7_go_to_url                    | Navigate to a URL in browser                                                         | bb7_go_to_url({url: 'https://example.com'})                                                  |
| bb7_initialize_browser           | Start a new browser instance                                                         | bb7_initialize_browser({headless: true, task: 'Scrape data'})                                |
| bb7_input_text                   | Input text into a browser element                                                    | bb7_input_text({index: 0, text: 'hello'})                                                    |
| bb7_inspect_page                 | List interactive elements and extract content from page                              | bb7_inspect_page()                                                                           |
| bb7_open_tab                     | Open a URL in a new browser tab                                                      | bb7_open_tab({url: 'https://example.com'})                                                   |
| bb7_scroll_down                  | Scroll down the page                                                                 | bb7_scroll_down({amount: 200})                                                               |
| bb7_scroll_to_text               | Scroll to an element containing specified text                                       | bb7_scroll_to_text({text: 'Submit'})                                                         |
| bb7_scroll_up                    | Scroll up the page                                                                   | bb7_scroll_up({amount: 100})                                                                 |
| bb7_search_google                | Search Google in the current tab                                                     | bb7_search_google({query: 'ImpressionCore'})                                                 |
| bb7_select_dropdown_option       | Select an option from a dropdown by text                                             | bb7_select_dropdown_option({index: 1, text: 'Option 2'})                                     |
| bb7_send_keys                    | Send keyboard keys/shortcuts to the page                                             | bb7_send_keys({keys: 'Enter'})                                                               |
| bb7_switch_tab                   | Switch to a browser tab by page ID                                                   | bb7_switch_tab({page_id: 2})                                                                 |
| bb7_validate_page                | Validate page state or check for expected text                                       | bb7_validate_page({expected_text: 'Welcome'})                                                |
| bb7_wait                         | Wait for a number of seconds in browser automation                                   | bb7_wait({seconds: 5})                                                                       |
| bb7_fetch                        | Fetch a URL and extract content as markdown                                          | bb7_fetch({url: 'https://example.com', max_length: 1000})                                    |



## Example Scenarios

### Example 1: Search for a Python function in the codebase

```python
semantic_search({"query": "def generate_diagram"})
```

### Example 2: Run a SQL query on a database

```python
dbcode-execute-query({
    "connectionId": "abc123",
    "connectionName": "main-db",
    "databaseName": "users",
    "query": "SELECT * FROM users;"
})
```

### Example 3: Edit a file

```python
insert_edit_into_file({
    "code": "# ...existing code...\nnew_code_here\n# ...existing code...",
    "explanation": "Add new function",
    "filePath": "/src/core/utils/file.py"
})
```

### Example 4: Automate browser to fill a form

```python
bb7_initialize_browser({"headless": true, "task": "Fill form"})
bb7_go_to_url({"url": "https://example.com/form"})
bb7_input_text({"index": 0, "text": "John Doe"})
bb7_click_element({"index": 1})
```

---

For more details on each tool, see the full API documentation or use the cheat sheet above for quick reference.
