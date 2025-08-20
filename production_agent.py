"""
Production-Ready AI Agent with Database Storage
MongoDB Atlas + MySQL Integration
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import google.generativeai as genai

# Database imports
from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
genai.configure(api_key=api_key)

@dataclass
class AgentMemory:
    """Enhanced memory structure for production"""
    id: str
    timestamp: datetime
    content_hash: str
    content_snippet: str
    analysis_result: Dict
    reasoning_process: List[str]
    decision_confidence: float
    processing_time: float
    agent_version: str
    session_id: str
    user_feedback: Optional[str] = None
    lessons_learned: Optional[str] = None

class DatabaseManager:
    """Production database manager for MongoDB and MySQL"""
    
    def __init__(self):
        # MongoDB Atlas connection
        self.mongo_uri = "mongodb+srv://akshith:1WRzwPw3fzuqPucv@cluster0.lb5yk0y.mongodb.net/contentanalyzer?retryWrites=true&w=majority"
        self.mongo_client = None
        self.mongo_db = None
        
        # MySQL connection details
        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '6305027175@Aa',
            'database': 'content_analyzer'
        }
        self.mysql_connection = None
        
        # Initialize connections
        self.connect_databases()
        self.setup_schemas()
    
    def connect_databases(self):
        """Establish database connections"""
        try:
            # MongoDB Atlas connection
            self.mongo_client = MongoClient(self.mongo_uri)
            self.mongo_db = self.mongo_client['contentanalyzer']
            
            # Test MongoDB connection
            self.mongo_client.admin.command('ping')
            logger.info("✅ MongoDB Atlas connected successfully")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.mongo_client = None
        
        try:
            # MySQL connection
            self.mysql_connection = mysql.connector.connect(**self.mysql_config)
            
            if self.mysql_connection.is_connected():
                logger.info("✅ MySQL connected successfully")
                
        except Error as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            # Try to create database if it doesn't exist
            try:
                temp_config = self.mysql_config.copy()
                del temp_config['database']
                temp_conn = mysql.connector.connect(**temp_config)
                cursor = temp_conn.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS content_analyzer")
                temp_conn.commit()
                cursor.close()
                temp_conn.close()
                logger.info("📚 Created content_analyzer database")
                
                # Reconnect with database
                self.mysql_connection = mysql.connector.connect(**self.mysql_config)
                logger.info("✅ MySQL connected after database creation")
                
            except Error as create_error:
                logger.error(f"❌ Failed to create database: {create_error}")
                self.mysql_connection = None
    
    def setup_schemas(self):
        """Set up database schemas"""
        self.setup_mysql_schema()
        self.setup_mongodb_collections()
    
    def setup_mysql_schema(self):
        """Create MySQL tables if they don't exist"""
        if not self.mysql_connection:
            return
            
        try:
            cursor = self.mysql_connection.cursor()
            
            # Agent sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id VARCHAR(36) PRIMARY KEY,
                    agent_name VARCHAR(100) NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    total_analyses INT DEFAULT 0,
                    avg_confidence FLOAT DEFAULT 0.0,
                    performance_score FLOAT DEFAULT 0.0
                )
            """)
            
            # Content analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_analyses (
                    id VARCHAR(36) PRIMARY KEY,
                    session_id VARCHAR(36),
                    content_hash VARCHAR(64) NOT NULL,
                    decision ENUM('APPROVE', 'FLAG', 'REJECT') NOT NULL,
                    confidence FLOAT NOT NULL,
                    risk_level ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
                    processing_time FLOAT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(36),
                    metric_name VARCHAR(50) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
                )
            """)
            
            # Learning patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    pattern_type VARCHAR(50) NOT NULL,
                    pattern_data JSON NOT NULL,
                    confidence_score FLOAT NOT NULL,
                    usage_count INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            self.mysql_connection.commit()
            cursor.close()
            logger.info("📋 MySQL schema setup completed")
            
        except Error as e:
            logger.error(f"❌ MySQL schema setup failed: {e}")
    
    def setup_mongodb_collections(self):
        """Set up MongoDB collections and indexes"""
        if self.mongo_db is None:
            return
            
        try:
            # Create collections
            collections = [
                'agent_memories',
                'reasoning_processes', 
                'context_analyses',
                'learning_data',
                'user_interactions'
            ]
            
            for collection_name in collections:
                if collection_name not in self.mongo_db.list_collection_names():
                    self.mongo_db.create_collection(collection_name)
            
            # Create indexes for performance
            self.mongo_db.agent_memories.create_index([("timestamp", -1)])
            self.mongo_db.agent_memories.create_index([("content_hash", 1)])
            self.mongo_db.agent_memories.create_index([("session_id", 1)])
            
            logger.info("🗂️ MongoDB collections and indexes setup completed")
            
        except Exception as e:
            logger.error(f"❌ MongoDB setup failed: {e}")

