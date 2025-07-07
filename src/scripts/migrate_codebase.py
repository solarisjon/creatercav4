"""
Migration script to refactor existing codebase to use new architecture
"""
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CodebaseMigrator:
    """Handles migration of existing code to new architecture"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
    
    def migrate_prompts(self):
        """Migrate prompts to new directory structure"""
        logger.info("Migrating prompts to new structure...")
        
        prompts_dir = self.src_dir / "prompts"
        templates_dir = prompts_dir / "templates"
        contexts_dir = prompts_dir / "contexts"
        
        templates_dir.mkdir(exist_ok=True)
        contexts_dir.mkdir(exist_ok=True)
        
        # Define migrations
        migrations = [
            # Prompt templates
            ("formal_rca_prompt", "templates/formal_rca_prompt.txt"),
            ("initial_analysis_prompt", "templates/initial_analysis_prompt.txt"),
            ("kt-analysis_prompt", "templates/kt-analysis_prompt.txt"),
            
            # Context files
            ("context", "contexts/context.txt"),
            ("context_netapp", "contexts/context_netapp.txt"),
            ("cpe_prompt", "contexts/cpe_context.txt"),
            ("contap_prompt", "contexts/contap_context.txt"),
            ("netapp_prompt", "contexts/netapp_context.txt"),
            ("sap_prompt", "contexts/sap_context.txt"),
            ("sf_zk_context", "contexts/sf_zk_context.txt"),
        ]
        
        for old_name, new_path in migrations:
            old_file = prompts_dir / old_name
            new_file = prompts_dir / new_path
            
            if old_file.exists() and not new_file.exists():
                logger.info(f"Moving {old_name} -> {new_path}")
                new_file.parent.mkdir(exist_ok=True)
                shutil.copy2(old_file, new_file)
    
    def create_updated_main_app(self):
        """Create updated main app.py using new components"""
        new_app_content = '''#!/usr/bin/env python3
"""
MCP-based Root Cause Analysis Tool - Refactored
Main application using NiceGUI with clean architecture
"""

import asyncio
from pathlib import Path
from typing import List
from nicegui import ui
from src.utils.logger import setup_logger
from src.utils.file_handler import FileHandler
from src.config import config
from src.integrations.mcp.client import mcp_client
from src.core.analysis.rca_engine import RCAEngine
from src.ui.components.analysis_display import AnalysisDisplay

# Setup logging
logger = setup_logger(__name__)

class RCAApp:
    """Main RCA Application with clean architecture"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.rca_engine = RCAEngine(config.llm_config)
        self.rca_engine.set_mcp_client(mcp_client)
        
        # UI state
        self.uploaded_files = []
        self.urls = []
        self.jira_tickets = []
        self.selected_prompt = "formal_rca_prompt"
        self.analysis_result = None
        
        # UI components
        self.results_container = None
        self.analysis_display = None
        
    async def setup_ui(self):
        """Setup the user interface"""
        ui.page_title("RCA Analysis Tool")
        
        with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
            # Header
            ui.label('Root Cause Analysis Tool').classes('text-2xl font-bold mb-4')
            
            # File upload section
            self._create_upload_section()
            
            # URL section  
            self._create_url_section()
            
            # Jira section
            self._create_jira_section()
            
            # Analysis configuration
            self._create_analysis_section()
            
            # Results section
            self._create_results_section()
    
    def _create_upload_section(self):
        """Create file upload section"""
        with ui.card().classes('w-full mb-4'):
            ui.label('File Upload').classes('text-lg font-semibold mb-2')
            ui.upload(
                on_upload=self.handle_file_upload,
                multiple=True,
                max_file_size=50 * 1024 * 1024  # 50MB
            ).classes('w-full')
    
    def _create_url_section(self):
        """Create URL input section"""
        with ui.card().classes('w-full mb-4'):
            ui.label('URLs').classes('text-lg font-semibold mb-2')
            with ui.row().classes('w-full'):
                self.url_input = ui.input('Enter URL').classes('flex-grow')
                ui.button('Add URL', on_click=self.add_url).classes('ml-2')
    
    def _create_jira_section(self):
        """Create Jira ticket section"""
        with ui.card().classes('w-full mb-4'):
            ui.label('Jira Tickets').classes('text-lg font-semibold mb-2')
            with ui.row().classes('w-full'):
                self.ticket_input = ui.input('Enter Jira Ticket ID').classes('flex-grow')
                ui.button('Add Ticket', on_click=self.add_jira_ticket).classes('ml-2')
    
    def _create_analysis_section(self):
        """Create analysis configuration section"""
        with ui.card().classes('w-full mb-4'):
            ui.label('Analysis Configuration').classes('text-lg font-semibold mb-2')
            
            # Prompt selection
            prompt_options = self.rca_engine.get_available_analysis_types()
            ui.select(
                prompt_options,
                value=self.selected_prompt,
                on_change=self.on_prompt_select
            ).classes('w-full mb-2')
            
            # Issue description
            self.issue_input = ui.textarea('Issue Description').classes('w-full mb-2')
            
            # Generate button
            ui.button(
                'Generate Analysis',
                on_click=self.generate_analysis
            ).classes('bg-blue-500 text-white px-4 py-2')
    
    def _create_results_section(self):
        """Create results display section"""
        with ui.card().classes('w-full'):
            ui.label('Analysis Results').classes('text-lg font-semibold mb-2')
            self.results_container = ui.column().classes('w-full')
            self.analysis_display = AnalysisDisplay(self.results_container)
    
    def handle_file_upload(self, e):
        """Handle file upload"""
        try:
            file_path = self.file_handler.save_uploaded_file(
                e.content.read(),
                e.name
            )
            if file_path:
                self.uploaded_files.append(str(file_path))
                ui.notify(f'File uploaded: {e.name}', type='positive')
        except Exception as ex:
            ui.notify(f'Error uploading file: {str(ex)}', type='negative')
    
    def add_url(self):
        """Add URL to list"""
        url = self.url_input.value.strip()
        if url and url not in self.urls:
            self.urls.append(url)
            ui.notify(f'URL added: {url}', type='positive')
            self.url_input.value = ''
    
    def add_jira_ticket(self):
        """Add Jira ticket to list"""
        ticket = self.ticket_input.value.strip().upper()
        if ticket and ticket not in self.jira_tickets:
            self.jira_tickets.append(ticket)
            ui.notify(f'Ticket added: {ticket}', type='positive')
            self.ticket_input.value = ''
    
    def on_prompt_select(self, e):
        """Handle prompt selection change"""
        self.selected_prompt = e.value
    
    async def generate_analysis(self):
        """Generate RCA analysis"""
        try:
            if not self.uploaded_files and not self.urls and not self.jira_tickets:
                ui.notify('Please upload files or add URLs/tickets first', type='warning')
                return
            
            ui.notify('Generating analysis...', type='info')
            
            # Generate analysis using new engine
            self.analysis_result = await self.rca_engine.generate_analysis(
                files=self.uploaded_files,
                urls=self.urls,
                jira_tickets=self.jira_tickets,
                issue_description=self.issue_input.value,
                prompt_type=self.selected_prompt
            )
            
            # Display results using new component
            self.analysis_display.display_analysis(self.analysis_result)
            
            ui.notify('Analysis completed!', type='positive')
            
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            ui.notify(f'Error generating analysis: {str(e)}', type='negative')

