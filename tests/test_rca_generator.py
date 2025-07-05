import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.rca_generator import RCAGenerator
from src.config import Config

class TestRCAGenerator:
    @pytest.fixture
    def rca_generator(self, config_file, temp_dir):
        """Create RCAGenerator instance for testing"""
        with patch('src.rca_generator.config') as mock_config:
            mock_config.llm_config = {
                'openai_api_key': 'test_openai_key',
                'openai_model': 'gpt-4o',
                'openai_base_url': 'https://api.openai.com/v1',
                'anthropic_api_key': 'test_anthropic_key',
                'anthropic_model': 'claude-3-5-sonnet-20241022',
                'openrouter_api_key': 'test_openrouter_key',
                'openrouter_model': 'anthropic/claude-3.5-sonnet',
                'openrouter_base_url': 'https://openrouter.ai/api/v1',
                'default_llm': 'openai'
            }
            mock_config.app_config = {
                'output_directory': str(temp_dir / 'output')
            }
            mock_config.jira_config = {
                'escalation_project': 'TEST',
                'defect_project': 'TEST'
            }
            return RCAGenerator()
    
    @pytest.mark.asyncio
    async def test_collect_source_data_files(self, rca_generator, temp_dir):
        """Test collecting source data from files"""
        # Create test files
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test file content")
        
        with patch('src.rca_generator.mcp_client') as mock_mcp:
            mock_mcp.read_file = AsyncMock(return_value="Test file content")
            mock_mcp.process_pdf = AsyncMock(return_value="PDF content")
            mock_mcp.scrape_web_content = AsyncMock(return_value="Web content")
            mock_mcp.search_jira_tickets = AsyncMock(return_value=[{'key': 'TEST-123', 'summary': 'Test'}])
            
            source_data = await rca_generator._collect_source_data(
                files=[str(test_file)],
                urls=[],
                jira_tickets=[]
            )
            
            assert str(test_file) in source_data['files']
            assert source_data['files'][str(test_file)]['content'] == "Test file content"
    
    @pytest.mark.asyncio
    async def test_collect_source_data_pdf_files(self, rca_generator, temp_dir):
        """Test collecting source data from PDF files"""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        with patch('src.rca_generator.mcp_client') as mock_mcp:
            mock_mcp.process_pdf = AsyncMock(return_value="PDF text content")
            
            source_data = await rca_generator._collect_source_data(
                files=[str(pdf_file)],
                urls=[],
                jira_tickets=[]
            )
            
            assert str(pdf_file) in source_data['files']
            assert source_data['files'][str(pdf_file)]['content'] == "PDF text content"
            mock_mcp.process_pdf.assert_called_once_with(str(pdf_file))
    
    @pytest.mark.asyncio
    async def test_collect_source_data_urls(self, rca_generator):
        """Test collecting source data from URLs"""
        test_url = "https://example.com"
        
        with patch('src.rca_generator.mcp_client') as mock_mcp:
            mock_mcp.scrape_web_content = AsyncMock(return_value="Web page content")
            
            source_data = await rca_generator._collect_source_data(
                files=[],
                urls=[test_url],
                jira_tickets=[]
            )
            
            assert test_url in source_data['urls']
            assert source_data['urls'][test_url]['content'] == "Web page content"
            mock_mcp.scrape_web_content.assert_called_once_with(test_url)
    
    @pytest.mark.asyncio
    async def test_collect_source_data_jira_tickets(self, rca_generator, sample_jira_ticket):
        """Test collecting source data from Jira tickets"""
        ticket_id = "TEST-123"
        
        with patch('src.rca_generator.mcp_client') as mock_mcp:
            mock_mcp.search_jira_tickets = AsyncMock(return_value=[sample_jira_ticket])
            
            source_data = await rca_generator._collect_source_data(
                files=[],
                urls=[],
                jira_tickets=[ticket_id]
            )
            
            assert ticket_id in source_data['jira_tickets']
            assert source_data['jira_tickets'][ticket_id] == sample_jira_ticket
            mock_mcp.search_jira_tickets.assert_called_once_with(f"key = {ticket_id}", max_results=1)
    
    @pytest.mark.asyncio
    async def test_collect_source_data_error_handling(self, rca_generator, temp_dir):
        """Test error handling in source data collection"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        with patch('src.rca_generator.mcp_client') as mock_mcp:
            mock_mcp.read_file = AsyncMock(side_effect=Exception("File read error"))
            
            source_data = await rca_generator._collect_source_data(
                files=[str(test_file)],
                urls=[],
                jira_tickets=[]
            )
            
            assert str(test_file) in source_data['files']
            assert 'error' in source_data['files'][str(test_file)]
            assert source_data['files'][str(test_file)]['error'] == "File read error"
    
    def test_prepare_llm_context(self, rca_generator):
        """Test LLM context preparation"""
        source_data = {
            'files': {
                'test.txt': {'content': 'File content'}
            },
            'urls': {
                'https://example.com': {'content': 'Web content'}
            },
            'jira_tickets': {
                'TEST-123': {'key': 'TEST-123', 'summary': 'Test issue', 'description': 'Test description', 'status': 'Open', 'priority': 'Medium'}
            }
        }
        
        issue_description = "Test issue description"
        
        context = rca_generator._prepare_llm_context(source_data, issue_description)
        
        assert "Test issue description" in context
        assert "File content" in context
        assert "Web content" in context
        assert "TEST-123" in context
        assert "Test issue" in context
    
    @pytest.mark.asyncio
    async def test_generate_with_openai_success(self, rca_generator, mock_openai_response):
        """Test successful analysis generation with OpenAI"""
        context = "Test context for analysis"
        
        with patch('openai.AsyncOpenAI') as mock_openai_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = json.dumps(mock_openai_response)
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            analysis = await rca_generator._generate_with_openai(context)
            
            assert analysis == mock_openai_response
            mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_openai_error(self, rca_generator):
        """Test OpenAI analysis generation with error"""
        context = "Test context"
        
        with patch('openai.AsyncOpenAI') as mock_openai_class:
            mock_openai_class.side_effect = Exception("OpenAI API error")
            
            with pytest.raises(Exception):
                await rca_generator._generate_with_openai(context)
    
    @pytest.mark.asyncio
    async def test_generate_with_anthropic_success(self, rca_generator, mock_openai_response):
        """Test successful analysis generation with Anthropic"""
        context = "Test context for analysis"
        
        with patch('anthropic.AsyncAnthropic') as mock_anthropic_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps(mock_openai_response)
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_anthropic_class.return_value = mock_client
            
            analysis = await rca_generator._generate_with_anthropic(context)
            
            assert analysis == mock_openai_response
            mock_client.messages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_anthropic_error(self, rca_generator):
        """Test Anthropic analysis generation with error"""
        context = "Test context"
        
        with patch('anthropic.AsyncAnthropic') as mock_anthropic_class:
            mock_anthropic_class.side_effect = Exception("Anthropic API error")
            
            with pytest.raises(Exception):
                await rca_generator._generate_with_anthropic(context)
    
    @pytest.mark.asyncio
    async def test_create_rca_document(self, rca_generator, mock_openai_response, temp_dir):
        """Test RCA document creation"""
        analysis = mock_openai_response
        
        document_path = await rca_generator._create_rca_document(analysis)
        
        assert document_path.exists()
        assert document_path.suffix == '.json'
        
        # Verify content
        with open(document_path, 'r') as f:
            saved_analysis = json.load(f)
        
        assert saved_analysis == analysis
    
    
    @pytest.mark.asyncio
    async def test_generate_rca_analysis_full_flow(self, rca_generator, temp_dir, mock_openai_response):
        """Test complete RCA analysis generation flow"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        files = [str(test_file)]
        urls = ["https://example.com"]
        jira_tickets = ["TEST-123"]
        issue_description = "Test issue requiring analysis"
        
        with patch('src.rca_generator.mcp_client') as mock_mcp, \
             patch.object(rca_generator, '_generate_analysis') as mock_generate:
            
            # Setup mocks
            mock_mcp.read_file = AsyncMock(return_value="File content")
            mock_mcp.scrape_web_content = AsyncMock(return_value="Web content")
            mock_mcp.search_jira_tickets = AsyncMock(return_value=[{'key': 'TEST-123', 'summary': 'Test'}])
            
            mock_generate.return_value = mock_openai_response
            
            result = await rca_generator.generate_rca_analysis(
                files=files,
                urls=urls,
                jira_tickets=jira_tickets,
                issue_description=issue_description
            )
            
            # Verify result structure
            assert 'analysis' in result
            assert 'document_path' in result
            assert 'timestamp' in result
            assert 'source_data_summary' in result
            
            # Verify source data summary
            summary = result['source_data_summary']
            assert summary['files_processed'] == 1
            assert summary['urls_processed'] == 1
            assert summary['jira_tickets_referenced'] == 1
    
    @pytest.mark.asyncio
    async def test_generate_analysis_openai_path(self, rca_generator, mock_openai_response):
        """Test analysis generation using OpenAI path"""
        source_data = {'files': {}, 'urls': {}, 'jira_tickets': {}}
        issue_description = "Test issue"
        
        with patch.object(rca_generator, '_generate_with_openai') as mock_openai:
            mock_openai.return_value = mock_openai_response
            
            analysis = await rca_generator._generate_analysis(source_data, issue_description)
            
            assert analysis == mock_openai_response
            mock_openai.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_analysis_anthropic_path(self, rca_generator, mock_openai_response):
        """Test analysis generation using Anthropic path"""
        rca_generator.config['default_llm'] = 'anthropic'
        source_data = {'files': {}, 'urls': {}, 'jira_tickets': {}}
        issue_description = "Test issue"
        
        with patch.object(rca_generator, '_generate_with_anthropic') as mock_anthropic:
            mock_anthropic.return_value = mock_openai_response
            
            analysis = await rca_generator._generate_analysis(source_data, issue_description)
            
            assert analysis == mock_openai_response
            mock_anthropic.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_openrouter_success(self, rca_generator, mock_openai_response):
        """Test successful analysis generation with OpenRouter"""
        context = "Test context for analysis"
        
        with patch('openai.AsyncOpenAI') as mock_openai_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = json.dumps(mock_openai_response)
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            analysis = await rca_generator._generate_with_openrouter(context)
            
            assert analysis == mock_openai_response
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify OpenRouter-specific headers were included
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert 'extra_headers' in call_kwargs
            assert 'HTTP-Referer' in call_kwargs['extra_headers']
    
    @pytest.mark.asyncio
    async def test_generate_with_openrouter_error(self, rca_generator):
        """Test OpenRouter analysis generation with error"""
        context = "Test context"
        
        with patch('openai.AsyncOpenAI') as mock_openai_class:
            mock_openai_class.side_effect = Exception("OpenRouter API error")
            
            with pytest.raises(Exception):
                await rca_generator._generate_with_openrouter(context)
    
    @pytest.mark.asyncio
    async def test_generate_analysis_openrouter_path(self, rca_generator, mock_openai_response):
        """Test analysis generation using OpenRouter path"""
        rca_generator.config['default_llm'] = 'openrouter'
        source_data = {'files': {}, 'urls': {}, 'jira_tickets': {}}
        issue_description = "Test issue"
        
        with patch.object(rca_generator, '_generate_with_openrouter') as mock_openrouter:
            mock_openrouter.return_value = mock_openai_response
            
            analysis = await rca_generator._generate_analysis(source_data, issue_description)
            
            assert analysis == mock_openai_response
            mock_openrouter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_try_fallback_llms_success(self, rca_generator, mock_openai_response):
        """Test successful fallback to different LLMs"""
        context = "Test context"
        
        with patch.object(rca_generator, '_generate_with_anthropic') as mock_anthropic:
            mock_anthropic.return_value = mock_openai_response
            
            analysis = await rca_generator._try_fallback_llms(['anthropic', 'openrouter'], context)
            
            assert analysis == mock_openai_response
            mock_anthropic.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_try_fallback_llms_all_fail(self, rca_generator):
        """Test when all fallback LLMs fail"""
        context = "Test context"
        
        # Set all API keys to None to simulate missing keys
        rca_generator.config['openai_api_key'] = None
        rca_generator.config['anthropic_api_key'] = None
        rca_generator.config['openrouter_api_key'] = None
        
        with pytest.raises(Exception, match="All LLM providers failed"):
            await rca_generator._try_fallback_llms(['openai', 'anthropic', 'openrouter'], context)
    
    @pytest.mark.asyncio
    async def test_generate_analysis_unsupported_llm(self, rca_generator):
        """Test analysis generation with unsupported LLM"""
        rca_generator.config['default_llm'] = 'unsupported'
        source_data = {'files': {}, 'urls': {}, 'jira_tickets': {}}
        issue_description = "Test issue"
        
        with pytest.raises(ValueError, match="Unsupported LLM"):
            await rca_generator._generate_analysis(source_data, issue_description)