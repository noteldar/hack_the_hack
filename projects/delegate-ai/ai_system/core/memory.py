"""
Agent Memory Manager - Persistent memory and learning system
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pickle
from pathlib import Path
import logging

from .base_agent import TaskResult

class AgentMemoryManager:
    """
    Manages persistent memory for all agents in the system.
    Enables learning from past experiences and user preferences.
    """

    def __init__(self, db_path: str = "./data/agent_memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("delegate.memory")

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Task results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    task_id TEXT PRIMARY KEY,
                    agent_name TEXT,
                    status TEXT,
                    result TEXT,
                    error TEXT,
                    execution_time REAL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    preference_key TEXT PRIMARY KEY,
                    preference_value TEXT,
                    agent_name TEXT,
                    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence REAL DEFAULT 0.5
                )
            """)

            # Agent interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_interactions (
                    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_agent TEXT,
                    to_agent TEXT,
                    message TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Context memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_memory (
                    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    context_type TEXT,
                    context_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expiry_date DATETIME
                )
            """)

            # Learning patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_agent ON task_results(agent_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_timestamp ON task_results(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pref_agent ON user_preferences(agent_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_agent ON context_memory(agent_name)")

            conn.commit()

    def initialize_agent_memory(self, agent_id: str):
        """Initialize memory structures for a new agent"""
        self.logger.info(f"Initializing memory for agent: {agent_id}")

        # Create agent-specific memory structures if needed
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if agent already exists
            cursor.execute(
                "SELECT COUNT(*) FROM context_memory WHERE agent_name = ?",
                (agent_id,)
            )

            if cursor.fetchone()[0] == 0:
                # Initialize with basic context
                cursor.execute("""
                    INSERT INTO context_memory (agent_name, context_type, context_data, expiry_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    agent_id,
                    "initialization",
                    json.dumps({"initialized": True, "timestamp": datetime.now().isoformat()}),
                    (datetime.now() + timedelta(days=365)).isoformat()
                ))

                conn.commit()

    async def store_task_result(self, agent_name: str, result: TaskResult):
        """Store a task result in memory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO task_results
                (task_id, agent_name, status, result, error, execution_time, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.task_id,
                agent_name,
                result.status,
                json.dumps(result.result) if result.result else None,
                result.error,
                result.execution_time,
                json.dumps(result.metadata),
                result.timestamp.isoformat()
            ))

            conn.commit()

            # Learn from the result
            await self._learn_from_result(agent_name, result)

    async def _learn_from_result(self, agent_name: str, result: TaskResult):
        """Extract learning patterns from task results"""
        if result.status == "success":
            # Identify successful patterns
            pattern_data = {
                "task_type": result.metadata.get("task_type"),
                "parameters": result.metadata.get("parameters"),
                "execution_time": result.execution_time
            }

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if similar pattern exists
                cursor.execute("""
                    SELECT pattern_id, frequency, success_rate
                    FROM learning_patterns
                    WHERE agent_name = ? AND pattern_type = ?
                """, (agent_name, pattern_data.get("task_type", "unknown")))

                existing = cursor.fetchone()

                if existing:
                    # Update existing pattern
                    pattern_id, frequency, success_rate = existing
                    new_frequency = frequency + 1
                    new_success_rate = (success_rate * frequency + 1) / new_frequency

                    cursor.execute("""
                        UPDATE learning_patterns
                        SET frequency = ?, success_rate = ?, last_updated = ?
                        WHERE pattern_id = ?
                    """, (new_frequency, new_success_rate, datetime.now().isoformat(), pattern_id))
                else:
                    # Create new pattern
                    cursor.execute("""
                        INSERT INTO learning_patterns
                        (agent_name, pattern_type, pattern_data, success_rate)
                        VALUES (?, ?, ?, ?)
                    """, (
                        agent_name,
                        pattern_data.get("task_type", "unknown"),
                        json.dumps(pattern_data),
                        1.0
                    ))

                conn.commit()

    def store_user_preference(
        self,
        agent_name: str,
        preference_key: str,
        preference_value: Any,
        confidence: float = 0.5
    ):
        """Store a learned user preference"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences
                (preference_key, preference_value, agent_name, confidence)
                VALUES (?, ?, ?, ?)
            """, (
                preference_key,
                json.dumps(preference_value),
                agent_name,
                confidence
            ))

            conn.commit()

    def get_user_preferences(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve user preferences"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if agent_name:
                cursor.execute("""
                    SELECT preference_key, preference_value, confidence
                    FROM user_preferences
                    WHERE agent_name = ?
                    ORDER BY confidence DESC
                """, (agent_name,))
            else:
                cursor.execute("""
                    SELECT preference_key, preference_value, confidence
                    FROM user_preferences
                    ORDER BY confidence DESC
                """)

            preferences = {}
            for key, value, confidence in cursor.fetchall():
                preferences[key] = {
                    "value": json.loads(value),
                    "confidence": confidence
                }

            return preferences

    def store_agent_interaction(
        self,
        from_agent: str,
        to_agent: str,
        message: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None
    ):
        """Store inter-agent communication for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO agent_interactions (from_agent, to_agent, message, response)
                VALUES (?, ?, ?, ?)
            """, (
                from_agent,
                to_agent,
                json.dumps(message),
                json.dumps(response) if response else None
            ))

            conn.commit()

    def store_context(
        self,
        agent_name: str,
        context_type: str,
        context_data: Dict[str, Any],
        ttl_hours: int = 24
    ):
        """Store contextual information with TTL"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            expiry_date = datetime.now() + timedelta(hours=ttl_hours)

            cursor.execute("""
                INSERT INTO context_memory
                (agent_name, context_type, context_data, expiry_date)
                VALUES (?, ?, ?, ?)
            """, (
                agent_name,
                context_type,
                json.dumps(context_data),
                expiry_date.isoformat()
            ))

            conn.commit()

    def get_context(
        self,
        agent_name: str,
        context_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve valid context for an agent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clean expired context
            cursor.execute("""
                DELETE FROM context_memory
                WHERE expiry_date < ?
            """, (datetime.now().isoformat(),))

            # Retrieve valid context
            if context_type:
                cursor.execute("""
                    SELECT context_type, context_data, timestamp
                    FROM context_memory
                    WHERE agent_name = ? AND context_type = ?
                    AND expiry_date > ?
                    ORDER BY timestamp DESC
                """, (agent_name, context_type, datetime.now().isoformat()))
            else:
                cursor.execute("""
                    SELECT context_type, context_data, timestamp
                    FROM context_memory
                    WHERE agent_name = ?
                    AND expiry_date > ?
                    ORDER BY timestamp DESC
                """, (agent_name, datetime.now().isoformat()))

            contexts = []
            for ctx_type, ctx_data, timestamp in cursor.fetchall():
                contexts.append({
                    "type": ctx_type,
                    "data": json.loads(ctx_data),
                    "timestamp": timestamp
                })

            return contexts

    def get_task_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve task history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if agent_name:
                cursor.execute("""
                    SELECT task_id, agent_name, status, result, error,
                           execution_time, metadata, timestamp
                    FROM task_results
                    WHERE agent_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (agent_name, limit))
            else:
                cursor.execute("""
                    SELECT task_id, agent_name, status, result, error,
                           execution_time, metadata, timestamp
                    FROM task_results
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))

            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    "task_id": row[0],
                    "agent_name": row[1],
                    "status": row[2],
                    "result": json.loads(row[3]) if row[3] else None,
                    "error": row[4],
                    "execution_time": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {},
                    "timestamp": row[7]
                })

            return tasks

    def get_learning_patterns(
        self,
        agent_name: str,
        min_frequency: int = 2
    ) -> List[Dict[str, Any]]:
        """Retrieve learned patterns for an agent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT pattern_type, pattern_data, frequency, success_rate
                FROM learning_patterns
                WHERE agent_name = ? AND frequency >= ?
                ORDER BY success_rate DESC, frequency DESC
            """, (agent_name, min_frequency))

            patterns = []
            for pattern_type, pattern_data, frequency, success_rate in cursor.fetchall():
                patterns.append({
                    "type": pattern_type,
                    "data": json.loads(pattern_data),
                    "frequency": frequency,
                    "success_rate": success_rate
                })

            return patterns

    def get_collaboration_insights(self) -> Dict[str, Any]:
        """Analyze inter-agent collaboration patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get collaboration frequency
            cursor.execute("""
                SELECT from_agent, to_agent, COUNT(*) as interaction_count
                FROM agent_interactions
                GROUP BY from_agent, to_agent
                ORDER BY interaction_count DESC
            """)

            collaborations = {}
            for from_agent, to_agent, count in cursor.fetchall():
                if from_agent not in collaborations:
                    collaborations[from_agent] = {}
                collaborations[from_agent][to_agent] = count

            return {
                "collaboration_matrix": collaborations,
                "most_collaborative": max(
                    collaborations.items(),
                    key=lambda x: sum(x[1].values())
                )[0] if collaborations else None
            }

    async def save_all(self):
        """Save all in-memory data to persistent storage"""
        # In this implementation, we're already using SQLite for persistence
        # This method could be used for additional cleanup or optimization
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")  # Optimize database
            conn.commit()

        self.logger.info("Memory manager saved all data")

    def clear_old_data(self, days: int = 30):
        """Clear old data from memory"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clear old task results
            cursor.execute("""
                DELETE FROM task_results
                WHERE timestamp < ?
            """, (cutoff_date,))

            # Clear old interactions
            cursor.execute("""
                DELETE FROM agent_interactions
                WHERE timestamp < ?
            """, (cutoff_date,))

            # Clear expired context
            cursor.execute("""
                DELETE FROM context_memory
                WHERE expiry_date < ?
            """, (datetime.now().isoformat(),))

            conn.commit()

            self.logger.info(f"Cleared data older than {days} days")