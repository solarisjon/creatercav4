#!/usr/bin/env python3
"""
Debug script to isolate the 'exceptions' import error in formal RCA
"""

import sys
import traceback

print("Starting formal RCA debug...")

try:
    print("1. Importing config...")
    from src.config import config
    print("   ✓ Config imported successfully")

    print("2. Importing FileHandler...")
    from src.utils.file_handler import FileHandler
    print("   ✓ FileHandler imported successfully")

    print("3. Importing MCP client...")
    from src.mcp_client import mcp_client
    print("   ✓ MCP client imported successfully")

    print("4. Importing RCAEngine...")
    from src.core.analysis.rca_engine import RCAEngine
    print("   ✓ RCAEngine imported successfully")

    print("5. Creating RCAEngine instance...")
    rca_config = {
        **config.llm_config,
        'output_directory': config.app_config['output_directory']
    }
    rca_engine = RCAEngine(rca_config)
    print("   ✓ RCAEngine instance created successfully")

    print("6. Setting MCP client...")
    rca_engine.set_mcp_client(mcp_client)
    print("   ✓ MCP client set successfully")

    print("7. Testing analysis generation with formal RCA prompt...")
    
    # This will help us see exactly where the exceptions import fails
    import asyncio
    async def test_analysis():
        try:
            result = await rca_engine.generate_analysis(
                files=[],
                urls=[],
                jira_tickets=[],
                analysis_type="formal_rca_prompt",
                issue_description="Test issue"
            )
            print("   ✓ Analysis generated successfully")
            return result
        except Exception as e:
            print(f"   ✗ Analysis generation failed: {e}")
            traceback.print_exc()
            return None

    result = asyncio.run(test_analysis())
    
    if result:
        print("\nSUCCESS: Formal RCA analysis completed without errors")
    else:
        print("\nFAILED: Could not complete formal RCA analysis")

except Exception as e:
    print(f"\nERROR at step: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    # Print the specific line that's causing the import error
    print(f"\nError type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    if "No module named 'exceptions'" in str(e):
        print("\n*** FOUND THE EXCEPTIONS IMPORT ERROR ***")
        print("This error occurs when code tries to 'import exceptions' which was removed in Python 3")
        print("The error likely comes from old code or a library that hasn't been updated")
