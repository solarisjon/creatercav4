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
        """Create the NiceGUI interface with NetApp branding"""
        # Set page title and favicon
        ui.page_title("NetApp RCA Tool")
        ui.add_head_html("""
        <link rel="icon" type="image/png" href="https://www.netapp.com/wp-content/uploads/2021/05/cropped-netapp-favicon-32x32.png">
        <style>
            body { background: #f7f9fa; }
            .netapp-header { background: #0067c5; color: white; border-radius: 8px; }
            .netapp-logo { height: 48px; margin-right: 18px; }
            .netapp-title { font-size: 2.2rem; font-weight: 700; letter-spacing: 1px; }
            .netapp-subtitle { font-size: 1.1rem; color: #e3eaf2; }
            .netapp-card { border: 1px solid #e3eaf2; border-radius: 8px; background: white; }
            .netapp-btn-primary { background: #0067c5 !important; color: white !important; }
            .netapp-btn-secondary { background: #e3eaf2 !important; color: #0067c5 !important; }
        </style>
        """)

        # Main container
        with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
            # NetApp Header with logo
            with ui.row().classes('w-full items-center mb-6 netapp-header p-4'):
                ui.image('https://www.netapp.com/wp-content/uploads/2021/05/netapp-logo.png').classes('netapp-logo')
                ui.label('Root Cause Analysis Tool').classes('netapp-title')
                ui.label('Powered by MCP & LLM').classes('ml-4 netapp-subtitle')

            # Instructions
            with ui.card().classes('w-full mb-6 netapp-card'):
                ui.label('Instructions').classes('text-xl font-semibold mb-2 text-[#0067c5]')
                ui.markdown("""
                1. **Upload Files**: Add support case PDFs, documentation, logs, etc.
                2. **Add URLs**: Include links to Confluence pages, documentation, or other web resources.
                3. **Reference Jira Tickets**: Add existing ticket IDs for context.
                4. **Describe Issue**: Provide a clear description of the problem.
                5. **Generate Analysis**: Click to create the comprehensive RCA report.
                """)

            # File Upload Section
            with ui.card().classes('w-full mb-4 netapp-card'):
                ui.label('File Upload').classes('text-lg font-semibold mb-2 text-[#0067c5]')
                ui.upload(
                    on_upload=self.handle_file_upload,
                    multiple=True,
                    max_file_size=self.config['max_file_size_mb'] * 1024 * 1024
                ).classes('w-full').props('accept=".pdf,.txt,.docx,.md"')
                self.files_list = ui.column().classes('mt-2')
                self.update_files_display()

            # URLs Section
            with ui.card().classes('w-full mb-4 netapp-card'):
                ui.label('Web Resources').classes('text-lg font-semibold mb-2 text-[#0067c5]')
                with ui.row().classes('w-full'):
                    self.url_input = ui.input('Enter URL').classes('flex-grow')
                    ui.button('Add URL', on_click=self.add_url).classes('ml-2 netapp-btn-secondary')
                self.urls_list = ui.column().classes('mt-2')
                self.update_urls_display()

            # Jira Tickets Section
            with ui.card().classes('w-full mb-4 netapp-card'):
                ui.label('Jira Tickets').classes('text-lg font-semibold mb-2 text-[#0067c5]')
                with ui.row().classes('w-full'):
                    self.ticket_input = ui.input('Enter Jira Ticket ID (e.g., CPE-1234)').classes('flex-grow')
                    ui.button('Add Ticket', on_click=lambda: self.add_jira_ticket()).classes('ml-2 netapp-btn-secondary')
                self.tickets_list = ui.column().classes('mt-2')
                self.update_tickets_display()

            # Issue Description Section
            # (Removed as per request)

            # Analysis Section
            with ui.card().classes('w-full mb-4 netapp-card'):
                ui.label('Generate Analysis').classes('text-lg font-semibold mb-2 text-[#0067c5]')
                with ui.row().classes('w-full'):
                    ui.button('Generate RCA Report', on_click=self.generate_analysis).classes('netapp-btn-primary')
                    ui.button('Clear All', on_click=self.clear_all).classes('ml-2 netapp-btn-secondary')
                    ui.button('Reset Context', on_click=self.reset_context).classes('ml-2 netapp-btn-secondary')
                self.progress_bar = ui.linear_progress(value=0).classes('w-full mt-2')
                self.progress_bar.visible = False
                self.results_container = ui.column().classes('w-full mt-4')

                # Add buttons to read Executive Summary and Problem Issue sections
                with ui.row().classes('w-full mt-2'):
                    ui.button('Read Executive Summary', on_click=self.read_executive_summary).classes('netapp-btn-secondary')
                    ui.button('Read Problem Issue', on_click=self.read_problem_issue).classes('ml-2 netapp-btn-secondary')

            # Chat/Agentic RCA Refinement Section
            with ui.card().classes('w-full mb-4 netapp-card'):
                ui.label('RCA Agentic Chat & Deep Analysis').classes('text-lg font-semibold mb-2 text-[#0067c5]')
                ui.markdown(
                    "Use this chat to ask deep questions about the uploaded cases, request section rewrites, or instruct the agent to extract or expand on specific RCA sections. "
                    "The agent will use all available context and prior analysis to answer or refine the RCA."
                ).classes('text-sm mb-2')
                self.chat_history = ui.column().classes('w-full min-h-[120px] max-h-[300px] overflow-y-auto bg-[#f7f9fa] p-2 rounded')
                self.chat_messages: List[dict] = []
                with ui.row().classes('w-full'):
                    self.chat_input = ui.input('Ask a question, request a section rewrite, or instruct the agent...').classes('flex-grow')
                    ui.button('Send', on_click=self.handle_chat_message).classes('ml-2 netapp-btn-primary')
    
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

        # Fetch linked issues using MCP client directly for accurate grouping
        try:
            from src.mcp_client import mcp_client
            grouped = await mcp_client.get_linked_issues_grouped(ticket)
            # Flatten grouped dict into a list of dicts with link_type and direction
            linked_issues = []
            for link_type, issues in grouped.items():
                for issue in issues:
                    issue['link_type'] = link_type
                    linked_issues.append(issue)
        except Exception as e:
            logger.error(f"Failed to fetch linked issues for {ticket}: {e}")
            linked_issues = []

        # Always show a dialog, even if no linked issues, for confirmation
        await self.show_linked_issues_dialog(linked_issues, main_ticket=ticket)

    async def show_linked_issues_dialog(self, linked_issues, main_ticket=None):
        """Show a dialog with a checklist of linked issues for user to add, and always add the main ticket if confirmed.
        No file upload for tickets in this dialog.
        The dialog is less opaque and more condensed for better UX.
        """
        # Use a less opaque, more compact dialog
        dialog = ui.dialog().props('persistent').props('max-width=420px').style('background:rgba(255,255,255,0.95);')
        with dialog:
            with ui.column().classes('gap-2 p-2'):
                if linked_issues:
                    ui.label('Add Linked Jira Issues').classes('text-base font-semibold mb-1')
                    ui.markdown('Select any linked Jira issues to include. The main ticket will always be included.').classes('text-sm mb-2')
                else:
                    ui.label('Add Jira Ticket').classes('text-base font-semibold mb-1')
                    ui.markdown('No linked issues found. Confirm to add this ticket.').classes('text-sm mb-2')

                # Show the main ticket as always checked and disabled
                if main_ticket:
                    ui.checkbox(f"{main_ticket} (Main ticket)", value=True).props('disable').classes('text-xs')
                checkboxes = []
                for issue in linked_issues:
                    key = issue.get('key', '')
                    summary = issue.get('summary', '')
                    link_type = issue.get('link_type', '')
                    direction = issue.get('direction', '')
                    label = f"{key} ({link_type}, {direction}) - {summary}"
                    cb = ui.checkbox(label, value=False).classes('text-xs')
                    checkboxes.append((cb, key))
                with ui.row().classes('gap-2 mt-2'):
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
                    ui.button('Add Selected', on_click=on_confirm).props('color=primary').classes('min-w-0 px-2 py-1 text-xs')
                    ui.button('Cancel', on_click=dialog.close).classes('min-w-0 px-2 py-1 text-xs')
        dialog.open()
    
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
                issue_description=""
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

            # Show sources used at the top
            sources = analysis.get("sources_used")
            if sources:
                with ui.card().classes('w-full mb-4'):
                    ui.label("Sources Used").classes('text-lg font-semibold mb-2')
                    for src in sources:
                        ui.markdown(f"- {src}")

            shown_keys = set()
            # Add synonym mapping for template fields
            synonym_map = {
                "customer": ["customer", "customer_name", "client", "account"],
                "cases": ["cases", "case", "support_case", "support_cases", "tickets", "jira_tickets"],
                "synopsis": ["synopsis", "summary", "executive_summary", "overview", "description"],
                "issue_tracking_number": ["issue_tracking_number", "case", "cases", "support_case", "sap_case", "tracking_number"],
            }
            if template_sections:
                for section in template_sections:
                    header = section['header']
                    # Try to find a matching key in analysis (case-insensitive, underscores/space-insensitive)
                    norm_header = header.lower().replace(" ", "_")
                    key = None
                    # Try direct match
                    for k in analysis.keys():
                        if k.lower().replace(" ", "_") == norm_header:
                            key = k
                            break
                    # Try synonyms if direct match fails
                    if key is None:
                        for syn_header, syn_list in synonym_map.items():
                            if norm_header == syn_header:
                                for syn in syn_list:
                                    for k in analysis.keys():
                                        if k.lower().replace(" ", "_") == syn:
                                            key = k
                                            break
                                    if key:
                                        break
                            if key:
                                break
                    # Only show if not already shown
                    if key is not None and key not in shown_keys:
                        value = analysis.get(key)
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

            # Do NOT show any remaining keys in analysis not already shown (prevents duplicate output)
            # (If you want to show them, uncomment below)
            # for k, v in analysis.items():
            #     if k in shown_keys:
            #         continue
            #     with ui.card().classes('w-full mb-4'):
            #         ui.label(k.replace("_", " ").title()).classes('text-lg font-semibold mb-2')
            #         if isinstance(v, list):
            #             for item in v:
            #                 ui.markdown(f"• {item}")
            #         else:
            #             ui.markdown(str(v))

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
        self.analysis_result = None
        
        self.update_files_display()
        self.update_urls_display()
        self.update_tickets_display()
        self.results_container.clear()
        
        ui.notify('All data cleared', type='info')

    def read_executive_summary(self):
        """Read aloud the Executive Summary section if available."""
        if not self.analysis_result or 'analysis' not in self.analysis_result:
            ui.notify("No analysis available. Please generate the RCA report first.", type='warning')
            return
        summary = self.analysis_result['analysis'].get('executive_summary')
        if not summary:
            ui.notify("Executive Summary not found in the analysis.", type='warning')
            return
        ui.notify("Reading Executive Summary...", type='info')
        # Use browser's SpeechSynthesis API via JavaScript
        ui.run_javascript(f"""
            if ('speechSynthesis' in window) {{
                var utter = new window.SpeechSynthesisUtterance({json.dumps(summary)});
                utter.lang = 'en-US';
                window.speechSynthesis.speak(utter);
            }}
        """)

    def read_problem_issue(self):
        """Read aloud the Problem Issue/Problem Summary section if available."""
        if not self.analysis_result or 'analysis' not in self.analysis_result:
            ui.notify("No analysis available. Please generate the RCA report first.", type='warning')
            return
        # Try both 'problem_issue' and 'problem_summary' keys for compatibility
        problem = self.analysis_result['analysis'].get('problem_issue') \
            or self.analysis_result['analysis'].get('problem_summary') \
            or self.analysis_result['analysis'].get('problem_statement')
        if not problem:
            ui.notify("Problem Issue/Problem Summary not found in the analysis.", type='warning')
            return
        ui.notify("Reading Problem Issue/Summary...", type='info')
        # Use browser's SpeechSynthesis API via JavaScript
        ui.run_javascript(f"""
            if ('speechSynthesis' in window) {{
                var utter = new window.SpeechSynthesisUtterance({json.dumps(problem)});
                utter.lang = 'en-US';
                window.speechSynthesis.speak(utter);
            }}
        """)

    def reset_context(self):
        """Reset the context for a new RCA session (clears all files, URLs, tickets, and results)"""
        self.clear_all()
        self.chat_messages = []
        if hasattr(self, "chat_history"):
            self.chat_history.clear()
        ui.notify('Context has been reset. You can now start a new RCA without any previous data.', type='info')

    async def agentic_chat(self, user_message: str):
        """
        Use the LLM to answer questions or refine RCA sections based on the current context and analysis.
        This agentic methodology will:
        - Deeply analyze all uploaded files, Jira tickets, and URLs.
        - Allow the user to request extraction, expansion, or rewriting of any RCA section.
        - Allow follow-up questions and iterative refinement.
        """
        # Compose context for the agent
        context = ""
        if self.analysis_result:
            context += "Current RCA Analysis:\n"
            for k, v in self.analysis_result['analysis'].items():
                context += f"{k}: {v}\n"
        else:
            context += "No RCA analysis has been generated yet.\n"
        if self.uploaded_files or self.urls or self.jira_tickets:
            context += "\nFiles: " + ", ".join([str(Path(f).name) for f in self.uploaded_files])
            context += "\nURLs: " + ", ".join(self.urls)
            context += "\nJira Tickets: " + ", ".join(self.jira_tickets)
        context += "\n\nChat History:\n"
        for msg in self.chat_messages:
            context += f"{msg['role'].capitalize()}: {msg['content']}\n"
        context += "\n"

        # Compose the agentic prompt
        prompt = (
            "You are an expert RCA agent. Your job is to deeply analyze all provided case data, Jira tickets, and supporting documents. "
            "You can extract, expand, or rewrite any RCA section on request, and answer follow-up questions using all available context. "
            "If the user asks to rewrite or expand a section, return only the improved text for that section. "
            "If the user asks a question, answer concisely and reference the RCA data. "
            "If you need more information, ask the user for clarification. "
            "Always use as much detail as possible from the context and prior analysis.\n\n"
            f"User message: {user_message}\n"
            f"{context}"
        )

        # Use the LLM (OpenAI/Anthropic/etc.) to get a response
        try:
            from src.rca_generator import rca_generator
            # Try the configured LLM, fallback to others if needed
            llm_method = None
            llm_name = rca_generator.config.get('default_llm', 'openai')
            if llm_name == 'openai':
                llm_method = rca_generator._generate_with_openai
            elif llm_name == 'anthropic':
                llm_method = rca_generator._generate_with_anthropic
            elif llm_name == 'openrouter':
                llm_method = rca_generator._generate_with_openrouter
            elif llm_name == 'llmproxy':
                llm_method = rca_generator._generate_with_llmproxy
            else:
                llm_method = rca_generator._generate_with_openai

            try:
                llm_response = await llm_method(prompt)
                return llm_response if isinstance(llm_response, str) else str(llm_response)
            except Exception as e:
                logger.warning(f"Primary LLM failed in agentic chat: {e}. Trying fallback LLMs...")
                # Try all LLMs in fallback order
                fallback_order = ['openai', 'anthropic', 'openrouter', 'llmproxy']
                for fallback in fallback_order:
                    if fallback == llm_name:
                        continue
                    try:
                        method = getattr(rca_generator, f"_generate_with_{fallback}")
                        llm_response = await method(prompt)
                        return llm_response if isinstance(llm_response, str) else str(llm_response)
                    except Exception as fallback_e:
                        logger.warning(f"Agentic chat fallback LLM {fallback} failed: {fallback_e}")
                logger.error(f"All LLMs failed in agentic chat.")
                return "Error: All LLM providers failed to generate a response. Please check your API keys, network, and quota."
        except Exception as e:
            logger.error(f"Agentic chat LLM error: {e}")
            return f"Error: {e}"

    def update_chat_history(self):
        """Update the chat message display in the UI."""
        import json
        if hasattr(self, "chat_history"):
            self.chat_history.clear()
            for msg in self.chat_messages:
                if msg['role'] == 'user':
                    with self.chat_history:
                        ui.markdown(f"**You:** {msg['content']}").classes('text-right text-blue-800')
                else:
                    with self.chat_history:
                        content = msg['content']
                        formatted = None
                        # If the agent returned a Python dict as a string, pretty-print it as readable text
                        if isinstance(content, dict):
                            pretty = "\n\n".join(f"**{k.replace('_',' ').title()}**:\n{v}" for k, v in content.items())
                            formatted = pretty
                        else:
                            # Try to parse as JSON or Python dict string
                            try:
                                parsed = json.loads(content)
                                pretty = "\n\n".join(f"**{k.replace('_',' ').title()}**:\n{v}" for k, v in parsed.items())
                                formatted = pretty
                            except Exception:
                                # Try to eval as Python dict (dangerous in general, but safe for LLM output)
                                try:
                                    import ast
                                    parsed = ast.literal_eval(content)
                                    if isinstance(parsed, dict):
                                        pretty = "\n\n".join(f"**{k.replace('_',' ').title()}**:\n{v}" for k, v in parsed.items())
                                        formatted = pretty
                                except Exception:
                                    # Try to extract JSON from within text
                                    import re
                                    match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
                                    if match:
                                        try:
                                            parsed = json.loads(match.group(1))
                                            pretty = "\n\n".join(f"**{k.replace('_',' ').title()}**:\n{v}" for k, v in parsed.items())
                                            formatted = pretty
                                        except Exception:
                                            pass
                        if formatted:
                            ui.markdown(f"**Agent:**\n{formatted}").classes('text-left text-gray-800')
                        else:
                            # If it's a dict-like string, try to pretty print as key-value pairs
                            if content.strip().startswith("{") and content.strip().endswith("}"):
                                try:
                                    import ast
                                    parsed = ast.literal_eval(content)
                                    if isinstance(parsed, dict):
                                        pretty = "\n\n".join(f"**{k.replace('_',' ').title()}**:\n{v}" for k, v in parsed.items())
                                        ui.markdown(f"**Agent:**\n{pretty}").classes('text-left text-gray-800')
                                        continue
                                except Exception:
                                    pass
                            ui.markdown(f"**Agent:** {content}").classes('text-left text-gray-800')

    def handle_chat_message(self):
        """Handle user chat input and update the chat history."""
        user_message = self.chat_input.value.strip()
        if not user_message:
            ui.notify("Please enter a message.", type='warning')
            return
        self.chat_messages.append({'role': 'user', 'content': user_message})
        self.update_chat_history()
        self.chat_input.value = ''
        # Run the agentic chat in the background
        async def run_agentic():
            agent_response = await self.agentic_chat(user_message)
            self.chat_messages.append({'role': 'agent', 'content': agent_response})
            self.update_chat_history()
        asyncio.create_task(run_agentic())

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
