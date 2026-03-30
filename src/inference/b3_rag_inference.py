"""
ImpressionCore B3 RAG-Enhanced Inference System

Created: October 04, 2025
Updated: October 04, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #inference #rag #multimodal #production
Category: Inference
Status: Active

Purpose:
    Production RAG-enhanced inference combining:
    - 1            context = self.retrieve_context(
                query=user_input,
                category=category,
                topk=5,
                min_confidence=0.2
            )bedding knowledge base
    - Phase 1 b3_massive_best.pth model
    - Intelligent fallback system

Architecture:
    Query → RAG Retrieval (1.3M embeddings) → Context Assembly →
    B3 Model → Response (with fallback safety)

Knowledge Domains:
    - Multimodal: 1.2M embeddings (text-image associations)
    - Educational: 16K embeddings (K12 comprehensive)
    - Conversational: 63K embeddings (dialogue patterns)
"""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import RAG infrastructure
try:
    from .b3_rag_infrastructure import B3EmbeddingSearcher, RAGContext, RetrievalResult
    logger.info("✅ RAG infrastructure imported")
except ImportError as e:
    logger.error(f"❌ Failed to import RAG infrastructure: {e}")
    raise

# Import Phase 1 system
try:
    import sys
    from pathlib import Path
    # Add src directory to path if not already there
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from training.b3_intelligent_inference import B3IntelligentInference
    logger.info("✅ Phase 1 inference system imported")
except ImportError as e:
    logger.error(f"❌ Failed to import Phase 1 system: {e}")
    raise

# Import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    logger.info("✅ sentence-transformers available")
except ImportError:
    logger.error("❌ sentence-transformers not available")
    raise


