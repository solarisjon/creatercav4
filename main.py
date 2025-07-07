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
import platform
import os

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
        from src.ui.main_app import create_app
        
        # Create and configure the app
        app = create_app()
        
        # Setup static file serving for NetApp assets
        from pathlib import Path
        from nicegui import app as nicegui_app
        static_dir = Path(__file__).parent / "src" / "ui" / "static"
        nicegui_app.add_static_files('/static', static_dir)
        
        # Determine host and port
        host = args.host or config.app_config['host']
        port = args.port or config.app_config['port']
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Patch NiceGUI to support async add_jira_ticket (for linked issues dialog)
        # This is needed because NiceGUI expects sync handlers by default
        # We patch the button in the UI creation to call the async method
        # (see src/app.py for lambda: self.add_jira_ticket())
        # No further action needed here, but this comment documents the async support

        # Run the application
        ui.run(
            host=host,
            port=port,
            title=config.app_config['title'],
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
    # Set the path for the PEM file used for SSL certificate verification
    platformtype = platform.system()

    if platformtype == "Linux":
        os.environ['REQUESTS_CA_BUNDLE'] = "/etc/ssl/certs/ca-certificates.crt"
        os.environ['SSL_CERT_FILE']      = "/etc/ssl/certs/ca-certificates.crt"
    elif platformtype == "Darwin":
        pem_path = "/usr/local/etc/openssl@3/certs/../cert.pem"
        os.environ['REQUESTS_CA_BUNDLE'] = pem_path
        os.environ['SSL_CERT_FILE'] = pem_path
    else:
        print("Unsupported platform. Please set the SSL_CERT_FILE environment variable manually.")
    main()
