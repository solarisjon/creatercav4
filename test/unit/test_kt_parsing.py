#!/usr/bin/env python3
"""Test script to check KT parsing patterns"""

import re

# Sample text from the actual output
sample_text = """```json
{
  "executive_summary": "The issue involves API calls not being updated in Active IQ due to a Zookeeper problem, affecting a cluster-wide environment. The root cause is identified as a concurrency issue in Zookeeper updates, leading to missing JSON key-value pairs.",
  "problem_statement": "API calls are not being updated in Active IQ, affecting volume and snapshot management due to a Zookeeper issue.",
  "timeline": "The issue was first observed on 2025-06-05 and escalated on 2025-06-10. Investigation and updates continued until 2025-07-02.",
  "root_cause": "Concurrency issues in Zookeeper updates leading to missing JSON key-value pairs.",
  "contributing_factors": "Concurrent StartSync operations and non-thread safe accesses during Zookeeper updates.",
  "impact_assessment": "Cluster-wide impact affecting all volumes and snapshots, preventing API updates.",
  "corrective_actions": "Implement serialization for snapshot schedules and ensure thread-safe operations in Zookeeper updates.",
  "preventive_measures": "Review and enhance thread safety in Zookeeper operations and implement monitoring for API update failures.",
  "recommendations": "Prioritize the development of a patch to address concurrency issues in Zookeeper updates.",
  "escalation_needed": "Yes, to ensure timely resolution and prevent similar issues in the future.",
  "defect_tickets_needed": "Yes, to track and resolve the concurrency issue in Zookeeper updates.",
  "severity": "High",
  "priority": "P2"
}
```

---

### a) Kepner-Tregoe Problem Analysis Template

#### 1. Problem Statement
- **Clearly define the problem:** API calls are not being updated in Active IQ.
- **What is happening?** Zookeeper issue prevents API calls related to volumes and snapshots from being performed.
- **What are the effects of the problem?** Cluster-wide impact on volume and snapshot management.

#### 2. Problem Analysis

**2.1. Problem Details**
- **When does the problem occur?** Since 2025-06-05.
- **Where does the problem occur?** Cluster-wide.
- **Who is affected by the problem?** All users relying on Active IQ for volume and snapshot management.
- **What are the symptoms of the problem?** API calls not updating, segmentation fault in core file.

**2.2. Problem History**
- **What has changed in the environment or process?** Metadata drive ejected, core file created.
- **Have there been any previous occurrences of this problem?** Similar issues observed in ELEM-17246 and ELEM-17254.

#### 3. Cause Analysis

**3.1. Potential Causes**
- Concurrency issues in Zookeeper updates.
- Non-thread safe accesses during Zookeeper operations.

**3.2. Validation of Causes**
- Evidence of concurrency issues in log analysis.
- Core file analysis shows segmentation fault related to RPC calls.

**3.3. Root Cause Identification**
- Concurrency issues in Zookeeper updates leading to missing JSON key-value pairs.

#### 4. Solution Development

**4.1. Possible Solutions**
- Implement serialization for snapshot schedules.
- Ensure thread-safe operations in Zookeeper updates.

**4.2. Solution Evaluation**
- **Effectiveness:** High, addresses root cause.
- **Feasibility:** Medium, requires development effort.
- **Cost:** Moderate.
- **Time to implement:** Estimated 2-4 weeks.

**4.3. Recommended Solution**
- Implement serialization and thread-safe operations as a priority.

#### 5. Action Plan
- **What needs to be done?** Develop and deploy a patch for Zookeeper updates.
- **Who will do it?** Development team.
- **When will it be completed?** Target completion by 2025-08-01.
- **Resources Required:** Development and testing resources.

#### 6. Follow-up
- **Define metrics for measuring the effectiveness of the solution:** Monitor API update success rates.
- **Set a timeline for follow-up to ensure the problem is resolved:** Follow-up review on 2025-08-15.

---

### b) Problem Assessment

| Problem Assessment              | IS                                                        | IS NOT                                |
|---------------------------------|-----------------------------------------------------------|---------------------------------------|
| **What**                        |                                                           |                                       |
| What object?                    | API calls related to volumes and snapshots                | Other unrelated API calls             |
| What deviation?                 | API calls not updating in Active IQ                       | API calls updating correctly          |
| **Where**                       |                                                           |                                       |
| Where (geographically)?         | Cluster-wide                                              | Specific node or volume               |
| Where else in the world?        | Not specified                                             |                                       |
| Where on object?                | Zookeeper updates                                         | Other system components               |
| **When**                        |                                                           |                                       |
| When first?                     | 2025-06-05                                                | Before 2025-06-05                     |
| When since?                     | Continuous since first observed                           | Sporadic                              |
| When in the lifecycle?          | During API update operations                              |                                       |
| **Extent**                      |                                                           |                                       |
| How many objects?               | All volumes and snapshots                                 | Specific subset                       |
| What is size?                   | Cluster-wide                                              | Specific node or volume               |
| How many deviations?            | Multiple API calls                                        | Single API call                       |
| What is the trend?              | Persistent                                                | Temporary                             |
"""

# Test patterns
kt_section_patterns = {
    'kepner_tregoe_template': r'### a\) Kepner-Tregoe Problem Analysis Template\s*(.*?)(?=### b\)|$)',
    'problem_assessment_table': r'### b\) Problem Assessment.*?\n(.*?)(?=\n\s*$|$)',
    'issue_description': r'### ISSUE DESCRIPTION:?\s*(.*?)(?=###|---|\n\n\n|$)',
    'source_data_analysis': r'### SOURCE DATA ANALYSIS:?\s*(.*?)(?=###|---|\n\n\n|$)',
    'jira_tickets_referenced': r'### JIRA TICKETS REFERENCED:?\s*(.*?)(?=###|---|\n\n\n|$)'
}

print("Testing KT parsing patterns...")
print("=" * 50)

for section_name, pattern in kt_section_patterns.items():
    match = re.search(pattern, sample_text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        print(f"\n✅ {section_name}:")
        print(f"Length: {len(content)} characters")
        print(f"First 200 chars: {content[:200]}...")
        if section_name == 'problem_assessment_table':
            print(f"Contains table markers: {'|' in content}")
    else:
        print(f"\n❌ {section_name}: NO MATCH")
