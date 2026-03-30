# Phase 3: RAG Quality Optimization Strategy

**Created:** October 04, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\analysis\phase3_quality_optimization_strategy.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Context:** IPA research blocked by search API issues, corpus generation blocked by Unicode errors

---

## 🎯 OBJECTIVE

**Problem:** RAG retrieval works (64.3% success) but response quality is poor (0.81/5.0)  
**Examples:**

- Query: "Show me pictures of cats" → Response: "I'm here to assist. What would you like to know?"
- Query: "How's the weather?" → Response: "AI: AI: Machine" (truncated/incoherent)

**Root Cause Hypothesis:** Retrieved context is not being properly utilized by the model  
**Target:** Improve quality from 0.81/5.0 to 4.0+/5.0 without changing retrieval system

---

## 📊 CURRENT SYSTEM STATE

``` text
Knowledge Base: 1,284,923 embeddings
Performance: 64.3% RAG usage, 78.6% success rate
Quality Issue: Retrieved context exists but isn't used effectively

Test Example (Educational):
- Query: "What is photosynthesis?"
- Retrieved: 3 docs, confidence 0.262
- Response: Generic/irrelevant instead of using retrieved educational content
```

---

## 🔬 ROOT CAUSE ANALYSIS

Based on `b3_rag_infrastructure.py` and test results:

### **1. Context Not Injected into Prompt**

**Current Code (Line ~600-650):**

```python
def generate_response(self, query: str, retrieved_docs: List[Dict]) -> str:
    # Retrieved docs are fetched but...
    # NO EXPLICIT CONTEXT INJECTION INTO PROMPT
    
    # Model generates response without context guidance
    response = self.model.generate(...)
    return response
```

**Problem:** Model doesn't know it should use retrieved documents  
**Fix:** Inject context explicitly into prompt template

---

### **2. No Prompt Engineering for RAG**

**Current Behavior:**

- Query passed directly to model
- No instruction to "use provided context"
- No formatting of retrieved documents
- No quality enforcement instructions

**Required Prompt Structure:**

``` text
System: You are a helpful AI assistant. Use the provided context to answer accurately.

Context:
- [Doc 1 content] (confidence: 0.85)
- [Doc 2 content] (confidence: 0.72)
- [Doc 3 content] (confidence: 0.61)

User Question: {query}

Instructions:
1. Answer based on the context provided above
2. If context is insufficient, say "I don't have enough information"
3. Be specific and cite relevant details from the context
4. Keep responses concise and relevant

Your Answer:
```

---

### **3. No Context Formatting**

**Current State:** Retrieved docs are Dict objects with metadata  
**Problem:** Model receives unstructured data  
**Fix:** Format docs into readable, numbered list with confidence scores

---

### **4. No "Insufficient Context" Handling**

**Current Behavior:** Model generates generic response even when docs are irrelevant  
**Fix:** Add confidence threshold check and explicit "no answer" instruction

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Immediate Fixes (1 hour) - TONIGHT**

#### **1.1: Create RAG Prompt Template**

**File:** `src/inference/b3_rag_infrastructure.py`  
**Location:** Add after line 580

```python
def format_rag_prompt(self, query: str, retrieved_docs: List[Dict]) -> str:
    """
    Format RAG prompt with explicit context injection.
    
    Args:
        query: User's question
        retrieved_docs: Retrieved documents with metadata
    
    Returns:
        Formatted prompt string with context and instructions
    """
    # Format context from retrieved docs
    if not retrieved_docs or len(retrieved_docs) == 0:
        context_text = "No relevant context available."
    else:
        context_lines = []
        for i, doc in enumerate(retrieved_docs[:5], 1):  # Top 5 docs
            text = doc.get('text', doc.get('chunk', 'N/A'))
            conf = doc.get('similarity', doc.get('score', 0.0))
            context_lines.append(f"{i}. {text[:200]}... (confidence: {conf:.3f})")
        context_text = "\n".join(context_lines)
    
    # Build RAG prompt with explicit instructions
    prompt = f"""System: You are a helpful AI assistant for ImpressionCore. Use the provided context to answer user questions accurately and specifically.

Context Information:
{context_text}

User Question: {query}

Instructions:
1. Base your answer primarily on the context provided above
2. If the context is insufficient or irrelevant (confidence < 0.3), respond with "I don't have specific information about that. Could you rephrase or ask something else?"
3. Be specific and reference details from the context when answering
4. Keep responses concise (2-3 sentences maximum)
5. Do not repeat the question or say "AI:"

Your Answer:"""
    
    return prompt
```

