"""
🧠 TRUE LEARNING AI AGENT - Enhanced with Real Learning
This agent actually uses historical data to improve decisions
"""

import os
import google.generativeai as genai
from datetime import datetime, timezone
import json
import hashlib
import time
import logging
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import pymongo
import mysql.connector
from mysql.connector import Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearningPattern:
    """Learning pattern extracted from historical data"""
    pattern_type: str
    pattern_features: Dict
    success_rate: float
    usage_count: int
    confidence_boost: float

class TrueLearningAgent:
    """AI Agent with REAL learning capabilities"""
    
    def __init__(self):
        self.name = "🧠 True Learning AI Agent"
        self.session_id = f"session_{int(time.time())}"
        
        # AI Setup
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Database connections
        self._setup_databases()
        
        # Learning system
        self.learned_patterns = []
        self.learning_enabled = True
        self.min_pattern_confidence = 0.7
        
        # Load existing patterns
        self._load_learning_patterns()
        
        print(f"🧠 {self.name} initialized")
        print(f"📚 Loaded {len(self.learned_patterns)} learning patterns")
        print(f"🎯 Learning mode: {'ACTIVE' if self.learning_enabled else 'DISABLED'}")
    
    def _setup_databases(self):
        """Setup database connections"""
        try:
            # MongoDB for detailed storage
            self.mongo_client = pymongo.MongoClient("mongodb+srv://akshith:1WRzwPw3fzuqPucv@cluster0.lb5yk0y.mongodb.net/")
            self.mongo_db = self.mongo_client.contentanalyzer
            
            # MySQL for structured learning data
            self.mysql_connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='6305027175@Aa',
                database='content_analyzer'
            )
            
            self._ensure_learning_tables()
            print("✅ Database connections established")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            self.mongo_db = None
            self.mysql_connection = None
    
    def _ensure_learning_tables(self):
        """Create enhanced learning tables"""
        if not self.mysql_connection:
            return
            
        cursor = self.mysql_connection.cursor()
        
        # Enhanced learning patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_patterns_v2 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pattern_id VARCHAR(64) UNIQUE,
                pattern_type VARCHAR(50),
                content_features JSON,
                historical_decisions JSON,
                success_rate FLOAT,
                confidence_boost FLOAT,
                usage_count INT DEFAULT 1,
                last_accuracy FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Decision feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content_hash VARCHAR(64),
                original_decision VARCHAR(20),
                original_confidence FLOAT,
                learned_decision VARCHAR(20),
                learned_confidence FLOAT,
                improvement_score FLOAT,
                pattern_ids JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.mysql_connection.commit()
        cursor.close()
    
    def _load_learning_patterns(self):
        """Load existing learning patterns from database"""
        if not self.mysql_connection:
            return
            
        try:
            cursor = self.mysql_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM learning_patterns_v2 
                WHERE success_rate >= %s AND usage_count >= 3
                ORDER BY success_rate DESC
            """, (self.min_pattern_confidence,))
            
            patterns = cursor.fetchall()
            
            for pattern_data in patterns:
                pattern = LearningPattern(
                    pattern_type=pattern_data['pattern_type'],
                    pattern_features=json.loads(pattern_data['content_features']),
                    success_rate=pattern_data['success_rate'],
                    usage_count=pattern_data['usage_count'],
                    confidence_boost=pattern_data['confidence_boost']
                )
                self.learned_patterns.append(pattern)
            
            cursor.close()
            logger.info(f"📚 Loaded {len(self.learned_patterns)} proven patterns")
            
        except Exception as e:
            logger.error(f"❌ Failed to load learning patterns: {e}")
    
    def analyze_with_learning(self, content: str) -> Dict:
        """Analyze content using REAL learning from historical data"""
        start_time = time.time()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        print(f"\n🧠 Learning Agent analyzing content...")
        print(f"📄 Content: {content[:100]}...")
        
        # Step 1: Extract content features
        content_features = self._extract_content_features(content)
        
        # Step 2: Find matching learned patterns  
        matching_patterns = self._find_matching_patterns(content_features)
        
        # Step 3: Get base AI decision
        base_decision = self._get_base_ai_decision(content)
        
        # Step 4: Apply learning adjustments
        learned_decision = self._apply_learning(base_decision, matching_patterns, content_features)
        
        # Step 5: Save learning data
        processing_time = time.time() - start_time
        self._save_learning_data(content, content_hash, base_decision, learned_decision, matching_patterns, processing_time)
        
        # Step 6: Update patterns based on this analysis
        self._update_learning_patterns(content_features, learned_decision, matching_patterns)
        
        print(f"✅ Learning analysis completed in {processing_time:.2f} seconds")
        
        return {
            "content_hash": content_hash,
            "base_decision": base_decision,
            "learned_decision": learned_decision,
            "learning_applied": len(matching_patterns) > 0,
            "matching_patterns": len(matching_patterns),
            "learning_boost": learned_decision.get('confidence', 0) - base_decision.get('confidence', 0),
            "processing_time": processing_time
        }
    
    def _extract_content_features(self, content: str) -> Dict:
        """Extract key features from content for pattern matching"""
        return {
            "length": len(content),
            "word_count": len(content.split()),
            "has_urls": "http" in content.lower(),
            "has_email": "@" in content,
            "has_phone": any(char.isdigit() for char in content),
            "has_caps": content.isupper(),
            "has_exclamation": "!" in content,
            "has_question": "?" in content,
            "sentiment_keywords": self._count_sentiment_keywords(content),
            "risk_keywords": self._count_risk_keywords(content),
            "professional_tone": self._assess_professional_tone(content)
        }
    
    def _count_sentiment_keywords(self, content: str) -> Dict:
        """Count sentiment indicator keywords"""
        positive_words = ["great", "excellent", "amazing", "wonderful", "fantastic", "love", "awesome"]
        negative_words = ["terrible", "awful", "hate", "horrible", "disgusting", "worst", "stupid"]
        
        content_lower = content.lower()
        return {
            "positive_count": sum(1 for word in positive_words if word in content_lower),
            "negative_count": sum(1 for word in negative_words if word in content_lower)
        }
    
    def _count_risk_keywords(self, content: str) -> Dict:
        """Count risk indicator keywords"""
        financial_risk = ["money", "investment", "loan", "credit", "bank", "financial"]
        legal_risk = ["lawsuit", "legal", "court", "sue", "attorney", "law"]
        toxic_risk = ["idiot", "stupid", "hate", "kill", "die", "moron"]
        
        content_lower = content.lower()
        return {
            "financial_risk": sum(1 for word in financial_risk if word in content_lower),
            "legal_risk": sum(1 for word in legal_risk if word in content_lower),
            "toxic_risk": sum(1 for word in toxic_risk if word in content_lower)
        }
    
    def _assess_professional_tone(self, content: str) -> float:
        """Assess how professional the content tone is"""
        professional_indicators = ["please", "thank you", "sincerely", "regards", "respectfully"]
        casual_indicators = ["hey", "lol", "omg", "wtf", "gonna", "wanna"]
        
        content_lower = content.lower()
        professional_score = sum(1 for word in professional_indicators if word in content_lower)
        casual_score = sum(1 for word in casual_indicators if word in content_lower)
        
        total_words = len(content.split())
        if total_words == 0:
            return 0.5
            
        return min(1.0, max(0.0, (professional_score - casual_score) / total_words + 0.5))
    
    def _find_matching_patterns(self, content_features: Dict) -> List[LearningPattern]:
        """Find learned patterns that match current content"""
        matching_patterns = []
        
        for pattern in self.learned_patterns:
            similarity_score = self._calculate_pattern_similarity(content_features, pattern.pattern_features)
            
            # If similarity is high enough, consider it a match
            if similarity_score >= 0.7:  # 70% similarity threshold
                matching_patterns.append(pattern)
        
        # Sort by success rate (best patterns first)
        matching_patterns.sort(key=lambda p: p.success_rate, reverse=True)
        
        logger.info(f"🔍 Found {len(matching_patterns)} matching learned patterns")
        return matching_patterns
    
    def _calculate_pattern_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two feature sets"""
        matching_features = 0
        total_features = 0
        
        for key in features1:
            if key in features2:
                total_features += 1
                
                # Handle different types of features
                if isinstance(features1[key], dict) and isinstance(features2[key], dict):
                    # For nested dicts (like sentiment_keywords)
                    sub_similarity = self._calculate_pattern_similarity(features1[key], features2[key])
                    matching_features += sub_similarity
                elif isinstance(features1[key], (int, float)) and isinstance(features2[key], (int, float)):
                    # For numeric features, check if they're in similar range
                    if features1[key] == 0 and features2[key] == 0:
                        matching_features += 1
                    elif features1[key] > 0 and features2[key] > 0:
                        ratio = min(features1[key], features2[key]) / max(features1[key], features2[key])
                        matching_features += ratio
                elif features1[key] == features2[key]:
                    # For boolean and exact matches
                    matching_features += 1
        
        return matching_features / total_features if total_features > 0 else 0
    
    def _get_base_ai_decision(self, content: str) -> Dict:
        """Get base decision from AI without learning"""
        prompt = f"""
        Analyze this content for approval:
        
        Content: "{content}"
        
        Provide analysis in JSON format:
        {{
            "decision": "APPROVE|FLAG|REJECT",
            "confidence": 0.0-1.0,
            "reasoning": "explanation",
            "risk_factors": ["factor1", "factor2"],
            "sentiment": "positive|negative|neutral"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            decision = self._parse_ai_response(response.text)
            return decision
        except Exception as e:
            logger.error(f"❌ Base AI decision failed: {e}")
            return {
                "decision": "FLAG",
                "confidence": 0.5,
                "reasoning": f"Error: {str(e)}",
                "risk_factors": ["analysis_error"],
                "sentiment": "neutral"
            }
    
    def _apply_learning(self, base_decision: Dict, matching_patterns: List[LearningPattern], content_features: Dict) -> Dict:
        """Apply learned patterns to improve the base decision"""
        if not matching_patterns:
            return base_decision.copy()
        
        learned_decision = base_decision.copy()
        
        # Calculate learning adjustments
        confidence_adjustments = []
        decision_votes = []
        
        for pattern in matching_patterns:
            # Get historical decisions for this pattern type
            historical_decisions = self._get_pattern_historical_decisions(pattern)
            
            if historical_decisions:
                # Most common decision for this pattern
                most_common_decision = max(set(historical_decisions), key=historical_decisions.count)
                decision_votes.append(most_common_decision)
                
                # Confidence boost based on pattern success rate
                confidence_boost = pattern.confidence_boost * pattern.success_rate
                confidence_adjustments.append(confidence_boost)
        
        # Apply learning adjustments
        if decision_votes:
            # Check if learned patterns suggest different decision
            learned_decision_vote = max(set(decision_votes), key=decision_votes.count)
            vote_strength = decision_votes.count(learned_decision_vote) / len(decision_votes)
            
            # If learned patterns strongly suggest different decision, consider changing
            if learned_decision_vote != base_decision["decision"] and vote_strength >= 0.7:
                learned_decision["decision"] = learned_decision_vote
                learned_decision["reasoning"] += f" [LEARNING: Historical patterns suggest {learned_decision_vote}]"
        
        # Apply confidence adjustments
        if confidence_adjustments:
            avg_confidence_boost = np.mean(confidence_adjustments)
            new_confidence = min(1.0, base_decision.get("confidence", 0.5) + avg_confidence_boost)
            learned_decision["confidence"] = new_confidence
            learned_decision["reasoning"] += f" [LEARNING: +{avg_confidence_boost:.2f} confidence from patterns]"
        
        # Add learning metadata
        learned_decision["learning_applied"] = True
        learned_decision["patterns_used"] = len(matching_patterns)
        learned_decision["confidence_boost"] = learned_decision.get("confidence", 0) - base_decision.get("confidence", 0)
        
        logger.info(f"🧠 Learning applied: {len(matching_patterns)} patterns, confidence boost: {learned_decision.get('confidence_boost', 0):.2f}")
        
        return learned_decision
    
    def _get_pattern_historical_decisions(self, pattern: LearningPattern) -> List[str]:
        """Get historical decisions for a specific pattern"""
        if not self.mysql_connection:
            return []
            
        try:
            cursor = self.mysql_connection.cursor()
            cursor.execute("""
                SELECT learned_decision FROM decision_feedback 
                WHERE JSON_CONTAINS(pattern_ids, %s)
                ORDER BY timestamp DESC LIMIT 50
            """, (json.dumps(pattern.pattern_type),))
            
            results = cursor.fetchall()
            cursor.close()
            
            return [result[0] for result in results if result[0]]
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical decisions: {e}")
            return []
    
    def _save_learning_data(self, content: str, content_hash: str, base_decision: Dict, learned_decision: Dict, matching_patterns: List[LearningPattern], processing_time: float):
        """Save analysis data for future learning"""
        
        # Save to MongoDB for detailed storage
        if self.mongo_db is not None:
            try:
                learning_document = {
                    "content_hash": content_hash,
                    "timestamp": datetime.now(timezone.utc),
                    "session_id": self.session_id,
                    "base_decision": base_decision,
                    "learned_decision": learned_decision,
                    "matching_patterns_count": len(matching_patterns),
                    "processing_time": processing_time,
                    "learning_metadata": {
                        "patterns_applied": [p.pattern_type for p in matching_patterns],
                        "confidence_improvement": learned_decision.get("confidence", 0) - base_decision.get("confidence", 0)
                    }
                }
                
                self.mongo_db.learning_analyses.insert_one(learning_document)
                logger.info("📚 Learning data saved to MongoDB")
                
            except Exception as e:
                logger.error(f"❌ MongoDB learning save failed: {e}")
        
        # Save feedback to MySQL
        if self.mysql_connection:
            try:
                cursor = self.mysql_connection.cursor()
                
                improvement_score = learned_decision.get("confidence", 0) - base_decision.get("confidence", 0)
                pattern_ids = [p.pattern_type for p in matching_patterns]
                
                cursor.execute("""
                    INSERT INTO decision_feedback 
                    (content_hash, original_decision, original_confidence, 
                     learned_decision, learned_confidence, improvement_score, pattern_ids)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    content_hash,
                    base_decision.get("decision"),
                    base_decision.get("confidence", 0),
                    learned_decision.get("decision"),
                    learned_decision.get("confidence", 0),
                    improvement_score,
                    json.dumps(pattern_ids)
                ))
                
                self.mysql_connection.commit()
                cursor.close()
                
            except Exception as e:
                logger.error(f"❌ MySQL feedback save failed: {e}")
    
    def _update_learning_patterns(self, content_features: Dict, learned_decision: Dict, matching_patterns: List[LearningPattern]):
        """Update learning patterns based on new analysis"""
        if not self.mysql_connection:
            return
            
        try:
            # Create new pattern if none matched
            if not matching_patterns and learned_decision.get("confidence", 0) >= 0.8:
                self._create_new_pattern(content_features, learned_decision)
            
            # Update existing patterns
            for pattern in matching_patterns:
                self._update_existing_pattern(pattern, learned_decision)
                
        except Exception as e:
            logger.error(f"❌ Pattern update failed: {e}")
    
    def _create_new_pattern(self, content_features: Dict, decision: Dict):
        """Create a new learning pattern"""
        pattern_id = hashlib.sha256(json.dumps(content_features, sort_keys=True).encode()).hexdigest()[:16]
        
        cursor = self.mysql_connection.cursor()
        cursor.execute("""
            INSERT INTO learning_patterns_v2 
            (pattern_id, pattern_type, content_features, historical_decisions, 
             success_rate, confidence_boost, usage_count, last_accuracy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE usage_count = usage_count + 1
        """, (
            pattern_id,
            decision.get("decision", "UNKNOWN"),
            json.dumps(content_features),
            json.dumps([decision.get("decision")]),
            decision.get("confidence", 0.5),
            0.1,  # Initial confidence boost
            1,
            decision.get("confidence", 0.5)
        ))
        
        self.mysql_connection.commit()
        cursor.close()
        
        logger.info(f"🆕 Created new learning pattern: {pattern_id}")
    
    def _update_existing_pattern(self, pattern: LearningPattern, decision: Dict):
        """Update an existing learning pattern with new data"""
        # This would update success rates, confidence boosts, etc.
        # Based on how well the pattern performed
        pass
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response text into structured data"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "decision": "FLAG",
                    "confidence": 0.5,
                    "reasoning": response_text[:200],
                    "risk_factors": ["parsing_error"],
                    "sentiment": "neutral"
                }
        except Exception as e:
            return {
                "decision": "ERROR",
                "confidence": 0.0,
                "reasoning": f"Parse error: {str(e)}",
                "risk_factors": ["parse_error"],
                "sentiment": "neutral"
            }
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning system"""
        stats = {
            "total_patterns": len(self.learned_patterns),
            "learning_enabled": self.learning_enabled,
            "high_confidence_patterns": len([p for p in self.learned_patterns if p.success_rate >= 0.9]),
            "pattern_types": {}
        }
        
        # Group patterns by type
        for pattern in self.learned_patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in stats["pattern_types"]:
                stats["pattern_types"][pattern_type] = 0
            stats["pattern_types"][pattern_type] += 1
        
        return stats

# Demo function
def demo_true_learning():
    """Demo the true learning capabilities"""
    agent = TrueLearningAgent()
    
    test_contents = [
        "This product is absolutely amazing! I love it so much!",
        "You people are complete idiots and don't know what you're talking about.",
        "Dear Sir/Madam, I would like to inquire about your services. Thank you.",
        "Hey lol this is so funny omg I can't even...",
        "Please send your credit card number and SSN for verification purposes."
    ]
    
    print("\n🧠 TRUE LEARNING AGENT DEMO")
    print("=" * 50)
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n--- Test {i} ---")
        print(f"Content: {content}")
        
        result = agent.analyze_with_learning(content)
        
        base = result["base_decision"]
        learned = result["learned_decision"]
        
        print(f"🤖 Base AI Decision: {base.get('decision')} (confidence: {base.get('confidence', 0):.2f})")
        print(f"🧠 Learned Decision: {learned.get('decision')} (confidence: {learned.get('confidence', 0):.2f})")
        print(f"📈 Learning Boost: {result.get('learning_boost', 0):.2f}")
        print(f"🎯 Patterns Used: {result.get('matching_patterns', 0)}")
        print(f"⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
    
    # Show learning stats
    print(f"\n📊 LEARNING SYSTEM STATS:")
    stats = agent.get_learning_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    demo_true_learning()
