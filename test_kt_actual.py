#!/usr/bin/env python3
"""Test script to check actual KT parsing"""

import sys
sys.path.append('src')
from core.analysis.parsers import ResponseParser

# Load the actual response from the JSON file
import json
with open('output/kt-analysis_prompt_20250706_203434.json', 'r') as f:
    data = json.load(f)

raw_response = data['analysis']['raw_response']
parser = ResponseParser()

# Parse the response
result = parser.parse_llm_response(raw_response, 'kt-analysis_prompt')

print('Extracted sections:')
for key, value in result.items():
    if key in ['kepner_tregoe_template', 'problem_assessment_table']:
        print(f'{key}: {len(str(value))} characters')
        if 'table' in key:
            print(f'  Contains table markers: {"|" in str(value)}')
            print(f'  First 200 chars: {str(value)[:200]}...')
        print()

# Check if problem_assessment_table was extracted
if 'problem_assessment_table' in result:
    print("✅ Problem Assessment Table was extracted!")
    table_content = result['problem_assessment_table']
    print(f"Table content length: {len(table_content)}")
    print("Table content:")
    print(table_content[:500] + "..." if len(table_content) > 500 else table_content)
else:
    print("❌ Problem Assessment Table was NOT extracted!")
    print("Available keys:", list(result.keys()))
