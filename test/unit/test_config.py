import pytest
import os
from pathlib import Path
from src.config import Config

class TestConfig:
    def test_load_config_success(self, config_file):
        """Test successful configuration loading"""
        config = Config(str(config_file))
        
        assert config.get('LLM', 'openai_api_key') == 'test_openai_key'
        assert config.get('JIRA', 'jira_url') == 'https://test.atlassian.net'
        assert config.getint('APPLICATION', 'app_port') == 8080
        assert config.getboolean('APPLICATION', 'debug_mode') is True
    
    def test_load_config_file_not_found(self, temp_dir):
        """Test configuration loading with missing file"""
        non_existent_file = temp_dir / "non_existent.ini"
        
        with pytest.raises(FileNotFoundError):
            Config(str(non_existent_file))
    
    def test_get_with_fallback(self, config_file):
        """Test get method with fallback values"""
        config = Config(str(config_file))
        
        # Existing key
        assert config.get('LLM', 'openai_api_key') == 'test_openai_key'
        
        # Non-existing key with fallback
        assert config.get('LLM', 'non_existent_key', 'default_value') == 'default_value'
        
        # Non-existing section with fallback
        assert config.get('NON_EXISTENT', 'key', 'default') == 'default'
    
    def test_getint_with_fallback(self, config_file):
        """Test getint method with fallback values"""
        config = Config(str(config_file))
        
        # Existing integer key
        assert config.getint('APPLICATION', 'app_port') == 8080
        
        # Non-existing key with fallback
        assert config.getint('APPLICATION', 'non_existent_port', 9000) == 9000
        
        # Invalid integer with fallback
        config.config.set('APPLICATION', 'invalid_port', 'not_a_number')
        assert config.getint('APPLICATION', 'invalid_port', 3000) == 3000
    
    def test_getboolean_with_fallback(self, config_file):
        """Test getboolean method with fallback values"""
        config = Config(str(config_file))
        
        # Existing boolean key
        assert config.getboolean('APPLICATION', 'debug_mode') is True
        
        # Non-existing key with fallback
        assert config.getboolean('APPLICATION', 'non_existent_flag', False) is False
    
    def test_getfloat_with_fallback(self, config_file):
        """Test getfloat method with fallback values"""
        config = Config(str(config_file))
        
        # Add a float value for testing
        config.config.set('APPLICATION', 'test_float', '3.14')
        assert config.getfloat('APPLICATION', 'test_float') == 3.14
        
        # Non-existing key with fallback
        assert config.getfloat('APPLICATION', 'non_existent_float', 2.5) == 2.5
    
    def test_llm_config_property(self, config_file):
        """Test LLM configuration property"""
        config = Config(str(config_file))
        llm_config = config.llm_config
        
        assert llm_config['openai_api_key'] == 'test_openai_key'
        assert llm_config['openai_model'] == 'gpt-4o'
        assert llm_config['anthropic_api_key'] == 'test_anthropic_key'
        assert llm_config['default_llm'] == 'openai'
    
    def test_jira_config_property(self, config_file):
        """Test Jira configuration property"""
        config = Config(str(config_file))
        jira_config = config.jira_config
        
        assert jira_config['url'] == 'https://test.atlassian.net'
        assert jira_config['username'] == 'test@example.com'
        assert jira_config['api_token'] == 'test_token'
        assert jira_config['project_key'] == 'TEST'
    
    def test_mcp_config_property(self, config_file):
        """Test MCP configuration property"""
        config = Config(str(config_file))
        mcp_config = config.mcp_config
        
        assert mcp_config['server_timeout'] == 30
        assert mcp_config['max_retries'] == 3
        assert mcp_config['filesystem_enabled'] is True
        assert mcp_config['jira_enabled'] is True
    
    def test_app_config_property(self, config_file):
        """Test application configuration property"""
        config = Config(str(config_file))
        app_config = config.app_config
        
        assert app_config['title'] == 'Test RCA Tool'
        assert app_config['host'] == '127.0.0.1'
        assert app_config['port'] == 8080
        assert app_config['debug'] is True
        assert app_config['max_file_size_mb'] == 10
    
    def test_security_config_property(self, config_file):
        """Test security configuration property"""
        config = Config(str(config_file))
        security_config = config.security_config
        
        assert security_config['session_secret_key'] == 'test_secret'
        assert security_config['max_login_attempts'] == 5
        assert security_config['session_timeout_minutes'] == 60
    
    def test_logging_config_property(self, config_file):
        """Test logging configuration property"""
        config = Config(str(config_file))
        logging_config = config.logging_config
        
        assert logging_config['level'] == 'DEBUG'
        assert logging_config['max_size_mb'] == 1
        assert logging_config['backup_count'] == 2
    
    def test_create_directories(self, config_file, temp_dir):
        """Test directory creation during config loading"""
        config = Config(str(config_file))
        
        # Check that directories were created
        upload_dir = Path(config.get('APPLICATION', 'upload_directory'))
        output_dir = Path(config.get('APPLICATION', 'output_directory'))
        logs_dir = Path('./logs')
        servers_dir = Path('./servers')
        
        assert upload_dir.exists()
        assert output_dir.exists()
        assert logs_dir.exists()
        assert servers_dir.exists()