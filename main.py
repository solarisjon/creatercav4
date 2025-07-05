#!/usr/bin/env python3
"""
MCP-based Root Cause Analysis Tool
Main application entry point
"""

import sys
import argparse
from src.utils.logger import setup_logger
from src.config import config
from nicegui import ui

# Setup logging
logger = setup_logger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='MCP-based Root Cause Analysis Tool')
    parser.add_argument('--host', default=None, help='Host to bind to (default: from config.ini)')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to (default: from config.ini)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def main():
    """Main application entry point"""
    try:
        args = parse_args()
        logger.info("Starting MCP-based RCA Tool")
        
        # Import the app module to register routes
        from src.app import create_app
        
        # Create and configure the app
        app = create_app()
        
        # Determine host and port
        host = args.host or config.app_config['host']
        port = args.port or config.app_config['port']
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Run the application
        ui.run(
            host=host,
            port=port,
            title=config.app_config['title'],
            favicon='🔍',
            show=True,
            reload=args.debug
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        if "Address already in use" in str(e):
            logger.error(f"Port {port if 'port' in locals() else config.app_config['port']} is already in use.")
            logger.error("Try using a different port with --port <number> or kill the existing process:")
            logger.error(f"lsof -ti:{port if 'port' in locals() else config.app_config['port']} | xargs kill -9")
        sys.exit(1)

if __name__ == "__main__":
    main()
