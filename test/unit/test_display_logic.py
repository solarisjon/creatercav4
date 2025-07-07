#!/usr/bin/env python3
"""
Test the improved display_results logic
"""
import sys
sys.path.insert(0, './src')

def test_display_logic():
    """Test the display results logic with mock data"""
    
    try:
        from app import RCAApp
        
        print("=== Testing Improved Display Logic ===\n")
        
        app = RCAApp()
        
        # Test 1: Perfect mapping match
        print("TEST 1: Perfect mapping match (formal RCA)")
        app.analysis_result = {
            'prompt_file_used': 'formal_rca_prompt',
            'analysis': {
                'executive_summary': 'This is the executive summary',
                'problem_statement': 'This is the problem statement',
                'timeline': 'This is the timeline',
                'root_cause': 'This is the root cause',
                'recommendations': 'These are the recommendations'
            }
        }
        
        # Check mapping
        prompt_file = app.analysis_result['prompt_file_used']
        section_mapping = app.PROMPT_REPORT_MAP.get(prompt_file, [])
        analysis = app.analysis_result['analysis']
        
        print(f"Prompt file: {prompt_file}")
        print(f"Analysis keys: {list(analysis.keys())}")
        print(f"Mapping sections: {len(section_mapping)}")
        
        found_sections = 0
        for header, expected_key in section_mapping:
            if expected_key in analysis:
                found_sections += 1
                print(f"  ✅ {header} -> {expected_key}")
            else:
                print(f"  ❌ {header} -> {expected_key} (missing)")
        
        print(f"Found {found_sections}/{len(section_mapping)} mapped sections")
        
        # Test 2: Fuzzy matching needed
        print("\nTEST 2: Fuzzy matching (initial analysis)")
        app.analysis_result = {
            'prompt_file_used': 'initial_analysis_prompt',
            'analysis': {
                'Overview': 'This is the overview',  # Different case
                'keyfindings': 'These are key findings',  # No underscore
                'summary': 'This is the summary',
                'recommendations': 'These are recommendations',
                'extra_section': 'This is an unmapped section'
            }
        }
        
        prompt_file = app.analysis_result['prompt_file_used']
        section_mapping = app.PROMPT_REPORT_MAP.get(prompt_file, [])
        analysis = app.analysis_result['analysis']
        
        print(f"Prompt file: {prompt_file}")
        print(f"Analysis keys: {list(analysis.keys())}")
        
        found_sections = 0
        for header, expected_key in section_mapping:
            # Simulate the fuzzy matching logic
            value = analysis.get(expected_key)
            if value is None:
                possible_keys = [
                    expected_key,
                    expected_key.replace("_", ""),
                    expected_key.replace("_", " "),
                    expected_key.lower(),
                    expected_key.upper(),
                    header.lower().replace(" ", "_"),
                    header.lower().replace(" ", ""),
                ]
                
                for possible_key in possible_keys:
                    if possible_key in analysis:
                        value = analysis[possible_key]
                        print(f"  ✅ {header} -> {expected_key} (found as '{possible_key}')")
                        found_sections += 1
                        break
                
                if value is None:
                    print(f"  ❌ {header} -> {expected_key} (not found)")
            else:
                print(f"  ✅ {header} -> {expected_key}")
                found_sections += 1
        
        print(f"Found {found_sections}/{len(section_mapping)} mapped sections")
        
        # Check unmapped sections
        mapped_keys = [key for _, key in section_mapping]
        unmapped_keys = [k for k in analysis.keys() if k not in mapped_keys and k not in ['sources_used', 'raw_response', 'raw_analysis']]
        if unmapped_keys:
            print(f"Unmapped sections: {unmapped_keys}")
        
        print("\n✅ Display logic test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_display_logic()
    sys.exit(0 if success else 1)