class ProductionContentAgent:
    """Production-ready AI Content Analysis Agent with Database Storage"""
    
    def __init__(self):
        self.name = "ContentGuardian-Pro"
        self.version = "2.0.0"
        self.session_id = self._generate_session_id()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize Gemini AI
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Agent state
        self.performance_metrics = {
            "accuracy": 0.85,
            "false_positives": 0.12,
            "false_negatives": 0.08,
            "user_satisfaction": 0.78,
            "avg_processing_time": 2.1
        }
        
        # Start new session
        self._start_session()
        
        print(f"🤖 {self.name} v{self.version} Initialized")
        print(f"📊 Session ID: {self.session_id}")
        print(f"🗄️ Database: {'✅ Connected' if self.db_manager.mongo_client and self.db_manager.mysql_connection else '❌ Offline Mode'}")
    
    def _generate_session_id(self):
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.md5(f"{self.name}-{timestamp}".encode()).hexdigest()[:12]
    
    def _start_session(self):
        """Start a new agent session"""
        if not self.db_manager.mysql_connection:
            return
            
        try:
            cursor = self.db_manager.mysql_connection.cursor()
            cursor.execute("""
                INSERT INTO agent_sessions (id, agent_name, start_time)
                VALUES (%s, %s, %s)
            """, (self.session_id, self.name, datetime.now()))
            
            self.db_manager.mysql_connection.commit()
            cursor.close()
            logger.info(f"📝 Session {self.session_id} started")
            
        except Error as e:
            logger.error(f"❌ Failed to start session: {e}")
    
    def analyze_content_production(self, content: str, context: Dict = None) -> Dict:
        """Production-ready content analysis with full database integration"""
        start_time = time.time()
        
        print(f"\n🔍 {self.name} analyzing content...")
        print(f"📄 Content: {content[:100]}...")
        
        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if we've analyzed this content before
        previous_analysis = self._get_previous_analysis(content_hash)
        if previous_analysis:
            print("🔄 Found previous analysis, using cached result")
            return previous_analysis
        
        try:
            # Step 1: Context analysis with AI
            context_analysis = self._analyze_context_production(content, context)
            
            # Step 2: Multi-step reasoning
            reasoning_steps = self._reasoning_process_production(content, context_analysis)
            
            # Step 3: AI decision making
            decision = self._make_intelligent_decision_production(content, reasoning_steps)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            decision['processing_time'] = processing_time
            
            # Step 4: Save to databases
            self._save_analysis_to_databases(content, content_hash, decision, reasoning_steps, processing_time)
            
            # Step 5: Update learning patterns
            self._update_learning_patterns(content, decision, reasoning_steps)
            
            # Step 6: Update performance metrics
            self._update_performance_metrics(decision, processing_time)
            
            print(f"✅ Analysis completed in {processing_time:.2f} seconds")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {
                "decision": "FLAG",
                "confidence": 0.0,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def _get_previous_analysis(self, content_hash: str) -> Optional[Dict]:
        """Check for previous analysis in MongoDB"""
        if self.db_manager.mongo_db is None:
            return None
            
        try:
            result = self.db_manager.mongo_db.agent_memories.find_one(
                {"content_hash": content_hash},
                sort=[("timestamp", -1)]
            )
            
            if result and result.get('analysis_result'):
                return result['analysis_result']
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve previous analysis: {e}")
        
        return None
    
    def _analyze_context_production(self, content: str, context: Dict = None) -> Dict:
        """Production context analysis with error handling"""
        prompt = f"""
        As an expert content analyst, analyze this content's context:
        
        Content: "{content}"
        Context: {context or "None"}
        
        Provide analysis in JSON format:
        {{
            "content_type": "social_media|business|news|review|comment|other",
            "audience_level": "general|professional|academic|children",
            "cultural_sensitivity": "low|medium|high",
            "risk_factors": ["list", "of", "potential", "risks"],
            "context_score": 0.0-1.0
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self._parse_ai_response(response.text)
            
            # Save context analysis to MongoDB
            if self.db_manager.mongo_db is not None:
                self.db_manager.mongo_db.context_analyses.insert_one({
                    "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                    "analysis": analysis,
                    "timestamp": datetime.now(timezone.utc),
                    "session_id": self.session_id
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Context analysis failed: {e}")
            return {
                "content_type": "unknown",
                "context_score": 0.5,
                "error": str(e)
            }
    
    def _reasoning_process_production(self, content: str, context_analysis: Dict) -> List[str]:
        """Production reasoning with database storage"""
        prompt = f"""
        As {self.name}, provide step-by-step reasoning for this content:
        
        Content: "{content}"
        Context: {json.dumps(context_analysis, indent=2)}
        
        My performance metrics: {self.performance_metrics}
        
        Provide 5 clear reasoning steps as a numbered list.
        """
        
        try:
            response = self.model.generate_content(prompt)
            reasoning_text = response.text
            
            # Extract reasoning steps
            steps = []
            for line in reasoning_text.split('\n'):
                if line.strip() and (line.strip()[0].isdigit() or line.startswith('-')):
                    steps.append(line.strip())
            
            # Save reasoning to MongoDB
            if self.db_manager.mongo_db is not None:
                self.db_manager.mongo_db.reasoning_processes.insert_one({
                    "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                    "reasoning_steps": steps,
                    "timestamp": datetime.now(timezone.utc),
                    "session_id": self.session_id
                })
            
            return steps
            
        except Exception as e:
            logger.error(f"❌ Reasoning failed: {e}")
            return ["Error in reasoning process", f"Technical issue: {str(e)}"]
    
    def _make_intelligent_decision_production(self, content: str, reasoning_steps: List[str]) -> Dict:
        """Production decision making with comprehensive data"""
        prompt = f"""
        As {self.name}, make a final decision about this content:
        
        Content: "{content}"
        Reasoning: {chr(10).join(f"{i+1}. {step}" for i, step in enumerate(reasoning_steps))}
        
        My current performance:
        - Accuracy: {self.performance_metrics['accuracy']:.2f}
        - False Positive Rate: {self.performance_metrics['false_positives']:.2f}
        
        Provide decision in JSON format:
        {{
            "decision": "APPROVE|FLAG|REJECT",
            "confidence": 0.0-1.0,
            "risk_level": "LOW|MEDIUM|HIGH", 
            "key_concerns": ["concern1", "concern2"],
            "recommended_actions": ["action1", "action2"],
            "explanation": "detailed explanation",
            "ai_reasoning": "why this decision",
            "confidence_factors": ["factor1", "factor2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            decision = self._parse_ai_response(response.text)
            
            # Ensure required fields
            decision.setdefault('decision', 'FLAG')
            decision.setdefault('confidence', 0.5)
            decision.setdefault('risk_level', 'MEDIUM')
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Decision making failed: {e}")
            return {
                "decision": "FLAG",
                "confidence": 0.0,
                "risk_level": "HIGH",
                "explanation": f"Error in AI decision making: {str(e)}",
                "error": True
            }
    
    def _save_analysis_to_databases(self, content: str, content_hash: str, decision: Dict, reasoning_steps: List[str], processing_time: float):
        """Save comprehensive analysis data to both databases"""
        
        # Save to MongoDB (detailed data)
        if self.db_manager.mongo_db is not None:
            try:
                memory_document = {
                    "id": f"{self.session_id}_{int(time.time())}",
                    "timestamp": datetime.now(timezone.utc),
                    "content_hash": content_hash,
                    "content_snippet": content[:500],  # First 500 chars
                    "analysis_result": decision,
                    "reasoning_process": reasoning_steps,
                    "decision_confidence": decision.get('confidence', 0.0),
                    "processing_time": processing_time,
                    "agent_version": self.version,
                    "session_id": self.session_id
                }
                
                self.db_manager.mongo_db.agent_memories.insert_one(memory_document)
                logger.info("💾 Analysis saved to MongoDB")
                
            except Exception as e:
                logger.error(f"❌ MongoDB save failed: {e}")
        
        # Save to MySQL (structured metrics)
        if self.db_manager.mysql_connection:
            try:
                cursor = self.db_manager.mysql_connection.cursor()
                
                analysis_id = f"{self.session_id}_{int(time.time())}"
                cursor.execute("""
                    INSERT INTO content_analyses 
                    (id, session_id, content_hash, decision, confidence, risk_level, processing_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    analysis_id,
                    self.session_id,
                    content_hash,
                    decision.get('decision', 'FLAG'),
                    decision.get('confidence', 0.0),
                    decision.get('risk_level', 'MEDIUM'),
                    processing_time
                ))
                
                self.db_manager.mysql_connection.commit()
                cursor.close()
                logger.info("📊 Analysis metrics saved to MySQL")
                
            except Error as e:
                logger.error(f"❌ MySQL save failed: {e}")
    
    def _update_learning_patterns(self, content: str, decision: Dict, reasoning_steps: List[str]):
        """Update learning patterns in database"""
        if not self.db_manager.mysql_connection:
            return
            
        try:
            # Extract patterns from content and decision
            pattern_data = {
                "content_length": len(content),
                "decision": decision.get('decision'),
                "confidence": decision.get('confidence', 0.0),
                "risk_level": decision.get('risk_level'),
                "reasoning_count": len(reasoning_steps)
            }
            
            cursor = self.db_manager.mysql_connection.cursor()
            cursor.execute("""
                INSERT INTO learning_patterns (pattern_type, pattern_data, confidence_score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                usage_count = usage_count + 1,
                updated_at = CURRENT_TIMESTAMP
            """, (
                decision.get('decision', 'UNKNOWN'),
                json.dumps(pattern_data),
                decision.get('confidence', 0.0)
            ))
            
            self.db_manager.mysql_connection.commit()
            cursor.close()
            
        except Error as e:
            logger.error(f"❌ Learning pattern update failed: {e}")
    
    def _update_performance_metrics(self, decision: Dict, processing_time: float):
        """Update performance metrics"""
        if not self.db_manager.mysql_connection:
            return
            
        try:
            cursor = self.db_manager.mysql_connection.cursor()
            
            # Update processing time metric
            cursor.execute("""
                INSERT INTO performance_metrics (session_id, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, (self.session_id, 'processing_time', processing_time))
            
            # Update confidence metric
            cursor.execute("""
                INSERT INTO performance_metrics (session_id, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, (self.session_id, 'confidence', decision.get('confidence', 0.0)))
            
            self.db_manager.mysql_connection.commit()
            cursor.close()
            
        except Error as e:
            logger.error(f"❌ Performance metrics update failed: {e}")
    
    def get_analytics_dashboard(self) -> Dict:
        """Get comprehensive analytics from databases"""
        analytics = {
            "session_info": {},
            "performance_summary": {},
            "learning_insights": {},
            "recent_analyses": []
        }
        
        # Get session info from MySQL
        if self.db_manager.mysql_connection:
            try:
                cursor = self.db_manager.mysql_connection.cursor(dictionary=True)
                
                # Session summary
                cursor.execute("""
                    SELECT COUNT(*) as total_analyses,
                           AVG(confidence) as avg_confidence,
                           AVG(processing_time) as avg_processing_time
                    FROM content_analyses 
                    WHERE session_id = %s
                """, (self.session_id,))
                
                session_data = cursor.fetchone()
                analytics["session_info"] = session_data or {}
                
                # Decision distribution
                cursor.execute("""
                    SELECT decision, COUNT(*) as count
                    FROM content_analyses 
                    WHERE session_id = %s
                    GROUP BY decision
                """, (self.session_id,))
                
                decision_dist = cursor.fetchall()
                analytics["performance_summary"]["decision_distribution"] = decision_dist
                
                cursor.close()
                
            except Error as e:
                logger.error(f"❌ Analytics query failed: {e}")
        
        # Get recent analyses from MongoDB
        if self.db_manager.mongo_db is not None:
            try:
                recent = list(self.db_manager.mongo_db.agent_memories.find(
                    {"session_id": self.session_id}
                ).sort("timestamp", -1).limit(5))
                
                analytics["recent_analyses"] = [
                    {
                        "timestamp": doc["timestamp"],
                        "decision": doc["analysis_result"].get("decision"),
                        "confidence": doc["analysis_result"].get("confidence"),
                        "content_preview": doc["content_snippet"][:100]
                    }
                    for doc in recent
                ]
                
            except Exception as e:
                logger.error(f"❌ MongoDB analytics failed: {e}")
        
        return analytics
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response to extract JSON"""
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {"raw_response": response_text}
        except:
            return {"raw_response": response_text}
    
    def close_session(self):
        """Close agent session and database connections"""
        try:
            # Update session end time in MySQL
            if self.db_manager.mysql_connection:
                cursor = self.db_manager.mysql_connection.cursor()
                cursor.execute("""
                    UPDATE agent_sessions 
                    SET end_time = %s 
                    WHERE id = %s
                """, (datetime.now(), self.session_id))
                
                self.db_manager.mysql_connection.commit()
                cursor.close()
                self.db_manager.mysql_connection.close()
            
            # Close MongoDB connection
            if self.db_manager.mongo_client:
                self.db_manager.mongo_client.close()
            
            logger.info(f"📝 Session {self.session_id} closed")
            
        except Exception as e:
            logger.error(f"❌ Session close failed: {e}")

def main():
    """Production agent demonstration"""
    print("🚀 PRODUCTION AI CONTENT AGENT")
    print("=" * 60)
    print("🗄️ MongoDB Atlas + MySQL Integration")
    print("🤖 Advanced AI Reasoning with Persistence")
    print("📊 Real-time Analytics & Learning")
    print("=" * 60)
    
    # Initialize production agent
    agent = ProductionContentAgent()
    
    # Interactive analysis
    print("\n💬 Interactive Content Analysis")
    print("Type 'analytics' to see dashboard")
    print("Type 'quit' to exit")
    
    try:
        while True:
            print("\n" + "="*60)
            user_input = input("📝 Enter content to analyze: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'analytics':
                analytics = agent.get_analytics_dashboard()
                print("\n📊 ANALYTICS DASHBOARD")
                print("="*40)
                print(f"📈 Session Info: {analytics['session_info']}")
                print(f"🎯 Performance: {analytics['performance_summary']}")
                print(f"📚 Recent Analyses: {len(analytics['recent_analyses'])}")
                continue
            elif not user_input:
                print("⚠️ Please enter some content")
                continue
            
            # Analyze content
            context = {"platform": "interactive", "user_type": "developer"}
            result = agent.analyze_content_production(user_input, context)
            
            # Display results
            print(f"\n🎯 DECISION: {result.get('decision', 'UNKNOWN')}")
            print(f"📊 Confidence: {result.get('confidence', 0):.2f}")
            print(f"🔒 Risk Level: {result.get('risk_level', 'UNKNOWN')}")
            print(f"⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('explanation'):
                print(f"💡 Explanation: {result['explanation'][:150]}...")
                
            if result.get('key_concerns'):
                print(f"⚠️ Concerns: {', '.join(result['key_concerns'])}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down agent...")
    
    finally:
        # Close session and connections
        agent.close_session()
        print("✅ Production agent session completed")

if __name__ == "__main__":
    main()
