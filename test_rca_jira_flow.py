#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, './src')

async def test_rca_jira_flow():
    """Test the exact Jira flow that the RCA generator uses"""
    
    try:
        from rca_generator import RCAGenerator
        from mcp_client import mcp_client
        
        print("Testing RCA Generator Jira flow...")
        
        # Initialize MCP client (like the main app does)
        await mcp_client.initialize()
        print("✅ MCP client initialized")
        
        # Create RCA generator
        rca_gen = RCAGenerator()
        print("✅ RCA generator created")
        
        # Test the exact method that processes Jira tickets
        test_ticket_id = "CPE-9659"  # Use a valid test ticket
        
        print(f"\nTesting Jira ticket retrieval for: {test_ticket_id}")
        
        # This is the exact call that happens in _collect_source_data
        jql = f"key = {test_ticket_id}"
        tickets = await mcp_client.search_jira_tickets(jql, max_results=1)
        
        if tickets:
            print(f"✅ Successfully retrieved Jira ticket: {tickets[0]['key']}")
            print(f"   Summary: {tickets[0]['summary'][:100]}...")
            print(f"   Status: {tickets[0]['status']}")
        else:
            print(f"⚠️  No ticket found for {test_ticket_id} (this might be expected)")
            
        # Test with a broader search to see if connection works
        print(f"\nTesting broader Jira search...")
        jql = "project = CPE ORDER BY created DESC"
        tickets = await mcp_client.search_jira_tickets(jql, max_results=2)
        
        print(f"✅ Successfully searched Jira! Found {len(tickets)} tickets")
        for ticket in tickets:
            print(f"   - {ticket['key']}: {ticket['summary'][:60]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ RCA Jira flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rca_jira_flow())
    sys.exit(0 if success else 1)
