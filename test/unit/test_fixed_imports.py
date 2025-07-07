#!/usr/bin/env python3
"""
Test the fixed MCP client import issue
"""

print("Testing import chain...")

try:
    print("1. Testing simple MCP client...")
    from src.mcp_client_simple import simple_mcp_client
    print("   ✓ Simple MCP client imported")

    print("2. Testing config...")
    from src.config import config
    print("   ✓ Config imported")

    print("3. Testing RCA engine...")
    from src.core.analysis.rca_engine import RCAEngine
    print("   ✓ RCA engine imported")

    print("4. Creating RCA engine instance...")
    rca_config = {
        **config.llm_config,
        'output_directory': config.app_config['output_directory']
    }
    engine = RCAEngine(rca_config)
    print("   ✓ RCA engine created")

    print("5. Setting simple MCP client...")
    engine.set_mcp_client(simple_mcp_client)
    print("   ✓ Simple MCP client set")

    print("\nSUCCESS: All components can be imported and created!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
