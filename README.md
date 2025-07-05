# MCP-based Root Cause Analysis Tool

A modern web-based Root Cause Analysis (RCA) tool that leverages Model Context Protocol (MCP) servers instead of traditional RAG (Retrieval-Augmented Generation) for enhanced data access and analysis.

## Features

- **Multi-Source Data Integration**: Process PDF files, web URLs, and Jira tickets
- **MCP Server Architecture**: Uses Model Context Protocol for efficient data access
- **Modern Web UI**: Built with NiceGUI for responsive, interactive experience
- **Jira Integration**: Read and reference existing Jira tickets for context
- **Comprehensive Analysis**: Generate detailed RCA reports with LLM assistance
- **Multi-LLM Support**: Works with OpenAI GPT, Anthropic Claude, OpenRouter, and corporate LLM proxy models
- **Comprehensive Testing**: Full unit test coverage for reliable operation

## Architecture

```
+------------------+    +------------------+    +------------------+
|   NiceGUI App    |--->|   MCP Client     |--->|  MCP Servers     |
|                  |    |                  |    |                  |
| - File Upload    |    | - Protocol       |    | - Jira MCP       |
| - URL Input      |    |   Handler        |    | - Filesystem     |
| - RCA Display    |    | - Context Mgmt   |    | - Web Scraper    |
+------------------+    +------------------+    +------------------+
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/solarisjon/creatercav4.git
   cd creatercav4
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Configure the application**
   - Copy `config.ini.example` to `config.ini`
   - Update `config.ini` with your API keys and settings
   - Set your LLM API keys (OpenAI or Anthropic)
   - Configure Jira connection details

## Configuration

The application uses `config.ini` for all configuration settings:

### LLM Configuration
```ini
[LLM]
# Choose your preferred LLM
default_llm = anthropic  # or openai, openrouter, or llmproxy

# OpenAI Configuration
openai_api_key = your_openai_key_here
openai_model = gpt-4o

# Anthropic Configuration  
anthropic_api_key = your_anthropic_key_here
anthropic_model = claude-3-5-sonnet-20241022

# OpenRouter Configuration (access to many models)
openrouter_api_key = your_openrouter_key_here
openrouter_model = anthropic/claude-3.5-sonnet
# Available models: gpt-4, claude-3.5-sonnet, llama-3, etc.

# LLM Proxy Configuration (corporate proxy for OpenAI-compatible models)
llmproxy_api_key = your_llmproxy_api_key_here
llmproxy_model = gpt-4o
llmproxy_base_url = https://your-company-llmproxy.com/v1
```

### Jira Configuration
```ini
[JIRA]
# Jira Configuration (Read-Only Access)
# Used to read existing tickets for RCA context
jira_url = https://your-domain.atlassian.net
jira_username = your_email@company.com
jira_api_token = your_jira_api_token_here
jira_project_key = CPE
```

**Note**: The application uses Bearer token authentication for Jira connections. Ensure your API token has appropriate read permissions for the specified project.

### Application Settings
```ini
[APPLICATION]
app_host = 0.0.0.0
app_port = 8090
max_file_size_mb = 50
allowed_file_types = .pdf,.txt,.docx,.md
```

## Usage

1. **Start the application**
   ```bash
   python main.py
   
   # Or with custom settings
   python main.py --port 9000 --debug
   ```

2. **Open your browser** to `http://localhost:8090`

3. **Upload source materials**:
   - PDF files (support cases, documentation)
   - Add web URLs (Confluence pages, documentation)
   - Reference Jira tickets for context (read-only)

4. **Describe the issue** requiring root cause analysis

5. **Generate RCA report** - the system will:
   - Process all uploaded files and URLs
   - Read and analyze referenced Jira tickets for context
   - Generate comprehensive RCA using LLM
   - Create detailed analysis report

## Project Structure

```
creatercav4/
├── main.py                    # Application entry point
├── config.ini.example        # Configuration template
├── src/
│   ├── app.py                # NiceGUI web application
│   ├── config.py             # Configuration management
│   ├── mcp_client.py         # MCP protocol client
│   ├── rca_generator.py      # RCA analysis engine
│   └── utils/
│       ├── logger.py         # Logging utilities
│       └── file_handler.py   # Secure file operations
├── tests/                     # Comprehensive unit tests
│   ├── conftest.py           # Test fixtures and configuration
│   ├── test_config.py        # Configuration tests
│   ├── test_file_handler.py  # File handling tests
│   ├── test_mcp_client.py    # MCP client tests
│   └── test_rca_generator.py # RCA generation tests
├── uploads/                   # Secure file upload directory
├── output/                    # Generated RCA reports
└── logs/                      # Application logs
```

## Development

### Running Tests

The project includes comprehensive unit tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite covers:
- Configuration loading and validation
- File upload and processing
- MCP client operations
- RCA analysis generation
- Error handling and edge cases

### Adding New MCP Servers

1. Install the MCP server following its documentation
2. Configure the server in `config.ini`
3. Add integration logic in `src/mcp_client.py`
4. Update `src/rca_generator.py` to use the new server
5. Add corresponding tests

### Extending Analysis Capabilities

The RCA analysis can be extended by:
- Adding new data sources in `src/mcp_client.py`
- Enhancing the analysis prompts in `src/rca_generator.py`
- Adding new output formats
- Writing tests for new functionality

