#!/usr/bin/env python3
"""Test RCA Engine import chain to find exceptions error"""

import sys
sys.path.append('src')

def test_imports():
    try:
        print("1. Testing basic imports...")
        import logging
        from typing import Dict, Any, List, Optional
        from datetime import datetime
        from pathlib import Path
        print("   ✅ Basic imports successful")
        
        print("2. Testing core LLM client import...")
        from src.core.llm.client import UnifiedLLMClient
        print("   ✅ LLM client import successful")
        
        print("3. Testing prompt manager import...")
        from src.core.analysis.prompt_manager import PromptManager
        print("   ✅ Prompt manager import successful")
        
        print("4. Testing parsers import...")
        from src.core.analysis.parsers import ResponseParser
        print("   ✅ Parsers import successful")
        
        print("5. Testing RCA engine import...")
        from src.core.analysis.rca_engine import RCAEngine
        print("   ✅ RCA engine import successful")
        
        print("6. Testing MCP client import...")
        from src.mcp_client import mcp_client
        print("   ✅ MCP client import successful")
        
        print("7. Testing RCA engine instantiation...")
        config = {'default_llm': 'openai', 'output_directory': 'output'}
        engine = RCAEngine(config)
        print("   ✅ RCA engine instantiation successful")
        
        print("8. Testing MCP client injection...")
        engine.set_mcp_client(mcp_client)
        print("   ✅ MCP client injection successful")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error at step: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_imports()
