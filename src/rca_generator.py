import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
from src.config import config
from src.mcp_client import mcp_client

logger = logging.getLogger(__name__)

class RCAGenerator:
    def __init__(self):
        self.config = config.llm_config
        self.template_path = Path("data/rca_template.docx")
        self.output_dir = Path(config.app_config['output_directory'])
        
    async def generate_rca_analysis(self, 
                                   files: List[str], 
                                   urls: List[str], 
                                   jira_tickets: List[str],
                                   issue_description: str) -> Dict[str, Any]:
        """Generate RCA analysis based on provided inputs"""
        try:
            logger.info("Starting RCA analysis generation")
            
            # Collect all source data
            source_data = await self._collect_source_data(files, urls, jira_tickets)
            
            # Generate analysis using LLM
            analysis = await self._generate_analysis(source_data, issue_description)
            
            # Create RCA document
            document_path = await self._create_rca_document(analysis)
            
            result = {
                'analysis': analysis,
                'document_path': str(document_path),
                'timestamp': datetime.now().isoformat(),
                'source_data_summary': {
                    'files_processed': len(files),
                    'urls_processed': len(urls),
                    'jira_tickets_referenced': len(jira_tickets)
                }
            }
            
            logger.info("RCA analysis generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate RCA analysis: {e}")
            raise
    
    async def _collect_source_data(self, files: List[str], urls: List[str], jira_tickets: List[str]) -> Dict[str, Any]:
        """Collect data from all sources"""
        source_data = {
            'files': {},
            'urls': {},
            'jira_tickets': {},
            'summary': ''
        }
        
        # Process files
        for file_path in files:
            try:
                if file_path.lower().endswith('.pdf'):
                    content = await mcp_client.process_pdf(file_path)
                else:
                    content = await mcp_client.read_file(file_path)
                
                source_data['files'][file_path] = {
                    'content': content,
                    'size': len(content),
                    'type': Path(file_path).suffix
                }
                logger.info(f"Processed file: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                source_data['files'][file_path] = {'error': str(e)}
        
        # Process URLs
        for url in urls:
            try:
                content = await mcp_client.scrape_web_content(url)
                source_data['urls'][url] = {
                    'content': content,
                    'size': len(content),
                    'scraped_at': datetime.now().isoformat()
                }
                logger.info(f"Scraped URL: {url}")
                
            except Exception as e:
                logger.error(f"Failed to scrape URL {url}: {e}")
                source_data['urls'][url] = {'error': str(e)}
        
        # Process Jira tickets
        for ticket_id in jira_tickets:
            try:
                # Search for specific ticket
                jql = f"key = {ticket_id}"
                tickets = await mcp_client.search_jira_tickets(jql, max_results=1)
                
                if tickets:
                    source_data['jira_tickets'][ticket_id] = tickets[0]
                    logger.info(f"Retrieved Jira ticket: {ticket_id}")
                else:
                    source_data['jira_tickets'][ticket_id] = {'error': 'Ticket not found'}
                    
            except Exception as e:
                logger.error(f"Failed to retrieve Jira ticket {ticket_id}: {e}")
                source_data['jira_tickets'][ticket_id] = {'error': str(e)}
        
        return source_data
    
    async def _generate_analysis(self, source_data: Dict[str, Any], issue_description: str) -> Dict[str, Any]:
        """Generate RCA analysis using LLM"""
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(source_data, issue_description)
            
            # Generate analysis using configured LLM
            if self.config['default_llm'] == 'openai':
                try:
                    analysis = await self._generate_with_openai(context)
                except Exception as e:
                    logger.warning(f"OpenAI failed: {e}. Trying fallback...")
                    analysis = await self._try_fallback_llms(['anthropic', 'openrouter'], context)
            elif self.config['default_llm'] == 'anthropic':
                try:
                    analysis = await self._generate_with_anthropic(context)
                except Exception as e:
                    logger.warning(f"Anthropic failed: {e}. Trying fallback...")
                    analysis = await self._try_fallback_llms(['openrouter', 'openai'], context)
            elif self.config['default_llm'] == 'openrouter':
                try:
                    analysis = await self._generate_with_openrouter(context)
                except Exception as e:
                    logger.warning(f"OpenRouter failed: {e}. Trying fallback...")
                    analysis = await self._try_fallback_llms(['anthropic', 'openai'], context)
            else:
                raise ValueError(f"Unsupported LLM: {self.config['default_llm']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis: {e}")
            raise
    
    def _prepare_llm_context(self, source_data: Dict[str, Any], issue_description: str) -> str:
        """Prepare context string for LLM"""
        context_parts = [
            f"ISSUE DESCRIPTION:\n{issue_description}\n",
            "\n" + "="*50 + "\n",
            "SOURCE DATA ANALYSIS:\n"
        ]
        
        # Add file contents
        if source_data['files']:
            context_parts.append("FILES ANALYZED:")
            for file_path, file_data in source_data['files'].items():
                if 'content' in file_data:
                    context_parts.append(f"\n--- {file_path} ---")
                    context_parts.append(file_data['content'][:5000])  # Limit content length
                    if len(file_data['content']) > 5000:
                        context_parts.append("... (content truncated)")
                else:
                    context_parts.append(f"\n--- {file_path} (ERROR) ---")
                    context_parts.append(file_data.get('error', 'Unknown error'))
        
        # Add URL contents
        if source_data['urls']:
            context_parts.append("\n\nWEB CONTENT ANALYZED:")
            for url, url_data in source_data['urls'].items():
                if 'content' in url_data:
                    context_parts.append(f"\n--- {url} ---")
                    context_parts.append(url_data['content'][:3000])  # Limit content length
                    if len(url_data['content']) > 3000:
                        context_parts.append("... (content truncated)")
                else:
                    context_parts.append(f"\n--- {url} (ERROR) ---")
                    context_parts.append(url_data.get('error', 'Unknown error'))
        
        # Add Jira ticket data
        if source_data['jira_tickets']:
            context_parts.append("\n\nJIRA TICKETS REFERENCED:")
            for ticket_id, ticket_data in source_data['jira_tickets'].items():
                if 'key' in ticket_data:
                    context_parts.append(f"\n--- {ticket_id} ---")
                    context_parts.append(f"Summary: {ticket_data['summary']}")
                    context_parts.append(f"Status: {ticket_data['status']}")
                    context_parts.append(f"Priority: {ticket_data['priority']}")
                    context_parts.append(f"Description: {ticket_data['description']}")
                else:
                    context_parts.append(f"\n--- {ticket_id} (ERROR) ---")
                    context_parts.append(ticket_data.get('error', 'Unknown error'))
        
        return "\n".join(context_parts)
    
    async def _generate_with_openai(self, context: str) -> Dict[str, Any]:
        """Generate analysis using OpenAI"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.config['openai_api_key'],
                base_url=self.config['openai_base_url']
            )
            
            prompt = f"""
            Based on the provided context, generate a comprehensive Root Cause Analysis (RCA) report. 
            Structure your response as a JSON object with the following fields:
            
            {{
                "executive_summary": "Brief summary of the issue and findings",
                "problem_statement": "Clear statement of the problem",
                "timeline": "Chronological sequence of events",
                "root_cause": "Primary root cause identified",
                "contributing_factors": ["List of contributing factors"],
                "impact_assessment": "Assessment of impact",
                "corrective_actions": ["List of immediate corrective actions"],
                "preventive_measures": ["List of preventive measures for the future"],
                "recommendations": ["List of recommendations"],
                "escalation_needed": "true/false - whether escalation is needed",
                "defect_tickets_needed": "true/false - whether defect tickets should be created",
                "severity": "Critical/High/Medium/Low",
                "priority": "P1/P2/P3/P4"
            }}
            
            Context:
            {context}
            """
            
            response = await client.chat.completions.create(
                model=self.config['openai_model'],
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content
            logger.debug(f"OpenAI response content: {analysis_text}")
            
            if not analysis_text or analysis_text.strip() == "":
                logger.error("OpenAI returned empty response")
                raise ValueError("Empty response from OpenAI")
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {analysis_text}")
                
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError:
                        # Fallback: create a basic analysis structure
                        analysis = self._create_fallback_analysis(analysis_text)
                else:
                    # Fallback: create a basic analysis structure
                    analysis = self._create_fallback_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis with OpenAI: {e}")
            raise
    
    async def _generate_with_anthropic(self, context: str) -> Dict[str, Any]:
        """Generate analysis using Anthropic"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(
                api_key=self.config['anthropic_api_key']
            )
            
            prompt = f"""
            Based on the provided context, generate a comprehensive Root Cause Analysis (RCA) report. 
            Structure your response as a JSON object with the following fields:
            
            {{
                "executive_summary": "Brief summary of the issue and findings",
                "problem_statement": "Clear statement of the problem",
                "timeline": "Chronological sequence of events",
                "root_cause": "Primary root cause identified",
                "contributing_factors": ["List of contributing factors"],
                "impact_assessment": "Assessment of impact",
                "corrective_actions": ["List of immediate corrective actions"],
                "preventive_measures": ["List of preventive measures for the future"],
                "recommendations": ["List of recommendations"],
                "escalation_needed": "true/false - whether escalation is needed",
                "defect_tickets_needed": "true/false - whether defect tickets should be created",
                "severity": "Critical/High/Medium/Low",
                "priority": "P1/P2/P3/P4"
            }}
            
            Context:
            {context}
            """
            
            response = await client.messages.create(
                model=self.config['anthropic_model'],
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse JSON response
            analysis_text = response.content[0].text
            logger.debug(f"Anthropic response content: {analysis_text}")
            
            if not analysis_text or analysis_text.strip() == "":
                logger.error("Anthropic returned empty response")
                raise ValueError("Empty response from Anthropic")
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {analysis_text}")
                
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError:
                        # Fallback: create a basic analysis structure
                        analysis = self._create_fallback_analysis(analysis_text)
                else:
                    # Fallback: create a basic analysis structure
                    analysis = self._create_fallback_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis with Anthropic: {e}")
            raise
    
    async def _generate_with_openrouter(self, context: str) -> Dict[str, Any]:
        """Generate analysis using OpenRouter"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.config['openrouter_api_key'],
                base_url=self.config['openrouter_base_url']
            )
            
            prompt = f"""
            Based on the provided context, generate a comprehensive Root Cause Analysis (RCA) report. 
            Structure your response as a JSON object with the following fields:
            
            {{
                "executive_summary": "Brief summary of the issue and findings",
                "problem_statement": "Clear statement of the problem",
                "timeline": "Chronological sequence of events",
                "root_cause": "Primary root cause identified",
                "contributing_factors": ["List of contributing factors"],
                "impact_assessment": "Assessment of impact",
                "corrective_actions": ["List of immediate corrective actions"],
                "preventive_measures": ["List of preventive measures for the future"],
                "recommendations": ["List of recommendations"],
                "escalation_needed": "true/false - whether escalation is needed",
                "defect_tickets_needed": "true/false - whether defect tickets should be created",
                "severity": "Critical/High/Medium/Low",
                "priority": "P1/P2/P3/P4"
            }}
            
            Context:
            {context}
            """
            
            response = await client.chat.completions.create(
                model=self.config['openrouter_model'],
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                extra_headers={
                    "HTTP-Referer": "https://github.com/solarisjon/creatercav4",
                    "X-Title": "MCP RCA Tool"
                }
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content
            logger.debug(f"OpenRouter response content: {analysis_text}")
            
            if not analysis_text or analysis_text.strip() == "":
                logger.error("OpenRouter returned empty response")
                raise ValueError("Empty response from OpenRouter")
            
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {analysis_text}")
                
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError:
                        # Fallback: create a basic analysis structure
                        analysis = self._create_fallback_analysis(analysis_text)
                else:
                    # Fallback: create a basic analysis structure
                    analysis = self._create_fallback_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis with OpenRouter: {e}")
            raise
    
    async def _try_fallback_llms(self, fallback_order: List[str], context: str) -> Dict[str, Any]:
        """Try fallback LLMs in order until one succeeds"""
        for llm_name in fallback_order:
            try:
                logger.info(f"Trying fallback LLM: {llm_name}")
                
                if llm_name == 'openai' and self.config.get('openai_api_key'):
                    return await self._generate_with_openai(context)
                elif llm_name == 'anthropic' and self.config.get('anthropic_api_key'):
                    return await self._generate_with_anthropic(context)
                elif llm_name == 'openrouter' and self.config.get('openrouter_api_key'):
                    return await self._generate_with_openrouter(context)
                else:
                    logger.warning(f"No API key available for {llm_name}")
                    continue
                    
            except Exception as e:
                logger.warning(f"Fallback LLM {llm_name} failed: {e}")
                continue
        
        # If all fallbacks fail, raise the last exception
        raise Exception("All LLM providers failed to generate analysis")
    
    def _create_fallback_analysis(self, raw_text: str) -> Dict[str, Any]:
        """Create a fallback analysis structure when JSON parsing fails"""
        logger.warning("Using fallback analysis structure due to JSON parsing error")
        
        return {
            "executive_summary": "RCA analysis generated with limited parsing. Please review the raw analysis below.",
            "problem_statement": "Unable to parse structured analysis from LLM response.",
            "timeline": "Timeline information not available in structured format.",
            "root_cause": "Root cause analysis requires manual review of the raw response.",
            "contributing_factors": ["JSON parsing failure", "LLM response format issue"],
            "impact_assessment": "Impact assessment requires manual review.",
            "corrective_actions": ["Review raw LLM response", "Adjust prompt formatting", "Check API configuration"],
            "preventive_measures": ["Improve response parsing", "Add response validation"],
            "recommendations": ["Manual review of raw analysis", "Check LLM API configuration"],
            "escalation_needed": "false",
            "defect_tickets_needed": "true",
            "severity": "Medium",
            "priority": "P3",
            "raw_response": raw_text[:2000]  # Include first 2000 chars of raw response
        }
    
    async def _create_rca_document(self, analysis: Dict[str, Any]) -> Path:
        """Create RCA document from analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"rca_report_{timestamp}.json"
            
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # For now, save as JSON. Later we can implement Word document generation
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"RCA document created: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to create RCA document: {e}")
            raise
    

# Global RCA generator instance
rca_generator = RCAGenerator()