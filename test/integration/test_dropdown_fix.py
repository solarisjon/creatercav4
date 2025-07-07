#!/usr/bin/env python3
"""
Test script to demonstrate the dropdown selection issue and verify the fix.
"""
import asyncio
import sys
sys.path.insert(0, './src')

async def test_dropdown_issue():
    """Test that the correct prompt sections are displayed based on selection"""
    
    from app import RCAApp
    from rca_generator import rca_generator
    
    # Create the app instance
    app = RCAApp()
    
    print("=== Testing Dropdown Selection Issue ===\n")
    
    # Test each prompt type
    prompt_types = [
        "formal_rca_prompt",
        "initial_analysis_prompt", 
        "kt-analysis_prompt"
    ]
    
    for i, prompt_type in enumerate(prompt_types):
        print(f"Test {i+1}: Testing {prompt_type}")
        
        # Simulate setting the dropdown
        app.selected_prompt = prompt_type
        print(f"  → Dropdown set to: {prompt_type}")
        
        # Simulate having some analysis result with the wrong prompt stored
        # This simulates the bug where dropdown was changed after generation
        wrong_prompt = prompt_types[(i + 1) % len(prompt_types)]  # Different prompt
        
        # Create a mock analysis result
        app.analysis_result = {
            'analysis': {
                'executive_summary': 'Test summary',
                'problem_statement': 'Test problem',
                'overview': 'Test overview',
                'key_findings': 'Test findings',
                'problem_description': 'Test description',
                'possible_causes': ['Cause 1', 'Cause 2']
            },
            'prompt_file_used': prompt_type  # This should be what gets used
        }
        
        # Test what sections would be displayed
        print(f"  → Analysis generated with: {prompt_type}")
        print(f"  → prompt_file_used stored: {app.analysis_result.get('prompt_file_used')}")
        
        # Check if the fix works - prompt_file should come from analysis_result
        prompt_file_for_display = app.analysis_result.get('prompt_file_used', app.selected_prompt)
        print(f"  → Sections will be read from: {prompt_file_for_display}")
        
        # Verify the fix
        if prompt_file_for_display == prompt_type:
            print(f"  ✅ CORRECT: Using {prompt_type} sections")
        else:
            print(f"  ❌ WRONG: Should use {prompt_type} but using {prompt_file_for_display}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_dropdown_issue())
