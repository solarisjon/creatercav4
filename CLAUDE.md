# Project Definition
This project is intended to use MCP servers to augment the LLM with extra data and show a clean way to use MCP over RAG.
I am particularly interested in augmenting the LLM with data from Jira, web urls, SAP support data PDFs and other misc PDFs to generate a root cause analysis document.
This document is currently a word docx document in data called rca_template.docx.

## Project Status - COMPLETED INITIAL IMPLEMENTATION

### ✅ Completed Features
- **MCP Server Architecture**: Implemented MCP client with support for filesystem, Jira, and web scraping
- **NiceGUI Web Interface**: Modern responsive web UI for file uploads, URL input, and results display
- **Configuration Management**: Centralized config.ini for all settings (LLM keys, Jira, MCP servers)
- **Multi-LLM Support**: Works with both OpenAI GPT and Anthropic Claude models
- **File Processing**: Secure file upload with validation, PDF text extraction, web scraping
- **Jira Integration**: Full Jira ticket creation, search, and data extraction capabilities
- **RCA Generation**: Comprehensive root cause analysis with structured JSON output
- **Automated Ticket Creation**: Creates escalation and defect tickets based on analysis
- **Comprehensive Testing**: Full unit test suite with 80%+ coverage requirement
- **Security Features**: File validation, path restrictions, input sanitization
- **Structured Project**: Clean src/ directory structure with proper module organization

### 🔧 Technical Architecture
```
test_mcp/
├── main.py                    # NiceGUI application entry point
├── config.ini                # Configuration (LLM keys, Jira, etc.)
├── src/
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

### 🚀 Key Capabilities
1. **Multi-Source Data Integration**: PDFs, web URLs, Jira tickets
2. **MCP vs RAG**: Uses Model Context Protocol for efficient data access
3. **LLM-Powered Analysis**: Generates structured RCA reports with recommendations
4. **Automated Workflows**: Creates Jira tickets based on analysis severity
5. **Security-First Design**: Input validation, file restrictions, secure configurations
6. **Testing Coverage**: Comprehensive test suite for reliable operation

### 💻 Usage Instructions
1. Configure API keys in config.ini (OpenAI/Anthropic, Jira)
2. Run: `python main.py`
3. Open: http://localhost:8080
4. Upload files, add URLs, reference Jira tickets
5. Describe the issue needing analysis
6. Generate comprehensive RCA report with automated ticket creation

### 🧪 Testing
- Run tests: `pytest`
- Coverage report: `pytest --cov=src --cov-report=html`
- All modules have comprehensive unit tests with mocking for external services

### 📋 Next Steps (If Needed)
- Deploy to production environment
- Add more MCP servers as needed
- Integrate with additional data sources
- Enhance RCA templates
- Add user authentication/authorization

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

