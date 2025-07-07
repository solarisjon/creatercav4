#!/usr/bin/env python3
"""
Simple test to check MCP client import without initialization
"""

print("Testing MCP client import...")

try:
    print("1. Importing basic modules...")
    import asyncio
    import json
    from pathlib import Path
    print("   ✓ Basic modules imported")

    print("2. Importing httpx...")
    import httpx
    print("   ✓ httpx imported")

    print("3. Importing mcp...")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    print("   ✓ mcp imported")

    print("4. Importing config...")
    from src.config import config
    print("   ✓ config imported")

    print("5. Importing MCPClient class...")
    from src.mcp_client import MCPClient
    print("   ✓ MCPClient imported")

    print("6. Creating MCPClient instance...")
    client = MCPClient()
    print("   ✓ MCPClient instance created")

    print("\nSUCCESS: MCP client can be imported and instantiated")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
