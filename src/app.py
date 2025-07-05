#!/usr/bin/env python3
"""
MCP-based Root Cause Analysis Tool
Main application using NiceGUI
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
from nicegui import ui, app
from src.utils.logger import setup_logger
from src.utils.file_handler import FileHandler
from src.config import config
from src.mcp_client import mcp_client
from src.rca_generator import rca_generator

# Setup logging
logger = setup_logger(__name__)

class RCAApp:
    def __init__(self):
        self.config = config.app_config
        self.file_handler = FileHandler(
            upload_dir=self.config['upload_directory'],
            allowed_extensions=self.config['allowed_file_types'],
            max_size_mb=self.config['max_file_size_mb']
        )
        self.uploaded_files: List[str] = []
        self.urls: List[str] = []
        self.jira_tickets: List[str] = []
        self.analysis_result: Optional[dict] = None
        
    async def initialize(self):
        """Initialize MCP client and other components"""
        try:
            await mcp_client.initialize()
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            ui.notify("Failed to initialize MCP client", type='negative')
    
    def create_ui(self):
        """Create the NiceGUI interface"""
        # Set page title and favicon
        ui.page_title(self.config['title'])
        
        # Main container
        with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
            # Header
            with ui.row().classes('w-full items-center mb-6'):
                ui.icon('analytics', size='2em').classes('text-blue-600')
                ui.label(self.config['title']).classes('text-3xl font-bold text-gray-800')
            
            # Instructions
            with ui.card().classes('w-full mb-6'):
                ui.label('Instructions').classes('text-xl font-semibold mb-2')
                ui.markdown("""
                1. **Upload Files**: Add support case PDFs, documentation, logs, etc.
                2. **Add URLs**: Include links to Confluence pages, documentation, or other web resources
                3. **Reference Jira Tickets**: Add existing ticket IDs for context
                4. **Describe Issue**: Provide a clear description of the problem
                5. **Generate Analysis**: Click to create the comprehensive RCA report
                """)
            
            # File Upload Section
            with ui.card().classes('w-full mb-4'):
                ui.label('File Upload').classes('text-lg font-semibold mb-2')
                ui.upload(
                    on_upload=self.handle_file_upload,
                    multiple=True,
                    max_file_size=self.config['max_file_size_mb'] * 1024 * 1024
                ).classes('w-full').props('accept=".pdf,.txt,.docx,.md"')
                
                # Display uploaded files
                self.files_list = ui.column().classes('mt-2')
                self.update_files_display()
            
            # URLs Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Web Resources').classes('text-lg font-semibold mb-2')
                with ui.row().classes('w-full'):
                    self.url_input = ui.input('Enter URL').classes('flex-grow')
                    ui.button('Add URL', on_click=self.add_url).classes('ml-2')
                
                # Display URLs
                self.urls_list = ui.column().classes('mt-2')
                self.update_urls_display()
            
            # Jira Tickets Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Jira Tickets').classes('text-lg font-semibold mb-2')
                with ui.row().classes('w-full'):
                    self.ticket_input = ui.input('Enter Jira Ticket ID (e.g., CPE-1234)').classes('flex-grow')
                    ui.button('Add Ticket', on_click=lambda: self.add_jira_ticket()).classes('ml-2')
                
                # Display Jira tickets
                self.tickets_list = ui.column().classes('mt-2')
                self.update_tickets_display()
            
            # Issue Description Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Issue Description').classes('text-lg font-semibold mb-2')
                self.issue_description = ui.textarea('Describe the issue that needs root cause analysis...').classes('w-full')
            
            # Analysis Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Generate Analysis').classes('text-lg font-semibold mb-2')
                
                with ui.row().classes('w-full'):
                    ui.button('Generate RCA Report', on_click=self.generate_analysis).classes('bg-blue-600 text-white')
                    ui.button('Clear All', on_click=self.clear_all).classes('bg-gray-500 text-white ml-2')
                
                # Progress indicator
                self.progress_bar = ui.linear_progress(value=0).classes('w-full mt-2')
                self.progress_bar.visible = False
                
                # Analysis results
                self.results_container = ui.column().classes('w-full mt-4')
    
    def handle_file_upload(self, e):
        """Handle file upload"""
        try:
            file_path = self.file_handler.save_uploaded_file(
                e.content.read(),
                e.name
            )
            
            if file_path:
                self.uploaded_files.append(str(file_path))
                self.update_files_display()
                ui.notify(f'File uploaded: {e.name}', type='positive')
                logger.info(f"File uploaded successfully: {file_path}")
            else:
                ui.notify(f'Failed to upload file: {e.name}', type='negative')
                logger.error(f"Failed to upload file: {e.name}")
                
        except Exception as ex:
            ui.notify(f'Error uploading file: {str(ex)}', type='negative')
            logger.error(f"Error uploading file {e.name}: {ex}")
    
    def add_url(self):
        """Add URL to list"""
        url = self.url_input.value.strip()
        if url:
            if url not in self.urls:
                self.urls.append(url)
                self.update_urls_display()
                ui.notify(f'URL added: {url}', type='positive')
            else:
                ui.notify('URL already added', type='warning')
            self.url_input.value = ''
        else:
            ui.notify('Please enter a valid URL', type='negative')
    
    async def add_jira_ticket(self):
        """Add Jira ticket to list and fetch linked issues for user selection, always show dialog for confirmation."""
        ticket = self.ticket_input.value.strip().upper()
        if not ticket:
            ui.notify('Please enter a valid Jira ticket ID', type='negative')
            return

        if ticket in self.jira_tickets:
            ui.notify('Ticket already added', type='warning')
            self.ticket_input.value = ''
            return

        # Fetch linked issues using RCA generator's source data collection
        try:
            from src.rca_generator import rca_generator
            source_data = await rca_generator._collect_source_data([], [], [ticket])
            linked_issues = source_data.get('jira_linked_issues', {}).get(ticket, [])
        except Exception as e:
            logger.error(f"Failed to fetch linked issues for {ticket}: {e}")
            linked_issues = []

        # Always show a dialog, even if no linked issues, for confirmation and possible future file upload
        await self.show_linked_issues_dialog(linked_issues, main_ticket=ticket)

    async def show_linked_issues_dialog(self, linked_issues, main_ticket=None):
        """Show a dialog with a checklist of linked issues for user to add, and always add the main ticket if confirmed.
        No file upload for tickets in this dialog.
        """
        dialog = ui.dialog().props('persistent')
        with dialog:
            if linked_issues:
                ui.label('Add Linked Jira Issues').classes('text-lg font-semibold mb-2')
                ui.markdown('This ticket has linked Jira issues. Select any you want to include in the RCA context. The main ticket will always be included.')
            else:
                ui.label('Add Jira Ticket').classes('text-lg font-semibold mb-2')
                ui.markdown('No linked issues found. Confirm to add this ticket to the RCA context.')

            # Show the main ticket as always checked and disabled
            if main_ticket:
                ui.checkbox(f"{main_ticket} (Main ticket)", value=True).props('disable')
            checkboxes = []
            for issue in linked_issues:
                key = issue.get('key', '')
                summary = issue.get('summary', '')
                link_type = issue.get('link_type', '')
                direction = issue.get('direction', '')
                label = f"{key} ({link_type}, {direction}) - {summary}"
                cb = ui.checkbox(label, value=False)
                checkboxes.append((cb, key))
            with ui.row():
                async def on_confirm():
                    added = 0
                    # Always add the main ticket if not already present
                    if main_ticket and main_ticket not in self.jira_tickets:
                        self.jira_tickets.append(main_ticket)
                        added += 1
                    # Read checkbox values for linked issues
                    for cb, key in checkboxes:
                        if cb.value and key not in self.jira_tickets:
                            self.jira_tickets.append(key)
                            added += 1
                    self.update_tickets_display()
                    if added == 1 and main_ticket:
                        ui.notify(f"Added main Jira ticket: {main_ticket}", type='positive')
                    elif added > 0:
                        ui.notify(f"Added {added} Jira issues", type='positive')
                    else:
                        ui.notify("No new Jira issues added", type='info')
                    self.ticket_input.value = ''
                    dialog.close()
                ui.button('Add Selected', on_click=on_confirm).props('color=primary')
                ui.button('Cancel', on_click=dialog.close)
        await dialog.open()
    
    def update_files_display(self):
        """Update the files display"""
        self.files_list.clear()
        for i, file_path in enumerate(self.uploaded_files):
            file_name = Path(file_path).name
            with self.files_list:
                with ui.row().classes('w-full items-center'):
                    ui.icon('attach_file').classes('text-blue-600')
                    ui.label(file_name).classes('flex-grow')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_file(idx)).classes('text-red-600')
    
    def update_urls_display(self):
        """Update the URLs display"""
        self.urls_list.clear()
        for i, url in enumerate(self.urls):
            with self.urls_list:
                with ui.row().classes('w-full items-center'):
                    ui.icon('link').classes('text-green-600')
                    ui.label(url).classes('flex-grow')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_url(idx)).classes('text-red-600')
    
    def update_tickets_display(self):
        """Update the Jira tickets display, showing linked issues visually."""
        self.tickets_list.clear()
        for i, ticket in enumerate(self.jira_tickets):
            is_linked = False
            # Heuristic: if ticket is not the first/main ticket, mark as linked
            if i > 0:
                is_linked = True
            with self.tickets_list:
                with ui.row().classes('w-full items-center'):
                    if is_linked:
                        ui.icon('call_merge').classes('text-purple-600')
                        ui.label(f"{ticket} (Linked)").classes('flex-grow text-purple-800')
                    else:
                        ui.icon('confirmation_number').classes('text-orange-600')
                        ui.label(ticket).classes('flex-grow')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_ticket(idx)).classes('text-red-600')
    
    def remove_file(self, index: int):
        """Remove file from list"""
        if 0 <= index < len(self.uploaded_files):
            removed_file = self.uploaded_files.pop(index)
            self.update_files_display()
            ui.notify(f'File removed: {Path(removed_file).name}', type='info')
    
    def remove_url(self, index: int):
        """Remove URL from list"""
        if 0 <= index < len(self.urls):
            removed_url = self.urls.pop(index)
            self.update_urls_display()
            ui.notify(f'URL removed: {removed_url}', type='info')
    
    def remove_ticket(self, index: int):
        """Remove Jira ticket from list"""
        if 0 <= index < len(self.jira_tickets):
            removed_ticket = self.jira_tickets.pop(index)
            self.update_tickets_display()
            ui.notify(f'Ticket removed: {removed_ticket}', type='info')
    
    async def generate_analysis(self):
        """Generate RCA analysis"""
        try:
            # Validate inputs
            if not self.issue_description.value.strip():
                ui.notify('Please provide an issue description', type='negative')
                return
            
            if not self.uploaded_files and not self.urls and not self.jira_tickets:
                ui.notify('Please add at least one file, URL, or Jira ticket', type='negative')
                return
            
            # Show progress
            self.progress_bar.visible = True
            self.progress_bar.value = 0.1
            ui.notify('Starting RCA analysis...', type='info')
            
            # Generate analysis
            self.analysis_result = await rca_generator.generate_rca_analysis(
                files=self.uploaded_files,
                urls=self.urls,
                jira_tickets=self.jira_tickets,
                issue_description=self.issue_description.value.strip()
            )
            
            self.progress_bar.value = 1.0
            self.display_results()
            ui.notify('RCA analysis completed successfully!', type='positive')
            
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg:
                ui.notify('OpenAI quota exceeded. Switching to Anthropic...', type='warning')
            elif "Expecting value" in error_msg:
                ui.notify('LLM response parsing error. Check logs for details.', type='negative')
            else:
                ui.notify(f'Error generating analysis: {error_msg}', type='negative')
            logger.error(f"Error generating analysis: {e}")
        finally:
            self.progress_bar.visible = False
    
    def display_results(self):
        """Display analysis results"""
        if not self.analysis_result:
            return

        self.results_container.clear()

        with self.results_container:
            ui.label('Analysis Results').classes('text-xl font-semibold mb-4')

            analysis = self.analysis_result['analysis']

            # Dynamically display all sections from the template, or fallback to all keys in analysis
            try:
                from src.rca_generator import rca_generator
                template_sections = rca_generator.get_template_prompts()
            except Exception:
                template_sections = []

            shown_keys = set()
            if template_sections:
                for section in template_sections:
                    header = section['header']
                    # Try to find a matching key in analysis (case-insensitive, underscores/space-insensitive)
                    norm_header = header.lower().replace(" ", "_")
                    key = None
                    for k in analysis.keys():
                        if k.lower().replace(" ", "_") == norm_header:
                            key = k
                            break
                    value = analysis.get(key) if key else None
                    shown_keys.add(key)
                    with ui.card().classes('w-full mb-4'):
                        ui.label(header).classes('text-lg font-semibold mb-2')
                        if isinstance(value, list):
                            for v in value:
                                ui.markdown(f"• {v}")
                        elif value is not None:
                            ui.markdown(str(value))
                        else:
                            ui.markdown("N/A")
            else:
                # Fallback: show all keys in analysis
                for k, v in analysis.items():
                    with ui.card().classes('w-full mb-4'):
                        ui.label(k.replace("_", " ").title()).classes('text-lg font-semibold mb-2')
                        if isinstance(v, list):
                            for item in v:
                                ui.markdown(f"• {item}")
                        else:
                            ui.markdown(str(v))

            # Show any remaining keys in analysis not already shown
            for k, v in analysis.items():
                if k in shown_keys:
                    continue
                with ui.card().classes('w-full mb-4'):
                    ui.label(k.replace("_", " ").title()).classes('text-lg font-semibold mb-2')
                    if isinstance(v, list):
                        for item in v:
                            ui.markdown(f"• {item}")
                    else:
                        ui.markdown(str(v))

            # Raw Response (if available)
            if analysis.get('raw_response'):
                with ui.card().classes('w-full mb-4'):
                    ui.label('Raw LLM Response').classes('text-lg font-semibold mb-2')
                    ui.markdown("⚠️ **Note**: This analysis used fallback parsing due to JSON format issues.")
                    with ui.expansion('View Raw Response', icon='code').classes('w-full'):
                        ui.code(analysis['raw_response']).classes('w-full')

            # Download Report
            with ui.card().classes('w-full mb-4'):
                ui.label('Report Download').classes('text-lg font-semibold mb-2')
                ui.markdown(f"Report saved to: `{self.analysis_result['document_path']}`")
    
    def clear_all(self):
        """Clear all inputs and results"""
        self.uploaded_files.clear()
        self.urls.clear()
        self.jira_tickets.clear()
        self.issue_description.value = ''
        self.analysis_result = None
        
        self.update_files_display()
        self.update_urls_display()
        self.update_tickets_display()
        self.results_container.clear()
        
        ui.notify('All data cleared', type='info')

# Global app instance
rca_app = RCAApp()

@ui.page('/')
async def index():
    """Main page"""
    await rca_app.initialize()
    rca_app.create_ui()

def create_app():
    """Create and configure the NiceGUI application"""
    app.on_startup(rca_app.initialize)
    return app