## LLM Providers

### OpenRouter Integration

OpenRouter provides access to multiple LLM models through a single API:

**Popular Models Available:**
- `anthropic/claude-3.5-sonnet` - Latest Claude model
- `openai/gpt-4o` - OpenAI's flagship model  
- `meta-llama/llama-3-70b-instruct` - Open source alternative
- `google/gemini-pro` - Google's advanced model
- `mistralai/mixtral-8x7b-instruct` - Fast and efficient

**Benefits:**
- Single API key for multiple models
- Competitive pricing across providers
- Automatic fallback between models
- No need for separate accounts with each provider

**Usage:**
Set `default_llm = openrouter` in config.ini and choose your preferred model in `openrouter_model`.

### Corporate LLM Proxy Support

For corporate environments with internal LLM proxies:

**Configuration:**
```ini
[LLM]
default_llm = llmproxy
llmproxy_api_key = your_corporate_api_key
llmproxy_model = gpt-4o  # or any OpenAI-compatible model
llmproxy_base_url = https://your-company-llmproxy.com/v1
```

**Benefits:**
- Use corporate-approved LLM infrastructure
- Maintain data security and compliance
- Leverage internal rate limiting and monitoring
- Compatible with OpenAI API format

## MCP Servers

The application supports multiple MCP servers:

### Available Servers
- **Filesystem MCP**: Secure file operations with access controls
- **Jira MCP**: Read and search existing tickets for context
- **Web Scraper MCP**: Content extraction from web URLs

### Third-Party MCP Servers
- **Atlassian Remote MCP**: Official Atlassian integration (beta)
- **Community Servers**: Various open-source implementations

## Security Considerations

- All file uploads are validated and sanitized
- API keys are stored in configuration files (not in code)
- File access is restricted to configured allowed paths
- Session management with configurable timeouts
- Input validation and error handling throughout

## Testing Strategy

### Unit Tests
- **Configuration**: Test all config loading and validation
- **File Handling**: Test file operations, validation, and security
- **MCP Client**: Test all MCP server interactions with mocking
- **RCA Generator**: Test analysis generation and document creation

### Test Fixtures
- Temporary directories for safe file operations
- Mock configurations for isolated testing
- Sample data (PDFs, Jira tickets, web content)
- Mock API responses for LLM services

### Continuous Integration
Configure your CI/CD pipeline to:
```bash
# Install dependencies
pip install -e .

# Run tests with coverage
pytest --cov=src --cov-fail-under=80

# Run linting (if using)
# ruff check src tests
```

## Command Line Options

```bash
# Basic usage
python main.py

# Custom host and port
python main.py --host 127.0.0.1 --port 9000

# Enable debug mode
python main.py --debug

# Show help
python main.py --help
```

## Troubleshooting

### Common Issues

1. **Jira Authentication Errors ("Unauthorized")**
   - Ensure you're using a valid Jira API token (not password)
   - The application uses Bearer token authentication automatically
   - Verify the API token has read permissions for your Jira project
   - Check that jira_url points to the correct Jira instance
   
   **Testing Jira Connection:**
   ```bash
   # Test Jira connectivity
   python -c "
   import asyncio
   import sys
   sys.path.insert(0, './src')
   from mcp_client import mcp_client
   
   async def test():
       await mcp_client.initialize()
       tickets = await mcp_client.search_jira_tickets('project = YOUR_PROJECT ORDER BY created DESC', max_results=1)
       print(f'✅ Found {len(tickets)} tickets')
   
   asyncio.run(test())
   "
   ```

2. **SSL Certificate Issues**
   - The application automatically configures SSL certificates for macOS/Linux
   - If SSL issues persist, check your system's certificate store
   - Corporate networks may require additional certificate configuration

3. **Port already in use**
   ```bash
   # Kill existing process
   lsof -ti:8090 | xargs kill -9
   
   # Or use different port
   python main.py --port 9000
   ```

2. **LLM API Errors**
   - Check API keys in `config.ini`
   - Verify quota/billing status
   - Switch between OpenAI/Anthropic/OpenRouter in config
   - OpenRouter provides access to multiple models with unified billing

3. **File Upload Issues**
   - Check file size limits in config
   - Verify file extensions are allowed
   - Check upload directory permissions

4. **Test Failures**
   - Ensure all dependencies are installed
   - Check test configuration in `pytest.ini`
   - Verify mock configurations in test fixtures

### Debugging

1. **Enable Debug Mode**
   ```ini
   [APPLICATION]
   debug_mode = true
   
   [LOGGING]
   log_level = DEBUG
   ```

2. **Check Application Logs**
   ```bash
   tail -f logs/app.log
   ```

3. **Run Individual Tests**
   ```bash
   pytest tests/test_config.py::TestConfig::test_load_config_success -v
   ```

### Logs
Application logs are stored in `logs/app.log` with configurable rotation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Submit a pull request

### Code Quality
- Follow existing code style and patterns
- Add docstrings to new functions and classes
- Write tests for new functionality
- Update documentation as needed

## License

[Add your license information here]

## Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Run the test suite to verify functionality
- Create an issue in the repository

---

**Note**: This tool is designed for internal use and should be deployed in a secure environment with proper access controls.