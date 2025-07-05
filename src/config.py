import configparser
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        self.config.read(self.config_file)
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        dirs_to_create = [
            self.get('APPLICATION', 'upload_directory', './uploads'),
            self.get('APPLICATION', 'output_directory', './output'),
            './logs',
            './servers'
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value with fallback"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value with fallback"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value with fallback"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value with fallback"""
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    # Convenience methods for common configuration sections
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            'openai_api_key': self.get('LLM', 'openai_api_key'),
            'openai_model': self.get('LLM', 'openai_model', 'gpt-4o'),
            'openai_base_url': self.get('LLM', 'openai_base_url', 'https://api.openai.com/v1'),
            'anthropic_api_key': self.get('LLM', 'anthropic_api_key'),
            'anthropic_model': self.get('LLM', 'anthropic_model', 'claude-3-5-sonnet-20241022'),
            'openrouter_api_key': self.get('LLM', 'openrouter_api_key'),
            'openrouter_model': self.get('LLM', 'openrouter_model', 'anthropic/claude-3.5-sonnet'),
            'openrouter_base_url': self.get('LLM', 'openrouter_base_url', 'https://openrouter.ai/api/v1'),
            'default_llm': self.get('LLM', 'default_llm', 'openai')
        }
    
    @property
    def jira_config(self) -> Dict[str, Any]:
        """Get Jira configuration"""
        return {
            'url': self.get('JIRA', 'jira_url'),
            'username': self.get('JIRA', 'jira_username'),
            'api_token': self.get('JIRA', 'jira_api_token'),
            'project_key': self.get('JIRA', 'jira_project_key', 'CPE'),
            'escalation_project': self.get('JIRA', 'jira_escalation_project', 'CPE'),
            'defect_project': self.get('JIRA', 'jira_defect_project', 'CPE')
        }
    
    @property
    def mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration"""
        return {
            'server_timeout': self.getint('MCP', 'mcp_server_timeout', 30),
            'max_retries': self.getint('MCP', 'mcp_max_retries', 3),
            'filesystem_enabled': self.getboolean('MCP', 'filesystem_mcp_enabled', True),
            'filesystem_allowed_paths': self.get('MCP', 'filesystem_mcp_allowed_paths', '/tmp,./uploads,./data').split(','),
            'jira_enabled': self.getboolean('MCP', 'jira_mcp_enabled', True),
            'jira_server_path': self.get('MCP', 'jira_mcp_server_path', './servers/jira-mcp'),
            'web_scraper_enabled': self.getboolean('MCP', 'web_scraper_mcp_enabled', True),
            'web_scraper_server_path': self.get('MCP', 'web_scraper_mcp_server_path', './servers/web-scraper-mcp')
        }
    
    @property
    def app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return {
            'title': self.get('APPLICATION', 'app_title', 'Root Cause Analysis Tool'),
            'host': self.get('APPLICATION', 'app_host', '0.0.0.0'),
            'port': self.getint('APPLICATION', 'app_port', 8080),
            'debug': self.getboolean('APPLICATION', 'debug_mode', False),
            'max_file_size_mb': self.getint('APPLICATION', 'max_file_size_mb', 50),
            'allowed_file_types': self.get('APPLICATION', 'allowed_file_types', '.pdf,.txt,.docx,.md').split(','),
            'upload_directory': self.get('APPLICATION', 'upload_directory', './uploads'),
            'output_directory': self.get('APPLICATION', 'output_directory', './output')
        }
    
    @property
    def security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'session_secret_key': self.get('SECURITY', 'session_secret_key'),
            'max_login_attempts': self.getint('SECURITY', 'max_login_attempts', 5),
            'session_timeout_minutes': self.getint('SECURITY', 'session_timeout_minutes', 60)
        }
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.get('LOGGING', 'log_level', 'INFO'),
            'file': self.get('LOGGING', 'log_file', './logs/app.log'),
            'max_size_mb': self.getint('LOGGING', 'log_max_size_mb', 10),
            'backup_count': self.getint('LOGGING', 'log_backup_count', 5)
        }

# Global configuration instance
config = Config()