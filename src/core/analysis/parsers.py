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
            'kepner_tregoe_template': r'### a\) Kepner-Tregoe Problem Analysis Template\s*(.*?)(?=### b\)|###\s*b\)|$)',
            'problem_assessment_table': r'### b\) Problem Assessment.*?\n\s*(.*?)(?=###|---|\n\n\n|$)',
            'issue_description': r'### ISSUE DESCRIPTION:?\s*(.*?)(?=###|---|\n\n\n|$)',
            'source_data_analysis': r'### SOURCE DATA ANALYSIS:?\s*(.*?)(?=###|---|\n\n\n|$)',
            'jira_tickets_referenced': r'### JIRA TICKETS REFERENCED:?\s*(.*?)(?=###|---|\n\n\n|$)'
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
        
        # Try to extract JSON first
        json_data = self._extract_json(response_text)
        if json_data:
            result.update(json_data)
        
        # Store full raw response
        result['raw_response'] = response_text
        
        # For KT analysis, extract additional sections
        if analysis_type == "kt-analysis":
            kt_sections = self._parse_kt_sections(response_text)
            result.update(kt_sections)
            
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
        
        # Special handling for Problem Assessment table
        if 'problem_assessment_table' in kt_sections:
            kt_sections['problem_assessment_table'] = self._clean_markdown_table(
                kt_sections['problem_assessment_table']
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
