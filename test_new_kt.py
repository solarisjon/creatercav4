#!/usr/bin/env python3
"""Test the new KT prompt structure and parsing"""

# Sample response that matches the new KT format
sample_response = '''```json
{
  "executive_summary": "API calls not updating in Active IQ due to Zookeeper concurrency issues",
  "problem_statement": "API calls for volumes and snapshots failing to update in Active IQ",
  "timeline": "First observed 2025-06-05, escalated 2025-06-10",
  "root_cause": "Concurrency issues in Zookeeper updates",
  "contributing_factors": "Non-thread safe operations, concurrent StartSync operations",
  "impact_assessment": "Cluster-wide impact affecting all volumes and snapshots",
  "corrective_actions": "Implement serialization for snapshot schedules",
  "preventive_measures": "Enhanced thread safety monitoring",
  "recommendations": "Develop patch for Zookeeper concurrency issues",
  "escalation_needed": "Yes",
  "defect_tickets_needed": "Yes",
  "severity": "High",
  "priority": "P2"
}
```

---

### KEPNER-TREGOE PROBLEM ANALYSIS

#### 1. Problem Statement
- **What is happening**: API calls are not being updated in Active IQ
- **Deviation from expected**: Zookeeper operations should complete successfully
- **Business impact**: Volume and snapshot management affected cluster-wide

#### 2. Problem Specification (IS/IS NOT Analysis)

| Dimension | IS (Facts about the problem) | IS NOT (Facts that distinguish) |
|-----------|------------------------------|----------------------------------|
| **WHAT** | | |
| Object affected | API calls related to volumes and snapshots | Other unrelated API calls |
| Deviation observed | API calls not updating in Active IQ | API calls updating correctly |
| **WHERE** | | |
| Geographic location | Cluster-wide | Specific node or volume |
| System location | Zookeeper updates | Other system components |
| **WHEN** | | |
| First occurrence | 2025-06-05 | Before 2025-06-05 |
| Pattern/frequency | Continuous since first observed | Sporadic |
| Lifecycle timing | During API update operations | During normal operations |
| **EXTENT** | | |
| Number of objects | All volumes and snapshots | Specific subset |
| Size/scope | Cluster-wide | Node-specific |
| Trend | Persistent | Temporary |

#### 3. Root Cause Analysis
- **Potential Causes**: Zookeeper concurrency issues, thread safety problems
- **Cause Validation**: Evidence found in logs and core file analysis
- **Root Cause**: Concurrency issues in Zookeeper updates leading to missing key-value pairs
- **Contributing Factors**: Non-thread safe accesses, concurrent StartSync operations

#### 4. Solution Development
- **Immediate Actions**: Monitor API update failures
- **Long-term Solutions**: Implement serialization for snapshot schedules
- **Implementation Plan**: 2-4 week development timeline
- **Risk Assessment**: Medium development effort required

#### 5. Prevention Strategy
- **Process Improvements**: Enhanced thread safety in Zookeeper operations
- **Monitoring Enhancements**: API update success rate monitoring
- **Training Needs**: Thread safety best practices

### RECOMMENDATIONS AND NEXT STEPS
- Prioritize development of Zookeeper concurrency patch
- Implement enhanced monitoring for early detection
- Schedule follow-up review for August 15, 2025
- Assign development team to address thread safety issues
'''

import sys
import os
sys.path.append('src')
from core.analysis.parsers import ResponseParser

# Test the new parsing
parser = ResponseParser()
result = parser.parse_llm_response(sample_response, 'kt-analysis_prompt')

print("=== NEW KT PARSING TEST ===")
print(f"Total sections found: {len(result)}")
print("\nJSON sections:")
json_fields = ['executive_summary', 'problem_statement', 'timeline', 'root_cause']
for field in json_fields:
    if field in result:
        print(f"  ✅ {field}: {len(result[field])} chars")
    else:
        print(f"  ❌ {field}: MISSING")

print("\nKT Special sections:")
kt_sections = ['kepner_tregoe_analysis', 'is_is_not_table', 'root_cause_analysis', 'recommendations']
for section in kt_sections:
    if section in result:
        print(f"  ✅ {section}: {len(result[section])} chars")
        if section == 'is_is_not_table':
            print(f"      Contains table: {'|' in result[section]}")
    else:
        print(f"  ❌ {section}: MISSING")

print("\nIS/IS NOT Table preview:")
if 'is_is_not_table' in result:
    table_content = result['is_is_not_table']
    print(table_content[:300] + "..." if len(table_content) > 300 else table_content)
else:
    print("Table not found!")
