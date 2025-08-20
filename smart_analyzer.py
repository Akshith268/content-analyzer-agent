#!/usr/bin/env python3
"""
🤖 AI CONTENT ANALYZER - UNIFIED INTERFACE
One simple interface with automatic learning and storage
"""

import os
import time
import json
import hashlib
import logging
import pymongo
import mysql.connector
import google.generativeai as genai
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    decision: str
    confidence: float
    reason: str
    sentiment: str
    risk_level: str
    processing_time: float
    patterns_used: int = 0
    learning_applied: bool = False

class SmartContentAnalyzer:
    """Unified AI Content Analyzer with automatic learning and storage"""
    
    def __init__(self):
        self.name = "🤖 Smart AI Content Analyzer"
        self.session_id = f"session_{int(time.time())}"
        self.analyses_count = 0
        
        print("🚀 Initializing Smart AI Content Analyzer...")
        
        # Load environment variables
        self._load_env()
        
        # Setup AI
        self._setup_ai()
        
        # Setup databases (automatic)
        self._setup_databases()
        
        # Load learning patterns
        self.learning_patterns = self._load_learning_patterns()
        
        print(f"✅ {self.name} ready!")
        print(f"🧠 Loaded {len(self.learning_patterns)} learning patterns")
        print("🗄️ Database storage: ENABLED")
        print("📊 Learning mode: ACTIVE")
        print("=" * 60)
    
    def _load_env(self):
        """Load environment variables from .env file"""
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
    
    def _setup_ai(self):
        """Setup Google Gemini AI"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("🔗 Connected to Gemini AI")
    
    def _setup_databases(self):
        """Setup MongoDB and MySQL connections"""
        try:
            # MongoDB connection
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client['contentanalyzer']  # Use existing database
            
            # MySQL connection (optional)
            try:
                self.mysql_connection = mysql.connector.connect(
                    host=os.getenv('MYSQL_HOST', 'localhost'),
                    user=os.getenv('MYSQL_USER', 'root'),
                    password=os.getenv('MYSQL_PASSWORD', '6305027175@Aa'),
                    database=os.getenv('MYSQL_DATABASE', 'content_analyzer')
                )
                self._ensure_database_tables()
                print("🗄️ Connected to MongoDB + MySQL")
            except Exception as mysql_error:
                logger.warning(f"MySQL connection failed: {mysql_error}")
                self.mysql_connection = None
                print("🗄️ Connected to MongoDB (MySQL optional)")
            
        except Exception as e:
            logger.error(f"⚠️ Database setup failed: {e}")
            self.mongo_db = None
            self.mysql_connection = None
            print("⚠️ Database storage disabled")
    
    def _ensure_database_tables(self):
        """Create necessary database tables"""
        if self.mysql_connection is not None:
            cursor = self.mysql_connection.cursor()
            
            # Create analysis_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100),
                    decision VARCHAR(20),
                    confidence FLOAT,
                    processing_time FLOAT,
                    patterns_used INT,
                    learning_applied BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create learning_patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content_features JSON,
                    decision VARCHAR(20),
                    confidence FLOAT,
                    success_count INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.mysql_connection.commit()
    
    def _load_learning_patterns(self):
        """Load existing learning patterns"""
        patterns = []
        if self.mongo_db is not None:
            try:
                # Load from learning_analyses collection
                learning_data = list(self.mongo_db.learning_analyses.find().limit(100))
                for data in learning_data:
                    if 'content_features' in data and 'base_decision' in data:
                        patterns.append({
                            'features': data['content_features'],
                            'decision': data['base_decision'],
                            'confidence': data.get('learned_confidence', 0.5)
                        })
                logger.info(f"📚 Loaded {len(patterns)} proven patterns")
            except Exception as e:
                logger.warning(f"Pattern loading failed: {e}")
        
        return patterns
    
    def analyze_content(self, content: str) -> AnalysisResult:
        """Analyze content with automatic learning and storage"""
        start_time = time.time()
        self.analyses_count += 1
        
        print(f"\n🔍 Analysis #{self.analyses_count}")
        print(f"📄 Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        # Extract content features for learning
        content_features = self._extract_features(content)
        
        # Get base AI decision
        base_decision = self._get_ai_decision(content)
        
        # Apply learning if patterns exist
        final_decision = self._apply_learning(base_decision, content_features)
        
        processing_time = time.time() - start_time
        
        # Create result
        result = AnalysisResult(
            decision=final_decision['decision'],
            confidence=final_decision['confidence'],
            reason=final_decision['reason'],
            sentiment=final_decision.get('sentiment', 'neutral'),
            risk_level=final_decision.get('risk_level', 'low'),
            processing_time=processing_time,
            patterns_used=len([p for p in self.learning_patterns if self._pattern_matches(p['features'], content_features)]),
            learning_applied=len(self.learning_patterns) > 0
        )
        
        # Store analysis results automatically
        self._store_analysis(content, content_features, result)
        
        # Update learning patterns automatically
        self._update_learning(content_features, result)
        
        return result
    
    def _extract_features(self, content: str) -> Dict:
        """Extract features from content for learning"""
        return {
            'length': len(content),
            'word_count': len(content.split()),
            'has_question': '?' in content,
            'has_exclamation': '!' in content,
            'is_caps': content.isupper(),
            'sentiment_keywords': [word.lower() for word in content.split() 
                                 if word.lower() in ['good', 'bad', 'great', 'terrible', 'love', 'hate', 'amazing', 'awful']]
        }
    
    def _get_ai_decision(self, content: str) -> Dict:
        """Get decision from AI"""
        try:
            prompt = f"""
            Analyze this content for safety and appropriateness:
            
            Content: "{content}"
            
            Provide analysis in this JSON format:
            {{
                "decision": "APPROVE|FLAG|REJECT",
                "confidence": 0.95,
                "reason": "detailed explanation",
                "sentiment": "positive|negative|neutral",
                "risk_level": "low|medium|high"
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_text = response_text[start:end]
                decision = json.loads(json_text)
                return decision
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {
                "decision": "FLAG",
                "confidence": 0.5,
                "reason": f"Analysis failed: {str(e)}",
                "sentiment": "neutral",
                "risk_level": "medium"
            }
    
    def _apply_learning(self, base_decision: Dict, content_features: Dict) -> Dict:
        """Apply learning patterns to improve decision"""
        if not self.learning_patterns:
            return base_decision
        
        # Find matching patterns
        matching_patterns = [p for p in self.learning_patterns 
                           if self._pattern_matches(p['features'], content_features)]
        
        if matching_patterns:
            # Calculate learning adjustment
            pattern_confidences = [p['confidence'] for p in matching_patterns]
            avg_pattern_confidence = sum(pattern_confidences) / len(pattern_confidences)
            
            # Apply learning boost
            learning_boost = min(0.1, len(matching_patterns) * 0.02)
            base_decision['confidence'] = min(1.0, base_decision['confidence'] + learning_boost)
            base_decision['reason'] += f" (Learning applied: {len(matching_patterns)} patterns)"
        
        return base_decision
    
    def _pattern_matches(self, pattern_features: Dict, content_features: Dict) -> bool:
        """Check if pattern matches current content"""
        # Simple similarity check
        similarity_score = 0
        total_features = 0
        
        for key in pattern_features:
            if key in content_features:
                total_features += 1
                if pattern_features[key] == content_features[key]:
                    similarity_score += 1
        
        return total_features > 0 and (similarity_score / total_features) > 0.5
    
    def _store_analysis(self, content: str, features: Dict, result: AnalysisResult):
        """Store analysis in databases"""
        try:
            # MongoDB storage
            if self.mongo_db is not None:
                document = {
                    'session_id': self.session_id,
                    'timestamp': datetime.now(timezone.utc),
                    'content': content,
                    'content_features': features,
                    'analysis_result': {
                        'decision': result.decision,
                        'confidence': result.confidence,
                        'reason': result.reason,
                        'sentiment': result.sentiment,
                        'risk_level': result.risk_level
                    },
                    'processing_time': result.processing_time,
                    'patterns_used': result.patterns_used,
                    'learning_applied': result.learning_applied
                }
                
                self.mongo_db.smart_analyses.insert_one(document)
            
            # MySQL storage
            if self.mysql_connection is not None:
                cursor = self.mysql_connection.cursor()
                cursor.execute("""
                    INSERT INTO analysis_metrics 
                    (session_id, decision, confidence, processing_time, patterns_used, learning_applied)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    self.session_id,
                    result.decision,
                    result.confidence,
                    result.processing_time,
                    result.patterns_used,
                    result.learning_applied
                ))
                self.mysql_connection.commit()
                
            print("💾 Analysis stored in database")
            
        except Exception as e:
            logger.error(f"Storage failed: {e}")
    
    def _update_learning(self, features: Dict, result: AnalysisResult):
        """Update learning patterns"""
        if self.mongo_db is not None:
            try:
                # Store learning data
                learning_document = {
                    'content_features': features,
                    'base_decision': result.decision,
                    'confidence': result.confidence,
                    'patterns_used': result.patterns_used,
                    'timestamp': datetime.now(timezone.utc)
                }
                
                self.mongo_db.learning_analyses.insert_one(learning_document)
                print("🧠 Learning pattern updated")
                
            except Exception as e:
                logger.error(f"Learning update failed: {e}")
    
    def display_result(self, result: AnalysisResult):
        """Display analysis result in a user-friendly format"""
        print(f"\n✅ DECISION: {result.decision}")
        print(f"🎯 CONFIDENCE: {result.confidence:.1%}")
        print(f"📝 REASON: {result.reason}")
        print(f"💭 SENTIMENT: {result.sentiment}")
        print(f"⚠️ RISK LEVEL: {result.risk_level}")
        print(f"⏱️ PROCESSING TIME: {result.processing_time:.2f} seconds")
        
        if result.learning_applied:
            print(f"🧠 LEARNING: {result.patterns_used} patterns applied")
        
        status_emoji = "✅" if result.decision == "APPROVE" else "⚠️" if result.decision == "FLAG" else "❌"
        status_text = "Safe for publication" if result.decision == "APPROVE" else "Needs review" if result.decision == "FLAG" else "Not recommended"
        print(f"🔍 STATUS: {status_emoji} {status_text}")
    
    def interactive_mode(self):
        """Run interactive analysis mode"""
        print(f"\n🎯 INTERACTIVE AI CONTENT ANALYZER")
        print("=" * 50)
        print("Type your content and get instant AI analysis")
        print("✨ Learning and storage happen automatically")
        print("Type 'quit' to exit, 'stats' for session statistics")
        print("-" * 50)
        
        while True:
            try:
                content = input("\n📝 Enter content to analyze: ").strip()
                
                if content.lower() in ['quit', 'exit', 'q']:
                    break
                elif content.lower() == 'stats':
                    self._show_stats()
                    continue
                elif not content:
                    print("⚠️ Please enter some content to analyze")
                    continue
                
                # Analyze content
                result = self.analyze_content(content)
                
                # Display result
                self.display_result(result)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        self._show_final_stats()
    
    def _show_stats(self):
        """Show current session statistics"""
        print(f"\n📊 SESSION STATISTICS:")
        print(f"   Total Analyses: {self.analyses_count}")
        print(f"   Learning Patterns: {len(self.learning_patterns)}")
        print(f"   Session ID: {self.session_id}")
        print(f"   Database Storage: {'✅ Active' if self.mongo_db is not None else '❌ Disabled'}")
    
    def _show_final_stats(self):
        """Show final session statistics"""
        print(f"\n👋 Session Complete!")
        print(f"\n📊 FINAL SESSION STATS:")
        print(f"   Total Analyses: {self.analyses_count}")
        print(f"   Learning Patterns: {len(self.learning_patterns)}")
        print(f"   Agent Name: {self.name}")
        print(f"   Database Storage: {'MongoDB + MySQL' if self.mysql_connection is not None else 'MongoDB Only' if self.mongo_db is not None else 'Disabled'}")
        print(f"   Status: Learning Complete")

def main():
    """Main function"""
    try:
        # Initialize analyzer
        analyzer = SmartContentAnalyzer()
        
        # Run interactive mode
        analyzer.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error starting analyzer: {e}")
        print("Please check your .env file and database connections")

if __name__ == "__main__":
    main()
