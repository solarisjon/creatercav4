#!/usr/bin/env python3
"""
Test script to verify formal RCA parsing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.analysis.parsers import ResponseParser

# Sample formal RCA response
sample_response = """
## I. INCIDENT OVERVIEW

### A. Timeline
Create a detailed chronological timeline that merges key events from SAP, CPE, and CONTAP cases. Include:
- January 2024: Initial issue reported
- February 2024: Escalation to engineering
- March 2024: Root cause identified

### B. Case Information
**Case Numbers:** Case 123456789 (CPE-1234 / CONTAP-5678)
**Issue Synopsis:** NFS performance degradation during peak hours
**Customer:** Acme Corporation  
**CAP:** Red

### C. Executive Summary
This incident involved a critical NFS performance degradation that affected customer operations during peak business hours. The issue was traced to a configuration mismatch in the cluster networking setup that caused excessive latency during high concurrent access patterns.

## II. TECHNICAL ANALYSIS

### A. Problem Summary
The problem began on January 15, 2024, when users reported severe NFS read performance degradation during peak business hours (9 AM - 5 PM). The affected system was the primary NFS cluster nas01-cluster in datacenter A, running ONTAP 9.12.1P5.

### B. Impact Assessment
**Technical Impact:** Complete NFS service degradation during peak hours
**Operational Impact:** 200+ users unable to access shared filesystems
**Business Impact:** Estimated $50,000 in productivity loss
**Scope of Impact:** Engineering department operations halted

### C. Root Cause Analysis
The root cause was identified as a misconfigured network interface card (NIC) bonding configuration that created asymmetric routing during high-load scenarios. This caused packet retransmissions and timeout issues that manifested as severe performance degradation.

## III. RISK ASSESSMENT

### A. Likelihood of Occurrence
**Risk Rating: Medium**
The likelihood of recurrence is Medium due to the specific configuration pattern present in this customer's environment.

### B. Vulnerability in Existing Environment
**Vulnerable Systems:** Other clusters using similar bonding configurations
**Risk Criteria:** ONTAP 9.12.x with specific NIC bonding setups
**Environmental Factors:** High-concurrency access patterns

### C. Overall Risk Profile
**Risk Matrix:** Medium Likelihood × High Impact = High Overall Risk
**Customer Constraints:** Limited maintenance windows
**Control Effectiveness:** Monitoring gaps identified

## IV. MITIGATION AND RESOLUTION

### A. Workaround Solutions
**Implementation Details:** Temporary load balancing configuration implemented
**Feasibility Assessment:** Successfully reduced impact by 80%
**Prerequisites:** Minimal downtime required

### B. Known Defect Resolution
**Resolution Approach:** Apply patch bundle to existing ONTAP release
**Implementation Path:** Scheduled maintenance window required
**Requirements:** 2-hour downtime, cluster failover capabilities

### C. New Defect Management
**Defect Details:** New defect ID 98765 opened for configuration validation
**Patch Process:** Targeted fix for Q2 2024 release
**Interim Measures:** Enhanced monitoring and alerting

### D. Recommended System/Environmental Changes
**Hardware Upgrades:** Network switch configuration updates
**Software Updates:** ONTAP upgrade to latest stable release
**Configuration Optimization:** NIC bonding parameter adjustments

## V. PREVENTION STRATEGY

### A. Current Environment Prevention
**Immediate Actions:** Configuration validation scripts deployed
**Monitoring Enhancements:** Additional network performance metrics
**Configuration Reviews:** Monthly validation procedures established

### B. Future Prevention Initiatives
**Process Improvements:** Enhanced configuration change management
**Best Practices Updates:** Updated deployment procedures
**Testing Enhancements:** Pre-production validation requirements

### C. Monitoring and Detection
**Health Monitoring:** Real-time network performance dashboards
**Vulnerability Detection:** Automated configuration scanning
**Real-time Alerting:** Proactive performance threshold monitoring
"""

def test_formal_rca_parsing():
    parser = ResponseParser()
    
    print("Testing formal RCA parsing...")
    result = parser.parse_llm_response(sample_response, "formal_rca_prompt")
    
    print(f"\nExtracted {len(result)} sections:")
    for key, value in result.items():
        if key != 'raw_response':
            print(f"- {key}: {len(value) if isinstance(value, str) else 'N/A'} characters")
    
    print("\nSample section content:")
    if 'executive_summary' in result:
        print(f"Executive Summary: {result['executive_summary'][:200]}...")
    
    if 'timeline' in result:
        print(f"Timeline: {result['timeline'][:200]}...")
    
    if 'root_cause' in result:
        print(f"Root Cause: {result['root_cause'][:200]}...")

if __name__ == "__main__":
    test_formal_rca_parsing()
