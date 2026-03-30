# ImpressionCore B3 Phase 2 Fine-Tuned Model Evaluation Report

**Created:** October 04, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\analysis\B3_FINETUNED_EVALUATION_REPORT_20251004_085218.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Generated:** October 04, 2025 08:53:09
**Model:** b3_finetuned_best.pth
**Device:** cuda

## Executive Summary

- **Total Tests:** 25
- **Success Rate:** 100.0%
- **Average Quality:** 3.12/5
- **Model Responses:** 4 (16.0%)
- **Fallback Rate:** 84.0%

## Phase Comparison

| Metric | Baseline | Phase 1 | Phase 2 | Change from Phase 1 |
|--------|----------|---------|---------|---------------------|
| Success Rate | 68.0% | 100.0% | 100.0% | - |
| Avg Quality | 3.32/5 | 4.32/5 | 3.12/5 | -1.20 |
| Fallback Rate | 0.0% | 20.0% | 84.0% | 64.0pp |

## Category Performance

### GREETINGS

- **Average Score:** 3.20/5
- **Fallback Rate:** 80.0%
- **Model Responses:** 1/5

**Test Results:**

- **Prompt:** "Hello"
  - Score: 4.0/5
  - Confidence: 0.90

- **Prompt:** "Hi there" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Good morning" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "How are you?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "What's up?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

### ASSISTANCE

- **Average Score:** 3.00/5
- **Fallback Rate:** 80.0%
- **Model Responses:** 1/5

**Test Results:**

- **Prompt:** "Can you help me?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "I need assistance"
  - Score: 3.0/5
  - Confidence: 0.60

- **Prompt:** "I have a question" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Please explain" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "I don't understand" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

### AI_KNOWLEDGE

- **Average Score:** 3.20/5
- **Fallback Rate:** 80.0%
- **Model Responses:** 1/5

**Test Results:**

- **Prompt:** "What is AI?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Explain machine learning"
  - Score: 4.0/5
  - Confidence: 0.90

- **Prompt:** "What are neural networks?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "How does deep learning work?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "What is natural language processing?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

### CONTEXT

- **Average Score:** 3.20/5
- **Fallback Rate:** 80.0%
- **Model Responses:** 1/5

**Test Results:**

- **Prompt:** "Tell me more"
  - Score: 4.0/5
  - Confidence: 0.90

- **Prompt:** "Can you elaborate?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "What do you mean?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Are you intelligent?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "What can you do?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

### COMPLEX

- **Average Score:** 3.00/5
- **Fallback Rate:** 100.0%
- **Model Responses:** 0/5

**Test Results:**

- **Prompt:** "Explain the difference between AI and machine learning" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "How do transformers work in natural language processing?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "What is the relationship between deep learning and neural networks?" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Compare supervised and unsupervised learning" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50

- **Prompt:** "Describe the attention mechanism in neural networks" [FALLBACK]
  - Score: 3.0/5
  - Confidence: 0.50
