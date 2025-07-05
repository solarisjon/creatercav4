#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_client import mcp_client

async def test_jira():
    try:
        print("Initializing MCP client...")
        await mcp_client.initialize()
        
        print("Testing Jira connection...")
        # Test with a simple JQL query that should return minimal results
        results = await mcp_client.search_jira_tickets('project = CPE ORDER BY created DESC', max_results=1)
        print('✅ Jira connection successful!')
        print(f'Query executed successfully, got {len(results)} results')
        
        if results:
            print(f"Sample result: {results[0]['key']} - {results[0]['summary']}")
            
    except Exception as e:
        print(f'❌ Jira connection failed: {e}')
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    asyncio.run(test_jira())
