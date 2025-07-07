import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.mcp_client import MCPClient
from src.config import Config

class TestMCPClient:
    @pytest.fixture
    def mcp_client(self, config_file):
        """Create MCPClient instance for testing"""
        with patch('src.mcp_client.config') as mock_config:
            mock_config.mcp_config = {
                'server_timeout': 30,
                'max_retries': 3,
                'filesystem_enabled': True,
                'filesystem_allowed_paths': ['/tmp', './uploads', './data'],
                'jira_enabled': True,
                'jira_server_path': './servers/jira-mcp',
                'web_scraper_enabled': True,
                'web_scraper_server_path': './servers/web-scraper-mcp'
            }
            mock_config.jira_config = {
                'url': 'https://test.atlassian.net',
                'username': 'test@example.com',
                'api_token': 'test_token',
                'project_key': 'TEST'
            }
            return MCPClient()
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mcp_client):
        """Test successful MCP client initialization"""
        await mcp_client.initialize()
        
        assert 'filesystem' in mcp_client.servers
        assert 'jira' in mcp_client.servers
        assert 'web_scraper' in mcp_client.servers
    
    @pytest.mark.asyncio
    async def test_read_file_success(self, mcp_client, temp_dir):
        """Test successful file reading"""
        # Create test file in allowed path
        test_file = temp_dir / "uploads" / "test.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_content = "Test file content"
        test_file.write_text(test_content)
        
        # Update allowed paths to include temp_dir
        mcp_client.config['filesystem_allowed_paths'] = [str(temp_dir / "uploads")]
        
        content = await mcp_client.read_file(str(test_file))
        
        assert content == test_content
    
    @pytest.mark.asyncio
    async def test_read_file_not_allowed_path(self, mcp_client, temp_dir):
        """Test file reading from non-allowed path"""
        test_file = temp_dir / "forbidden" / "test.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("Test content")
        
        with pytest.raises(PermissionError):
            await mcp_client.read_file(str(test_file))
    
    @pytest.mark.asyncio
    async def test_read_file_not_exists(self, mcp_client, temp_dir):
        """Test reading non-existent file"""
        non_existent_file = temp_dir / "uploads" / "non_existent.txt"
        
        # Update allowed paths
        mcp_client.config['filesystem_allowed_paths'] = [str(temp_dir / "uploads")]
        
        with pytest.raises(FileNotFoundError):
            await mcp_client.read_file(str(non_existent_file))
    
    @pytest.mark.asyncio
    async def test_process_pdf_success(self, mcp_client, temp_dir, sample_pdf_content):
        """Test successful PDF processing"""
        # Create test PDF file
        pdf_file = temp_dir / "uploads" / "test.pdf"
        pdf_file.parent.mkdir(parents=True, exist_ok=True)
        pdf_file.write_bytes(sample_pdf_content)
        
        # Update allowed paths
        mcp_client.config['filesystem_allowed_paths'] = [str(temp_dir / "uploads")]
        
        with patch('src.mcp_client.PdfReader') as mock_pdf_reader:
            # Mock PDF reader
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader
            
            content = await mcp_client.process_pdf(str(pdf_file))
            
            assert "Test PDF content" in content
    
    @pytest.mark.asyncio
    async def test_process_pdf_not_allowed_path(self, mcp_client, temp_dir, sample_pdf_content):
        """Test PDF processing from non-allowed path"""
        pdf_file = temp_dir / "forbidden" / "test.pdf"
        pdf_file.parent.mkdir(parents=True, exist_ok=True)
        pdf_file.write_bytes(sample_pdf_content)
        
        with pytest.raises(PermissionError):
            await mcp_client.process_pdf(str(pdf_file))
    
    @pytest.mark.asyncio
    async def test_scrape_web_content_success(self, mcp_client, mock_httpx_client):
        """Test successful web content scraping"""
        url = "https://example.com"
        
        with patch('src.mcp_client.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            content = await mcp_client.scrape_web_content(url)
            
            assert "Test Page" in content
            assert "Test content for scraping" in content
            mock_httpx_client.get.assert_called_once_with(url)
    
    @pytest.mark.asyncio
    async def test_scrape_web_content_http_error(self, mcp_client):
        """Test web scraping with HTTP error"""
        url = "https://nonexistent.com"
        
        with patch('src.mcp_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP Error")
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception):
                await mcp_client.scrape_web_content(url)
    
    @pytest.mark.asyncio
    async def test_create_jira_ticket_success(self, mcp_client):
        """Test successful Jira ticket creation"""
        ticket_data = {
            'summary': 'Test ticket',
            'description': 'Test description',
            'issue_type': 'Bug',
            'priority': 'High'
        }
        
        with patch('src.mcp_client.JIRA') as mock_jira_class:
            mock_jira = Mock()
            mock_issue = Mock()
            mock_issue.key = 'TEST-123'
            mock_jira.create_issue.return_value = mock_issue
            mock_jira_class.return_value = mock_jira
            
            ticket_key = await mcp_client.create_jira_ticket(ticket_data)
            
            assert ticket_key == 'TEST-123'
            mock_jira.create_issue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_jira_ticket_error(self, mcp_client):
        """Test Jira ticket creation with error"""
        ticket_data = {
            'summary': 'Test ticket',
            'description': 'Test description'
        }
        
        with patch('src.mcp_client.JIRA') as mock_jira_class:
            mock_jira_class.side_effect = Exception("JIRA connection error")
            
            with pytest.raises(Exception):
                await mcp_client.create_jira_ticket(ticket_data)
    
    @pytest.mark.asyncio
    async def test_search_jira_tickets_success(self, mcp_client, sample_jira_ticket):
        """Test successful Jira ticket search"""
        jql = "project = TEST"
        
        with patch('src.mcp_client.JIRA') as mock_jira_class:
            mock_jira = Mock()
            mock_issue = Mock()
            
            # Setup mock issue fields
            mock_issue.key = sample_jira_ticket['key']
            mock_issue.fields.summary = sample_jira_ticket['summary']
            mock_issue.fields.status.name = sample_jira_ticket['status']
            
            mock_assignee = Mock()
            mock_assignee.displayName = sample_jira_ticket['assignee']
            mock_issue.fields.assignee = mock_assignee
            
            mock_issue.fields.created = sample_jira_ticket['created']
            mock_issue.fields.updated = sample_jira_ticket['updated']
            mock_issue.fields.description = sample_jira_ticket['description']
            
            mock_priority = Mock()
            mock_priority.name = sample_jira_ticket['priority']
            mock_issue.fields.priority = mock_priority
            
            mock_issuetype = Mock()
            mock_issuetype.name = sample_jira_ticket['issue_type']
            mock_issue.fields.issuetype = mock_issuetype
            
            mock_jira.search_issues.return_value = [mock_issue]
            mock_jira_class.return_value = mock_jira
            
            results = await mcp_client.search_jira_tickets(jql)
            
            assert len(results) == 1
            assert results[0]['key'] == sample_jira_ticket['key']
            assert results[0]['summary'] == sample_jira_ticket['summary']
    
    @pytest.mark.asyncio
    async def test_search_jira_tickets_error(self, mcp_client):
        """Test Jira ticket search with error"""
        jql = "invalid jql"
        
        with patch('src.mcp_client.JIRA') as mock_jira_class:
            mock_jira_class.side_effect = Exception("JQL error")
            
            with pytest.raises(Exception):
                await mcp_client.search_jira_tickets(jql)
    
    @pytest.mark.asyncio
    async def test_get_server_info(self, mcp_client):
        """Test getting server information"""
        await mcp_client.initialize()
        
        server_info = await mcp_client.get_server_info()
        
        assert 'servers' in server_info
        assert 'config' in server_info
        assert 'sessions' in server_info
        assert len(server_info['servers']) == 3  # filesystem, jira, web_scraper
    
    @pytest.mark.asyncio
    async def test_close(self, mcp_client):
        """Test closing MCP client"""
        # Add some mock sessions
        mock_session = AsyncMock()
        mcp_client.sessions['test'] = mock_session
        
        await mcp_client.close()
        
        mock_session.close.assert_called_once()
        assert len(mcp_client.sessions) == 0