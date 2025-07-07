"""
Analysis display component for NiceGUI
Handles rendering of analysis results with proper formatting
"""
import logging
from typing import Dict, Any, List, Tuple, Optional
from nicegui import ui

logger = logging.getLogger(__name__)

class AnalysisDisplay:
    """Handles display of analysis results in the UI"""
    
    # Mapping of prompt types to their expected sections
    PROMPT_SECTION_MAPS = {
        "formal_rca_prompt": [
            ("Executive Summary", "executive_summary"),
            ("Incident Overview", "incident_overview"),
            ("Timeline", "timeline"),
            ("Case Information", "case_information"),
            ("Problem Summary", "problem_summary"),
            ("Technical Analysis", "technical_analysis"),
            ("Impact Assessment", "impact_assessment"),
            ("Root Cause Analysis", "root_cause"),
            ("Risk Assessment", "risk_assessment"),
            ("Likelihood of Occurrence", "likelihood_of_occurrence"),
            ("Vulnerability Assessment", "vulnerability_assessment"),
            ("Overall Risk Profile", "risk_profile"),
            ("Workaround Solutions", "workaround_solutions"),
            ("Known Defect Resolution", "defect_resolution"),
            ("New Defect Management", "new_defect_management"),
            ("Recommended Changes", "recommended_changes"),
            ("Prevention Strategy", "prevention"),
            ("Current Environment Prevention", "current_prevention"),
            ("Future Prevention", "future_prevention"),
            ("Monitoring and Detection", "monitoring_detection"),
            ("Next Steps", "next_steps"),
            ("Escalation", "escalation"),
            ("Customer Impact", "customer_impact"),
            ("Technical Summary", "technical_summary"),
        ],
        "initial_analysis_prompt": [
            ("CAP Information", "cap_info"),  # will be handled specially
            ("People", "people"),
            ("Timeline", "timeline"),
            ("Technical Summary", "technical_summary"),
            ("Impact", "impact"),
            ("Next Steps", "next_steps"),
            ("Escalation", "escalation"),
            ("Recommendations", "recommendations"),
            ("Overview", "overview"),  # fallback
        ],
        "kt-analysis_prompt": [
            ("Executive Summary", "executive_summary"),
            ("Problem Statement", "problem_statement"),
            ("Timeline", "timeline"),
            ("Root Cause", "root_cause"),
            ("Contributing Factors", "contributing_factors"),
            ("Impact Assessment", "impact_assessment"),
            ("Corrective Actions", "corrective_actions"),
            ("Preventive Measures", "preventive_measures"),
            ("Recommendations", "recommendations"),
            ("Escalation Needed", "escalation_needed"),
            ("Defect Tickets Needed", "defect_tickets_needed"),
            ("Severity", "severity"),
            ("Priority", "priority"),
        ]
    }
    
    def __init__(self, container):
        """Initialize with a UI container"""
        self.container = container
    
    def display_analysis(self, analysis_result: Dict[str, Any]):
        """Display complete analysis results"""
        if not analysis_result:
            return
        
        self.container.clear()
        
        with self.container:
            analysis = analysis_result.get('analysis', {})
            prompt_file = analysis_result.get('prompt_file_used', 'unknown')
            
            # Display title
            ui.label(f"Analysis Report: {prompt_file.replace('_', ' ').title()}").classes(
                'text-xl font-semibold mb-4'
            )
            
            # Handle KT analysis specially
            if prompt_file == "kt-analysis_prompt":
                self._display_kt_analysis(analysis)
            else:
                self._display_standard_analysis(analysis, prompt_file)
    
    def _display_kt_analysis(self, analysis: Dict[str, Any]):
        """Display KT analysis with special handling for tables and sections"""
        logger.info("Displaying KT analysis with enhanced section detection")
        
        # First, try to use raw_analysis if available and main fields are empty
        working_analysis = self._get_best_kt_data(analysis)
        
        # Display sources used
        self._display_sources(working_analysis)
        
        # Display JSON-structured sections first
        self._display_json_sections(working_analysis, "kt-analysis_prompt")
        
        # Display KT-specific sections from raw response
        self._display_kt_special_sections(working_analysis)
    
    def _get_best_kt_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get the best data source for KT analysis"""
        # Check if main fields are mostly empty
        main_fields = ['problem_description', 'possible_causes', 'data_collection', 'solution']
        empty_fields = sum(1 for field in main_fields if not analysis.get(field, '').strip())
        
        # If most fields are empty, prefer raw_analysis
        if empty_fields >= len(main_fields) - 1 and 'raw_analysis' in analysis:
            raw_analysis = analysis.get('raw_analysis', {})
            if isinstance(raw_analysis, dict) and raw_analysis:
                logger.info("Using raw_analysis for KT display (main fields mostly empty)")
                # Merge keeping sources from original
                result = raw_analysis.copy()
                result['sources_used'] = analysis.get('sources_used', [])
                # Also keep the KT special sections if they exist
                for key in ['kepner_tregoe_analysis', 'is_is_not_table', 
                           'root_cause_analysis', 'solution_development', 'prevention_strategy', 'recommendations']:
                    if key in analysis:
                        result[key] = analysis[key]
                return result
        
        return analysis
    
    def _display_sources(self, analysis: Dict[str, Any]):
        """Display sources used section with wide card format"""
        sources = analysis.get("sources_used", [])
        if sources:
            with ui.card().classes('w-full mb-6 netapp-card').style('max-width: 80%; margin: 0 auto;'):
                with ui.column().classes('netapp-card-content w-full'):
                    ui.html('<div class="netapp-card-header"><i class="material-icons" style="vertical-align: middle; margin-right: 8px;">source</i>Sources Used</div>')
                    
                    # Display sources in a list format
                    for src in sources:
                        ui.markdown(f"📄 {src}").classes('text-sm mb-1')
    
    def _display_json_sections(self, analysis: Dict[str, Any], prompt_type: str):
        """Display sections from JSON structure in a single column with wide cards"""
        section_mapping = self.PROMPT_SECTION_MAPS.get(prompt_type, [])
        
        if not section_mapping:
            # Dynamic section detection
            section_mapping = self._detect_sections(analysis)
        
        # Display sections in single column with wide cards
        for header, key in section_mapping:
            value = analysis.get(key)
            if self._should_display_section(value, prompt_type):
                with ui.card().classes('w-full mb-4 netapp-card').style('max-width: 80%; margin: 0 auto;'):
                    with ui.column().classes('netapp-card-content w-full'):
                        ui.html(f'<div class="netapp-card-header">{header}</div>')
                        self._render_content(value)
    
    def _display_kt_special_sections(self, analysis: Dict[str, Any]):
        """Display KT-specific sections in single column with wide cards"""
        kt_special_sections = [
            ("Kepner-Tregoe Problem Analysis", "kepner_tregoe_analysis"),
            ("Problem Specification (IS/IS NOT Analysis)", "is_is_not_table"),
            ("Root Cause Analysis", "root_cause_analysis"), 
            ("Solution Development", "solution_development"),
            ("Prevention Strategy", "prevention_strategy"),
            ("Recommendations and Next Steps", "recommendations")
        ]
        
        for header, key in kt_special_sections:
            value = analysis.get(key)
            if value and str(value).strip():
                with ui.card().classes('netapp-card netapp-fade-in w-full mb-6').style('max-width: 80%; margin: 0 auto;'):
                    with ui.column().classes('netapp-card-content w-full'):
                        ui.html(f'<div class="netapp-card-header">{header}</div>')
                        
                        # Special handling for IS/IS NOT table
                        if key == "is_is_not_table":
                            self._render_kt_table(value)
                        else:
                            self._render_content(value)
    
    def _render_kt_table(self, table_content: str):
        """Render KT Problem Assessment table with proper HTML formatting"""
        try:
            # Parse markdown table and convert to proper HTML table
            html_table = self._convert_markdown_table_to_html(table_content)
            if html_table:
                ui.html(html_table)
                return
        except Exception as e:
            logger.warning(f"Error converting table to HTML: {e}")
        
        # Fallback: try markdown rendering
        try:
            import markdown
            from markdown.extensions.tables import TableExtension
            html = markdown.markdown(table_content, extensions=[TableExtension()])
            ui.html(html)
        except ImportError:
            # Final fallback: render as preformatted text
            ui.html(f"<pre class='whitespace-pre-wrap font-mono text-sm bg-gray-100 p-3 rounded'>{table_content}</pre>")
        except Exception as e:
            logger.warning(f"Error rendering KT table: {e}")
            # Ultimate fallback
            ui.markdown(table_content)
    
    def _convert_markdown_table_to_html(self, markdown_table: str) -> str:
        """Convert markdown table to HTML table with proper styling"""
        lines = markdown_table.strip().split('\n')
        if not lines:
            return ""
        
        # Find table lines (contain |)
        table_lines = [line.strip() for line in lines if line.strip() and '|' in line]
        if len(table_lines) < 2:
            return ""
        
        # Parse header
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]
        
        # Skip separator line (usually line with --- )
        data_lines = []
        for line in table_lines[1:]:
            if not line.replace('|', '').replace('-', '').replace(' ', ''):
                continue  # Skip separator lines
            data_lines.append(line)
        
        # Build HTML table with NetApp styling and full width
        html_parts = [
            '<div class="overflow-x-auto w-full">',
            '<table class="w-full min-w-full bg-white border border-gray-300 rounded-lg shadow-sm netapp-results">',
            '<thead>',
            '<tr>'
        ]
        
        # Add headers with NetApp styling
        for header in headers:
            # Clean up markdown formatting in headers
            clean_header = header.replace('**', '').replace('*', '')
            html_parts.append(f'<th class="px-4 py-3 text-left text-sm font-semibold text-white bg-blue-600 border-b border-gray-300">{clean_header}</th>')
        
        html_parts.extend(['</tr>', '</thead>', '<tbody>'])
        
        # Add data rows with NetApp styling
        for i, line in enumerate(data_lines):
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(cells) >= len(headers):  # Only process complete rows
                row_class = "bg-white hover:bg-gray-100" if i % 2 == 0 else "bg-gray-50 hover:bg-gray-200"
                html_parts.append(f'<tr class="{row_class}">')
                
                for j, cell in enumerate(cells[:len(headers)]):  # Match header count
                    # Clean up markdown formatting and handle empty cells
                    clean_cell = cell.replace('**', '').replace('*', '').strip()
                    if not clean_cell:
                        clean_cell = "&nbsp;"
                    
                    # Style first column differently (dimension labels) with NetApp colors
                    if j == 0:
                        cell_class = "px-4 py-3 text-sm font-medium text-gray-900 border-b border-gray-200 bg-blue-50"
                    else:
                        cell_class = "px-4 py-3 text-sm text-gray-700 border-b border-gray-200"
                    
                    html_parts.append(f'<td class="{cell_class}">{clean_cell}</td>')
                
                html_parts.append('</tr>')
        
        html_parts.extend(['</tbody>', '</table>', '</div>'])
        
        return '\n'.join(html_parts)
    
    def _render_content(self, value: Any):
        """Render content based on its type"""
        if isinstance(value, list):
            for item in value:
                ui.markdown(f"• {item}")
        elif isinstance(value, str):
            if "<table" in value.lower():
                ui.html(value)
            elif "|" in value and value.count("|") > 2:
                # Markdown table - convert to HTML
                try:
                    html_table = self._convert_markdown_table_to_html(value)
                    if html_table:
                        ui.html(html_table)
                    else:
                        ui.markdown(value)
                except Exception:
                    # Fallback to markdown rendering
                    try:
                        import markdown
                        from markdown.extensions.tables import TableExtension
                        html = markdown.markdown(value, extensions=[TableExtension()])
                        ui.html(html)
                    except ImportError:
                        ui.code(value).classes('w-full')
            else:
                ui.markdown(str(value))
        else:
            ui.markdown(str(value))
    
    def _should_display_section(self, value: Any, prompt_type: str) -> bool:
        """Determine if a section should be displayed"""
        if value is None:
            return False
        
        str_value = str(value).strip()
        if not str_value or str_value in ["", "N/A", "None", "..."]:
            return False
        
        # For KT analysis, be more lenient
        if prompt_type == "kt-analysis_prompt":
            return bool(str_value)
        
        # For other types, use stricter criteria
        return str_value != "N/A"
    
    def _detect_sections(self, analysis: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Dynamically detect sections from analysis keys"""
        sections = []
        skip_keys = {'sources_used', 'raw_response', 'raw_analysis', 'kepner_tregoe_template',
                    'problem_assessment_table', 'issue_description', 'source_data_analysis', 
                    'jira_tickets_referenced'}
        
        for key in analysis.keys():
            if key not in skip_keys:
                header = self._key_to_header(key)
                sections.append((header, key))
        
        return sections
    
    def _key_to_header(self, key: str) -> str:
        """Convert a key to a readable header"""
        # Handle special cases
        special_cases = {
            'executive_summary': 'Executive Summary',
            'problem_statement': 'Problem Statement',
            'root_cause': 'Root Cause',
            'contributing_factors': 'Contributing Factors',
            'impact_assessment': 'Impact Assessment',
            'corrective_actions': 'Corrective Actions',
            'preventive_measures': 'Preventive Measures',
            'escalation_needed': 'Escalation Needed',
            'defect_tickets_needed': 'Defect Tickets Needed'
        }
        
        if key in special_cases:
            return special_cases[key]
        
        # Default: title case with underscores replaced
        return key.replace("_", " ").title()
    
    def _display_standard_analysis(self, analysis: Dict[str, Any], prompt_file: str):
        """Display standard analysis (non-KT)"""
        # Display sources
        self._display_sources(analysis)
        
        # Special handling for initial analysis CAP information
        if prompt_file == "initial_analysis_prompt":
            self._display_cap_info(analysis)
        
        # Display sections
        self._display_json_sections(analysis, prompt_file)
        
        # If no structured sections found, display raw response
        if not any(analysis.get(key) for _, key in self.PROMPT_SECTION_MAPS.get(prompt_file, [])):
            raw_response = analysis.get('raw_response', '')
            if raw_response:
                with ui.card().classes('w-full mb-4 netapp-card').style('max-width: 80%; margin: 0 auto;'):
                    with ui.column().classes('netapp-card-content w-full'):
                        ui.html('<div class="netapp-card-header">Analysis Result</div>')
                        self._render_content(raw_response)

    def _display_cap_info(self, analysis: Dict[str, Any]):
        """Display CAP information for initial analysis"""
        cap_fields = ['cap_color', 'cpe_case', 'sap_case', 'customer_name', 'synopsis']
        if any(analysis.get(field) for field in cap_fields):
            with ui.card().classes('w-full mb-4 netapp-card').style('max-width: 80%; margin: 0 auto;'):
                with ui.column().classes('netapp-card-content w-full'):
                    ui.html('<div class="netapp-card-header">CAP Information</div>')
                    
                    cap_info = []
                    if analysis.get('cap_color'):
                        cap_info.append(f"**CAP Color:** {analysis['cap_color']}")
                    if analysis.get('cpe_case'):
                        cap_info.append(f"**CPE Case:** {analysis['cpe_case']}")
                    if analysis.get('sap_case'):
                        cap_info.append(f"**SAP Case:** {analysis['sap_case']}")
                    if analysis.get('customer_name'):
                        cap_info.append(f"**Customer:** {analysis['customer_name']}")
                    if analysis.get('synopsis'):
                        cap_info.append(f"**Synopsis:** {analysis['synopsis']}")
                    
                    if cap_info:
                        ui.markdown('\n\n'.join(cap_info))
