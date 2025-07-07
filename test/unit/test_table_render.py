#!/usr/bin/env python3
"""Test the new HTML table rendering"""

# Sample IS/IS NOT table content
sample_table = """| Dimension | IS (Facts about the problem) | IS NOT (Facts that distinguish) |
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
| Trend | Persistent | Temporary |"""

import sys
sys.path.append('src')

# Create a mock AnalysisDisplay instance to test the table conversion
class TestAnalysisDisplay:
    def _convert_markdown_table_to_html(self, markdown_table: str) -> str:
        """Convert markdown table to HTML table with proper styling"""
        lines = markdown_table.strip().split('\n')
        if not lines:
            return ""
        
        # Find table lines (contain |)
        table_lines = [line.strip() for line in lines if line.strip() and '|' in line]
        if len(table_lines) < 2:
            return ""
        
        # Parse header
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]
        
        # Skip separator line (usually line with --- )
        data_lines = []
        for line in table_lines[1:]:
            if not line.replace('|', '').replace('-', '').replace(' ', ''):
                continue  # Skip separator lines
            data_lines.append(line)
        
        # Build HTML table
        html_parts = [
            '<div class="overflow-x-auto">',
            '<table class="min-w-full bg-white border border-gray-300 rounded-lg shadow-sm">',
            '<thead class="bg-gray-50">',
            '<tr>'
        ]
        
        # Add headers
        for header in headers:
            # Clean up markdown formatting in headers
            clean_header = header.replace('**', '').replace('*', '')
            html_parts.append(f'<th class="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-300">{clean_header}</th>')
        
        html_parts.extend(['</tr>', '</thead>', '<tbody>'])
        
        # Add data rows
        for i, line in enumerate(data_lines):
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(cells) >= len(headers):  # Only process complete rows
                row_class = "bg-white" if i % 2 == 0 else "bg-gray-50"
                html_parts.append(f'<tr class="{row_class}">')
                
                for j, cell in enumerate(cells[:len(headers)]):  # Match header count
                    # Clean up markdown formatting and handle empty cells
                    clean_cell = cell.replace('**', '').replace('*', '').strip()
                    if not clean_cell:
                        clean_cell = "&nbsp;"
                    
                    # Style first column differently (dimension labels)
                    if j == 0:
                        cell_class = "px-4 py-3 text-sm font-medium text-gray-900 border-b border-gray-200"
                    else:
                        cell_class = "px-4 py-3 text-sm text-gray-700 border-b border-gray-200"
                    
                    html_parts.append(f'<td class="{cell_class}">{clean_cell}</td>')
                
                html_parts.append('</tr>')
        
        html_parts.extend(['</tbody>', '</table>', '</div>'])
        
        return '\n'.join(html_parts)

# Test the conversion
display = TestAnalysisDisplay()
html_table = display._convert_markdown_table_to_html(sample_table)

print("=== HTML TABLE CONVERSION TEST ===")
print(f"Input table lines: {len(sample_table.splitlines())}")
print(f"Output HTML length: {len(html_table)} characters")
print("\nGenerated HTML:")
print(html_table)

# Save to a test file to view in browser
with open('test_table.html', 'w') as f:
    f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>KT Table Test</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="p-8">
    <h1 class="text-2xl font-bold mb-4">KT Problem Specification (IS/IS NOT Analysis)</h1>
    {html_table}
</body>
</html>
""")

print(f"\n✅ Test HTML file saved as 'test_table.html'")
print("You can open this file in a browser to see the rendered table.")
