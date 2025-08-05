#!/usr/bin/env python3
"""
Basic test to verify the Adventure Outfitters agent system is working.
This test doesn't require API keys and tests the basic structure.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        from src.common.logging import logger
        from src.common.message import Message
        from src.common.io import load_json
        from src.prompt.manage import TemplateManager
        from src.constants import BRAND_NAME
        
        print("✅ Core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test that data files can be loaded."""
    try:
        from src.common.io import load_json
        
        # Test loading customer orders
        orders = load_json('./data/customer_orders.json')
        if not orders:
            print("❌ Customer orders file is empty")
            return False
            
        # Test loading product catalog
        products = load_json('./data/product_catalog.json')
        if not products:
            print("❌ Product catalog file is empty")
            return False
            
        print("✅ Data files loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_message_creation():
    """Test that Message objects can be created."""
    try:
        from src.common.message import Message
        
        msg = Message(
            content="Test message",
            sender="TestAgent",
            recipient="Customer"
        )
        
        if msg.content != "Test message":
            print("❌ Message content not set correctly")
            return False
            
        print("✅ Message creation works")
        return True
    except Exception as e:
        print(f"❌ Message creation error: {e}")
        return False

def test_config_files():
    """Test that configuration files exist."""
    try:
        config_files = [
            './config/adventure_outfitters.yml',
            './config/templates/coordinator/route/system_instructions.txt',
            './config/templates/coordinator/route/user_instructions.txt',
            './config/templates/coordinator/consolidate/system_instructions.txt',
            './config/templates/coordinator/consolidate/user_instructions.txt',
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                print(f"❌ Missing config file: {config_file}")
                return False
                
        print("✅ Configuration files exist")
        return True
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def test_template_manager():
    """Test that TemplateManager can load templates."""
    try:
        from src.prompt.manage import TemplateManager
        
        tm = TemplateManager('./config/adventure_outfitters.yml')
        template = tm.create_template('coordinator', 'route')
        
        if 'system' not in template or 'user' not in template:
            print("❌ Template structure incorrect")
            return False
            
        if not template['system'] or not template['user']:
            print("❌ Template content is empty")
            return False
            
        print("✅ Template manager works")
        return True
    except Exception as e:
        print(f"❌ Template manager error: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🏔️ Adventure Outfitters Agent - Basic System Test 🏔️")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Data Loading Test", test_data_loading),
        ("Message Creation Test", test_message_creation),
        ("Config Files Test", test_config_files),
        ("Template Manager Test", test_template_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready to run.")
        print("🏔️ To start the chat interface:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print("   python -m src.chat_interface")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
