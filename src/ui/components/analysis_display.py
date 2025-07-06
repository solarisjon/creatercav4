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
        ],
        "initial_analysis_prompt": [
            ("Overview", "overview"),
            ("Key Findings", "key_findings"),
            ("Summary", "summary"),
            ("Recommendations", "recommendations"),
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
                for key in ['kepner_tregoe_template', 'problem_assessment_table', 
                           'issue_description', 'source_data_analysis', 'jira_tickets_referenced']:
                    if key in analysis:
                        result[key] = analysis[key]
                return result
        
        return analysis
    
    def _display_sources(self, analysis: Dict[str, Any]):
        """Display sources used section"""
        sources = analysis.get("sources_used", [])
        if sources:
            with ui.card().classes('w-full mb-4'):
                ui.label("Sources Used").classes('text-lg font-semibold mb-2')
                for src in sources:
                    ui.markdown(f"- {src}")
    
    def _display_json_sections(self, analysis: Dict[str, Any], prompt_type: str):
        """Display sections from JSON structure"""
        section_mapping = self.PROMPT_SECTION_MAPS.get(prompt_type, [])
        
        if not section_mapping:
            # Dynamic section detection
            section_mapping = self._detect_sections(analysis)
        
        for header, key in section_mapping:
            value = analysis.get(key)
            if self._should_display_section(value, prompt_type):
                with ui.card().classes('w-full mb-4'):
                    ui.label(header).classes('text-lg font-semibold mb-2')
                    self._render_content(value)
    
    def _display_kt_special_sections(self, analysis: Dict[str, Any]):
        """Display KT-specific sections that come from raw response parsing"""
        kt_special_sections = [
            ("Kepner-Tregoe Analysis Template", "kepner_tregoe_template"),
            ("Problem Assessment Table", "problem_assessment_table"),
            ("Issue Description", "issue_description"), 
            ("Source Data Analysis", "source_data_analysis"),
            ("JIRA Tickets Referenced", "jira_tickets_referenced")
        ]
        
        for header, key in kt_special_sections:
            value = analysis.get(key)
            if value and str(value).strip():
                with ui.card().classes('w-full mb-4'):
                    ui.label(header).classes('text-lg font-semibold mb-2')
                    
                    # Special handling for Problem Assessment table
                    if key == "problem_assessment_table":
                        self._render_kt_table(value)
                    else:
                        self._render_content(value)
    
    def _render_kt_table(self, table_content: str):
        """Render KT Problem Assessment table with proper formatting"""
        try:
            # Try to render as HTML table using markdown
            import markdown
            from markdown.extensions.tables import TableExtension
            html = markdown.markdown(table_content, extensions=[TableExtension()])
            ui.html(html)
        except ImportError:
            # Fallback: render as preformatted text
            ui.html(f"<pre class='whitespace-pre-wrap font-mono text-sm bg-gray-100 p-3 rounded'>{table_content}</pre>")
        except Exception as e:
            logger.warning(f"Error rendering KT table: {e}")
            # Final fallback
            ui.markdown(table_content)
    
    def _render_content(self, value: Any):
        """Render content based on its type"""
        if isinstance(value, list):
            for item in value:
                ui.markdown(f"• {item}")
        elif isinstance(value, str):
            if "<table" in value.lower():
                ui.html(value)
            elif "|" in value and value.count("|") > 2:
                # Markdown table
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
        
        # Display sections
        self._display_json_sections(analysis, prompt_file)
