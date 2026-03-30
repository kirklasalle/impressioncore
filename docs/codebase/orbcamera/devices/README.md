# README.md

**Created:** February 20, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\codebase\orbcamera\devices\README.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Device Manager Python Application

This project is a Python application that detects system hardware and displays it in a tree structure, categorized by hardware type.

## Features

- Detects various hardware components of the system.
- Displays hardware information in a user-friendly tree view.
- Categorizes hardware for easy navigation.

## Project Structure

``` text
devices
├── src
│   ├── main.py              # Entry point of the application
│   ├── hardware             # Contains hardware detection logic
│   │   ├── __init__.py
│   │   ├── detector.py      # Class for detecting hardware
│   │   └── categories.py     # Class for organizing hardware into categories
│   ├── ui                   # Contains UI components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   └── tree_view.py      # Displays hardware information in a tree structure
│   └── utils                # Utility functions
│       ├── __init__.py
│       └── system_info.py    # Functions to retrieve system information
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```
   cd device-manager-py
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:

``` text
python src/main.py
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.
