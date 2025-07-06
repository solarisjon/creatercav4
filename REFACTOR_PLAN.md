# 🏗️ RCA Tool - Refactoring Plan

## New Directory Structure

```
creatercav4/
├── 📁 src/
│   ├── 🎨 ui/                      # User Interface Layer
│   │   ├── __init__.py
│   │   ├── main_app.py             # Main NiceGUI application
│   │   ├── components/             # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── file_upload.py      # File upload widget
│   │   │   ├── analysis_display.py # Results display widget
│   │   │   ├── prompt_selector.py  # Prompt selection widget
│   │   │   └── chat_interface.py   # Chat/agentic interface
│   │   └── utils/                  # UI-specific utilities
│   │       ├── __init__.py
│   │       └── formatters.py       # HTML/markdown formatters
│   │
│   ├── 🧠 core/                    # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── analysis/               # Analysis engine
│   │   │   ├── __init__.py
│   │   │   ├── rca_engine.py       # Core RCA logic
│   │   │   ├── kt_analyzer.py      # Kepner-Tregoe specific logic
│   │   │   ├── parsers.py          # Response parsing logic
│   │   │   └── prompt_manager.py   # Prompt loading and management
│   │   ├── llm/                    # LLM Integration
│   │   │   ├── __init__.py
│   │   │   ├── providers/          # LLM provider implementations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── openai_provider.py
│   │   │   │   ├── anthropic_provider.py
│   │   │   │   ├── openrouter_provider.py
│   │   │   │   └── llmproxy_provider.py
│   │   │   ├── client.py           # Unified LLM client
│   │   │   └── fallback.py         # LLM fallback logic
│   │   └── data/                   # Data Processing
│   │       ├── __init__.py
│   │       ├── collectors/         # Data collection
│   │       │   ├── __init__.py
│   │       │   ├── file_collector.py
│   │       │   ├── url_collector.py
│   │       │   └── jira_collector.py
│   │       └── processors/         # Data processing
│   │           ├── __init__.py
│   │           ├── pdf_processor.py
│   │           └── text_processor.py
│   │
│   ├── 🔌 integrations/            # External Integrations
│   │   ├── __init__.py
│   │   ├── mcp/                    # MCP client and servers
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # MCP client
│   │   │   └── servers/            # MCP server configs
│   │   │       ├── __init__.py
│   │   │       ├── jira_server.py
│   │   │       └── filesystem_server.py
│   │   └── jira/                   # Jira integration
│   │       ├── __init__.py
│   │       ├── api_client.py
│   │       └── ticket_parser.py
│   │
│   ├── 📊 models/                  # Data Models
│   │   ├── __init__.py
│   │   ├── analysis.py             # Analysis result models
│   │   ├── ticket.py               # Jira ticket models
│   │   └── document.py             # Document models
│   │
│   ├── 🛠️ utils/                   # Shared Utilities
│   │   ├── __init__.py
│   │   ├── logger.py               # Logging setup
│   │   ├── file_handler.py         # File operations
│   │   ├── config_loader.py        # Configuration loading
│   │   └── validators.py           # Input validation
│   │
│   ├── 📋 prompts/                 # Prompt Templates
│   │   ├── __init__.py
│   │   ├── templates/              # Prompt template files
│   │   │   ├── formal_rca.txt
│   │   │   ├── kt_analysis.txt
│   │   │   └── initial_analysis.txt
│   │   ├── contexts/               # Context files
│   │   │   ├── netapp_context.txt
│   │   │   └── cpe_context.txt
│   │   └── schemas/                # Response schemas
│   │       ├── formal_rca_schema.json
│   │       └── kt_analysis_schema.json
│   │
│   ├── config.py                   # Configuration management
│   └── __init__.py
│
├── 📁 tests/                       # Organized Tests
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_core/
│   │   ├── test_ui/
│   │   └── test_integrations/
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   ├── test_llm_providers.py
│   │   └── test_mcp_integration.py
│   ├── e2e/                        # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_full_workflow.py
│   └── fixtures/                   # Test data
│       ├── sample_pdfs/
│       ├── mock_responses/
│       └── test_configs/
│
├── 📁 docs/                        # Documentation
│   ├── README.md                   # Main documentation
│   ├── ARCHITECTURE.md             # System architecture
│   ├── API.md                      # API documentation
│   ├── DEPLOYMENT.md               # Deployment guide
│   ├── TROUBLESHOOTING.md          # Common issues
│   └── DEVELOPMENT.md              # Development guide
│
├── 📁 scripts/                     # Utility Scripts
│   ├── setup_dev.py               # Development setup
│   ├── migrate_config.py          # Config migration
│   ├── test_connectivity.py       # Connection testing
│   └── cleanup_old_files.py       # Cleanup script
│
├── 📁 data/                        # Data Directory
│   ├── templates/                  # Report templates
│   ├── uploads/                    # File uploads
│   ├── output/                     # Generated reports
│   └── logs/                       # Application logs
│
├── 📁 config/                      # Configuration
│   ├── config.ini.example         # Example config
│   ├── prompts.yaml               # Prompt configurations
│   └── llm_settings.yaml          # LLM configurations
│
├── 📄 Root Files
├── main.py                         # Application entry point
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Dependencies
├── .gitignore                      # Git ignore rules
└── LICENSE                         # License file
```

## Benefits of This Structure

### 🎯 **Separation of Concerns**
- **UI Layer**: Pure presentation logic
- **Core Layer**: Business logic and domain models
- **Integration Layer**: External service connections
- **Models**: Data structures and validation

### 🔧 **Maintainability**
- **Smaller Files**: Each file has a single responsibility
- **Clear Dependencies**: Layered architecture with clear boundaries
- **Testable**: Each component can be unit tested in isolation

### 📈 **Scalability**
- **Modular**: Easy to add new LLM providers or analysis types
- **Extensible**: New features fit into existing structure
- **Configurable**: Settings separated from code

### 🧪 **Testing**
- **Organized Tests**: Unit, integration, and E2E tests separated
- **Mock Data**: Centralized test fixtures
- **CI/CD Ready**: Structure supports automated testing

## Migration Plan

1. **Phase 1**: Clean up temporary files and organize existing code
2. **Phase 2**: Extract UI components from main app
3. **Phase 3**: Refactor core business logic
4. **Phase 4**: Separate LLM providers and MCP integration
5. **Phase 5**: Update documentation and tests
6. **Phase 6**: Add new features (better KT table handling, etc.)

## Next Steps

Would you like me to:
1. Start with Phase 1 (cleanup) and show you the refactored structure?
2. Focus on a specific area (like the KT table issue)?
3. Create a migration script to automate the refactoring?
