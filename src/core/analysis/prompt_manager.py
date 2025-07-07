"""
Prompt management system for handling different analysis types
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages prompts, contexts, and response schemas for different analysis types"""
    
    def __init__(self, prompts_dir: str = "src/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.templates_dir = self.prompts_dir / "templates"
        self.contexts_dir = self.prompts_dir / "contexts" 
        self.schemas_dir = self.prompts_dir / "schemas"
        
        # Cache for loaded prompts
        self._prompt_cache = {}
        self._context_cache = {}
        self._schema_cache = {}
    
    def get_prompt_template(self, prompt_type: str) -> str:
        """Get prompt template for specified type"""
        if prompt_type in self._prompt_cache:
            return self._prompt_cache[prompt_type]
        
        # Try new template location first
        template_file = self.templates_dir / f"{prompt_type}.txt"
        if not template_file.exists():
            # Fallback to old location
            template_file = self.prompts_dir / prompt_type
        
        if template_file.exists():
            template = template_file.read_text(encoding='utf-8')
            self._prompt_cache[prompt_type] = template
            return template
        else:
            logger.error(f"Prompt template not found: {prompt_type}")
            return self._get_default_prompt()
    
    def get_context(self, context_name: str) -> str:
        """Get context content for specified context"""
        if context_name in self._context_cache:
            return self._context_cache[context_name]
        
        context_file = self.contexts_dir / f"{context_name}.txt"
        if not context_file.exists():
            # Fallback to old location
            context_file = self.prompts_dir / context_name
        
        if context_file.exists():
            context = context_file.read_text(encoding='utf-8')
            self._context_cache[context_name] = context
            return context
        else:
            logger.warning(f"Context not found: {context_name}")
            return ""
    
    def get_response_schema(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """Get expected response schema for prompt type"""
        if prompt_type in self._schema_cache:
            return self._schema_cache[prompt_type]
        
        schema_file = self.schemas_dir / f"{prompt_type}_schema.json"
        if schema_file.exists():
            try:
                schema = json.loads(schema_file.read_text(encoding='utf-8'))
                self._schema_cache[prompt_type] = schema
                return schema
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON schema for {prompt_type}: {e}")
        
        return None
    
    def build_prompt(self, prompt_type: str, context_data: str, 
                    issue_description: str = "", 
                    additional_context: Optional[str] = None) -> str:
        """
        Build complete prompt from template, context, and data
        
        Args:
            prompt_type: Type of analysis prompt
            context_data: Source data for analysis
            issue_description: User's description of the issue
            additional_context: Additional context to include
            
        Returns:
            Complete formatted prompt
        """
        template = self.get_prompt_template(prompt_type)
        
        # Add NetApp context for technical prompts
        netapp_context = ""
        if prompt_type in ["formal_rca_prompt", "kt-analysis_prompt", "initial_analysis_prompt"]:
            netapp_context = self.get_context("netapp_context")
        
        # Build the complete prompt
        prompt_parts = []
        
        # Add template
        prompt_parts.append(template)
        
        # Add issue description if provided
        if issue_description.strip():
            prompt_parts.append(f"\n\n## Issue Description:\n{issue_description}")
        
        # Add NetApp context
        if netapp_context:
            prompt_parts.append(f"\n\n## NetApp Context:\n{netapp_context}")
        
        # Add additional context
        if additional_context:
            prompt_parts.append(f"\n\n## Additional Context:\n{additional_context}")
        
        # Add source data
        prompt_parts.append(f"\n\n## Source Data for Analysis:\n{context_data}")
        
        # For KT analysis, add specific instructions about format
        if prompt_type == "kt-analysis_prompt":
            prompt_parts.append(self._get_kt_format_instructions())
        
        return "\n".join(prompt_parts)
    
    def _get_kt_format_instructions(self) -> str:
        """Get specific formatting instructions for KT analysis"""
        return """
        
## Response Format Instructions:

Please provide your response in TWO parts:

1. **JSON Structure** containing:
   - executive_summary
   - problem_statement  
   - timeline
   - root_cause
   - contributing_factors
   - impact_assessment
   - corrective_actions
   - preventive_measures
   - recommendations
   - escalation_needed
   - defect_tickets_needed
   - severity
   - priority

2. **Formatted Sections** (after the JSON):
   - a) Kepner-Tregoe Problem Analysis Template (formatted for web display)
   - b) Problem Assessment table (as markdown table)
   - Additional sections as specified in the prompt

This dual format ensures both structured data extraction and proper presentation formatting.
"""
    
    def _get_default_prompt(self) -> str:
        """Get default prompt when specific template not found"""
        return """
Based on the provided context and source data, please analyze the issue and provide:

1. Executive Summary
2. Problem Statement  
3. Root Cause Analysis
4. Recommendations
5. Next Steps

Please structure your response as a JSON object with these fields.
"""
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt types"""
        prompts = []
        
        # Check templates directory
        if self.templates_dir.exists():
            for file in self.templates_dir.glob("*.txt"):
                prompts.append(file.stem)
        
        # Check old location
        for file in self.prompts_dir.glob("*"):
            if file.is_file() and not file.name.startswith('.') and file.suffix != '.txt':
                if file.name not in prompts:
                    prompts.append(file.name)
        
        return sorted(prompts)
    
    def migrate_prompts_to_new_structure(self):
        """Migrate existing prompts to new directory structure"""
        logger.info("Starting prompt migration to new structure")
        
        # Create directories
        self.templates_dir.mkdir(exist_ok=True)
        self.contexts_dir.mkdir(exist_ok=True)
        self.schemas_dir.mkdir(exist_ok=True)
        
        # Migrate prompt files
        prompt_files = [
            "formal_rca_prompt",
            "initial_analysis_prompt", 
            "kt-analysis_prompt"
        ]
        
        for prompt_file in prompt_files:
            old_path = self.prompts_dir / prompt_file
            new_path = self.templates_dir / f"{prompt_file}.txt"
            
            if old_path.exists() and not new_path.exists():
                logger.info(f"Migrating {prompt_file} to templates/")
                new_path.write_text(old_path.read_text(encoding='utf-8'), encoding='utf-8')
        
        # Migrate context files
        context_files = [
            "context",
            "netapp_context",
            "cpe_prompt",
            "contap_prompt",
            "netapp_prompt",
            "sap_prompt"
        ]
        
        for context_file in context_files:
            old_path = self.prompts_dir / context_file
            new_path = self.contexts_dir / f"{context_file}.txt"
            
            if old_path.exists() and not new_path.exists():
                logger.info(f"Migrating {context_file} to contexts/")
                new_path.write_text(old_path.read_text(encoding='utf-8'), encoding='utf-8')
        
        logger.info("Prompt migration completed")
