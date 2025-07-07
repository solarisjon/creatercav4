"""
Simple MCP client implementation that doesn't use the problematic MCP library
This is a fallback for when the main MCP client has import issues
"""
import logging
import httpx
import asyncio
from typing import List, Dict, Any
from src.config import config

logger = logging.getLogger(__name__)

class SimpleMCPClient:
    """Simple MCP client that provides basic functionality without the MCP library"""
    
    def __init__(self):
        self.config = config.mcp_config
        
    async def get_file_content(self, file_path: str) -> str:
        """Get content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return f"Error reading file: {e}"
    
    async def get_web_content(self, url: str) -> str:
        """Get content from a web URL"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return f"Error fetching URL: {e}"
    
    async def get_jira_ticket(self, issue_key: str) -> str:
        """Get Jira ticket information - simplified version"""
        try:
            # This is a basic implementation - for full functionality, 
            # the main MCP client should be used
            return f"Jira ticket {issue_key} - simplified fetch (MCP client unavailable)"
        except Exception as e:
            logger.error(f"Failed to fetch Jira ticket {issue_key}: {e}")
            return f"Error fetching Jira ticket: {e}"
    
    async def get_linked_issues_grouped(self, main_ticket: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get linked issues - simplified version"""
        return {"blocks": [], "is blocked by": [], "relates to": []}
    
    async def initialize(self):
        """Initialize the simple client"""
        logger.info("SimpleMCPClient initialized (fallback mode)")
        
    async def cleanup(self):
        """Cleanup resources"""
        pass

# Simple client instance
simple_mcp_client = SimpleMCPClient()
