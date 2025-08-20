"""
🚀 AI Content Analyzer - Simple Launcher
Choose how you want to run the agent
"""

import os
import sys
import subprocess

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file if it exists"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env")
    else:
        print("⚠️  No .env file found. Please create one with your GOOGLE_API_KEY")

def print_banner():
    print("=" * 60)
    print("🤖 AI CONTENT ANALYZER")
    print("=" * 60)
    print("🧠 True Learning AI Agent")
    print("📊 Multiple Analysis Options") 
    print("🎯 Real Learning from Data")
    print("=" * 60)

def show_options():
    print("\n🎯 Choose how to run the agent:")
    print("1. � Simple Agent Demo (Recommended - Always Works)")
    print("2. �🧠 True Learning Agent Demo")
    print("3. 🤖 Original Production Agent") 
    print("4. 📊 Learning Proof Demo")
    print("5. 🌐 Web Dashboard (if dependencies available)")
    print("6. ❌ Exit")
    print("-" * 40)

def run_simple_agent():
    """Run the simple working agent"""
    print("\n🤖 Starting Simple Agent...")
    print("✅ Guaranteed to work - basic AI analysis")
    try:
        subprocess.run([sys.executable, "simple_agent.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def run_true_learning_agent():
    """Run the true learning agent"""
    print("\n🧠 Starting True Learning Agent...")
    print("📚 This agent actually learns from previous analyses")
    try:
        subprocess.run([sys.executable, "true_learning_agent.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def run_production_agent():
    """Run the original production agent"""
    print("\n🤖 Starting Production Agent...")
    print("📊 Database integration with basic learning")
    try:
        subprocess.run([sys.executable, "production_agent.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def run_learning_proof():
    """Run the learning proof demo"""
    print("\n📊 Starting Learning Proof Demo...")
    print("🎯 Shows difference between real vs fake learning")
    try:
        subprocess.run([sys.executable, "learning_proof.py"])
    except Exception as e:
        print(f"❌ Error: {e}")

def run_web_dashboard():
    """Try to run the web dashboard"""
    print("\n🌐 Starting Web Dashboard...")
    print("📊 Real-time analysis with beautiful interface")
    print("🔗 Will be available at: http://localhost:5000")
    
    try:
        # Check if flask is available
        import flask
        import flask_socketio
        subprocess.run([sys.executable, "web_dashboard.py"])
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install flask flask-socketio plotly")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print_banner()
    
    while True:
        show_options()
        
        try:
            choice = input("👉 Select option (1-6): ").strip()
            
            if choice == "1":
                run_simple_agent()
            elif choice == "2":
                run_true_learning_agent()
            elif choice == "3":
                run_production_agent()
            elif choice == "4":
                run_learning_proof()
            elif choice == "5":
                run_web_dashboard()
            elif choice == "6":
                print("👋 Thank you for using AI Content Analyzer!")
                break
            else:
                print("❌ Invalid option. Please choose 1-6.")
            
            input("\n⏸️ Press Enter to return to menu...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Load environment variables first
    load_env()
    main()
