#!/usr/bin/env python3
"""
Simple test to validate Phase 8B Week 1 implementation
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append('src')

async def test_assistant_basic_functionality():
    """Test basic assistant functionality"""
    try:
        # Import assistant components
        from assistant import AssistantCore, PersonalAssistant
        from assistant.core.query_processor import QueryProcessor
        from assistant.core.retrieval_engine import RetrievalEngine
        from assistant.nlp.nlu_engine import NLUEngine
        from assistant.core.context_manager import ContextManager
        from assistant.core.response_generator import ResponseGenerator
        from assistant.knowledge.uks_integration import UKSIntegration
        
        print("✅ All imports successful")
        
        # Test basic assistant creation
        assistant_core = AssistantCore()
        print("✅ AssistantCore creation successful")
        
        # Test initialization
        await assistant_core.initialize()
        print("✅ AssistantCore initialization successful")
        
        # Test basic query processing
        response = await assistant_core.process_query("Hello, how are you?")
        print(f"✅ Query processing successful: {response.content[:50]}...")
        
        print("\n🎉 Phase 8B Week 1 implementation validation SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_assistant_basic_functionality())
    sys.exit(0 if success else 1)
