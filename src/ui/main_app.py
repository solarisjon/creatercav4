#!/usr/bin/env python3
"""
MCP-based Root Cause Analysis Tool - Refactored
Main application using NiceGUI with clean architecture
"""

import asyncio
from pathlib import Path
from nicegui import ui
from src.utils.logger import setup_logger
from src.utils.file_handler import FileHandler
from src.config import config

# Setup logging first
logger = setup_logger(__name__)

# Try to import the main MCP client, fall back to simple client if it fails
try:
    from src.mcp_client import mcp_client
    logger.info("Main MCP client imported successfully")
except ImportError as e:
    logger.warning(f"Main MCP client failed to import: {e}. Using simple fallback.")
    from src.mcp_client_simple import simple_mcp_client as mcp_client

from src.core.analysis.rca_engine import RCAEngine
from src.ui.components.analysis_display import AnalysisDisplay

class RCAApp:
    """Main RCA Application with clean architecture"""
    
    # Available prompt types
    PROMPT_OPTIONS = {
        "formal_rca_prompt": "Formal RCA Report",
        "initial_analysis_prompt": "Initial Analysis",
        "kt-analysis_prompt": "Kepner-Tregoe Analysis"
    }
    
    def __init__(self):
        self.file_handler = FileHandler(
            upload_dir=config.app_config['upload_directory'],
            allowed_extensions=config.app_config['allowed_file_types'],
            max_size_mb=config.app_config['max_file_size_mb']
        )
        # Create a combined config for RCAEngine that includes both LLM and app configs
        rca_config = {
            **config.llm_config,
            'output_directory': config.app_config['output_directory']
        }
        self.rca_engine = RCAEngine(rca_config)
        # Inject the MCP client into the RCA engine
        self.rca_engine.set_mcp_client(mcp_client)
        
        # UI state
        self.uploaded_files = []
        self.urls = []
        self.jira_tickets = []
        self.selected_prompt = "formal_rca_prompt"
        self.analysis_result = None
        self.analysis_status = None  # Track analysis status for UI updates
        self.analysis_error = None   # Track analysis errors for UI updates
        
        # Progress tracking
        self.progress_steps = [
            "Initializing analysis...",
            "Loading prompt and context...", 
            "Processing uploaded files...",
            "Fetching URL content...",
            "Retrieving Jira tickets...",
            "Generating LLM analysis...",
            "Parsing response...",
            "Finalizing report..."
        ]
        self.current_step = 0
        
        # Jira fetch state
        self._jira_fetch_status = None
        self._jira_main_ticket = None
        self._jira_linked_issues = []
        self._jira_fetch_error = None
        self._jira_check_timer = None
        
        # UI components
        self.files_list = None
        self.urls_list = None
        self.tickets_list = None
        self.results_container = None
        self.analysis_display = None
        self.progress_bar = None
        self.progress_label = None
        self.progress_container = None
        self.status_timer = None  # Timer to check analysis status
        
    def setup_ui(self):
        """Setup the user interface with NetApp branding"""
        ui.page_title("NetApp RCA Analysis Tool")
        
        # Add custom CSS and JavaScript
        ui.add_head_html('''
            <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
            <link rel="stylesheet" href="/static/netapp_styles.css">
            <script>
                function removeFile(index) {
                    // Trigger file removal - this will be handled by the Python backend
                    window.dispatchEvent(new CustomEvent('removeFile', {detail: {index: index}}));
                }
                function removeUrl(index) {
                    window.dispatchEvent(new CustomEvent('removeUrl', {detail: {index: index}}));
                }
                function removeTicket(index) {
                    window.dispatchEvent(new CustomEvent('removeTicket', {detail: {index: index}}));
                }
            </script>
        ''')
        
        # NetApp Header
        with ui.row().classes('w-full netapp-header'):
            with ui.row().classes('w-full max-w-6xl mx-auto px-4').style('align-items: center'):
                ui.html('<img src="/static/netapp_logo.png" class="netapp-logo" alt="NetApp Logo">')
                with ui.column().classes('flex-grow'):
                    ui.html('<h1 class="netapp-title">Root Cause Analysis Tool</h1>')
                    ui.html('<p class="netapp-subtitle">Intelligent analysis for faster problem resolution</p>')
        
        # Main content area - single column with wide cards
        with ui.column().classes('w-full p-6 netapp-fade-in').style('max-width: 80%; margin: 0 auto;'):
            
            # File upload section
            self._create_upload_section()
            
            # URL section  
            self._create_url_section()
            
            # Jira section
            self._create_jira_section()
            
            # Analysis configuration
            self._create_analysis_section()
            
            # Control buttons
            self._create_control_section()
            
            # Progress section (initially hidden) - moved below controls
            with ui.card().classes('netapp-card').style('max-width: 80%; margin: 0 auto; width: 100%;') as self.progress_container:
                self.progress_container.visible = False
                with ui.column().classes('netapp-card-content w-full'):
                    ui.html('<div class="netapp-card-header">Analysis Progress</div>')
                    self.progress_label = ui.label('Ready to start analysis...').classes('text-sm mb-2 self-start')
                    self.progress_bar = ui.linear_progress(value=0).classes('w-full netapp-progress').style('max-width: 600px;')
        
        # Results section - full width
        self._create_results_section()
    
    def _create_upload_section(self):
        """Create file upload section with NetApp styling"""
        with ui.card().classes('netapp-card').style('max-width: 80%; margin: 0 auto; width: 100%;'):
            ui.html('<div class="netapp-card-header"><i class="material-icons netapp-icon-file" style="vertical-align: middle; margin-right: 8px;">attach_file</i>File Upload</div>')
            with ui.column().classes('netapp-card-content w-full'):
                ui.upload(
                    on_upload=self.handle_file_upload,
                    multiple=True,
                    max_file_size=50 * 1024 * 1024  # 50MB
                ).classes('w-full').style('border: 2px dashed var(--netapp-blue); border-radius: 8px; padding: 1rem; width: 100%;')
                
                # Display uploaded files
                ui.label('Uploaded Files:').classes('text-sm font-medium mt-3 mb-2 self-start')
                self.files_list = ui.column().classes('w-full')
    
    def _create_url_section(self):
        """Create URL input section with NetApp styling"""
        with ui.card().classes('netapp-card').style('max-width: 80%; margin: 0 auto; width: 100%;'):
            ui.html('<div class="netapp-card-header"><i class="material-icons netapp-icon-link" style="vertical-align: middle; margin-right: 8px;">link</i>URL Sources</div>')
            with ui.column().classes('netapp-card-content w-full'):
                with ui.row().classes('w-full gap-2 justify-center'):
                    self.url_input = ui.input('Enter URL').classes('flex-grow netapp-input').style('min-width: 300px;')
                    ui.button('Add URL', on_click=self.add_url).classes('netapp-btn-primary')
                
                # Display added URLs
                ui.label('Added URLs:').classes('text-sm font-medium mt-3 mb-2 self-start')
                self.urls_list = ui.column().classes('w-full')
    
    def _create_jira_section(self):
        """Create Jira ticket section with NetApp styling"""
        with ui.card().classes('netapp-card').style('max-width: 80%; margin: 0 auto; width: 100%;'):
            ui.html('<div class="netapp-card-header"><i class="material-icons netapp-icon-ticket" style="vertical-align: middle; margin-right: 8px;">confirmation_number</i>Jira Integration</div>')
            with ui.column().classes('netapp-card-content w-full'):
                with ui.row().classes('w-full gap-2 justify-center'):
                    self.ticket_input = ui.input('Enter Jira Ticket ID').classes('flex-grow netapp-input').style('min-width: 300px;')
                    ui.button('Add Ticket', on_click=self.add_jira_ticket_sync).classes('netapp-btn-primary')
                
                # Display added tickets
                ui.label('Added Tickets:').classes('text-sm font-medium mt-3 mb-2 self-start')
                self.tickets_list = ui.column().classes('w-full')
    
    def _create_analysis_section(self):
        """Create analysis configuration section with NetApp styling"""
        with ui.card().classes('netapp-card').style('max-width: 80%; margin: 0 auto; width: 100%;'):
            ui.html('<div class="netapp-card-header"><i class="material-icons" style="vertical-align: middle; margin-right: 8px;">settings</i>Analysis Configuration</div>')
            with ui.column().classes('netapp-card-content w-full'):
                # Prompt selection
                ui.label('Analysis Type:').classes('text-sm font-medium mb-2 self-start')
                self.prompt_select = ui.select(
                    self.PROMPT_OPTIONS,
                    value=self.selected_prompt,
                    on_change=self.on_prompt_select
                ).classes('w-full netapp-input').style('max-width: 400px;')
    
    def _create_control_section(self):
        """Create control buttons section with NetApp styling"""
        with ui.row().classes('w-full gap-3 mb-4 justify-center'):
            ui.button(
                'Generate Analysis', 
                on_click=self.start_analysis
            ).classes('netapp-btn-orange').style('min-width: 200px; font-size: 1.1rem;')
            
            ui.button(
                'Clear All', 
                on_click=self.clear_all
            ).classes('netapp-btn-secondary').style('min-width: 120px;')
    
    def _create_results_section(self):
        """Create results display section with NetApp styling - full width"""
        with ui.column().classes('w-full px-4 py-6'):
            with ui.card().classes('netapp-card netapp-results w-full'):
                ui.html('<div class="netapp-card-header"><i class="material-icons" style="vertical-align: middle; margin-right: 8px;">analytics</i>Analysis Results</div>')
                self.results_container = ui.column().classes('netapp-card-content w-full')
    
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
                ui.notify(f'File uploaded: {e.name}', type='positive', color='var(--netapp-success)')
                logger.info(f"File uploaded successfully: {file_path}")
            else:
                ui.notify(f'Failed to upload file: {e.name}', type='negative', color='var(--netapp-danger)')
                logger.error(f"Failed to upload file: {e.name}")
                
        except Exception as ex:
            ui.notify(f'Error uploading file: {str(ex)}', type='negative', color='var(--netapp-danger)')
            logger.error(f"Error uploading file {e.name}: {ex}")
    
    def add_url(self):
        """Add URL to list"""
        url = self.url_input.value.strip()
        if url:
            if url not in self.urls:
                self.urls.append(url)
                self.update_urls_display()
                ui.notify(f'URL added: {url}', type='positive', color='var(--netapp-success)')
            else:
                ui.notify('URL already added', type='warning', color='var(--netapp-warning)')
            self.url_input.value = ''
        else:
            ui.notify('Please enter a valid URL', type='negative', color='var(--netapp-danger)')
    
    def add_jira_ticket_sync(self):
        """Add Jira ticket to list with linked issues dialog"""
        ticket = self.ticket_input.value.strip().upper()
        if not ticket:
            ui.notify('Please enter a valid Jira ticket ID', type='negative')
            return

        if ticket in self.jira_tickets:
            ui.notify('Ticket already added', type='warning')
            self.ticket_input.value = ''
            return

        # Show loading and start background fetch
        ui.notify('Fetching linked issues...', type='info')
        
        # Set up state tracking for the async operation
        self._jira_fetch_status = 'fetching'
        self._jira_main_ticket = ticket
        
        # Start async task to fetch linked issues
        import asyncio
        asyncio.create_task(self._fetch_linked_issues_background(ticket))
        
        # Start a timer to check for completion
        self._jira_check_timer = ui.timer(0.5, self._check_jira_fetch_status)

    async def _fetch_linked_issues_background(self, main_ticket: str):
        """Fetch linked issues in background without UI interactions"""
        try:
            # Import the mcp_client
            from src.mcp_client import mcp_client
            
            # Fetch linked issues
            grouped = await mcp_client.get_linked_issues_grouped(main_ticket)
            linked_issues = []
            for link_type, issues in grouped.items():
                for issue in issues:
                    issue['link_type'] = link_type
                    linked_issues.append(issue)
            
            # Store the results for UI to pick up
            self._jira_linked_issues = linked_issues
            self._jira_fetch_status = 'completed'
            
        except Exception as e:
            logger.error(f"Failed to fetch linked issues for {main_ticket}: {e}")
            self._jira_fetch_error = str(e)
            self._jira_fetch_status = 'error'

    def _check_jira_fetch_status(self):
        """Check the status of Jira linked issues fetching"""
        if not hasattr(self, '_jira_fetch_status'):
            return
            
        if self._jira_fetch_status == 'completed':
            # Fetch completed successfully - show dialog
            self._jira_check_timer.cancel()
            self._show_linked_issues_dialog()
            
        elif self._jira_fetch_status == 'error':
            # Fetch failed - show error and add main ticket only
            self._jira_check_timer.cancel()
            error_msg = getattr(self, '_jira_fetch_error', 'Unknown error')
            ui.notify(f'Error fetching linked issues: {error_msg}. Adding main ticket only.', type='warning')
            self._add_single_ticket(self._jira_main_ticket)
            
            # Clean up
            self._cleanup_jira_fetch_state()

    def _cleanup_jira_fetch_state(self):
        """Clean up Jira fetch state variables"""
        for attr in ['_jira_fetch_status', '_jira_main_ticket', '_jira_linked_issues', '_jira_fetch_error']:
            if hasattr(self, attr):
                delattr(self, attr)

    def _add_single_ticket(self, ticket: str):
        """Add a single ticket without linked issues"""
        if ticket not in self.jira_tickets:
            self.jira_tickets.append(ticket)
            self.update_tickets_display()
            ui.notify(f'Ticket added: {ticket}', type='positive')
        self.ticket_input.value = ''

    def _show_linked_issues_dialog(self):
        """Show the linked issues selection dialog"""
        if not hasattr(self, '_jira_main_ticket'):
            return
            
        main_ticket = self._jira_main_ticket
        linked_issues = getattr(self, '_jira_linked_issues', [])
        
        # Create the dialog in proper UI context
        with ui.dialog() as dialog, ui.card():
            ui.label('Add Jira Issues').classes('text-lg font-semibold mb-2')
            
            # Main ticket (always selected)
            ui.checkbox(f"{main_ticket} (Main ticket)", value=True).props('disable')
            
            # Linked issues
            checkboxes = []
            if linked_issues:
                ui.label('Related Issues:').classes('text-sm font-medium mt-2 mb-1')
                for issue in linked_issues:
                    key = issue.get('key', '')
                    summary = issue.get('summary', '')
                    link_type = issue.get('link_type', '')
                    label = f"{key} ({link_type}) - {summary}"
                    cb = ui.checkbox(label, value=False)
                    checkboxes.append((cb, key))
            else:
                ui.label('No linked issues found.').classes('text-sm text-gray-600 mt-2')
            
            with ui.row().classes('mt-4'):
                def on_confirm():
                    # Add main ticket
                    if main_ticket not in self.jira_tickets:
                        self.jira_tickets.append(main_ticket)
                    
                    # Add selected linked issues
                    for cb, key in checkboxes:
                        if cb.value and key not in self.jira_tickets:
                            self.jira_tickets.append(key)
                    
                    self.update_tickets_display()
                    ui.notify(f"Added Jira ticket(s): {main_ticket}" + 
                             (f" + {sum(1 for cb, _ in checkboxes if cb.value)} linked issues" if any(cb.value for cb, _ in checkboxes) else ""), 
                             type='positive')
                    self.ticket_input.value = ''
                    dialog.close()
                    
                    # Clean up state
                    self._cleanup_jira_fetch_state()
                
                def on_cancel():
                    dialog.close()
                    # Clean up state
                    self._cleanup_jira_fetch_state()
                
                ui.button('Add Selected', on_click=on_confirm)
                ui.button('Cancel', on_click=on_cancel)
        
        dialog.open()

    def update_files_display(self):
        """Update the files display with NetApp styling"""
        self.files_list.clear()
        for i, file_path in enumerate(self.uploaded_files):
            file_name = Path(file_path).name
            with self.files_list:
                with ui.row().classes('netapp-file-item netapp-slide-up'):
                    with ui.row().style('align-items: center; flex-grow: 1;'):
                        ui.icon('attach_file').classes('netapp-icon-file mr-2')
                        ui.label(file_name).style('font-weight: 500;')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_file(idx)).classes('netapp-icon-delete').style('background: none; border: none; padding: 4px;')
    
    def update_urls_display(self):
        """Update the URLs display with NetApp styling"""
        self.urls_list.clear()
        for i, url in enumerate(self.urls):
            display_url = url[:50] + '...' if len(url) > 50 else url
            with self.urls_list:
                with ui.row().classes('netapp-file-item netapp-slide-up'):
                    with ui.row().style('align-items: center; flex-grow: 1;'):
                        ui.icon('link').classes('netapp-icon-link mr-2')
                        ui.label(display_url).style('font-weight: 500;')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_url(idx)).classes('netapp-icon-delete').style('background: none; border: none; padding: 4px;')
    
    def update_tickets_display(self):
        """Update the Jira tickets display with NetApp styling"""
        self.tickets_list.clear()
        for i, ticket in enumerate(self.jira_tickets):
            with self.tickets_list:
                with ui.row().classes('netapp-file-item netapp-slide-up'):
                    with ui.row().style('align-items: center; flex-grow: 1;'):
                        ui.icon('confirmation_number').classes('netapp-icon-ticket mr-2')
                        ui.label(ticket).style('font-weight: 500;')
                    ui.button(icon='delete', on_click=lambda idx=i: self.remove_ticket(idx)).classes('netapp-icon-delete').style('background: none; border: none; padding: 4px;')
    
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
    
    def on_prompt_select(self, e):
        """Handle prompt selection change"""
        self.selected_prompt = e.value
        logger.info(f"Prompt selection changed to: {self.selected_prompt}")
    
    def start_analysis(self):
        """Start analysis with enhanced progress tracking"""
        # Validate inputs first in sync context
        if not self.uploaded_files and not self.urls and not self.jira_tickets:
            ui.notify('Please add at least one file, URL, or Jira ticket', type='negative')
            return

        # Reset status and progress
        self.analysis_status = 'running'
        self.analysis_error = None
        self.analysis_result = None
        self.current_step = 0

        # Show progress container and initialize
        self.progress_container.visible = True
        self.progress_bar.value = 0
        self.progress_label.text = self.progress_steps[0]
        
        # Clear previous results
        if self.results_container:
            self.results_container.clear()
        
        ui.notify('Starting RCA analysis...', type='info')
        
        # Start the async analysis in background
        asyncio.create_task(self._generate_analysis_async())
        
        # Start status checking timer with progress updates
        self.status_timer = ui.timer(0.3, self._update_progress_display)

    def _update_progress_display(self):
        """Update progress display with current status and step"""
        if self.analysis_status == 'completed':
            # Analysis completed successfully
            self.progress_bar.value = 1.0
            self.progress_label.text = "Analysis completed successfully!"
            self.display_results()
            ui.notify('RCA analysis completed successfully!', type='positive')
            self.status_timer.cancel()
            # Hide progress after a brief delay
            ui.timer(2.0, lambda: setattr(self.progress_container, 'visible', False), once=True)
            self.analysis_status = None
            
        elif self.analysis_status == 'error':
            # Analysis failed
            self.progress_bar.value = 0
            self.progress_label.text = f"Error: {self.analysis_error or 'Unknown error occurred'}"
            ui.notify(f'Error generating analysis: {self.analysis_error}', type='negative')
            self.status_timer.cancel()
            # Hide progress after delay to show error
            ui.timer(5.0, lambda: setattr(self.progress_container, 'visible', False), once=True)
            self.analysis_status = None
            self.analysis_error = None
            
        elif self.analysis_status == 'running':
            # Update progress based on current step
            if self.current_step < len(self.progress_steps):
                progress_value = (self.current_step + 0.5) / len(self.progress_steps)
                self.progress_bar.value = min(progress_value, 0.95)  # Cap at 95% until complete
                self.progress_label.text = self.progress_steps[self.current_step]

    async def _generate_analysis_async(self):
        """Generate RCA analysis with progress tracking"""
        try:
            # Step 1: Initializing
            self.current_step = 0
            await asyncio.sleep(0.2)  # Brief pause to show step
            
            # Step 2: Loading prompt and context
            self.current_step = 1
            await asyncio.sleep(0.3)
            
            # Step 3: Processing files (if any)
            if self.uploaded_files:
                self.current_step = 2
                await asyncio.sleep(0.4)
            
            # Step 4: Fetching URLs (if any) 
            if self.urls:
                self.current_step = 3
                await asyncio.sleep(0.4)
            
            # Step 5: Retrieving Jira tickets (if any)
            if self.jira_tickets:
                self.current_step = 4
                await asyncio.sleep(0.4)
            
            # Step 6: Generating LLM analysis
            self.current_step = 5
            
            # Use the new RCA engine
            result = await self.rca_engine.generate_analysis(
                files=self.uploaded_files,
                urls=self.urls,
                jira_tickets=self.jira_tickets,
                analysis_type=self.selected_prompt,
                issue_description=""
            )
            
            # Step 7: Parsing response
            self.current_step = 6
            await asyncio.sleep(0.2)
            
            # Store the prompt file used for this analysis
            result['prompt_file_used'] = self.selected_prompt
            
            # Step 8: Finalizing
            self.current_step = 7
            await asyncio.sleep(0.2)
            
            # Update results and status
            self.analysis_result = result
            self.analysis_status = 'completed'

        except Exception as e:
            # Store error for UI update
            self.analysis_error = str(e)
            self.analysis_status = 'error'
            logger.error(f"Error generating analysis: {e}")

    def display_results(self):
        """Display analysis results using the new display component"""
        if not self.analysis_result:
            return

        self.results_container.clear()
        
        with self.results_container:
            # Create and use the new AnalysisDisplay component
            if not self.analysis_display:
                self.analysis_display = AnalysisDisplay(self.results_container)
            
            # Display the analysis using the new component
            self.analysis_display.display_analysis(self.analysis_result)
    
    def _advance_progress_step(self, step_name: str = None):
        """Advance to the next progress step"""
        if self.current_step < len(self.progress_steps) - 1:
            self.current_step += 1
        if step_name:
            # Override the default step message with a custom one
            self.progress_label.text = step_name

    def clear_all(self):
        """Clear all uploaded data and reset UI"""
        self.uploaded_files.clear()
        self.urls.clear()
        self.jira_tickets.clear()
        self.analysis_result = None
        self.analysis_status = None
        self.analysis_error = None
        self.selected_prompt = "formal_rca_prompt"
        self.prompt_select.value = self.selected_prompt

        # Cancel any running status timer
        if self.status_timer:
            self.status_timer.cancel()
            self.status_timer = None

        # Cancel any running Jira fetch timer
        if hasattr(self, '_jira_check_timer') and self._jira_check_timer:
            self._jira_check_timer.cancel()
            self._jira_check_timer = None
        
        # Clean up Jira fetch state
        self._cleanup_jira_fetch_state()

        self.update_files_display()
        self.update_urls_display()
        self.update_tickets_display()
        self.results_container.clear()

        ui.notify('All data cleared', type='info')


def create_app():
    """Create and setup the RCA application"""
    rca_app = RCAApp()
    rca_app.setup_ui()
    return rca_app


# Global app instance for main.py compatibility
rca_app = None

def get_app():
    """Get or create the global app instance"""
    global rca_app
    if rca_app is None:
        rca_app = create_app()
    return rca_app
