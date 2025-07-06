#!/usr/bin/env python3
"""
Final verification test for all initialization fixes
"""
import sys

def test_all_fixes():
    """Test all the initialization fixes"""
    print("🧪 Final Verification Test - All Initialization Fixes")
    print("=" * 60)
    
    try:
        # Test 1: Config loading
        print("1️⃣ Testing config loading...")
        from src.config import config
        print(f"   ✅ Config loaded successfully")
        print(f"   ✅ LLM config: {len(config.llm_config)} keys")
        print(f"   ✅ App config: {len(config.app_config)} keys")
        
        # Test 2: FileHandler initialization  
        print("\n2️⃣ Testing FileHandler with proper params...")
        from src.utils.file_handler import FileHandler
        file_handler = FileHandler(
            upload_dir=config.app_config['upload_directory'],
            allowed_extensions=config.app_config['allowed_file_types'],
            max_size_mb=config.app_config['max_file_size_mb']
        )
        print("   ✅ FileHandler initialized successfully")
        
        # Test 3: RCAEngine with dictionary config
        print("\n3️⃣ Testing RCAEngine with proper config...")
        from src.core.analysis.rca_engine import RCAEngine
        rca_config = {
            **config.llm_config,
            'output_directory': config.app_config['output_directory']
        }
        rca_engine = RCAEngine(rca_config)
        print("   ✅ RCAEngine initialized successfully")
        
        # Test 4: Full RCAApp initialization
        print("\n4️⃣ Testing complete RCAApp initialization...")
        from src.ui.main_app import RCAApp
        app = RCAApp()
        print("   ✅ RCAApp initialized successfully")
        
        # Test 5: Main application import
        print("\n5️⃣ Testing main application setup...")
        from src.ui.main_app import create_app
        main_app = create_app()
        print("   ✅ Main application created successfully")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ FileHandler initialization fixed")
        print("✅ RCAEngine config initialization fixed") 
        print("✅ All components integrate properly")
        print("✅ Application ready to start!")
        print("\n🚀 You can now run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_fixes()
    sys.exit(0 if success else 1)
