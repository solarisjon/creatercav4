#!/usr/bin/env python3
"""
Test script to demonstrate the wider table layout
"""
from nicegui import ui

# Sample KT table data (wider content)
sample_table = """
| Dimension | IS (What the problem is) | IS NOT (What the problem is not) |
|-----------|---------------------------|-----------------------------------|
| WHAT | NFS read operations taking 10+ seconds during peak hours | Write operations are normal speed. Other storage systems work fine |
| WHERE | Primary NFS server cluster (nas01-cluster) in datacenter A | Secondary clusters, backup systems, or test environments not affected |
| WHEN | During peak business hours (9 AM - 5 PM) on weekdays, especially Fridays | Nights, weekends, or low-usage periods show normal performance |
| WHO | End users accessing shared filesystems, particularly in engineering dept | Database servers, administrative users, or other service accounts unaffected |
| EXTENT | Approximately 50+ concurrent users, 2-hour duration episodes | Single users or small groups, short-duration access patterns work normally |
| PATTERN | Consistent degradation pattern during high concurrent access loads | Random or sporadic access does not trigger the performance issue |
"""

def create_test_ui():
    """Create test UI with wide table"""
    with ui.column().classes('w-full px-4'):
        ui.label('KT Analysis Width Test').classes('text-2xl font-bold mb-4')
        
        # Test the table HTML conversion
        from src.ui.components.analysis_display import AnalysisDisplay
        
        # Create a mock container
        display = AnalysisDisplay(ui.column())
        
        # Convert and display the table
        with ui.card().classes('w-full mb-4'):
            ui.label('Problem Specification (IS/IS NOT Analysis)').classes('text-lg font-semibold mb-2')
            
            # Use the table renderer directly
            html_table = display._convert_markdown_table_to_html(sample_table)
            if html_table:
                ui.html(html_table)
            else:
                ui.markdown(sample_table)

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    create_test_ui()
    ui.run(port=8091, title="Width Test Demo")
