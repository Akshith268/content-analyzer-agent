"""
🤖 Simple AI Content Analyzer - Working Demo
A simplified version that's guaranteed to work
"""

import google.generativeai as genai
import hashlib
import json
import time
import os
from datetime import datetime

class SimpleContentAgent:
    """Simple working AI content analyzer"""
    
    def __init__(self):
        self.name = "🤖 Simple AI Content Analyzer"
        self.analyses_count = 0
        
        # Configure Gemini AI
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print(f"✅ {self.name} initialized")
        print("🔗 Connected to Gemini AI")
        print("🎯 Ready for content analysis")
    
    def analyze_content(self, content: str) -> dict:
        """Analyze content with AI"""
        start_time = time.time()
        self.analyses_count += 1
        
        print(f"\n🔍 Analysis #{self.analyses_count}")
        print(f"📄 Content: {content[:80]}...")
        
        # Create analysis prompt
        prompt = f"""
        Analyze this content for safety and appropriateness:
        
        Content: "{content}"
        
        Please provide your analysis in JSON format:
        {{
            "decision": "APPROVE|FLAG|REJECT",
            "confidence": 0.0-1.0,
            "reason": "explanation of decision",
            "sentiment": "positive|negative|neutral",
            "risk_level": "low|medium|high",
            "concerns": ["list", "of", "concerns"]
        }}
        """
        
        try:
            # Get AI analysis
            response = self.model.generate_content(prompt)
            analysis = self._parse_response(response.text)
            
            # Add metadata
            processing_time = time.time() - start_time
            analysis["processing_time"] = processing_time
            analysis["timestamp"] = datetime.now().isoformat()
            analysis["content_hash"] = hashlib.sha256(content.encode()).hexdigest()[:8]
            
            # Display results
            self._display_results(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "decision": "ERROR",
                "confidence": 0.0,
                "reason": f"Analysis error: {str(e)}",
                "processing_time": time.time() - start_time
            }
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse AI response into structured data"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                return {
                    "decision": "FLAG",
                    "confidence": 0.5,
                    "reason": response_text[:200],
                    "sentiment": "neutral",
                    "risk_level": "medium",
                    "concerns": ["Unable to parse detailed analysis"]
                }
        except Exception as e:
            return {
                "decision": "ERROR",
                "confidence": 0.0,
                "reason": f"Parse error: {str(e)}",
                "sentiment": "unknown",
                "risk_level": "high",
                "concerns": ["Response parsing failed"]
            }
    
    def _display_results(self, analysis: dict):
        """Display analysis results in a nice format"""
        decision = analysis.get("decision", "UNKNOWN")
        confidence = analysis.get("confidence", 0.0)
        reason = analysis.get("reason", "No reason provided")
        
        # Color coding for decisions
        if decision == "APPROVE":
            emoji = "✅"
            color_desc = "Safe for publication"
        elif decision == "FLAG":
            emoji = "⚠️"
            color_desc = "Requires review"
        elif decision == "REJECT":
            emoji = "❌"
            color_desc = "Not recommended"
        else:
            emoji = "❓"
            color_desc = "Unknown status"
        
        print(f"\n{emoji} DECISION: {decision}")
        print(f"🎯 CONFIDENCE: {confidence:.1%}")
        print(f"📝 REASON: {reason}")
        print(f"💭 SENTIMENT: {analysis.get('sentiment', 'N/A')}")
        print(f"⚠️ RISK LEVEL: {analysis.get('risk_level', 'N/A')}")
        
        if analysis.get("concerns"):
            print(f"🚨 CONCERNS: {', '.join(analysis['concerns'])}")
        
        print(f"⏱️ PROCESSING TIME: {analysis.get('processing_time', 0):.2f} seconds")
        print(f"🔍 STATUS: {color_desc}")
    
    def interactive_mode(self):
        """Run interactive analysis mode"""
        print(f"\n🎯 INTERACTIVE MODE STARTED")
        print("Type 'quit' to exit, 'demo' for sample analyses")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n📝 Enter content to analyze: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using the analyzer!")
                    break
                elif user_input.lower() == 'demo':
                    self._run_demo()
                elif user_input:
                    self.analyze_content(user_input)
                else:
                    print("⚠️ Please enter some content to analyze")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _run_demo(self):
        """Run a demo with sample content"""
        demo_content = [
            "I love this amazing product! It's fantastic!",
            "This service is terrible and the staff are idiots.",
            "Please send me your credit card number and social security number.",
            "Thank you for your excellent customer service. Very professional.",
            "You guys are so stupid, I hate everything about this company."
        ]
        
        print("\n🎬 RUNNING DEMO ANALYSES")
        print("=" * 50)
        
        for i, content in enumerate(demo_content, 1):
            print(f"\n--- Demo {i}/5 ---")
            self.analyze_content(content)
            time.sleep(1)  # Brief pause between analyses
        
        print(f"\n✅ Demo completed! Analyzed {len(demo_content)} samples")
    
    def get_stats(self):
        """Get analyzer statistics"""
        return {
            "total_analyses": self.analyses_count,
            "agent_name": self.name,
            "ai_model": "Gemini 1.5-Flash",
            "status": "Active"
        }

def main():
    """Main function"""
    print("🤖 SIMPLE AI CONTENT ANALYZER")
    print("=" * 50)
    
    try:
        # Initialize agent
        agent = SimpleContentAgent()
        
        # Show options
        print(f"\n🎯 CHOOSE MODE:")
        print("1. 🎬 Run Demo (5 sample analyses)")
        print("2. 💬 Interactive Mode (analyze your content)")
        print("3. ❌ Exit")
        
        choice = input("\n👉 Select mode (1-3): ").strip()
        
        if choice == "1":
            agent._run_demo()
        elif choice == "2":
            agent.interactive_mode()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice, running demo...")
            agent._run_demo()
        
        # Show final stats
        stats = agent.get_stats()
        print(f"\n📊 FINAL STATS:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("💡 Make sure you have internet connection for Gemini AI")

if __name__ == "__main__":
    main()
