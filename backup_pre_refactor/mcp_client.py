import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx
import platform
import os
import urllib3

# Configure SSL certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
platformtype = platform.system()

if platformtype == "Linux":
    os.environ['REQUESTS_CA_BUNDLE'] = "/etc/ssl/certs/ca-certificates.crt"
    os.environ['SSL_CERT_FILE'] = "/etc/ssl/certs/ca-certificates.crt"
elif platformtype == "Darwin":
    pem_path = "/usr/local/etc/openssl@3/certs/../cert.pem"
    os.environ['REQUESTS_CA_BUNDLE'] = pem_path
    os.environ['SSL_CERT_FILE'] = pem_path

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
            
            # Use Bearer token authentication (like escalation_metrics)
            headers = {
                'Authorization': f'Bearer {jira_config["api_token"]}'
            }
            jira = JIRA(
                server=jira_config['url'],
                options={'headers': headers, 'verify': False}
            )
            logger.info("Successfully authenticated with Bearer token")
            
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
            
            # Use Bearer token authentication (like escalation_metrics)
            headers = {
                'Authorization': f'Bearer {jira_config["api_token"]}'
            }
            jira = JIRA(
                server=jira_config['url'],
                options={'headers': headers, 'verify': False}
            )
            logger.info("Successfully authenticated with Bearer token")
            
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
    
    async def get_linked_issues_grouped(self, issue_key: str) -> Dict[str, list]:
        """
        Fetch all linked issues for a Jira ticket, grouped by their link type (e.g., 'Relates').
        Returns a dict: { link_type: [ {key, summary, direction}, ... ] }
        """
        try:
            from jira import JIRA

            jira_config = config.jira_config

            headers = {
                'Authorization': f'Bearer {jira_config["api_token"]}'
            }
            jira = JIRA(
                server=jira_config['url'],
                options={'headers': headers, 'verify': False}
            )
            logger.info("Successfully authenticated with Bearer token")

            issue = jira.issue(issue_key, fields="issuelinks")
            grouped = {}

            for link in getattr(issue.fields, "issuelinks", []):
                # Outward (this issue links to another)
                if hasattr(link, "outwardIssue"):
                    linked = link.outwardIssue
                    link_type = link.type.outward or link.type.name
                    direction = "outward"
                # Inward (another issue links to this)
                elif hasattr(link, "inwardIssue"):
                    linked = link.inwardIssue
                    link_type = link.type.inward or link.type.name
                    direction = "inward"
                else:
                    continue

                entry = {
                    "key": linked.key,
                    "summary": getattr(linked.fields, "summary", ""),
                    "direction": direction
                }
                grouped.setdefault(link_type, []).append(entry)

            return grouped

        except Exception as e:
            logger.error(f"Failed to fetch linked issues for {issue_key}: {e}")
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
