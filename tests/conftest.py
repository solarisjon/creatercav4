import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import configparser

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def config_file(temp_dir):
    """Create test configuration file"""
    config_path = temp_dir / "test_config.ini"
    
    config = configparser.ConfigParser()
    config.add_section('LLM')
    config.set('LLM', 'openai_api_key', 'test_openai_key')
    config.set('LLM', 'openai_model', 'gpt-4o')
    config.set('LLM', 'openai_base_url', 'https://api.openai.com/v1')
    config.set('LLM', 'anthropic_api_key', 'test_anthropic_key')
    config.set('LLM', 'anthropic_model', 'claude-3-5-sonnet-20241022')
    config.set('LLM', 'default_llm', 'openai')
    
    config.add_section('JIRA')
    config.set('JIRA', 'jira_url', 'https://test.atlassian.net')
    config.set('JIRA', 'jira_username', 'test@example.com')
    config.set('JIRA', 'jira_api_token', 'test_token')
    config.set('JIRA', 'jira_project_key', 'TEST')
    
    config.add_section('MCP')
    config.set('MCP', 'mcp_server_timeout', '30')
    config.set('MCP', 'mcp_max_retries', '3')
    config.set('MCP', 'filesystem_mcp_enabled', 'true')
    config.set('MCP', 'filesystem_mcp_allowed_paths', f'{temp_dir}/uploads,{temp_dir}/data')
    config.set('MCP', 'jira_mcp_enabled', 'true')
    config.set('MCP', 'web_scraper_mcp_enabled', 'true')
    
    config.add_section('APPLICATION')
    config.set('APPLICATION', 'app_title', 'Test RCA Tool')
    config.set('APPLICATION', 'app_host', '127.0.0.1')
    config.set('APPLICATION', 'app_port', '8080')
    config.set('APPLICATION', 'debug_mode', 'true')
    config.set('APPLICATION', 'max_file_size_mb', '10')
    config.set('APPLICATION', 'allowed_file_types', '.pdf,.txt,.md')
    config.set('APPLICATION', 'upload_directory', str(temp_dir / 'uploads'))
    config.set('APPLICATION', 'output_directory', str(temp_dir / 'output'))
    
    config.add_section('SECURITY')
    config.set('SECURITY', 'session_secret_key', 'test_secret')
    config.set('SECURITY', 'max_login_attempts', '5')
    config.set('SECURITY', 'session_timeout_minutes', '60')
    
    config.add_section('LOGGING')
    config.set('LOGGING', 'log_level', 'DEBUG')
    config.set('LOGGING', 'log_file', str(temp_dir / 'logs' / 'test.log'))
    config.set('LOGGING', 'log_max_size_mb', '1')
    config.set('LOGGING', 'log_backup_count', '2')
    
    with open(config_path, 'w') as f:
        config.write(f)
    
    return config_path

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000208 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
295
%%EOF"""

@pytest.fixture
def sample_jira_ticket():
    """Sample Jira ticket data for testing"""
    return {
        'key': 'TEST-123',
        'summary': 'Test issue summary',
        'status': 'Open',
        'assignee': 'test.user@example.com',
        'created': '2024-01-01T10:00:00.000+0000',
        'updated': '2024-01-02T10:00:00.000+0000',
        'description': 'Test issue description with details',
        'priority': 'High',
        'issue_type': 'Bug'
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "executive_summary": "Test executive summary",
        "problem_statement": "Test problem statement",
        "timeline": "Test timeline",
        "root_cause": "Test root cause",
        "contributing_factors": ["Factor 1", "Factor 2"],
        "impact_assessment": "Test impact assessment",
        "corrective_actions": ["Action 1", "Action 2"],
        "preventive_measures": ["Measure 1", "Measure 2"],
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "escalation_needed": "true",
        "defect_tickets_needed": "true",
        "severity": "High",
        "priority": "P1"
    }

@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for web scraping"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.content = b"<html><body><h1>Test Page</h1><p>Test content for scraping</p></body></html>"
    mock_response.raise_for_status = Mock()
    mock_client.get.return_value = mock_response
    return mock_client