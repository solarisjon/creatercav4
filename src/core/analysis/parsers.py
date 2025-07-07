"""
Core analysis parsing logic extracted from rca_generator.py
Handles parsing of LLM responses for different analysis types
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ResponseParser:
    """Handles parsing of LLM responses for different analysis types"""
    
    def __init__(self):
        self.kt_section_patterns = {
            'kepner_tregoe_analysis': r'### KEPNER-TREGOE PROBLEM ANALYSIS\s*(.*?)(?=### RECOMMENDATIONS|$)',
            'is_is_not_table': r'#### 2\. Problem Specification \(IS/IS NOT Analysis\)\s*(.*?)(?=####|###|$)',
            'root_cause_analysis': r'#### 3\. Root Cause Analysis\s*(.*?)(?=####|###|$)',
            'solution_development': r'#### 4\. Solution Development\s*(.*?)(?=####|###|$)',
            'prevention_strategy': r'#### 5\. Prevention Strategy\s*(.*?)(?=####|###|$)',
            'recommendations': r'### RECOMMENDATIONS AND NEXT STEPS\s*(.*?)(?=###|$)'
        }
    
    def parse_llm_response(self, response_text: str, analysis_type: str = "standard") -> Dict[str, Any]:
        """
        Parse LLM response based on analysis type
        
        Args:
            response_text: Raw LLM response text
            analysis_type: Type of analysis ("standard", "kt-analysis", etc.)
            
        Returns:
            Parsed analysis dictionary
        """
        result = {}
        
        # Store full raw response first
        result['raw_response'] = response_text
        
        # Handle different analysis types
        if analysis_type == "kt-analysis_prompt":
            # Try to extract JSON first for KT analysis
            json_data = self._extract_json(response_text)
            if json_data:
                result.update(json_data)
            
            # Extract additional KT sections
            kt_sections = self._parse_kt_sections(response_text)
            result.update(kt_sections)
            
        elif analysis_type == "formal_rca_prompt":
            # For formal RCA, parse structured text sections
            rca_sections = self._parse_formal_rca_sections(response_text)
            result.update(rca_sections)
            
        elif analysis_type == "initial_analysis_prompt":
            # For initial analysis, parse the structured template format
            initial_sections = self._parse_initial_analysis_sections(response_text)
            result.update(initial_sections)
            
        else:
            # For other types, try JSON extraction
            json_data = self._extract_json(response_text)
            if json_data:
                result.update(json_data)
            
        return result
    
    def _extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from response text"""
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON block in text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.warning("Found JSON-like text but couldn't parse it")
            return None
    
    def _parse_kt_sections(self, response_text: str) -> Dict[str, str]:
        """Parse KT-specific sections from raw response"""
        kt_sections = {}
        
        for section_name, pattern in self.kt_section_patterns.items():
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content:
                    kt_sections[section_name] = content
                    logger.debug(f"Extracted KT section: {section_name}")
        
        # Special handling for IS/IS NOT table
        if 'is_is_not_table' in kt_sections:
            kt_sections['is_is_not_table'] = self._clean_markdown_table(
                kt_sections['is_is_not_table']
            )
        
        return kt_sections
    
    def _clean_markdown_table(self, table_text: str) -> str:
        """Clean and format markdown table for proper display"""
        lines = table_text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and '|' in line:
                # Ensure proper table formatting
                if not line.startswith('|'):
                    line = '| ' + line
                if not line.endswith('|'):
                    line = line + ' |'
                cleaned_lines.append(line)
            elif line and not line.startswith('-'):
                # Non-table content, keep as is
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_fallback_analysis(self, response_text: str) -> Dict[str, Any]:
        """Create a basic analysis structure when JSON parsing fails"""
        return {
            "executive_summary": "Analysis parsing failed. Please check the raw response.",
            "problem_statement": "Unable to parse structured response",
            "raw_content": response_text,
            "parsing_error": True
        }
    
    def _parse_formal_rca_sections(self, response_text: str) -> Dict[str, str]:
        """Parse formal RCA sections from structured text response"""
        sections = {}
        
        # Common section patterns for formal RCA
        section_patterns = {
            'timeline': r'(?:^|\n)(?:--|SECTION 1|A\.|Timeline).*?Timeline\s*(.*?)(?=(?:^|\n)(?:--|SECTION|B\.|[A-Z]\.|###)|$)',
            'customer_impact': r'(?:^|\n)(?:--|SECTION 2|B\.|Customer Impact).*?(?:Customer Impact|Impact)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|C\.|[A-Z]\.|###)|$)',
            'technical_summary': r'(?:^|\n)(?:--|SECTION 3|C\.|Technical Summary).*?(?:Technical Summary|Summary)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|D\.|[A-Z]\.|###)|$)',
            'root_cause': r'(?:^|\n)(?:--|SECTION 4|D\.|Root Cause).*?(?:Root Cause|Cause)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|E\.|[A-Z]\.|###)|$)',
            'next_steps': r'(?:^|\n)(?:--|SECTION 5|E\.|Next Steps).*?(?:Next Steps|Steps)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|F\.|[A-Z]\.|###)|$)',
            'prevention': r'(?:^|\n)(?:--|SECTION 6|F\.|Prevention).*?(?:Prevention|Preventive)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|G\.|[A-Z]\.|###)|$)',
            'escalation': r'(?:^|\n)(?:--|SECTION 7|G\.|Escalation).*?(?:Escalation|Escalated)\s*(.*?)(?=(?:^|\n)(?:--|SECTION|H\.|[A-Z]\.|###)|$)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                if content:
                    sections[section_name] = content
                    logger.debug(f"Extracted formal RCA section: {section_name}")
        
        # If no sections found, put everything in executive_summary
        if not sections:
            sections['executive_summary'] = response_text.strip()
            
        return sections

    def _parse_initial_analysis_sections(self, response_text: str) -> Dict[str, str]:
        """Parse initial analysis sections from template-based response"""
        sections = {}
        
        # Look for the CAP line format: CAP {Color} : {CPE-xxxx} : SAP {SAP Case} : {Customer} : {Synopsis}
        cap_match = re.search(r'CAP\s+([^:]+)\s*:\s*([^:]+)\s*:\s*SAP\s+([^:]+)\s*:\s*([^:]+)\s*:\s*(.+)', response_text, re.IGNORECASE)
        if cap_match:
            sections['cap_color'] = cap_match.group(1).strip()
            sections['cpe_case'] = cap_match.group(2).strip()
            sections['sap_case'] = cap_match.group(3).strip()
            sections['customer_name'] = cap_match.group(4).strip()
            sections['synopsis'] = cap_match.group(5).strip()
        
        # Parse numbered sections
        section_patterns = {
            'people': r'1\)\s*People\s*(.*?)(?=\d\)|$)',
            'timeline': r'2\)\s*Timeline\s*(.*?)(?=\d\)|$)',
            'technical_summary': r'3\)\s*Technical Summary\s*(.*?)(?=\d\)|$)',
            'impact': r'4\)\s*Impact\s*(.*?)(?=\d\)|$)',
            'next_steps': r'5\)\s*Next Steps\s*(.*?)(?=\d\)|$)',
            'escalation': r'6\)\s*Escalation\s*(.*?)(?=\d\)|$)',
            'recommendations': r'7\)\s*Recommendations\s*(.*?)(?=\d\)|$)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content:
                    sections[section_name] = content
                    logger.debug(f"Extracted initial analysis section: {section_name}")
        
        # If no structured sections found, put everything in overview
        if not any(key in sections for key in ['people', 'timeline', 'technical_summary']):
            sections['overview'] = response_text.strip()
            
        return sections
