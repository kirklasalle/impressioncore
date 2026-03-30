# IDS MCP Search Criteria Analysis

**Created:** June 10, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\ids_search_criteria_analysis.md #api #deployment #documentation #pytorch #testing  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 🔍 Search Functionality Analysis

### ✅ WORKING SEARCH PATTERNS

#### 1. Single Word Searches

- **Format:** Single words without spaces
- **Examples:** 
  - `python` → 923 results
  - `environment` → 51 results  
  - `system` → 190 results
  - `administration` → 2 results
  - `guide` → 198 results

#### 2. Underscore-Separated Terms

- **Format:** Multi-word terms connected with underscores
- **Examples:**
  - `python_environment` → 9 results
  - `documentation_system` → 63 results
  - `deployment_guide` → 1 result

#### 3. Exact Tag Name Matching

- **Format:** Complete tag names as they appear in the system
- **Examples:**
  - `impressioncore_system_administration_guide` → 1 result
  - `impressioncore_documentation_system` → multiple results

### ❌ NON-WORKING SEARCH PATTERNS

#### 1. Space-Separated Terms

- **Format:** Multi-word terms with spaces
- **Failed Examples:**
  - `system administration guide` → 0 results
  - `deployment guide` → 0 results
  - `python function` → 0 results
  - `ImpressionCore documentation system` → 0 results

#### 2. Hyphen-Separated Terms

- **Format:** Multi-word terms with hyphens
- **Failed Examples:**
  - `system-administration` → 0 results

#### 3. Mixed Case or Special Characters

- **Format:** Terms with mixed capitalization or special characters
- **Analysis:** Case sensitivity may be a factor

## 📋 SEARCH RULES DISCOVERED

### Core Search Principles

1. **Tag-Based Matching:** Search appears to match against indexed tags, not full-text content
2. **Exact Matching:** Search looks for exact tag matches or partial tag matches
3. **Underscore Convention:** Multi-word concepts use underscore separation in tags
4. **No Space Handling:** Spaces in search queries are not processed correctly
5. **Case Sensitivity:** May be case-sensitive (requires further testing)

### Recommended Search Strategies

#### For Users:

1. **Start Simple:** Use single words first (`python`, `guide`, `system`)
2. **Add Underscores:** For multi-word concepts, try underscore format (`python_environment`)
3. **Check Tag Lists:** Use `list-tags` to find exact tag names
4. **Build from Results:** Use results from simple searches to find more specific tags

#### For Developers:

1. **Tag Standardization:** Ensure consistent underscore-separated tag naming
2. **Search Enhancement:** Consider adding space-to-underscore preprocessing
3. **Documentation:** Provide clear search syntax guidance to users
4. **Index Optimization:** Review tag indexing process for better search coverage

## 🎯 SEARCH OPTIMIZATION RECOMMENDATIONS

### Immediate Improvements

1. **Search Preprocessing:**

   ```python

   # Convert spaces to underscores for search

   search_query = query.replace(" ", "_").lower()
   ```

2. **Multi-Strategy Search:**

   ```python

   # Try multiple search patterns

   patterns = [
       query,                          # Original
       query.replace(" ", "_"),        # Underscored
       query.replace(" ", ""),         # No spaces
       query.lower()                   # Lowercase
   ]
   ```

3. **Search Suggestion System:**
   - Suggest related tags when no results found
   - Provide "did you mean" functionality
   - Show popular search terms

### Tag System Improvements

1. **Consistent Naming:** Standardize all tags to use underscore separation
2. **Synonym Support:** Add tag aliases for common search terms
3. **Hierarchical Tags:** Implement tag categories for better organization
4. **Search Indexing:** Improve full-text search alongside tag matching

## 📊 SEARCH PERFORMANCE METRICS

| Search Type | Success Rate | Example Results |
|-------------|-------------|-----------------|
| Single Words | 100% | `python` (923), `guide` (198) |
| Underscore Terms | 100% | `python_environment` (9) |
| Exact Tag Names | 100% | `impressioncore_system_administration_guide` (1) |
| Space-Separated | 0% | All tested queries failed |
| Hyphen-Separated | 0% | All tested queries failed |

## 🚀 USER GUIDANCE

### How to Search Effectively

1. **Start with Keywords:** Use single, relevant words
2. **Connect with Underscores:** For multi-word concepts, use `word_word` format
3. **Browse Tags First:** Use `list-tags` to discover available search terms
4. **Iterate and Refine:** Build complex searches from simple successful ones

### Common Search Patterns

- **Technology:** `python`, `pytorch`, `api`
- **Documentation:** `guide`, `documentation`, `reference`  
- **System Areas:** `deployment`, `administration`, `environment`
- **Components:** `core`, `frontend`, `backend`

**Search Success Formula:** `Single_Words_With_Underscores`

---

**Analysis Conclusion:** The IDS search system uses tag-based matching with underscore-separated multi-word terms. Spaces and hyphens are not supported. This explains why previous searches failed and provides clear guidance for effective searching.
