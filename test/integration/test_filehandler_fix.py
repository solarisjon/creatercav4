#!/usr/bin/env python3
"""
Test script to verify the FileHandler fix and application startup
"""
import sys
import traceback

def test_filehandler_fix():
    """Test if FileHandler initialization works correctly"""
    try:
        print("🧪 Testing FileHandler initialization...")
        from src.utils.file_handler import FileHandler
        from src.config import config
        
        # Test FileHandler with proper parameters
        file_handler = FileHandler(
            upload_dir=config.app_config['upload_directory'],
            allowed_extensions=config.app_config['allowed_file_types'],
            max_size_mb=config.app_config['max_file_size_mb']
        )
        print("✅ FileHandler initialization successful!")
        
        # Test RCAApp initialization
        print("🧪 Testing RCAApp initialization...")
        from src.ui.main_app import RCAApp
        app = RCAApp()
        print("✅ RCAApp initialization successful!")
        
        # Test RCAEngine initialization
        print("🧪 Testing RCAEngine...")
        from src.core.analysis.rca_engine import RCAEngine
        engine = RCAEngine(config)
        print("✅ RCAEngine initialization successful!")
        
        print("\n🎉 All components initialized successfully!")
        print("✅ The FileHandler fix is working correctly")
        print("✅ The application should now start without errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_filehandler_fix()
    sys.exit(0 if success else 1)
