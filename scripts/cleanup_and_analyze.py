#!/usr/bin/env python3
"""
Cleanup script to remove temporary files and organize the codebase
"""
import os
import shutil
from pathlib import Path

def cleanup_temporary_files():
    """Remove temporary test and debug files"""
    root_dir = Path(".")
    
    # Files to remove (temporary test/debug files)
    temp_patterns = [
        "test_*.py",
        "debug_*.py", 
        "simple_connectivity_test.py",
        "detailed_jira_test.py"
    ]
    
    # Files to keep (legitimate tests)
    keep_files = [
        "tests/test_*.py",  # Proper unit tests
        "test_dropdown_fix.py"  # Current issue being worked on
    ]
    
    files_to_remove = []
    
    # Find temporary files
    for pattern in temp_patterns:
        for file in root_dir.glob(pattern):
            # Check if it's in the tests directory (keep those)
            if not any(file.match(keep_pattern) for keep_pattern in keep_files):
                files_to_remove.append(file)
    
    print("🧹 Cleaning up temporary files...")
    for file in files_to_remove:
        print(f"  - Removing: {file}")
        # file.unlink()  # Uncomment to actually delete
    
    print(f"\n📊 Found {len(files_to_remove)} temporary files to remove")
    print("Note: Uncomment file.unlink() in script to actually delete files")

def create_new_directory_structure():
    """Create the new directory structure"""
    new_dirs = [
        "src/ui",
        "src/ui/components", 
        "src/ui/utils",
        "src/core",
        "src/core/analysis",
        "src/core/llm",
        "src/core/llm/providers",
        "src/core/data",
        "src/core/data/collectors",
        "src/core/data/processors",
        "src/integrations",
        "src/integrations/mcp",
        "src/integrations/mcp/servers",
        "src/integrations/jira",
        "src/models",
        "src/prompts/templates",
        "src/prompts/contexts", 
        "src/prompts/schemas",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tests/fixtures",
        "docs",
        "scripts",
        "config"
    ]
    
    print("🏗️  Creating new directory structure...")
    for dir_path in new_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if dir_path.startswith("src/"):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
        print(f"  ✅ Created: {dir_path}")

def analyze_current_files():
    """Analyze current file sizes and complexity"""
    src_files = list(Path("src").glob("*.py"))
    
    print("📋 Current source file analysis:")
    print("-" * 50)
    
    for file in sorted(src_files):
        if file.name != "__init__.py":
            line_count = len(file.read_text().splitlines())
            status = "🔴 Large" if line_count > 500 else "🟡 Medium" if line_count > 200 else "🟢 Small"
            print(f"{status:12} {file.name:20} ({line_count:4} lines)")

def show_migration_recommendations():
    """Show specific recommendations for each large file"""
    recommendations = {
        "app.py": [
            "Split into UI components (src/ui/main_app.py)",
            "Extract display logic to src/ui/components/analysis_display.py", 
            "Move chat logic to src/ui/components/chat_interface.py",
            "Keep only main app orchestration"
        ],
        "rca_generator.py": [
            "Split LLM providers into src/core/llm/providers/",
            "Extract parsing logic to src/core/analysis/parsers.py",
            "Move prompt management to src/core/analysis/prompt_manager.py",
            "Create unified LLM client in src/core/llm/client.py"
        ],
        "mcp_client.py": [
            "Move to src/integrations/mcp/client.py",
            "Extract Jira logic to src/integrations/jira/api_client.py",
            "Create separate collectors in src/core/data/collectors/"
        ]
    }
    
    print("\n🎯 File migration recommendations:")
    print("=" * 60)
    
    for file, recs in recommendations.items():
        print(f"\n📄 {file}:")
        for rec in recs:
            print(f"  → {rec}")

def main():
    """Main cleanup and analysis function"""
    print("🏗️  RCA Tool Codebase Cleanup & Analysis")
    print("=" * 50)
    
    analyze_current_files()
    print()
    cleanup_temporary_files() 
    print()
    create_new_directory_structure()
    print()
    show_migration_recommendations()
    
    print("\n✅ Analysis complete!")
    print("\n📋 Next steps:")
    print("1. Review the recommendations above")
    print("2. Uncomment file deletion in cleanup_temporary_files() if you want to remove temp files")
    print("3. Run the migration for each component")
    print("4. Update imports and dependencies")
    print("5. Run tests to ensure everything works")

if __name__ == "__main__":
    main()