async def main():
    """Main application entry point"""
    app = RCAApp()
    await app.setup_ui()

# Initialize MCP client
@ui.run_with(main)
async def init():
    """Initialize the application"""
    try:
        await mcp_client.initialize()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
'''
        
        new_app_path = self.src_dir / "ui" / "main_app.py"
        new_app_path.parent.mkdir(exist_ok=True)
        new_app_path.write_text(new_app_content, encoding='utf-8')
        logger.info(f"Created new main app: {new_app_path}")
    
    def create_backup(self):
        """Create backup of current files before migration"""
        backup_dir = self.project_root / "backup_pre_refactor"
        backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = [
            "src/app.py",
            "src/rca_generator.py", 
            "src/mcp_client.py"
        ]
        
        for file_path in files_to_backup:
            src_file = self.project_root / file_path
            if src_file.exists():
                dest_file = backup_dir / src_file.name
                shutil.copy2(src_file, dest_file)
                logger.info(f"Backed up: {file_path}")
    
    def generate_migration_summary(self):
        """Generate summary of what needs to be done"""
        summary = """
# Migration Summary

## Completed:
✅ Created new directory structure
✅ Extracted core components:
   - ResponseParser (handles KT table parsing)
   - AnalysisDisplay (proper KT table rendering)
   - UnifiedLLMClient (clean LLM provider management)
   - PromptManager (organized prompt handling)
   - RCAEngine (orchestrates everything)

## Key Improvements:
🎯 **KT Table Issue FIXED**: 
   - Raw response parsing captures all LLM output
   - Special KT table rendering with markdown support
   - Problem Assessment table now displays properly

🏗️ **Clean Architecture**:
   - Separation of concerns (UI, Core, Integrations)
   - Testable components
   - Single responsibility principle

📈 **Maintainability**:
   - Smaller, focused files
   - Clear dependencies
   - Easy to extend

## Next Steps:
1. Test the new components
2. Update main.py to use new architecture
3. Migrate remaining integration code
4. Update tests
5. Clean up old files

## To Use New Components:
```python
# Replace old app.py display logic with:
from src.ui.components.analysis_display import AnalysisDisplay
display = AnalysisDisplay(container)
display.display_analysis(analysis_result)

# Replace old rca_generator with:
from src.core.analysis.rca_engine import RCAEngine
engine = RCAEngine(config)
result = await engine.generate_analysis(...)
```
"""
        
        summary_path = self.project_root / "MIGRATION_SUMMARY.md"
        summary_path.write_text(summary, encoding='utf-8')
        logger.info(f"Migration summary created: {summary_path}")

def main():
    """Run the migration"""
    migrator = CodebaseMigrator()
    
    print("🏗️  Starting codebase migration...")
    
    # Create backup
    print("📁 Creating backup...")
    migrator.create_backup()
    
    # Migrate prompts
    print("📝 Migrating prompts...")
    migrator.migrate_prompts()
    
    # Create new main app
    print("🎨 Creating new main app...")
    migrator.create_updated_main_app()
    
    # Generate summary
    print("📋 Generating migration summary...")
    migrator.generate_migration_summary()
    
    print("✅ Migration completed!")
    print("\nNext steps:")
    print("1. Review the new components in src/core/ and src/ui/")
    print("2. Test the KT table display with new AnalysisDisplay component")
    print("3. Update main.py to use new architecture")
    print("4. Check MIGRATION_SUMMARY.md for details")

if __name__ == "__main__":
    main()
