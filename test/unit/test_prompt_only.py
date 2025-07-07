#!/usr/bin/env python3
"""
Test formal RCA analysis up to the LLM call
"""

import asyncio

async def test_prompt_generation():
    print("Testing prompt generation for formal RCA...")

    try:
        print("1. Importing components...")
        from src.config import config
        from src.mcp_client_simple import simple_mcp_client
        from src.core.analysis.rca_engine import RCAEngine
        print("   ✓ All components imported")

        print("2. Setting up RCA engine...")
        rca_config = {
            **config.llm_config,
            'output_directory': config.app_config['output_directory']
        }
        engine = RCAEngine(rca_config)
        engine.set_mcp_client(simple_mcp_client)
        print("   ✓ RCA engine configured")

        print("3. Testing prompt building...")
        # Access the prompt manager directly to test prompt building
        prompt_manager = engine.prompt_manager
        
        print("4. Loading prompt template...")
        prompt = prompt_manager.build_prompt(
            prompt_type="formal_rca_prompt",
            context_data="Test data content",
            issue_description="Test issue"
        )
        
        print("   ✓ Prompt built successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        
        # Show first 200 chars of prompt
        print(f"\nPrompt preview:\n{prompt[:200]}...")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_prompt_generation())
    if success:
        print("\n✓ Prompt generation test PASSED!")
    else:
        print("\n✗ Prompt generation test FAILED")
