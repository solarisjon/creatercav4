#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, './src')

async def test_mcp_jira():
    from mcp_client import mcp_client
    
    try:
        print("Testing MCP Jira connection...")
        await mcp_client.initialize()
        
        # Test with a simple JQL query
        results = await mcp_client.search_jira_tickets('project = CPE ORDER BY created DESC', max_results=2)
        print(f'✅ MCP Jira connection successful! Found {len(results)} results')
        
        if results:
            for result in results:
                print(f"  - {result['key']}: {result['summary']}")
                
        return True
        
    except Exception as e:
        print(f'❌ MCP Jira connection failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_jira())
    sys.exit(0 if success else 1)