#### **1.2: Update `generate_response()` Method**

**File:** `src/inference/b3_rag_infrastructure.py`  
**Location:** Line ~600-650 (wherever generate_response is)

```python
def generate_response(self, query: str, category: str = "general") -> Dict[str, any]:
    """Generate response using RAG with proper context injection."""
    
    # Step 1: Retrieve documents (existing code works)
    retrieved_docs = self.retrieve(query, category=category)
    
    # Step 2: Format RAG prompt (NEW - use created method)
    rag_prompt = self.format_rag_prompt(query, retrieved_docs)
    
    # Step 3: Generate response with injected context (MODIFIED)
    response = self.model.generate(
        rag_prompt,  # Use formatted prompt instead of raw query
        max_length=150,  # Limit response length
        temperature=0.7,  # Balanced creativity
        top_p=0.9,
        do_sample=True
    )
    
    # Step 4: Return with metadata
    return {
        "response": response,
        "retrieved_docs": retrieved_docs,
        "rag_prompt_used": rag_prompt,  # For debugging
        "category": category
    }
```

#### **1.3: Add Confidence-Based Filtering**

**Location:** In `format_rag_prompt()` method

```python
# Filter out low-confidence docs
high_conf_docs = [doc for doc in retrieved_docs if doc.get('similarity', 0) >= 0.25]

if len(high_conf_docs) == 0:
    # No confident results - return "no info" instruction
    return f"""System: You are a helpful AI assistant.

User Question: {query}

Context: No relevant information found in the knowledge base.

Your Answer: I don't have specific information about that in my knowledge base. Could you rephrase your question or ask something else I might be able to help with?"""
```

---

### **Phase 2: Enhanced Improvements (2 hours) - TOMORROW**

#### **2.1: Category-Specific Prompt Templates**

Different categories need different instruction styles:

**Educational:**

```python
Instructions:
1. Explain concepts clearly and simply
2. Use analogies or examples from the context
3. Break down complex topics into steps
4. Define technical terms if present
```

**Multimodal:**

```python
Instructions:
1. Describe visual elements in detail (colors, objects, composition)
2. Reference specific image features from the context
3. Use descriptive language for non-visual users
```

**Conversational:**

```python
Instructions:
1. Provide a friendly, natural response
2. Use the context to give specific, helpful information
3. Be concise but warm in tone
```

#### **2.2: Response Quality Validation**

Add post-generation quality checks:

```python
def validate_response_quality(self, response: str, query: str, docs: List[Dict]) -> float:
    """
    Validate response quality against retrieved context.
    
    Returns quality score 0-5:
    - 0: Generic/useless response
    - 1-2: Partially relevant
    - 3-4: Good use of context
    - 5: Excellent, specific answer
    """
    quality_score = 0.0
    
    # Check 1: Not generic boilerplate
    generic_phrases = [
        "I'm here to assist",
        "How can I help",
        "What would you like to know",
        "AI: AI:",
        "I don't know"
    ]
    if not any(phrase in response for phrase in generic_phrases):
        quality_score += 1.5
    
    # Check 2: Contains words from retrieved context
    if docs:
        doc_words = set()
        for doc in docs[:3]:
            text = doc.get('text', doc.get('chunk', ''))
            doc_words.update(text.lower().split())
        
        response_words = set(response.lower().split())
        overlap = len(response_words & doc_words)
        
        if overlap >= 5:  # At least 5 words from context
            quality_score += 2.0
        elif overlap >= 2:
            quality_score += 1.0
    
    # Check 3: Response length reasonable (not too short/long)
    word_count = len(response.split())
    if 10 <= word_count <= 100:
        quality_score += 1.0
    
    # Check 4: No repetition or corruption
    if "AI: AI:" not in response and response.count(response.split()[0]) < 3:
        quality_score += 0.5
    
    return min(quality_score, 5.0)
```

