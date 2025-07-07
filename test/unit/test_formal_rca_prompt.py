#!/usr/bin/env python3
"""
Test to verify the correct formal RCA prompt is being used
"""

import asyncio

async def test_formal_rca_prompt():
    print("Testing if formal RCA uses the correct prompt...")

    try:
        from src.config import config
        from src.core.analysis.prompt_manager import PromptManager
        
        print("1. Creating prompt manager...")
        prompt_manager = PromptManager()
        
        print("2. Loading formal RCA prompt template...")
        template = prompt_manager.get_prompt_template("formal_rca_prompt")
        
        print(f"3. Template length: {len(template)} characters")
        print(f"4. First 200 characters:\n{template[:200]}...")
        
        # Check if it contains the expected formal RCA sections
        expected_sections = [
            "Timeline",
            "Executive Summary", 
            "Problem Summary",
            "Root Cause",
            "RISK ASSESSMENT",
            "PREVENTION"
        ]
        
        found_sections = []
        for section in expected_sections:
            if section in template:
                found_sections.append(section)
        
        print(f"\n5. Found {len(found_sections)}/{len(expected_sections)} expected sections:")
        for section in found_sections:
            print(f"   ✓ {section}")
        
        missing_sections = set(expected_sections) - set(found_sections)
        if missing_sections:
            print(f"\n   Missing sections: {missing_sections}")
        
        # Build a test prompt
        print("\n6. Building complete prompt...")
        complete_prompt = prompt_manager.build_prompt(
            prompt_type="formal_rca_prompt",
            context_data="Test data",
            issue_description="Test issue"
        )
        
        print(f"7. Complete prompt length: {len(complete_prompt)} characters")
        
        # Check if NetApp context is included
        if "netapp_context" in complete_prompt.lower() or "ontap" in complete_prompt.lower():
            print("   ✓ NetApp context appears to be included")
        else:
            print("   ⚠ NetApp context may not be included")
        
        return len(found_sections) == len(expected_sections)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_formal_rca_prompt())
    if success:
        print("\n✅ Formal RCA prompt test PASSED - using correct template!")
    else:
        print("\n❌ Formal RCA prompt test FAILED")
