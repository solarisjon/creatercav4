#!/usr/bin/env python3
"""
Test formal RCA analysis with the fixed import
"""

import asyncio

async def test_formal_rca():
    print("Testing formal RCA analysis...")

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

        print("3. Running formal RCA analysis...")
        result = await engine.generate_analysis(
            files=[],
            urls=[],
            jira_tickets=[],
            analysis_type="formal_rca_prompt",
            issue_description="Test formal RCA issue"
        )
        print("   ✓ Analysis completed successfully!")

        print(f"\nResult keys: {list(result.keys())}")
        if 'error' in result:
            print(f"Analysis error: {result['error']}")
        else:
            print("Analysis completed without errors.")

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_formal_rca())
    if success:
        print("\n✓ Formal RCA test PASSED - no 'exceptions' import error!")
    else:
        print("\n✗ Formal RCA test FAILED")
