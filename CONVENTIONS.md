# Code Conventions

This document outlines the coding conventions and best practices for the NetApp RCA Tool project.

## General Guidelines

- Follow the existing code style and patterns.
- Use type hints consistently across all functions and methods.
- Add comprehensive docstrings to all new functions and classes.
- Ensure all new code is covered by tests with a minimum of 80% test coverage.

## Python Code

- Use `async` and `await` for I/O-bound operations to ensure non-blocking behavior.
- Follow PEP 8 for code style, including naming conventions and indentation.
- Use `configparser` for configuration management, as seen in `src/config.py`.
- Implement abstract base classes for LLM providers, as demonstrated in `src/core/llm/client.py`.

## Testing

- Organize tests by type: unit, integration, and end-to-end.
- Use `pytest` for running tests and generating coverage reports.
- Mock external dependencies in tests to ensure isolation and reliability.

## Logging

- Use the `logging` module for logging, with a setup function like `setup_logger` in `src/utils/logger.py`.
- Ensure logs are stored in `logs/app.log` with configurable rotation.

## File Handling

- Validate and sanitize all file uploads.
- Use the `FileHandler` class for secure file operations, as implemented in `src/utils/file_handler.py`.

## UI Development

- Use NiceGUI for building responsive and interactive web interfaces.
- Follow the modular structure for UI components, as outlined in the project structure.

## Configuration

- Store all configuration settings in `config.ini`.
- Use the `Config` class in `src/config.py` for loading and accessing configuration values.

## Contribution

- Fork the repository and create a feature branch for new features.
- Ensure all tests pass and code quality checks are met before submitting a pull request.
- Update documentation for any new functionality or changes.
