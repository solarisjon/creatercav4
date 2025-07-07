#!/usr/bin/env python3
"""
Automated test to verify formal RCA analysis works without the 'exceptions' import error
"""

import asyncio
import tempfile
import os

async def test_full_formal_rca():
    print("Testing full formal RCA analysis flow...")

    try:
        print("1. Importing components...")
        from src.config import config
        from src.utils.file_handler import FileHandler
        from src.core.analysis.rca_engine import RCAEngine
        
        # Import MCP client with fallback
        try:
            from src.mcp_client import mcp_client
            print("   ✓ Main MCP client imported")
        except ImportError:
            from src.mcp_client_simple import simple_mcp_client as mcp_client
            print("   ✓ Simple MCP client imported (fallback)")
        
        print("   ✓ All components imported")

        print("2. Setting up components...")
        
        # Setup file handler
        file_handler = FileHandler(
            upload_dir=config.app_config['upload_directory'],
            allowed_extensions=config.app_config['allowed_file_types'],
            max_size_mb=config.app_config['max_file_size_mb']
        )
        
        # Setup RCA engine
        rca_config = {
            **config.llm_config,
            'output_directory': config.app_config['output_directory']
        }
        engine = RCAEngine(rca_config)
        engine.set_mcp_client(mcp_client)
        print("   ✓ Components configured")

        print("3. Creating test file...")
        # Create a temporary test file
        test_content = """
Test Issue Report
================

Issue: NFS performance degradation
Environment: ONTAP 9.16.1P3
Symptoms: High latency, timeouts
Impact: Customer productivity loss
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file_path = f.name
        
        try:
            print("   ✓ Test file created")

            print("4. Running formal RCA analysis...")
            # This is the critical test - this should NOT produce "No module named 'exceptions'" error
            result = await engine.generate_analysis(
                files=[test_file_path],
                urls=[],
                jira_tickets=[],
                analysis_type="formal_rca_prompt",
                issue_description="Test NFS performance issue"
            )
            
            print("   ✓ Analysis completed without exceptions import error!")

            print("5. Checking result...")
            if 'error' in result:
                print(f"   Analysis error (but no import error): {result['error']}")
                # Check if it's the specific "exceptions" import error
                if "No module named 'exceptions'" in str(result.get('error', '')):
                    print("   ✗ STILL HAS EXCEPTIONS IMPORT ERROR")
                    return False
                else:
                    print("   ℹ Analysis had other error (not exceptions import)")
            else:
                print("   ✓ Analysis completed successfully")
                
            print(f"\nResult keys: {list(result.keys())}")
            
        finally:
            # Clean up test file
            os.unlink(test_file_path)

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        
        # Check specifically for the "exceptions" import error
        if "No module named 'exceptions'" in str(e):
            print("\n✗ STILL GETTING EXCEPTIONS IMPORT ERROR!")
            return False
        else:
            print("\n(Different error, not the exceptions import issue)")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_full_formal_rca())
    if success:
        print("\n🎉 SUCCESS: Formal RCA analysis works without 'exceptions' import error!")
    else:
        print("\n❌ FAILED: Still getting the 'exceptions' import error")
