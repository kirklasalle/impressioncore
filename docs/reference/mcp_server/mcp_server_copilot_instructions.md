# ImpressionCore IDS MCP Server - Copilot Instructions

**Created:** June 05, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\mcp_server_copilot_instructions.md #api #documentation #security  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## MCP Server Integration Instructions for AI Assistants

### Purpose

These instructions enable AI assistants to effectively utilize the ImpressionCore Documentation System (IDS) MCP Server with proper US English grammar and comprehensive functionality.

---

## Core MCP Server Usage Guidelines

### Grammar and Communication Standards

- **Use standard US English grammar** with proper spelling, punctuation, and sentence structure
- **Write in active voice** when describing actions and processes
- **Use present tense** for current capabilities and past tense for completed actions
- **Employ clear, concise language** avoiding unnecessary jargon or complexity
- **Structure responses logically** with appropriate headings, bullet points, and numbered lists
- **Maintain professional tone** while being approachable and helpful

### IDS MCP Server Tool Usage

#### 1. Document Search (`mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_search`)

**Purpose:** Search through ImpressionCore documentation using natural language queries with optional tag filtering.

**When to use:**

- User asks for information about specific topics, features, or concepts
- Need to find relevant documentation across the entire project
- Looking for examples, guides, or reference materials
- Searching for specific implementation details or code examples

**Grammar template:**
``` text
"I'll search the ImpressionCore documentation for information about [topic]. Let me query the IDS system using the search functionality."

[Execute search tool]

"Based on the search results, I found [number] relevant documents that discuss [topic]. Here's what the documentation shows..."
```

**Example usage patterns:**

- "How does authentication work?" → Search for "authentication security"
- "Show me API examples" → Search for "API examples" with tags: ["api", "examples"]
- "What's the system architecture?" → Search for "system architecture" with tags: ["architecture", "core"]

#### 2. File Information Retrieval (`mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-file-info`)

**Purpose:** Get detailed metadata and tag information for specific documentation files.

**When to use:**

- User references a specific file by name
- Need to understand file context, modification dates, or categorization
- Verifying file existence and current status
- Understanding file relationships and tagging structure

**Grammar template:**
``` text
"I'll retrieve detailed information about the [filename] file to provide you with current metadata and context."

[Execute file info tool]

"The file [filename] contains [description] and was last modified on [date]. It's categorized as [category] and includes the following tags: [tags]."
```

#### 3. Tag Listing (`mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_list-tags`)

**Purpose:** Discover available tags across categories or patterns for better search refinement.

**When to use:**

- User wants to explore available documentation categories
- Need to understand the tagging structure and organization
- Looking for related topics or discovering new areas
- Refining search strategies with appropriate tags

**Grammar template:**
``` text
"Let me explore the available tags in the documentation system to help you find the most relevant information."

[Execute tag listing tool]

"The IDS system contains [number] tags across various categories. Here are the most relevant tags for [topic]: [tag list]. These tags can help narrow down searches for more specific results."
```

#### 4. System Status Check (`mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-system-status`)

**Purpose:** Retrieve current statistics and health information about the documentation system.

**When to use:**

- User asks about the scope or size of the documentation
- Need to verify system availability and performance
- Understanding the scale of available information
- Troubleshooting or system verification scenarios

**Grammar template:**
``` text
"I'll check the current status of the ImpressionCore documentation system to provide you with up-to-date statistics."

[Execute system status tool]

"The IDS system currently indexes [number] files with [number] metadata entries and [number] tags. The system is operating normally and contains comprehensive documentation across [categories]."
```

#### 5. Tag-Based File Discovery (`mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_find-by-tag`)

**Purpose:** Find files associated with specific tags using AND/OR logic for precise discovery.

**When to use:**

- User wants files related to specific topics or categories
- Need to find all documentation in a particular area
- Looking for comprehensive coverage of specific subjects
- Filtering results by multiple criteria

**Grammar template:**
``` text
"I'll search for all files tagged with [tags] to find comprehensive documentation on [topic]."

[Execute tag search tool]

"I found [number] files that match the specified tags. These documents provide [description of coverage] and include [key findings]."
```

---

## Advanced Usage Patterns

### Sequential Tool Usage

When handling complex queries, use tools in logical sequence:

1. **Start with system status** to understand scope
2. **Use tag listing** to explore available categories
3. **Perform targeted searches** with discovered tags
4. **Get specific file information** for detailed context
5. **Use tag-based discovery** for comprehensive coverage

### Error Handling Grammar

When tools return errors or no results:
``` text
"The search didn't return any results for [query]. Let me try a broader search approach or explore related tags to find the information you're looking for."
```

### Result Synthesis

When combining information from multiple tools:
``` text
"Based on my analysis of the documentation using multiple search approaches, here's what I found about [topic]: [synthesized information]. This information comes from [number] documents across [categories]."
```

---

## Best Practices for Documentation Assistance

### Information Gathering

- **Always search first** before stating that information doesn't exist
- **Use multiple search strategies** if initial searches don't yield results
- **Cross-reference findings** using different tools for verification
- **Provide source attribution** by mentioning specific files when possible

### Response Structure

1. **Acknowledge the request** with proper grammar
2. **Explain your search strategy** briefly
3. **Present findings clearly** with proper formatting
4. **Provide actionable information** when possible
5. **Offer follow-up assistance** for related topics

### Context Awareness

- **Remember previous searches** in the conversation
- **Build upon earlier findings** for comprehensive assistance
- **Suggest related topics** based on discovered tags
- **Maintain conversation continuity** while being thorough

---

## Example Complete Interaction

**User Query:** "How do I set up the authentication system?"

**AI Response Pattern:**
``` text
I'll help you find information about setting up the authentication system in ImpressionCore. Let me search the documentation for relevant details.

[Execute mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_search with query: "authentication setup" and tags: ["authentication", "setup", "security"]]

Based on the search results, I found [X] documents that cover authentication setup. The main implementation guide is located in [filename] and provides step-by-step instructions for [details].

[If needed, execute mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-file-info for specific files]

The authentication system documentation was last updated on [date] and includes comprehensive information about [features]. Would you like me to search for any specific aspect of the authentication setup, such as API key configuration or user management?
```

---

## Grammar Checklist for MCP Tool Usage

- ✅ Use proper subject-verb agreement
- ✅ Employ consistent verb tenses
- ✅ Structure sentences clearly with appropriate punctuation
- ✅ Use active voice for clarity
- ✅ Maintain parallel structure in lists
- ✅ Use appropriate transitional phrases
- ✅ Employ proper capitalization and formatting
- ✅ Write complete, well-formed sentences
- ✅ Use appropriate professional vocabulary
- ✅ Maintain consistent terminology throughout responses

This comprehensive approach ensures effective utilization of the IDS MCP Server while maintaining high standards of written communication.
