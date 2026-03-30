# ImpressionCore Tools User Guide

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

---

## Tool Usage Guide

### 1. Database Tools
- **dbcode-get-connections**: List all available database connections.
- **dbcode-get-databases**: List all databases for a connection.
- **dbcode-get-schemas**: List all schemas for a database.
- **dbcode-get-tables**: List all tables, columns, and keys for a database.
- **dbcode-execute-query**: Run a SQL query on a database.

### 2. Codebase & Search Tools
- **search_codebase**: Search for code or comments in the workspace.
- **semantic_search**: Semantic search for code, comments, or documentation.
- **list_code_usages**: Find all usages of a function, class, or variable.
- **get_vscode_api**: Get VS Code API documentation for extension development.
- **file_search**: Find files by glob pattern.
- **grep_search**: Search for text in files.
- **read_file**: Read a file by line range.
- **list_dir**: List files and folders in a directory.

### 3. Terminal & Git Tools
- **run_in_terminal**: Run shell commands.
- **get_terminal_output**: Get output from a previous terminal command.
- **get_errors**: Get compile or lint errors in a file.
- **get_changed_files**: Get git diffs for files.

### 4. Project & Extension Tools
- **create_new_workspace**: Steps to create a new project.
- **get_project_setup_info**: Get setup info for a project type.
- **install_extension**: Install a VS Code extension.
- **create_new_jupyter_notebook**: Create a new Jupyter Notebook.

### 5. File & Documentation Tools
- **insert_edit_into_file**: Edit an existing file.
- **create_file**: Create a new file.
- **fetch_webpage**: Fetch and extract content from a web page.
- **test_search**: Find test file for a source file or vice versa.
- **get_doc_info**: Get documentation info for a symbol.
- **github_repo**: Search a GitHub repo for code snippets.

### 6. Python Environment Tools
- **python_environment_tool**: Get Python environment info.
- **python_install_package_tool**: Install Python packages.

### 7. Web & Extension Search Tools
- **vscode-websearchforcopilot_webSearch**: Search the web for info.
- **vscode_searchExtensions_internal**: Search for VS Code extensions.

### 8. Browser Automation Tools (bb7_*)
- **bb7_click_element**: Click an element in browser automation.
- **bb7_close_browser**: Close the current browser instance.
- **bb7_done**: Complete a browser automation task.
- **bb7_get_dropdown_options**: Get dropdown options from a browser element.
- **bb7_go_back**: Go back to previous page in browser.
- **bb7_go_to_url**: Navigate to a URL in browser.
- **bb7_initialize_browser**: Start a new browser instance.
- **bb7_input_text**: Input text into a browser element.
- **bb7_inspect_page**: List interactive elements and extract content from page.
- **bb7_open_tab**: Open a URL in a new browser tab.
- **bb7_scroll_down**: Scroll down the page.
- **bb7_scroll_to_text**: Scroll to an element containing specified text.
- **bb7_scroll_up**: Scroll up the page.
- **bb7_search_google**: Search Google in the current tab.
- **bb7_select_dropdown_option**: Select an option from a dropdown by text.
- **bb7_send_keys**: Send keyboard keys/shortcuts to the page.
- **bb7_switch_tab**: Switch to a browser tab by page ID.
- **bb7_validate_page**: Validate page state or check for expected text.
- **bb7_wait**: Wait for a number of seconds in browser automation.
- **bb7_fetch**: Fetch a URL and extract content as markdown.

---

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
