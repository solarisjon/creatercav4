import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.config import config

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.config = config.mcp_config
        self.sessions: Dict[str, ClientSession] = {}
        self.servers: Dict[str, Any] = {}
    
    async def initialize(self):
        """Initialize MCP servers based on configuration"""
        try:
            # Initialize filesystem MCP server if enabled
            if self.config['filesystem_enabled']:
                await self._setup_filesystem_server()
            
            # Initialize Jira MCP server if enabled
            if self.config['jira_enabled']:
                await self._setup_jira_server()
            
            # Initialize web scraper MCP server if enabled
            if self.config['web_scraper_enabled']:
                await self._setup_web_scraper_server()
            
            logger.info(f"Initialized {len(self.sessions)} MCP servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
            raise
    
    async def _setup_filesystem_server(self):
        """Setup filesystem MCP server"""
        try:
            # For now, we'll use a simple file operations approach
            # This will be replaced with actual MCP server when available
            self.servers['filesystem'] = {
                'type': 'filesystem',
                'allowed_paths': self.config['filesystem_allowed_paths']
            }
            logger.info("Filesystem MCP server configured")
        except Exception as e:
            logger.error(f"Failed to setup filesystem MCP server: {e}")
    
    async def _setup_jira_server(self):
        """Setup Jira MCP server"""
        try:
            jira_config = config.jira_config
            
            # Configuration for Jira MCP server
            self.servers['jira'] = {
                'type': 'jira',
                'url': jira_config['url'],
                'username': jira_config['username'],
                'api_token': jira_config['api_token'],
                'project_key': jira_config['project_key']
            }
            logger.info("Jira MCP server configured")
        except Exception as e:
            logger.error(f"Failed to setup Jira MCP server: {e}")
    
    async def _setup_web_scraper_server(self):
        """Setup web scraper MCP server"""
        try:
            self.servers['web_scraper'] = {
                'type': 'web_scraper',
                'timeout': self.config['server_timeout']
            }
            logger.info("Web scraper MCP server configured")
        except Exception as e:
            logger.error(f"Failed to setup web scraper MCP server: {e}")
    
    async def read_file(self, file_path: str) -> str:
        """Read file content using filesystem MCP server"""
        try:
            file_path = Path(file_path)
            
            # Check if file is in allowed paths
            allowed = False
            for allowed_path in self.config['filesystem_allowed_paths']:
                if file_path.is_relative_to(Path(allowed_path)):
                    allowed = True
                    break
            
            if not allowed:
                raise PermissionError(f"File path {file_path} not in allowed paths")
            
            if not file_path.exists():
                raise FileNotFoundError(f"File {file_path} not found")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    async def process_pdf(self, pdf_path: str) -> str:
        """Process PDF file and extract text content"""
        try:
            from PyPDF2 import PdfReader
            
            pdf_path = Path(pdf_path)
            
            # Check if file is in allowed paths
            allowed = False
            for allowed_path in self.config['filesystem_allowed_paths']:
                if pdf_path.is_relative_to(Path(allowed_path)):
                    allowed = True
                    break
            
            if not allowed:
                raise PermissionError(f"PDF path {pdf_path} not in allowed paths")
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file {pdf_path} not found")
            
            # Extract text from PDF
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise
    
    async def scrape_web_content(self, url: str) -> str:
        """Scrape web content using web scraper MCP server"""
        try:
            async with httpx.AsyncClient(
                timeout=self.config['server_timeout'],
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Basic content extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
                
        except Exception as e:
            logger.error(f"Failed to scrape web content from {url}: {e}")
            raise
    
    async def create_jira_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a Jira ticket using Jira MCP server
        
        Note: This method is available for future use but is not currently 
        used by the RCA generator, which operates in read-only mode for Jira.
        """
        try:
            from jira import JIRA
            
            jira_config = config.jira_config
            
            # Create Jira client
            jira = JIRA(
                server=jira_config['url'],
                basic_auth=(jira_config['username'], jira_config['api_token'])
            )
            
            # Create issue
            issue = jira.create_issue(
                project=ticket_data.get('project', jira_config['project_key']),
                summary=ticket_data['summary'],
                description=ticket_data['description'],
                issuetype={'name': ticket_data.get('issue_type', 'Task')},
                priority={'name': ticket_data.get('priority', 'Medium')}
            )
            
            logger.info(f"Created Jira ticket: {issue.key}")
            return issue.key
            
        except Exception as e:
            logger.error(f"Failed to create Jira ticket: {e}")
            raise
    
    async def search_jira_tickets(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Jira tickets using JQL"""
        try:
            from jira import JIRA
            
            jira_config = config.jira_config
            
            # Create Jira client
            jira = JIRA(
                server=jira_config['url'],
                basic_auth=(jira_config['username'], jira_config['api_token'])
            )
            
            # Search issues
            issues = jira.search_issues(jql, maxResults=max_results)
            
            # Convert to dict format
            results = []
            for issue in issues:
                results.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'description': issue.fields.description,
                    'priority': issue.fields.priority.name if issue.fields.priority else None,
                    'issue_type': issue.fields.issuetype.name
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search Jira tickets: {e}")
            raise
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about available MCP servers"""
        return {
            'servers': list(self.servers.keys()),
            'config': self.config,
            'sessions': len(self.sessions)
        }
    
    async def close(self):
        """Close all MCP server connections"""
        for session in self.sessions.values():
            try:
                await session.close()
            except Exception as e:
                logger.error(f"Error closing MCP session: {e}")
        
        self.sessions.clear()
        logger.info("All MCP sessions closed")

# Global MCP client instance
mcp_client = MCPClient()