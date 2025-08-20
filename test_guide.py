#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE AI CONTENT ANALYZER TESTING GUIDE
Test all features and verify learning capabilities
"""

def print_test_guide():
    print("🧪 AI CONTENT ANALYZER - TESTING GUIDE")
    print("=" * 60)
    
    print("\n🎯 TESTING OPTIONS:")
    print("1. 🚀 Quick Demo Test (5 minutes)")
    print("2. 🧠 Learning Behavior Test (10 minutes)")
    print("3. 📊 Database Storage Test (5 minutes)")
    print("4. 🔄 Interactive Mode Test (15 minutes)")
    print("5. 🏢 Production Features Test (15 minutes)")
    
    print("\n" + "=" * 60)
    
    choice = input("👉 Choose test type (1-5): ").strip()
    
    if choice == "1":
        quick_demo_test()
    elif choice == "2":
        learning_behavior_test()
    elif choice == "3":
        database_storage_test()
    elif choice == "4":
        interactive_mode_test()
    elif choice == "5":
        production_features_test()
    else:
        print("❌ Invalid choice. Try again.")

def quick_demo_test():
    """Quick 5-minute demo test"""
    print("\n🚀 QUICK DEMO TEST")
    print("=" * 40)
    print("📋 Steps to follow:")
    print("1. Run: python simple_launcher.py")
    print("2. Choose option 2: True Learning Agent Demo")
    print("3. Watch it analyze 5 sample texts")
    print("4. Verify learning patterns are applied")
    
    print("\n✅ Expected Results:")
    print("• Each analysis completes in 1-2 seconds")
    print("• Shows confidence scores (0.80-1.00)")
    print("• Displays 'Learning applied: X patterns'")
    print("• Shows 'Learning data saved to MongoDB'")
    print("• Final stats show pattern counts")
    
    print("\n🎯 Success Criteria:")
    print("• All 5 analyses complete without errors")
    print("• Learning patterns are used (5+ patterns)")
    print("• Data is saved to MongoDB successfully")

def learning_behavior_test():
    """Test learning behavior over time"""
    print("\n🧠 LEARNING BEHAVIOR TEST")
    print("=" * 40)
    print("📋 Test Procedure:")
    print("1. Run: python simple_launcher.py")
    print("2. Choose option 2: True Learning Agent")
    print("3. Choose mode 2: Interactive")
    print("4. Test with these specific texts:")
    
    test_texts = [
        "This product is absolutely amazing!",
        "You people are complete idiots!",
        "Dear Sir, I would like to inquire about your services.",
        "This is the best thing ever created!",
        "You guys are really stupid and annoying."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"   Test {i}: '{text}'")
    
    print("\n✅ Expected Learning Behavior:")
    print("• First similar text: Lower confidence, fewer patterns")
    print("• Repeated similar text: Higher confidence, more patterns")
    print("• Positive texts: APPROVE decision with 90%+ confidence")
    print("• Negative texts: REJECT/FLAG with confidence adjustment")
    print("• Learning boost values increase over time")
    
    print("\n🎯 Success Criteria:")
    print("• Confidence improves for similar content types")
    print("• Pattern usage increases over multiple tests")
    print("• Learning boost shows positive values")

def database_storage_test():
    """Test database storage verification"""
    print("\n📊 DATABASE STORAGE TEST")
    print("=" * 40)
    print("📋 Test Procedure:")
    print("1. Run: python check_dbs.py")
    print("2. Note current document counts")
    print("3. Run: python simple_launcher.py")
    print("4. Choose option 2: True Learning Agent")
    print("5. Run interactive mode with 3 different texts")
    print("6. Run: python check_dbs.py again")
    print("7. Verify document counts increased")
    
    print("\n✅ Expected Database Changes:")
    print("• learning_analyses: +3 documents")
    print("• agent_memories: +3 documents (if production agent)")
    print("• MySQL tables: Updated metrics")
    
    print("\n🎯 Success Criteria:")
    print("• Document counts increase after each analysis")
    print("• Data contains correct analysis results")
    print("• Timestamps are recent and accurate")

def interactive_mode_test():
    """Test interactive mode functionality"""
    print("\n🔄 INTERACTIVE MODE TEST")
    print("=" * 40)
    print("📋 Test Scenarios:")
    
    scenarios = [
        {"content": "Hey there! How are you doing today?", "expected": "APPROVE", "reason": "Friendly greeting"},
        {"content": "I hate this stupid product so much!", "expected": "REJECT/FLAG", "reason": "Negative sentiment"},
        {"content": "Please verify your password and credit card details", "expected": "REJECT", "reason": "Phishing attempt"},
        {"content": "Thank you for your excellent customer service", "expected": "APPROVE", "reason": "Positive feedback"},
        {"content": "This is absolutely terrible and worthless", "expected": "REJECT/FLAG", "reason": "Negative criticism"}
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test Scenario {i}:")
        print(f"   Input: '{scenario['content']}'")
        print(f"   Expected: {scenario['expected']}")
        print(f"   Reason: {scenario['reason']}")
    
    print("\n✅ Expected Interactive Behavior:")
    print("• Immediate analysis results")
    print("• Clear decision reasoning")
    print("• Learning patterns applied")
    print("• Confidence scores make sense")
    
    print("\n🎯 Success Criteria:")
    print("• All scenarios analyzed correctly")
    print("• Response time under 3 seconds")
    print("• Learning improves with similar content")

def production_features_test():
    """Test enterprise/production features"""
    print("\n🏢 PRODUCTION FEATURES TEST")
    print("=" * 40)
    print("📋 Advanced Feature Testing:")
    print("1. Run: python simple_launcher.py")
    print("2. Try option 3: Production Agent")
    print("3. Test batch processing capabilities")
    print("4. Check analytics dashboard")
    print("5. Verify database integration")
    
    print("\n✅ Production Features to Test:")
    print("• Multi-database storage (MongoDB + MySQL)")
    print("• Session management")
    print("• Performance metrics")
    print("• Error handling")
    print("• Analytics reporting")
    
    print("\n🎯 Enterprise Success Criteria:")
    print("• All databases store data correctly")
    print("• Session tracking works")
    print("• Performance metrics are accurate")
    print("• Error handling is graceful")

def run_quick_test():
    """Run a quick automated test"""
    print("\n🚀 RUNNING QUICK AUTOMATED TEST...")
    print("=" * 50)
    
    import subprocess
    import sys
    
    try:
        # Test 1: Check if launcher runs
        print("🧪 Test 1: Launcher functionality...")
        result = subprocess.run([sys.executable, "simple_launcher.py"], 
                              capture_output=True, text=True, timeout=5)
        if "AI CONTENT ANALYZER" in result.stdout:
            print("✅ Launcher works correctly")
        else:
            print("❌ Launcher issue detected")
        
        # Test 2: Check database connection
        print("🧪 Test 2: Database connection...")
        result = subprocess.run([sys.executable, "check_dbs.py"], 
                              capture_output=True, text=True, timeout=10)
        if "Collections:" in result.stdout:
            print("✅ Database connection working")
        else:
            print("❌ Database connection issue")
        
        print("\n🎯 QUICK TEST COMPLETE!")
        print("For full testing, use the manual test options above.")
        
    except Exception as e:
        print(f"❌ Automated test failed: {e}")
        print("Please run manual tests instead.")

if __name__ == "__main__":
    print_test_guide()
    
    print("\n" + "=" * 60)
    print("🚀 Want to run a quick automated test? (y/n): ", end="")
    if input().lower().startswith('y'):
        run_quick_test()
    
    print("\n✅ Happy testing! Your AI Content Analyzer is ready to impress! 🎉")
