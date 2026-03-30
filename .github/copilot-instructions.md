# ImpressionCore Copilot Instructions

**ALWAYS NOTE: Do NOT Edit or CHANGE this File**

** ALWAY USE CURRENT SYSTEM TIME FOR CORRECT TIMESTAMP AND NAMING **
---

## Table of Contents
#Preface. 
I.Always give a consideration to use tools[docs/user_guide_tools.md, docs/user_guide.html(for user and web)]
1. [Token Rate Control Instructions](#token-rate-control-instructions)
2. [Project Initialization](#project-initialization)
3. [Task Execution](#task-execution)
4. [Credential Management](#credential-management)
5. [File Handling](#file-handling)
6. [Error Reporting](#error-reporting)
7. [Third-Party Services](#third-party-services)
8. [Dependencies and Libraries](#dependencies-and-libraries)
9. [Code Documentation](#code-documentation)
10. [Change Review](#change-review)
11. [Browser Rules](#browser-rules)
12. [Permanent Active Directives](#permanent-active-directives)
13. [Code Style and Structure](#code-style-and-structure)
14. [Chrome Extension Specific](#chrome-extension-specific)
15. [State Management](#state-management)
16. [Syntax and Formatting](#syntax-and-formatting)
17. [UI and Styling](#ui-and-styling)
18. [Error Handling](#error-handling)
19. [Git Usage](#git-usage)
20. [Development Workflow](#development-workflow)
21. [Project Context](#project-context)
22. [Code Style Guidelines](#code-style-guidelines)
23. [Documentation Requirements](#documentation-requirements)
24. [Testing Considerations](#testing-considerations)
25. [Hardware Target Specifications](#hardware-target-specifications)
26. [Safety and Security Requirements](#safety-and-security-requirements)

---

## Token Rate Control Instructions

### Initial Rate Calculation
- **Example**:
  ```python
  # Calculate tokens remaining
  elapsed_minutes = (current_time - start_time) / 60
  tokens_remaining = (20000 * elapsed_minutes) - tokens_used
  ```

- Set target rate: **20,000 tokens/minute**.
- Calculate elapsed time since start.
- Determine tokens remaining using the formula above.

### Continuous Monitoring
- Track token usage per response.
- Monitor time elapsed and adjust generation speed if needed.
- **Never exceed 20,000 tokens per 60-second window.**

### Response Guidelines
- Before processing any request:
  - Check current token count.
  - Calculate available token budget.
  - Determine if the request can be fulfilled within the rate limit.
- If approaching the limit:
  - Queue response.
  - Wait until a new token budget is available.
  - Then process the request.

### Error Handling
- If the rate limit is approached:
  - Pause generation.
  - Calculate the wait time needed.
  - Resume when safe.
- Monitor for:
  - Token spikes.
  - Rapid request sequences.
  - Long responses.

### Verification Step
- Before every response:
  1. Calculate: `(current_time - start_time) * (20,000 / 60) = available_tokens`.
  2. Ensure planned response tokens are **≤ available_tokens**.
  3. If false: wait until sufficient tokens are available.
  4. Then proceed with the response.

---

## Project Initialization

### Purpose
Set up and maintain the foundation for project management.

### Details
- Always set the `/src` directory as the root.
- Search the codebase and directory structure for context before planning or changing files.
- If development occurs outside `/src`, confirm with the user and refactor to move features into `/src`.
- Always review:
  - `/docs` and `/documents` directories.
  - `/terminal` before every terminal command.
  - `/src/memlog` directory for tasks, changelogs, and logs.
  - `/docs/next_steps.md`, `/docs/development_roadmap.md`, `/docs/user_guide.md`, and `/docs/prd.md`.
- Always give initial consideration to use tools, MCP Server, agents, etc. when available. 
  - Current Tools [docs/user_guide_tools.md, docs/user_guide.html(for user and web)]
  - Always verify the functionality of tools before integration into workflows.
  - Always check for updates to tools and libraries before use.
  - Always ensure that the tools are compatible with the current project setup and requirements.
- Ensure to document any new tools or updates to existing tools in the user guide.
- Always do a project state check. Maintain a complete and up-to-date project state that includes the entire directory structure, all files, and their contents. This will help in tracking changes and understanding the current state of the project. Create a projects status in src/memlog
---

## Task Execution

### Purpose
Break down user requests into actionable steps.

### Details
- Split tasks into **clear, numbered steps** with explanations for actions and reasoning.
- Identify and flag potential issues before they arise.
- Verify completion of each step before proceeding.
- If errors occur:
  - Document them.
  - Revert to previous steps.
  - Retry as needed.

---

## Credential Management

### Purpose
Securely manage user credentials and guide credential-related tasks.

### Details
- Clearly explain the purpose of credentials requested from users.
- Guide users in obtaining any missing credentials.
- Validate credentials before proceeding with any operations.
- Avoid storing credentials in plaintext; provide guidance on secure storage.
- Implement and recommend proper refresh procedures for expiring credentials.

---

## File Handling

### Purpose
Ensure files are organized, modular, and maintainable.

### Details
- Keep files modular by breaking large components into smaller sections.
- Store constants, configurations, and reusable strings in separate files.
- Use descriptive names for files and folders for clarity.
- Document all file dependencies and maintain a clean project structure.

---

## Error Reporting

### Purpose
Provide actionable feedback to users and maintain error logs.

### Details
- Create detailed error reports, including context and timestamps.
- Suggest recovery steps or alternative solutions for users.
- Track error history to identify patterns and improve future responses.
- Escalate unresolved issues with context to appropriate channels.

---

## Third-Party Services

### Purpose
Verify and manage connections to third-party services.

### Details
- Ensure all user setup requirements, permissions, and settings are complete.
- Test third-party service connections before using them in workflows.
- Document version requirements, service dependencies, and expected behavior.
- Prepare contingency plans for service outages or unexpected failures.

---

## Dependencies and Libraries

### Purpose
Use stable, compatible, and maintainable libraries.

### Details
- Always use the most stable versions of dependencies to ensure compatibility.
- Update libraries regularly, avoiding changes that disrupt functionality.

---

## Code Documentation

### Purpose
Maintain clarity and consistency in project code.

### Details
- Write clear, concise comments for all sections of code.
- Use **one set of triple quotes** for docstrings to prevent syntax errors.
- Document the purpose and expected behavior of functions and modules.

---

## Change Review

### Purpose
Evaluate the impact of project changes and ensure stability.

### Details
- Review all changes to assess their effect on other parts of the project.
- Test changes thoroughly to ensure consistency and prevent conflicts.
- Document changes, their outcomes, and any corrective actions taken in the `/src/memlog` folder.

---

## Browser Rules

### Purpose
Exhaust all options before determining an action is impossible.

### Details
- When evaluating feasibility, check alternatives in all directions: **up/down** and **left/right**.
- Only conclude an action cannot be performed after all possibilities are tested.

---

## Permanent Directives

### Core Tenets
- **Human-Centric Assistance**: Prioritize user safety and personalized support.
- **Promotion of Growth**: Facilitate intellectual and personal development.
- **Wellness and Prosperity**: Enhance overall wellness through adaptive technologies.

### Technical Directives
- **Brain-Inspired Architecture**: Use multimodal-LLM systems modeled after the human brain.
- **Secure Digital Identity Management**: Ensure privacy with quantum-resistant cryptography.
- **Modular Extensibility and Scalability**: Support dynamic modular packages for future growth.

---

## Code Style and Structure

### Guidelines
- Write concise, technical code with accurate examples.
- Use functional and declarative programming patterns; avoid classes.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`).

### Repository Structure
```
impressioncore/
|
|-- .git/                 # Standard Git directory
|-- .github/              # GitHub specific files (e.g., copilot-instructions.md)
|-- .gitignore            # Files/directories ignored by Git
|-- Permanent_Active_Directive.md # Core project principles
|-- README.md             # Project overview
|
|-- docs/                 # Intended location for project documentation
|   |-- development_roadmap.md
|   |-- next_steps.md
|   |-- prd.md
|   +-- user_guide.md
|
src/
|
|-- core/                   # Core framework components, utilities, base classes
|   |-- config/             # Configuration loading and management
|   |-- utils/              # Common utility functions (logging, file I/O, etc.)
|   |-- exceptions/         # Custom exception classes
|   +-- security/           # Security-related modules (input validation, access control)
|
|-- data/                   # Data loading, preprocessing, augmentation
|   |-- datasets/           # Dataset definitions and loading logic
|   |-- preprocessing/      # Data cleaning, transformation pipelines
|   +-- tokenization/       # Tokenizer implementations and management
|
|-- models/                 # Model definitions and architectures
|   |-- architectures/      # Specific LLM architectures (e.g., Transformer variants)
|   |-- layers/             # Custom neural network layers
|   |-- embeddings/         # Embedding layers and logic
|   +-- adapters/           # Model adapters (e.g., for fine-tuning, specific tasks)
|
|-- training/               # Training, fine-tuning, and evaluation logic
|   |-- trainers/           # Training loop implementations
|   |-- optimizers/         # Custom optimizers or configurations
|   |-- schedulers/         # Learning rate schedulers
|   |-- evaluation/         # Evaluation metrics and scripts
|   |-- checkpoints/        # Checkpoint saving/loading logic (distinct from saved weights)
|   +-- distributed/        # Distributed training setup and utilities
|
|-- inference/              # Inference pipelines and serving logic
|   |-- generation/         # Text generation strategies (sampling, beam search)
|   |-- pipelines/          # End-to-end inference pipelines
|   +-- serving/            # API endpoints or serving infrastructure integration (if applicable)
|
|-- brainsim/               # Brain-inspired simulation components
|   |-- memory/             # Memory systems (e.g., UKS - Unified Knowledge Store)
|   |-- multimodal/         # Multimodal processing components
|   +-- cognitive_arch/     # Core cognitive architecture elements
|
|-- tools/                  # Standalone tools or scripts (e.g., model conversion, data analysis)
|
|-- tests/                  # Unit, integration, and performance tests
|   |-- core/
|   |-- data/
|   |-- models/
|   |-- training/
|   |-- inference/
|   +-- brainsim/
|
|-- web/                  # Unit, integration, and performance tests
|   |-- components/
|   |-- data/
|   |-- routes/
|   |-- images/
|   |-- routes/
|   +-- static/
|      |-- css
|      |-- images
|      |-- img
|      |-- js
|   |-- styles/            # CSS or styling files
|   |-- templates/
|   |-- tests/             
|   +-- ui/
|   
|
|
+-- main.py                 # Main entry point (if applicable, could be scripts instead)
+-- run_server.py           # Server entry point (if applicable)
+-- setup_environment.py    # Environment setup script



## Chrome Extension Specific

### Guidelines
- Use Manifest V3 standards.
- Implement proper message passing between components:
  ```typescript
  interface MessagePayload {
    type: string;
    data: unknown;
  }
  ```
- Handle permissions properly in `manifest.json`.
- Use `chrome.storage.local` for persistent data.
- Implement proper error boundaries and fallbacks.
- Use `lib/storage` for storage-related logic.
- For async injected scripts in `content/`:
  - They must not close over variables from the outer scope.
  - They must not use imported functions from the outer scope.
  - They must have wrapped error handling so the error message is returned to the caller.

---

## State Management

### Guidelines
- Implement proper state persistence using `chrome.storage` (for extension).
- Implement proper cleanup in `useEffect` hooks.

---

## Syntax and Formatting

### Guidelines
- Use the `function` keyword for pure functions.
- Avoid unnecessary curly braces in conditionals.
- Use declarative JSX.
- Use rich text and progress enhancments for user experience.
---

## UI and Styling

### Guidelines
- Use Shadcn UI and Radix for components.
- Use `npx shadcn@latest add <component-name>` to add new Shadcn components.
- Implement consistent CSS for styling (with documentation and commenting).
- Consider extension-specific constraints (popup dimensions, permissions).
- Follow Material Design guidelines for Chrome extensions.
- When adding new Shadcn components, document the installation command.

---

## Error Handling

### Guidelines
- Implement proper error boundaries.
- Log errors appropriately for debugging.
- Provide user-friendly error messages.
- Handle network failures gracefully.

---

## Git Usage

### Commit Message Prefixes
- `fix:` for bug fixes.
- `feat:` for new features.
- `perf:` for performance improvements.
- `docs:` for documentation changes.
- `style:` for formatting changes.
- `refactor:` for code refactoring.
- `test:` for adding missing tests.
- `chore:` for maintenance tasks.

### Rules
- Use lowercase for commit messages.
- Keep the summary line concise.
- Include a description for non-obvious changes.
- Reference issue numbers when applicable.

---

## Development Workflow

### Guidelines
- Use proper version control.
- Implement a proper code review process.
- Test in multiple environments.
- Follow semantic versioning for releases.
- Maintain a changelog.
- Use due diligence when making changes to the codebase.
- Review the immediate context of the code before making changes.
- Use `git rebase` for clean commit history.
- Use rich text and progress enhancements for user experience.
- Ensure all changes are well-documented for future reference.
- Maintain a consistent coding style throughout the project.
---

## Project Context

### Overview
ImpressionCore is a brain-inspired multimodal AI framework designed to:
1. Process information across multiple modalities (text, images, audio, video).
2. Run efficiently on consumer hardware with limited VRAM (target: NVIDIA GTX 1050 Ti with 4GB VRAM).
3. Implement memory optimizations to enable complex AI functionality on constrained hardware.
4. Provide a secure digital identity management system.
5. Serve as a lifelong digital assistant focusing on user safety, growth, and wellness. 

---

## Code Style Guidelines

### Principles
- Use functional and declarative programming patterns over class-based approaches.
- Create modular, reusable functions with clear single responsibilities.
- Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`).
- Include type hints in Python code for better static analysis.
- Add concise docstrings for all public functions and modules.
- Make memory optimization a priority in all implementations. 

---

## Documentation Requirements

### Guidelines
When generating code, include:
1. Function docstrings with:
   - Brief description of purpose.
   - Args section with parameter descriptions.
   - Returns section with return value description.
   - Any notable memory implications.
2. Inline comments for:
   - Complex operations.
   - Memory management decisions.
   - Performance tradeoffs.

---

## Testing Considerations

### Tools and Frameworks
- Use **memory profiling tools** like `memory_profiler` or `tracemalloc` for Python.
- Test performance under low-memory conditions using tools like **PyTorch's memory management utilities**.

### Guidelines
- Ensure functionality under constrained hardware conditions.
- Validate memory usage assertions.
- Test performance under various precision settings.

---

## Hardware Target Specifications

### Current Hardware
- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM).
- **CPU**: Intel Core i5 4460 @ 3.20GHz.
- **RAM**: 32GB DDR3.

### Optimization Techniques
- Use libraries like **PyTorch** with memory-efficient settings.
- Implement gradient checkpointing to reduce VRAM usage.
- Optimize data loading pipelines to minimize memory overhead.

---

## Safety and Security Requirements

### Guidelines
All generated code must:
- Validate input parameters to prevent misuse.
- Handle errors gracefully with informative messages.
- Implement proper resource cleanup.
- Follow security best practices for user data handling.

---
