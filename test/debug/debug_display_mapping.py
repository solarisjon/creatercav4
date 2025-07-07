#!/usr/bin/env python3
"""
Test script to debug the browser vs CLI display issue
"""
import asyncio
import sys
sys.path.insert(0, './src')

async def debug_display_mapping():
    """Debug what sections are being generated vs displayed"""
    
    try:
        from app import RCAApp
        
        print("=== Debugging Browser vs CLI Display Issue ===\n")
        
        app = RCAApp()
        
        # Simulate different analysis results for each prompt type
        test_scenarios = [
            {
                'name': 'Formal RCA',
                'prompt_file': 'formal_rca_prompt',
                'analysis_keys': [
                    'executive_summary', 'problem_statement', 'timeline', 'root_cause',
                    'contributing_factors', 'impact_assessment', 'corrective_actions',
                    'preventive_measures', 'recommendations', 'escalation_needed',
                    'defect_tickets_needed', 'severity', 'priority'
                ]
            },
            {
                'name': 'Overview Analysis',
                'prompt_file': 'initial_analysis_prompt',
                'analysis_keys': ['overview', 'key_findings', 'summary', 'recommendations']
            },
            {
                'name': 'Problem Assessment',
                'prompt_file': 'kt-analysis_prompt',
                'analysis_keys': ['problem_description', 'possible_causes', 'data_collection', 'root_cause', 'solution']
            }
        ]
        
        for scenario in test_scenarios:
            print(f"SCENARIO: {scenario['name']}")
            print(f"Prompt file: {scenario['prompt_file']}")
            print("-" * 50)
            
            # Check predefined mapping
            predefined_mapping = app.PROMPT_REPORT_MAP.get(scenario['prompt_file'], [])
            print(f"Predefined mapping sections ({len(predefined_mapping)}):")
            for header, key in predefined_mapping:
                print(f"  - {header} -> {key}")
            
            print(f"\nExpected analysis keys from RCA generator ({len(scenario['analysis_keys'])}):")
            for key in scenario['analysis_keys']:
                print(f"  - {key}")
            
            # Check for mismatches
            predefined_keys = [key for _, key in predefined_mapping]
            missing_from_mapping = [key for key in scenario['analysis_keys'] if key not in predefined_keys]
            extra_in_mapping = [key for key in predefined_keys if key not in scenario['analysis_keys']]
            
            if missing_from_mapping:
                print(f"\n❌ Keys missing from predefined mapping:")
                for key in missing_from_mapping:
                    print(f"  - {key}")
            
            if extra_in_mapping:
                print(f"\n⚠️  Extra keys in predefined mapping:")
                for key in extra_in_mapping:
                    print(f"  - {key}")
            
            if not missing_from_mapping and not extra_in_mapping:
                print(f"\n✅ Perfect match between mapping and expected keys!")
            
            print("\n" + "="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_display_mapping())
    sys.exit(0 if success else 1)