#### **2.3: Iterative Response Refinement**

If quality check fails, retry with modified prompt:

```python
def generate_with_quality_check(self, query: str, category: str, max_retries=2) -> Dict:
    """Generate response with quality validation and retry."""
    
    for attempt in range(max_retries):
        # Generate response
        result = self.generate_response(query, category)
        
        # Validate quality
        quality = self.validate_response_quality(
            result['response'],
            query,
            result['retrieved_docs']
        )
        
        if quality >= 3.0:
            result['quality_score'] = quality
            result['attempts'] = attempt + 1
            return result
        
        # Low quality - modify prompt and retry
        if attempt < max_retries - 1:
            result['rag_prompt_used'] += "\n\nIMPORTANT: Provide a specific, detailed answer using the context above. Do not give generic responses."
    
    # Return best attempt even if quality is low
    result['quality_score'] = quality
    result['attempts'] = max_retries
    return result
```

---

### **Phase 3: Advanced Optimizations (2 hours) - NEXT DAY**

#### **3.1: Multi-Turn Context Memory**

Keep conversation history for context:

```python
class ConversationalRAG:
    def __init__(self):
        self.conversation_history = []
        self.max_history = 5
    
    def add_to_history(self, query: str, response: str):
        self.conversation_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time()
        })
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def format_history_context(self) -> str:
        """Format conversation history for context."""
        if not self.conversation_history:
            return ""
        
        history_lines = ["Recent Conversation:"]
        for turn in self.conversation_history[-3:]:  # Last 3 turns
            history_lines.append(f"User: {turn['query']}")
            history_lines.append(f"Assistant: {turn['response'][:100]}...")
        
        return "\n".join(history_lines)
```

#### **3.2: Re-ranking Retrieved Documents**

Use cross-encoder to re-rank docs for better relevance:

```python
from sentence_transformers import CrossEncoder

def rerank_documents(self, query: str, docs: List[Dict], top_k=5) -> List[Dict]:
    """Re-rank documents using cross-encoder for better relevance."""
    
    if not hasattr(self, 'reranker'):
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Prepare pairs for re-ranking
    pairs = [(query, doc.get('text', doc.get('chunk', ''))) for doc in docs]
    
    # Get cross-encoder scores
    scores = self.reranker.predict(pairs)
    
    # Re-rank by cross-encoder score
    for doc, score in zip(docs, scores):
        doc['rerank_score'] = float(score)
    
    reranked = sorted(docs, key=lambda x: x['rerank_score'], reverse=True)
    return reranked[:top_k]
```

#### **3.3: Fallback Response Strategies**

Graceful degradation when RAG fails:

```python
def get_fallback_response(self, query: str, category: str) -> str:
    """Provide fallback when RAG fails."""
    
    fallback_map = {
        "educational": "I don't have specific educational content on that topic in my knowledge base. Could you ask about another subject like math, science, or history?",
        
        "multimodal": "I don't have relevant images or visual content for that query. Try asking for specific objects, scenes, or people.",
        
        "conversational": "I'm not sure about that. Could you rephrase your question or ask something else?",
        
        "general": "I don't have information on that topic. Is there something else I can help with?"
    }
    
    return fallback_map.get(category, fallback_map["general"])
```

---

## 📈 EXPECTED IMPACT

### **After Phase 1 (Tonight):**

