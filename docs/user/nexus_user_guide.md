# NEXUS-RLM User Guide

**Created:** January 19, 2026  
**Updated:** January 19, 2026  
**Author:** Kirk LaSalle; Antigravity Agent  
**Tags:** #rlm #nexus #user_guide #brain_triad #document_analysis  
**Category:** User Documentation  
**Status:** Active  
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## What is NEXUS-RLM?

NEXUS-RLM is an exciting new capability in ImpressionCore that allows the AI to read and understand **very large documents** - up to 50 megabytes of text! This means you can:

- 📚 Analyze entire books or research papers
- 🔍 Search through large codebases
- 🧠 Get insights from comprehensive reports
- 💡 Ask questions about lengthy documents

---

## How It Works (Simple Explanation)

Instead of trying to fit an entire document into the AI's memory at once (which would be impossible for large files), NEXUS-RLM:

1. **Stores the document externally** - Like having a book on your desk
2. **Searches smartly** - The AI looks up only the relevant parts
3. **Analyzes in pieces** - Breaking the document into digestible chunks
4. **Synthesizes answers** - Combining insights from different parts

---

## Getting Started

### Step 1: Load Your Document

Using the NEXUS language, you can load any text document:

```lisp
(CONTEXT-LOAD "path/to/your/document.txt")
```

For example:
```lisp
(CONTEXT-LOAD "docs/user_guide.md")
```

### Step 2: Check Document Stats

See what you've loaded:

```lisp
(CONTEXT-STATS)
```

This shows:
- How many characters
- Estimated tokens
- Number of lines
- Number of paragraphs

### Step 3: Search for Information

Find specific topics in your document:

```lisp
(CONTEXT-SEARCH "installation")
```

### Step 4: Ask the AI to Analyze

Use the Brain-Triad to analyze your document:

```lisp
(LLM-QUERY "left" "What are the main topics covered in this document?")
(LLM-QUERY "right" "What creative applications could this enable?")
(LLM-QUERY "colossus" "Summarize the key takeaways")
```

---

## Understanding Brain-Triad Hemispheres

When you use `LLM-QUERY`, you're asking one of three specialized "minds":

| Hemisphere | Specialty | Best For |
|------------|-----------|----------|
| **LEFT** | Logical, analytical | Facts, structure, data analysis |
| **RIGHT** | Creative, imaginative | Ideas, alternatives, connections |
| **COLOSSUS** | Balanced synthesizer | Final summaries, conclusions |

### Example Workflow

```lisp
;; Load a research paper
(CONTEXT-LOAD "papers/quantum_computing.pdf.txt")

;; Ask LEFT for factual analysis
(LLM-QUERY "left" "What are the key findings and data points?")

;; Ask RIGHT for creative insights
(LLM-QUERY "right" "What unexpected applications could this research enable?")

;; Ask COLOSSUS to synthesize
(LLM-QUERY "colossus" "Create a comprehensive summary combining facts and insights")
```

---

## Available Commands

### Document Commands

| Command | What It Does |
|---------|--------------|
| `(CONTEXT-LOAD "path")` | Load a document |
| `(CONTEXT-SEARCH "text")` | Search for text |
| `(CONTEXT-CHUNK)` | Split into chunks |
| `(CONTEXT-STATS)` | Show document info |
| `(CONTEXT-LIST)` | List all loaded documents |

### Analysis Commands

| Command | What It Does |
|---------|--------------|
| `(LLM-QUERY "left" "prompt")` | Ask logical analysis |
| `(LLM-QUERY "right" "prompt")` | Ask creative analysis |
| `(LLM-QUERY "colossus" "prompt")` | Ask for synthesis |

### Status Commands

| Command | What It Does |
|---------|--------------|
| `(RECURSION-DEPTH)` | Check analysis depth |
| `(RLM-STATS)` | Show usage statistics |

---

## Practical Examples

### Example 1: Analyze a Book

```lisp
;; Load the book
(CONTEXT-LOAD "books/war_and_peace.txt" "tolstoy")

;; Check the size
(CONTEXT-STATS)

;; Search for a character
(CONTEXT-SEARCH "Natasha")

;; Get analysis
(LLM-QUERY "left" "Describe Natasha's character arc based on the text")
```

### Example 2: Code Review

```lisp
;; Load a large source file
(CONTEXT-LOAD "src/main_application.py" "app")

;; Search for function definitions
(CONTEXT-SEARCH "def " true 50)  ;; regex mode, 50 results

;; Ask for review
(LLM-QUERY "left" "What are the main functions and their purposes?")
(LLM-QUERY "right" "What improvements could be made to this code?")
```

### Example 3: Research Summary

```lisp
;; Load research paper
(CONTEXT-LOAD "papers/climate_study.txt")

;; Search for key sections
(CONTEXT-SEARCH "methodology")
(CONTEXT-SEARCH "results")
(CONTEXT-SEARCH "conclusion")

;; Get comprehensive summary
(LLM-QUERY "colossus" "Summarize the research methodology, key findings, and conclusions")
```

---

## Tips for Best Results

### ✅ Do:

1. **Start with CONTEXT-STATS** - Understand your document's size
2. **Use search before analysis** - Find relevant sections first
3. **Ask specific questions** - "What are the three main arguments?" is better than "Tell me about this"
4. **Use the right hemisphere** - LEFT for facts, RIGHT for ideas, COLOSSUS for summaries

### ❌ Avoid:

1. **Loading files over 50MB** - Split them first
2. **Vague prompts** - Be specific about what you want
3. **Ignoring search** - Don't ask about something without searching first

---

## Troubleshooting

### "File not found"

Make sure your file path is correct. Try using the full path:
```lisp
(CONTEXT-LOAD "C:/Users/You/Documents/file.txt")
```

### "No context loaded"

You need to load a document before searching or analyzing:
```lisp
(CONTEXT-LOAD "your_file.txt")  ;; Do this first!
(CONTEXT-SEARCH "keyword")       ;; Then this works
```

### "File too large"

Split your document into smaller parts (under 50MB each).

---

## What's Coming Next

In future versions, you'll be able to:

- 🚀 Get instant responses from LLM-QUERY (currently pending mode)
- ⚡ Run multiple analyses in parallel
- 📊 Visualize document structure
- 🔗 Cross-reference multiple documents

---

## Need Help?

- Check the [Developer Guide](../developer/nexus_rlm_developer_guide.md) for technical details
- See the [NEXUS Language Guide](nexus_language_guide.md) for all NEXUS commands
- Review example plans in the `plans/` directory

---

*Happy analyzing! 🎉*