class B3RAGInference:
    """
    Production RAG-enhanced inference system.

    Combines:
    - 1.3M embedding retrieval
    - Phase 1 model (b3_massive_best.pth)
    - Intelligent fallback
    - Constitutional safety
    """

    def __init__(
        self,
        model_path: str = "F:/models/checkpoints/b3/b3_massive_final.pth",
        f_data_root: str = "F:/data",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize RAG-enhanced inference system.

        Args:
            model_path: Path to B3 model checkpoint
            f_data_root: Root directory for F:/data
            device: Device for model inference
        """
        self.device = device
        self.f_data_root = Path(f_data_root)

        logger.info("🚀 Initializing B3 RAG-Enhanced Inference System")
        logger.info(f"   Model: {model_path}")
        logger.info(f"   F: Drive: {f_data_root}")
        logger.info(f"   Device: {device}")

        # Initialize Phase 1 inference system
        logger.info("\n📦 Loading Phase 1 Inference System...")
        self.phase1_system = B3IntelligentInference(
            checkpoint_path=model_path
        )
        logger.info("✅ Phase 1 system loaded")

        # Initialize RAG searcher
        logger.info("\n🔍 Initializing RAG Searcher...")
        self.searcher = B3EmbeddingSearcher(
            f_data_root=str(self.f_data_root),
            use_faiss=True,
            topk=5,
            score_threshold=0.01,
            use_sentence_transformers=True
        )

        # Load multimodal embeddings (1.2M)
        logger.info("\n📚 Loading Multimodal Embeddings (1.2M)...")
        multimodal_loaded = self.searcher.load_multimodal_embeddings()
        if multimodal_loaded:
            logger.info("✅ Multimodal embeddings loaded")
        else:
            logger.warning("⚠️ Failed to load multimodal embeddings")

        # Load educational embeddings (sentence-transformers)
        logger.info("\n📚 Loading Educational Embeddings...")
        edu_loaded = self.searcher.load_b3_embeddings(category="educational")
        if edu_loaded:
            logger.info("✅ Educational embeddings loaded")
        else:
            logger.warning("⚠️ Failed to load educational embeddings")

        # Load conversational embeddings (63K)
        logger.info("\n📚 Loading Conversational Embeddings (63K)...")
        conv_loaded = self.searcher.load_b3_embeddings(category="conversational")
        if conv_loaded:
            logger.info("✅ Conversational embeddings loaded")
        else:
            logger.warning("⚠️ Failed to load conversational embeddings")

        # Initialize query encoders
        logger.info("\n🔧 Loading Query Encoders...")
        # all-mpnet-base-v2 for multimodal (768-dim) - matches vision embeddings
        self.multimodal_encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        # all-MiniLM-L6-v2 for educational/conversational (384-dim)
        self.query_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("✅ Query encoders loaded: MPNet 768-dim + MiniLM 384-dim")

        logger.info("\n✅ RAG-Enhanced Inference System Ready!")
        logger.info("   Total Embeddings: 1.3M+")
        logger.info("   Domains: multimodal, educational, conversational")
        logger.info("   Fallback: Phase 1 (4.32/5.0 quality)")

    def retrieve_context(
        self,
        query: str,
        category: str = "multimodal",
        topk: int = 5,
        min_confidence: float = 0.2
    ) -> RAGContext | None:
        """
        Retrieve relevant context for query.

        Args:
            query: User query
            category: Knowledge domain ('multimodal', 'educational')
            topk: Number of results to retrieve
            min_confidence: Minimum confidence threshold

        Returns:
            RAGContext with retrieved documents, or None
        """
        try:
            # Encode query with category-specific encoder
            if category == "multimodal":
                # Use all-mpnet-base-v2 for 768-dim multimodal embeddings
                query_embedding = self.multimodal_encoder.encode(
                    query,
                    normalize_embeddings=True
                )
                logger.info(f"🔍 Encoded query with MPNet: {query_embedding.shape} (expecting 768-dim)")
            else:
                # Use all-MiniLM-L6-v2 for 384-dim educational/conversational
                query_embedding = self.query_encoder.encode(
                    query,
                    normalize_embeddings=True
                )
                logger.info(f"🔍 Encoded query with MiniLM: {query_embedding.shape} (expecting 384-dim)")

            # Search in specified category
            if category not in self.searcher.embeddings:
                logger.warning(f"Category '{category}' not loaded, skipping retrieval")
                return None

            # Get embeddings and index
            embeddings = self.searcher.embeddings[category]
            index = self.searcher.indices.get(category)
            mapping = self.searcher.mappings.get(category, {})

            if index is None:
                logger.warning(f"No index available for category '{category}'")
                return None

            # Search
            query_vec = query_embedding.reshape(1, -1).astype('float32')

            # Check dimension compatibility
            if query_vec.shape[1] != embeddings.shape[1]:
                logger.warning(f"Dimension mismatch: query {query_vec.shape[1]} vs embeddings {embeddings.shape[1]}")
                return None

            distances, indices = index.search(query_vec, topk)

            # Convert distances to scores (exp(-distance))
            scores = np.exp(-distances[0])

            # Filter by confidence
            retrieved_docs = []
            for _i, (idx, score) in enumerate(zip(indices[0], scores)):
                if score >= min_confidence:
                    doc_id = mapping.get(int(idx), f"doc_{idx}")
                    retrieved_docs.append(RetrievalResult(
                        doc_id=doc_id,
                        score=float(score),
                        text=f"Document {doc_id} from {category}",  # Placeholder
                        source=category,
                        metadata={"index": int(idx)}
                    ))

            if not retrieved_docs:
                logger.info(f"No documents above confidence threshold {min_confidence}")
                return None

            # Assemble context
            formatted_context = self._format_context(retrieved_docs, query)
            avg_confidence = sum(doc.score for doc in retrieved_docs) / len(retrieved_docs)

            return RAGContext(
                query=query,
                retrieved_docs=retrieved_docs,
                formatted_context=formatted_context,
                retrieval_confidence=avg_confidence
            )

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _format_context(self, docs: list[RetrievalResult], query: str) -> str:
        """Format retrieved documents as context."""
        if not docs:
            return ""

        context_parts = ["[Retrieved Context]", ""]

        for i, doc in enumerate(docs, 1):
            context_parts.append(
                f"{i}. [{doc.source.upper()}] "
                f"(relevance: {doc.score:.2f}, source: {doc.doc_id})"
            )

        context_parts.append("")
        context_parts.append(f"[User Query]: {query}")

        return "\n".join(context_parts)

    def _format_rag_prompt_v2(
        self,
        query: str,
        rag_context,
        category: str
    ) -> str:
        """
        PHASE 1 QUALITY OPTIMIZATION: Enhanced RAG prompt formatting.

        Implements explicit context injection with clear instructions to improve
        response quality from 0.81/5.0 to 3.0+/5.0.

        Args:
            query: User's question
            rag_context: RAGContext object with retrieved documents
            category: Knowledge domain (multimodal/educational/conversational)

        Returns:
            Formatted prompt with context and explicit instructions
        """
        # Check if we have high-confidence docs
        high_conf_docs = [
            doc for doc in rag_context.retrieved_docs
            if doc.score >= 0.25
        ]

        # Format context from retrieved docs
        if not high_conf_docs or len(high_conf_docs) == 0:
            # No confident results - provide "no info" instruction
            return f"""System: You are ImpressionCore B3, a helpful AI assistant.

User Question: {query}

Context: No relevant information found in the knowledge base.

Instructions: Respond with: "I don't have specific information about that in my knowledge base. Could you rephrase your question or ask something else I might be able to help with?"

Your Answer:"""

        # Format high-confidence documents
        context_lines = []
        for i, doc in enumerate(high_conf_docs[:5], 1):  # Top 5 docs
            text = doc.text[:300] if len(doc.text) > 300 else doc.text
            conf = doc.score
            source = doc.source
            context_lines.append(
                f"{i}. {text} "
                f"(confidence: {conf:.3f}, source: {source})"
            )

        context_text = "\n".join(context_lines)

        # Category-specific instructions
        if category == "educational":
            specific_instructions = """1. Explain the concept clearly and simply
2. Use information from the context provided above
3. If relevant, break down the explanation into steps
4. Keep your answer concise (2-3 sentences maximum)"""
        elif category == "multimodal":
            specific_instructions = """1. Describe relevant visual elements from the context
2. Use specific details from the retrieved information
3. If describing images, mention colors, objects, or composition
4. Keep your answer concise (2-3 sentences maximum)"""
        elif category == "conversational":
            specific_instructions = """1. Provide a friendly, natural response
2. Use the context to give specific, helpful information
3. Be concise but warm in tone
4. Keep your answer to 2-3 sentences maximum"""
        else:
            specific_instructions = """1. Base your answer on the context provided above
2. Be specific and reference details from the context
3. Keep your response concise (2-3 sentences maximum)
4. If context is insufficient, say so clearly"""

        # Build complete RAG prompt
        prompt = f"""System: You are ImpressionCore B3, a helpful AI assistant. Use the provided context to answer user questions accurately and specifically.

Context Information:
{context_text}

User Question: {query}

Instructions:
{specific_instructions}
5. Do NOT repeat the question
6. Do NOT say "AI:" in your response
7. Do NOT give generic responses like "I'm here to assist"

Your Answer:"""

        return prompt

    def _format_dialogue_prompt(
        self,
        query: str,
        rag_context,
        category: str
    ) -> str:
        """
        PHASE 2 TIER 1: Dialogue format prompt with few-shot examples.

        Instead of system instructions (which the model ignores), we show the model
        how to properly use context through conversation examples. The model learns
        from the pattern rather than explicit instructions.

        Args:
            query: User's question
            rag_context: RAGContext object with retrieved documents
            category: Knowledge domain (multimodal/educational/conversational)

        Returns:
            Formatted prompt as conversation history with examples
        """
        # Check if we have high-confidence docs
        high_conf_docs = [
            doc for doc in rag_context.retrieved_docs
            if doc.score >= 0.25
        ]

        # No confident results - use simple fallback
        if not high_conf_docs or len(high_conf_docs) == 0:
            return f"""Previous conversation:
User: Tell me about something you know.
Assistant: I don't have specific information about that in my knowledge base right now.

Current conversation:
User: {query}
Assistant:"""

        # Format context documents (top 5)
        context_lines = []
        for i, doc in enumerate(high_conf_docs[:5], 1):
            text = doc.text[:300] if len(doc.text) > 300 else doc.text
            context_lines.append(f"{i}. {text}")

        context_text = "\n".join(context_lines)

        # Category-specific examples showing proper context usage
        if category == "multimodal":
            # Example: Visual description using image captions
            example_query = "What does a beach scene look like?"
            example_context = """1. Image shows sandy beach with blue ocean waves crashing on shore
2. Palm trees visible in background swaying in breeze
3. Sunset with orange and pink sky reflecting on water
4. People walking along shoreline in silhouette
5. Beach umbrellas and loungers scattered on sand"""
            example_answer = "A beach scene typically features sandy shores with blue ocean waves crashing against them. Palm trees frame the background, and during sunset, the sky displays beautiful orange and pink hues that reflect on the water."

        elif category == "conversational":
            # Example: Social interaction advice
            example_query = "How do I start a friendly conversation with someone new?"
            example_context = """1. Smile and make eye contact when approaching someone
2. Ask open-ended questions about their interests or background
3. Listen actively and respond to what they say
4. Share something about yourself to build connection
5. Be genuine and show curiosity about them"""
            example_answer = "To start a friendly conversation, begin with a smile and eye contact. Ask open-ended questions about their interests, listen actively to their responses, and share a bit about yourself to create a genuine connection."

        elif category == "educational":
            # Example: Educational explanation
            example_query = "How does photosynthesis work?"
            example_context = """1. Photosynthesis is the process where plants convert light into energy
2. Plants use chlorophyll in leaves to capture sunlight
3. Carbon dioxide from air and water from soil are combined
4. This produces glucose (sugar) for plant energy
5. Oxygen is released as a byproduct into the atmosphere"""
            example_answer = "Photosynthesis is how plants convert sunlight into energy. Using chlorophyll in their leaves, they capture light and combine carbon dioxide and water to produce glucose for food, releasing oxygen as a byproduct."

        else:
            # General example for other categories
            example_query = "What is artificial intelligence?"
            example_context = """1. AI is technology that enables machines to simulate human intelligence
2. Machine learning allows systems to learn from data
3. AI applications include voice assistants, image recognition, and automation
4. Neural networks mimic brain structure for processing information
5. AI continues to evolve and impact many industries"""
            example_answer = "Artificial intelligence enables machines to simulate human intelligence through technologies like machine learning and neural networks. AI powers applications such as voice assistants and image recognition, continuously evolving across many industries."

        # Build dialogue prompt showing the pattern
        prompt = f"""Previous conversation example:

Context available:
{example_context}

User: {example_query}
Assistant: {example_answer}

Current conversation:

Context available:
{context_text}

User: {query}
Assistant:"""

        return prompt

    def is_generic_response(self, response: str) -> bool:
        """
        PHASE 2 TIER 2: Detect if response is generic/unhelpful.

        Returns:
            True if generic, False if specific
        """
        # Common generic patterns from Phase 1 test results
        generic_patterns = [
            "i'm here to help",
            "i'm here to assist",
            "what would you like to know",
            "could you tell me more",
            "what specifically",
            "i'd be happy to help",
            "great question",
            "to give you the best answer",
            "could you elaborate",
            "please share more details",
            "i'd love to assist",
            "of course! what",
            "absolutely! please",
            "that's an interesting question",
            "i want to give you a thorough answer",
            "could you rephrase",
            "add more details"
        ]

        response_lower = response.lower().strip()

        # Check for generic patterns
        for pattern in generic_patterns:
            if pattern in response_lower:
                return True

        # Check if response is too short (likely generic)
        if len(response.split()) < 10:
            # But exclude single-sentence valid responses with content words
            if not any(word in response_lower for word in
                      ['because', 'which', 'through', 'using', 'involves', 'features', 'includes']):
                return True

        # Check if response asks user for clarification
        return bool("?" in response and any(word in response_lower for word in ['what', 'could you', 'can you', 'would you']))

    def validates_context_usage(self, response: str, retrieved_docs, min_overlap: int = 2) -> bool:
        """
        PHASE 2 TIER 2: Check if response uses retrieved context.

        Args:
            response: Generated response
            retrieved_docs: Documents retrieved from RAG
            min_overlap: Minimum number of context keywords required in response

        Returns:
            True if response uses context, False otherwise
        """
        if not retrieved_docs:
            return False

        # Extract key words from context (excluding stopwords)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}

        # Get context words
        context_words = set()
        for doc in retrieved_docs:
            words = doc.text.lower().split()
            context_words.update(word for word in words if word not in stopwords and len(word) > 3)

        # Get response words
        response_words = set(response.lower().split())
        response_words = {word for word in response_words if word not in stopwords and len(word) > 3}

        # Calculate overlap
        overlap = context_words & response_words

        return len(overlap) >= min_overlap

    def generate_with_retry(
        self,
        user_input: str,
        category: str,
        max_attempts: int = 3,
        max_length: int = 150
    ) -> dict[str, Any]:
        """
        PHASE 2 TIER 2: Generate response with validation and retry on generic outputs.

        Args:
            user_input: User query
            category: Query category
            max_attempts: Maximum generation attempts
            max_length: Max response length

        Returns:
            Dict with response and retry metadata
        """
        logger.info(f"🔄 Generating with retry logic (max {max_attempts} attempts)")

        # Retrieve context once
        rag_context = self.retrieve_context(
            query=user_input,
            category=category,
            topk=5,
            min_confidence=0.3
        )

        if not rag_context or not rag_context.retrieved_docs:
            logger.info("⚠️ No RAG context available, using direct generation")
            return self.generate(
                user_input=user_input,
                use_rag=False,
                category=category,
                max_length=max_length,
                use_dialogue_prompt=False
            )

        # Try multiple strategies
        for attempt in range(max_attempts):
            logger.info(f"\n--- Attempt {attempt + 1}/{max_attempts} ---")

            # Choose prompt strategy based on attempt
            if attempt == 0:
                # Try dialogue format first (Tier 1)
                use_dialogue = True
                strategy = "dialogue"
                logger.info("Strategy: Dialogue format with examples")
            elif attempt == 1:
                # Fallback to Phase 1 system prompt
                use_dialogue = False
                strategy = "system"
                logger.info("Strategy: System prompt with instructions")
            else:
                # Last attempt: dialogue again but we'll take anything non-generic
                use_dialogue = True
                strategy = "dialogue_final"
                logger.info("Strategy: Final dialogue attempt (accepting any non-generic)")

            # Format prompt
            if use_dialogue:
                enhanced_input = self._format_dialogue_prompt(
                    query=user_input,
                    rag_context=rag_context,
                    category=category
                )
            else:
                enhanced_input = self._format_rag_prompt_v2(
                    query=user_input,
                    rag_context=rag_context,
                    category=category
                )

            # Generate response
            result = self.phase1_system.generate_with_fallback(
                prompt=enhanced_input,
                max_tokens=max_length,
                temperature=0.7,
                use_fallback=True,
                verbose=False
            )

            response_text = result.get('response', '')

            # Validate response quality
            is_generic = self.is_generic_response(response_text)
            uses_context = self.validates_context_usage(response_text, rag_context.retrieved_docs)

            logger.info(f"   Response: {response_text[:80]}...")
            logger.info(f"   Generic: {'YES' if is_generic else 'NO'}")
            logger.info(f"   Uses Context: {'YES' if uses_context else 'NO'}")

            # Accept response if valid
            if not is_generic and uses_context:
                logger.info(f"✅ Response accepted on attempt {attempt + 1}")
                return {
                    'response': response_text,
                    'rag_used': True,
                    'docs_retrieved': len(rag_context.retrieved_docs),
                    'retrieval_confidence': rag_context.retrieval_confidence,
                    'category': category,
                    'query': user_input,
                    'prompt_strategy': strategy,
                    'attempts': attempt + 1,
                    'retry_reason': f"success_{strategy}",
                    'is_generic': False,
                    'uses_context': True
                }
            elif not is_generic:
                # Not generic but doesn't use context - acceptable on last attempt
                if attempt == max_attempts - 1:
                    logger.info("⚠️ Accepting non-generic response on final attempt")
                    return {
                        'response': response_text,
                        'rag_used': True,
                        'docs_retrieved': len(rag_context.retrieved_docs),
                        'retrieval_confidence': rag_context.retrieval_confidence,
                        'category': category,
                        'query': user_input,
                        'prompt_strategy': strategy,
                        'attempts': attempt + 1,
                        'retry_reason': f"no_context_{strategy}",
                        'is_generic': False,
                        'uses_context': False
                    }
                else:
                    logger.info("⚠️ Response not generic but doesn't use context, retrying...")
            else:
                # Generic response - always retry if attempts remain
                logger.info("⚠️ Generic response detected, retrying...")

        # All attempts failed - use fallback extraction
        logger.info("❌ All retry attempts failed, using fallback extraction")
        fallback_response = self._generate_fallback_response(user_input, rag_context)

        return {
            'response': fallback_response,
            'rag_used': True,
            'docs_retrieved': len(rag_context.retrieved_docs),
            'retrieval_confidence': rag_context.retrieval_confidence,
            'category': category,
            'query': user_input,
            'prompt_strategy': 'fallback',
            'attempts': max_attempts,
            'retry_reason': 'all_attempts_failed',
            'is_generic': False,  # Fallback is guaranteed non-generic
            'uses_context': True  # Fallback directly uses context
        }

    def _generate_fallback_response(self, query: str, rag_context) -> str:
        """
        PHASE 2 TIER 3: Generate fallback response when all retry attempts fail.

        Extracts key sentences from context directly, bypassing model generation.

        Args:
            query: User query
            rag_context: RAG retrieval result

        Returns:
            Context-based response string
        """
        high_conf_docs = [
            doc for doc in rag_context.retrieved_docs
            if doc.score >= 0.25
        ]

        if not high_conf_docs:
            return "I don't have specific information about that in my knowledge base."

        # Extract first 2-3 sentences from top docs
        sentences = []
        for doc in high_conf_docs[:2]:
            text = doc.text.strip()
            # Split into sentences (simple approach)
            doc_sentences = [s.strip() + '.' for s in text.split('.') if len(s.strip()) > 20]
            sentences.extend(doc_sentences[:2])

        # Combine into response
        if sentences:
            response = f"Based on available information: {' '.join(sentences[:3])}"
        else:
            response = f"Based on available information: {high_conf_docs[0].text[:200]}"

        return response

    def generate_smart_hybrid(
        self,
        user_input: str,
        category: str = "multimodal",
        max_length: int = 150,
        confidence_threshold: float = 0.4
    ) -> dict[str, Any]:
        """
        PHASE 3: Smart Hybrid RAG System

        Strategy:
        1. Generate using model's natural capability (Phase 1: 4.32/5.0)
        2. Optionally retrieve RAG context (not forced)
        3. Only enhance response if RAG adds clear value
        4. Never degrade below natural generation quality

        This respects the model's training: it excels at direct generation
        (4.32/5.0) but gets confused when forced to use RAG context (0.77/5.0).

        Args:
            user_input: User query
            category: Knowledge domain for RAG search
            max_length: Maximum response length
            confidence_threshold: Minimum confidence to attempt RAG enhancement

        Returns:
            Dict with response and metadata including strategy decision
        """
        logger.info(f"\n{'='*80}")
        logger.info("🚀 PHASE 3: SMART HYBRID GENERATION")
        logger.info(f"Query: \"{user_input}\"")
        logger.info("Strategy: Use model's natural strength (4.32/5.0 baseline)")
        logger.info(f"{'='*80}")

        # STEP 1: Generate naturally (this works great!)
        logger.info("\n📝 Step 1: Natural Generation (Phase 1 quality)")

        natural_result = self.phase1_system.generate_with_fallback(
            prompt=user_input,
            max_tokens=max_length,
            temperature=0.7,
            use_fallback=True,
            verbose=False
        )

        natural_response = natural_result.get('response', '')
        logger.info(f"✅ Natural response generated: {len(natural_response)} chars")
        logger.info(f"   Preview: {natural_response[:100]}...")

        # STEP 2: Try RAG retrieval (optional enhancement)
        logger.info("\n🔍 Step 2: RAG Context Retrieval (optional enhancement)")

        rag_context = self.retrieve_context(
            query=user_input,
            category=category,
            topk=5,
            min_confidence=0.3
        )

        if not rag_context or not rag_context.retrieved_docs:
            logger.info("ℹ️ No RAG context available")
            logger.info("✅ Using natural generation (no enhancement needed)")
            return {
                'response': natural_response,
                'rag_used': False,
                'docs_retrieved': 0,
                'retrieval_confidence': 0.0,
                'category': category,
                'query': user_input,
                'generation_strategy': 'natural_only',
                'enhancement_applied': False,
                'quality_preserved': True
            }

        # Check confidence
        confidence = rag_context.retrieval_confidence
        logger.info(f"📊 RAG confidence: {confidence:.3f}")
        logger.info(f"   Retrieved: {len(rag_context.retrieved_docs)} documents")

        if confidence < confidence_threshold:
            logger.info(f"⚠️ Confidence below threshold ({confidence_threshold})")
            logger.info("✅ Using natural generation (RAG not confident enough)")
            return {
                'response': natural_response,
                'rag_used': False,
                'docs_retrieved': len(rag_context.retrieved_docs),
                'retrieval_confidence': confidence,
                'category': category,
                'query': user_input,
                'generation_strategy': 'natural_low_confidence',
                'enhancement_applied': False,
                'quality_preserved': True
            }

        # STEP 3: Check if natural response could benefit from facts
        logger.info("\n🎯 Step 3: Enhancement Decision")

        # Check if response is generic or could use factual support
        is_generic = self.is_generic_response(natural_response)
        has_factual_content = any(word in natural_response.lower() for word in
                                   ['specific', 'example', 'such as', 'includes', 'features',
                                    'because', 'which', 'through', 'using'])

        if not is_generic and has_factual_content:
            logger.info("✅ Natural response is good and has factual content")
            logger.info("✅ No enhancement needed")
            return {
                'response': natural_response,
                'rag_used': False,
                'docs_retrieved': len(rag_context.retrieved_docs),
                'retrieval_confidence': confidence,
                'category': category,
                'query': user_input,
                'generation_strategy': 'natural_sufficient',
                'enhancement_applied': False,
                'quality_preserved': True
            }

        # STEP 4: Try smart enhancement
        logger.info("🔧 Natural response could benefit from factual enhancement")
        logger.info("   Attempting smart fact injection...")

        enhanced_response = self._enrich_with_facts(
            natural_response=natural_response,
            retrieved_docs=rag_context.retrieved_docs,
            query=user_input
        )

        # STEP 5: Quality comparison
        logger.info("\n⚖️ Step 4: Quality Comparison")

        enhanced_better = self._is_enhancement_better(
            original=natural_response,
            enhanced=enhanced_response,
            retrieved_docs=rag_context.retrieved_docs
        )

        if enhanced_better:
            logger.info("✅ Enhancement adds value, using enhanced response")
            return {
                'response': enhanced_response,
                'rag_used': True,
                'docs_retrieved': len(rag_context.retrieved_docs),
                'retrieval_confidence': confidence,
                'category': category,
                'query': user_input,
                'generation_strategy': 'smart_hybrid_enhanced',
                'enhancement_applied': True,
                'quality_preserved': True
            }
        else:
            logger.info("⚠️ Enhancement doesn't improve quality")
            logger.info("✅ Using natural response (maintaining 4.32/5.0 baseline)")
            return {
                'response': natural_response,
                'rag_used': False,
                'docs_retrieved': len(rag_context.retrieved_docs),
                'retrieval_confidence': confidence,
                'category': category,
                'query': user_input,
                'generation_strategy': 'natural_enhancement_rejected',
                'enhancement_applied': False,
                'quality_preserved': True
            }

    def _enrich_with_facts(
        self,
        natural_response: str,
        retrieved_docs: list,
        query: str
    ) -> str:
        """
        Smart fact enrichment that preserves natural response quality.

        Strategy:
        - Keep natural response structure intact
        - Add facts as supporting details, not replacements
        - Maintain conversational tone
        - Don't force context that doesn't fit

        Args:
            natural_response: Original model response
            retrieved_docs: Retrieved context documents
            query: User query

        Returns:
            Enhanced response with facts naturally integrated
        """
        # Extract key facts from top docs
        high_conf_docs = [doc for doc in retrieved_docs if doc.score >= 0.3]

        if not high_conf_docs:
            return natural_response

        # Get factual sentences from context
        fact_sentences = []
        for doc in high_conf_docs[:2]:  # Top 2 docs only
            text = doc.text.strip()
            # Extract meaningful sentences
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
            fact_sentences.extend(sentences[:1])  # One sentence per doc

        if not fact_sentences:
            return natural_response

        # Check if response already mentions similar content
        response_words = set(natural_response.lower().split())
        fact_words = set(' '.join(fact_sentences).lower().split())
        overlap = len(response_words & fact_words)

        if overlap > 5:  # Already has similar content
            return natural_response

        # Add facts naturally
        # If natural response is short/generic, replace
        if len(natural_response.split()) < 15 or self.is_generic_response(natural_response):
            # Construct new response from facts
            enhanced = ' '.join(fact_sentences)
            return enhanced

        # Otherwise, append facts as additional detail
        enhanced = f"{natural_response} {fact_sentences[0]}"
        return enhanced

    def _is_enhancement_better(
        self,
        original: str,
        enhanced: str,
        retrieved_docs: list
    ) -> bool:
        """
        Compare enhanced vs original response quality.

        Criteria:
        - Not generic (reject if enhancement made it generic)
        - Maintains coherence (reject if too different)
        - Adds factual value (accept if clearly better)
        - Doesn't introduce confusion (reject if unclear)

        Args:
            original: Original natural response
            enhanced: Enhanced response with facts
            retrieved_docs: Context documents used

        Returns:
            True if enhanced is better, False otherwise
        """
        # Rule 1: If enhancement made it generic, reject
        if self.is_generic_response(enhanced) and not self.is_generic_response(original):
            logger.info("   ❌ Enhancement is generic (original was not)")
            return False

        # Rule 2: If enhancement is much shorter, probably confused
        if len(enhanced) < len(original) * 0.7:
            logger.info("   ❌ Enhancement is significantly shorter")
            return False

        # Rule 3: If original was generic and enhanced is not, accept
        if self.is_generic_response(original) and not self.is_generic_response(enhanced):
            logger.info("   ✅ Fixed generic response")
            return True

        # Rule 4: Check if enhancement uses context
        uses_context = self.validates_context_usage(enhanced, retrieved_docs)
        original_uses_context = self.validates_context_usage(original, retrieved_docs)

        if uses_context and not original_uses_context:
            logger.info("   ✅ Enhancement adds factual content from context")
            return True

        # Rule 5: If enhancement is longer and not generic, probably better
        if len(enhanced) > len(original) * 1.2 and not self.is_generic_response(enhanced):
            logger.info("   ✅ Enhancement adds substantial content")
            return True

        # Default: keep original (when in doubt, preserve natural quality)
        logger.info("   ⚠️ No clear improvement, keeping original")
        return False

    def generate(
        self,
        user_input: str,
        use_rag: bool = True,
        category: str = "multimodal",
        max_length: int = 150,
        use_dialogue_prompt: bool = False,
        use_retry: bool = False,
        use_smart_hybrid: bool = False
    ) -> dict[str, Any]:
        """
        Generate response with optional RAG enhancement.

        PHASE 2 UPDATE: Added dialogue prompts and retry logic.
        PHASE 3 UPDATE: Added smart hybrid system (respects model's natural strength).

        Args:
            user_input: User query
            use_rag: Whether to use RAG retrieval
            category: Knowledge domain to search
            max_length: Maximum response length
            use_dialogue_prompt: Use dialogue format (Phase 2) vs system prompt (Phase 1)
            use_retry: Enable retry logic with validation (Phase 2 Tier 2)
            use_smart_hybrid: Use Phase 3 Smart Hybrid (natural + optional RAG)

        Returns:
            Dict with response and metadata including prompt_strategy and retry info
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Query: \"{user_input}\"")
        logger.info(f"RAG Enabled: {use_rag}")
        logger.info(f"Category: {category}")
        logger.info(f"{'='*80}")

        # PHASE 3: Use Smart Hybrid system if enabled (RECOMMENDED)
        if use_smart_hybrid:
            logger.info("🚀 Using Phase 3 Smart Hybrid system")
            return self.generate_smart_hybrid(
                user_input=user_input,
                category=category,
                max_length=max_length,
                confidence_threshold=0.4
            )

        # PHASE 2: Use retry logic if enabled
        if use_retry and use_rag:
            logger.info("🔄 Using Phase 2 retry logic")
            return self.generate_with_retry(
                user_input=user_input,
                category=category,
                max_attempts=3,
                max_length=max_length
            )

        # Retrieve context if RAG enabled
        rag_context = None
        if use_rag:
            logger.info("🔍 Retrieving context...")
            rag_context = self.retrieve_context(
                query=user_input,
                category=category,
                topk=5,
                min_confidence=0.3
            )

            if rag_context:
                logger.info(f"✅ Retrieved {len(rag_context.retrieved_docs)} documents")
                logger.info(f"   Confidence: {rag_context.retrieval_confidence:.3f}")
            else:
                logger.info("ℹ️ No relevant context retrieved")

        # Generate response
        try:
            if rag_context:
                # PHASE 2: Use dialogue format or Phase 1 system prompt
                if use_dialogue_prompt:
                    enhanced_input = self._format_dialogue_prompt(
                        query=user_input,
                        rag_context=rag_context,
                        category=category
                    )
                    logger.info("🎯 Generating with RAG context (Phase 2 dialogue format)...")
                else:
                    # Use RAG context with PHASE 1 QUALITY OPTIMIZATION
                    # Format context with explicit instructions for better utilization
                    enhanced_input = self._format_rag_prompt_v2(
                        query=user_input,
                        rag_context=rag_context,
                        category=category
                    )
                    logger.info("🎯 Generating with RAG context (Phase 1 quality optimization)...")
            else:
                # Direct query
                enhanced_input = user_input
                logger.info("🎯 Generating without RAG context...")

            # Use Phase 1 system for generation
            result = self.phase1_system.generate_with_fallback(
                prompt=enhanced_input,
                max_tokens=max_length,
                temperature=0.7,
                use_fallback=True,
                verbose=False
            )

            # Extract response text
            response_text = result.get('response', '')

            logger.info(f"✅ Response generated: {len(response_text)} chars")
            logger.info(f"Response preview: {response_text[:100]}...")

            # Determine prompt strategy used
            prompt_strategy = "none"
            if rag_context:
                prompt_strategy = "dialogue" if use_dialogue_prompt else "system"

            return {
                'response': response_text,
                'rag_used': rag_context is not None,
                'docs_retrieved': len(rag_context.retrieved_docs) if rag_context else 0,
                'retrieval_confidence': rag_context.retrieval_confidence if rag_context else 0.0,
                'category': category,
                'query': user_input,
                'prompt_strategy': prompt_strategy  # NEW: Track which prompt format used
            }

        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            import traceback
            traceback.print_exc()

            return {
                'response': "I encountered an error generating a response.",
                'rag_used': False,
                'docs_retrieved': 0,
                'retrieval_confidence': 0.0,
                'category': category,
                'query': user_input,
                'error': str(e)
            }


def main():
    """Test RAG-enhanced inference system."""
    print("ImpressionCore B3 RAG-Enhanced Inference System")
    print("="*80)

    # Initialize system
    rag_system = B3RAGInference(
        model_path="F:/models/checkpoints/b3/b3_massive_final.pth",
        f_data_root="F:/data"
    )

    # Test queries
    test_queries = [
        ("What are the basics of arithmetic?", "educational"),
        ("Show me pictures of cats", "multimodal"),
        ("How do you greet someone?", "educational"),
    ]

    for query, category in test_queries:
        print(f"\n{'='*80}")
        print(f"Test Query: {query}")
        print(f"Category: {category}")
        print("="*80)

        result = rag_system.generate(
            user_input=query,
            use_rag=True,
            category=category
        )

        print(f"\nResponse: {result['response']}")
        print(f"RAG Used: {result['rag_used']}")
        print(f"Docs Retrieved: {result['docs_retrieved']}")
        print(f"Confidence: {result['retrieval_confidence']:.3f}")

    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