- Quality: 0.81 → **2.5-3.5** / 5.0 (+200-300% improvement)
- Responses use retrieved context instead of generic text
- No more "I'm here to assist" non-answers
- Proper handling of low-confidence results

### **After Phase 2 (Tomorrow):**

- Quality: 3.5 → **4.0-4.5** / 5.0
- Category-specific optimizations
- Automatic quality validation
- Iterative refinement for better answers

### **After Phase 3 (Next Day):**

- Quality: 4.5 → **4.5-5.0** / 5.0 (production-ready)
- Conversation memory for multi-turn dialogs
- Re-ranking for optimal document selection
- Graceful fallbacks for edge cases

---

## 🧪 TESTING STRATEGY

### **Quick Validation (After Each Phase):**

```bash
# Run existing test suite
python src/inference/test_expanded_rag.py

# Check quality scores in output
# Before: avg_quality ~0.81
# Target: avg_quality >4.0
```

### **Manual Spot Checks:**

```python
# Test 1: Educational query
query = "What is photosynthesis?"
# Expected: Uses educational context, explains process clearly

# Test 2: Multimodal query  
query = "Show me pictures of cats"
# Expected: Describes cat images from retrieved context

# Test 3: Conversational query
query = "How's the weather?"
# Expected: "I don't have weather information" (no context available)

# Test 4: Low confidence
query = "asdfghjkl nonsense query"
# Expected: "I don't have relevant information, could you rephrase?"
```

---

## 🎯 SUCCESS CRITERIA

**MUST ACHIEVE:**

- [ ] Quality score >= 4.0/5.0 (up from 0.81)
- [ ] Zero generic "I'm here to assist" responses
- [ ] Proper use of retrieved context in answers
- [ ] Graceful handling of low-confidence/no-context cases

**NICE TO HAVE:**

- [ ] Conversation history integration
- [ ] Re-ranking for better relevance
- [ ] Category-specific prompt templates
- [ ] Iterative refinement with quality validation

---

## 🚨 BLOCKERS RESOLUTION

### **IPA Research Blocked:**

- ✅ **RESOLVED:** Created practical strategy from existing ImpressionCore knowledge
- Alternative: Manual research if time permits tomorrow

### **Corpus Generation Blocked:**

- 🔄 **DEFERRED:** Unicode errors with Rich library in Windows PowerShell
- Alternative: Generate corpus in WSL or fix Unicode handling
- Impact: Educational corpus needed later, doesn't block quality improvements

---

## 📅 REVISED TIMELINE

**Tonight (Oct 4, 11:40 PM - 12:30 AM):**

- ✅ Create quality optimization strategy (DONE - this document)
- 🔄 NEXT: Implement Phase 1 fixes (1 hour)
- 🔄 Test and validate improvements

**Tomorrow (Oct 5):**

- Phase 2 enhancements (2 hours)
- Full test suite validation
- Expected: 70% RAG, 4.0+ quality ✅

**Next Day (Oct 6):**

- Phase 3 advanced optimizations
- Fix corpus generation Unicode issues
- Integrate educational corpus
- Expected: 77%+ RAG, 4.5+ quality ✅ PRODUCTION READY

---

## 🎓 KEY INSIGHTS

1. **RAG retrieval is working** - 64.3% success proves the system can find relevant docs
2. **Problem is utilization, not retrieval** - Context isn't being used by model
3. **Prompt engineering is critical** - Explicit instructions dramatically improve quality
4. **Quality validation enables iteration** - Retry with better prompts if first attempt fails
5. **Category-specific optimization needed** - Different query types need different approaches

---

**STATUS:** Ready to implement Phase 1 - Context injection and prompt engineering
**NEXT ACTION:** Modify `b3_rag_infrastructure.py` with Phase 1 fixes
**ESTIMATED TIME:** 60 minutes to implement + 15 minutes to test
**EXPECTED RESULT:** Quality 0.81 → 3.0+ / 5.0

---

*Document created by GitHub Copilot based on ImpressionCore Phase 3 RAG optimization analysis*
