# database.py - Optimized Version for Speed
"""
Database module for AI Response Evaluation Survey
Handles all data persistence, condition assignment, and statistics
OPTIMIZED FOR PERFORMANCE
"""

import sqlite3
import threading
import time
import json
import pandas as pd
from contextlib import contextmanager
from typing import Dict, List, Tuple, Optional

# Thread-safe database access
db_lock = threading.Lock()
DB_NAME = 'survey_data.db'

class SurveyDatabase:
    """Main database class for survey operations - OPTIMIZED"""
    
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.init_database()
        self._create_indexes()  # Add indexes for performance
    
    @contextmanager
    def get_connection(self):
        """Thread-safe database connection context manager"""
        with db_lock:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            # Enable WAL mode for better performance
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            try:
                yield conn
            finally:
                conn.close()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        with self.get_connection() as conn:
            try:
                # Index on participants condition for faster filtering
                conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_condition ON participants(condition)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_completed ON participants(completed)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_timestamp ON participants(timestamp)')
                
                # Index on responses for faster filtering
                conn.execute('CREATE INDEX IF NOT EXISTS idx_responses_participant_id ON responses(participant_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_responses_group_condition ON responses(group_condition)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON responses(timestamp)')
                
                # Index on metadata for faster settings lookup
                conn.execute('CREATE INDEX IF NOT EXISTS idx_metadata_key ON study_metadata(key)')
                
                conn.commit()
            except Exception:
                pass  # Indexes might already exist
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            # Participants table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition TEXT NOT NULL,
                    age INTEGER,
                    profession TEXT,
                    timestamp REAL NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Responses table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    participant_id INTEGER NOT NULL,
                    case_id TEXT NOT NULL,
                    response_number INTEGER NOT NULL,
                    group_condition TEXT NOT NULL,
                    user_age INTEGER,
                    user_profession TEXT,
                    agree_rating TEXT,
                    trust_rating BOOLEAN,
                    comment TEXT,
                    timestamp REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (participant_id) REFERENCES participants (id)
                )
            ''')
            
            # Study metadata table for dynamic settings
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize default settings
            cursor = conn.execute('SELECT value FROM study_metadata WHERE key = ?', ('target_participants',))
            if cursor.fetchone() is None:
                conn.execute('''
                    INSERT INTO study_metadata (key, value) VALUES (?, ?)
                ''', ('target_participants', '10'))
            
            cursor = conn.execute('SELECT value FROM study_metadata WHERE key = ?', ('study_active',))
            if cursor.fetchone() is None:
                conn.execute('''
                    INSERT INTO study_metadata (key, value) VALUES (?, ?)
                ''', ('study_active', 'true'))
            
            conn.commit()
    
    def get_target_participants(self) -> int:
        """Get the current target number of participants - OPTIMIZED"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT value FROM study_metadata WHERE key = ? LIMIT 1', ('target_participants',))
            result = cursor.fetchone()
            return int(result['value']) if result else 10
    
    def set_target_participants(self, target: int):
        """Set the target number of participants"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO study_metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', ('target_participants', str(target)))
            conn.commit()
    
    def is_study_active(self) -> bool:
        """Check if the study is currently accepting participants - OPTIMIZED"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT value FROM study_metadata WHERE key = ? LIMIT 1', ('study_active',))
            result = cursor.fetchone()
            return result['value'].lower() == 'true' if result else True
    
    def set_study_active(self, active: bool):
        """Set whether the study is accepting participants"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO study_metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', ('study_active', 'true' if active else 'false'))
            conn.commit()
    
    def get_current_participant_count(self) -> int:
        """Get the current number of participants - OPTIMIZED"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM participants')
            return cursor.fetchone()['count']
    
    def can_accept_participants(self) -> bool:
        """Check if study can accept more participants - OPTIMIZED"""
        with self.get_connection() as conn:
            # Single query to get all needed info
            cursor = conn.execute('''
                SELECT 
                    (SELECT value FROM study_metadata WHERE key = 'study_active' LIMIT 1) as active,
                    (SELECT value FROM study_metadata WHERE key = 'target_participants' LIMIT 1) as target,
                    (SELECT COUNT(*) FROM participants) as current_count
            ''')
            result = cursor.fetchone()
            
            if not result:
                return False
                
            active = result['active'] and result['active'].lower() == 'true'
            target = int(result['target']) if result['target'] else 10
            current = result['current_count'] or 0
            
            return active and current < target
    
    def get_next_condition(self) -> Tuple[str, int]:
        """Get next condition assignment using balanced allocation - OPTIMIZED"""
        if not self.can_accept_participants():
            raise Exception("Study is not accepting new participants")
        
        conditions = ["Control", "Group A - Warning Label"]
        
        with self.get_connection() as conn:
            # Single optimized query to get all needed data
            cursor = conn.execute('''
                SELECT 
                    condition, 
                    COUNT(*) as count,
                    (SELECT value FROM study_metadata WHERE key = 'target_participants' LIMIT 1) as target
                FROM participants 
                GROUP BY condition
            ''')
            
            results = cursor.fetchall()
            target_participants = int(results[0]['target']) if results else 10
            
            # Process counts
            counts = {}
            for row in results:
                counts[row['condition']] = row['count']
            
            total_participants = sum(counts.values())
            
            # Calculate target per condition
            base_per_condition = target_participants // 2
            remainder = target_participants % 2
            
            target_control = base_per_condition + remainder
            target_warning = base_per_condition
            
            current_control = counts.get('Control', 0)
            current_warning = counts.get('Group A - Warning Label', 0)
            
            # Assign based on which condition needs more participants
            if current_control < target_control and (current_warning >= target_warning or current_control <= current_warning):
                condition = 'Control'
            elif current_warning < target_warning:
                condition = 'Group A - Warning Label'
            else:
                condition = conditions[total_participants % 2]
            
            # Insert new participant
            cursor = conn.execute('''
                INSERT INTO participants (condition, timestamp) 
                VALUES (?, ?)
            ''', (condition, time.time()))
            
            participant_id = cursor.lastrowid
            conn.commit()
            
            return condition, participant_id
    
    def update_participant_info(self, participant_id: int, age: int, profession: str):
        """Update participant demographic information"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE participants 
                SET age = ?, profession = ?
                WHERE id = ?
            ''', (age, profession, participant_id))
            conn.commit()
    
    def save_response(self, participant_id: int, response_data: Dict):
        """Save a single survey response"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO responses (
                    participant_id, case_id, response_number, group_condition,
                    user_age, user_profession, agree_rating, trust_rating, 
                    comment, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                participant_id,
                response_data['case_id'],
                response_data['response_number'], 
                response_data['group'],
                response_data['user_age'],
                response_data['user_profession'],
                response_data['agree'],
                response_data['trust'],
                response_data['comment'],
                time.time()
            ))
            conn.commit()
    
    def mark_participant_completed(self, participant_id: int):
        """Mark participant as having completed the study"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE participants 
                SET completed = TRUE 
                WHERE id = ?
            ''', (participant_id,))
            conn.commit()
    
    def get_assignment_stats(self) -> Dict:
        """Get current assignment statistics - HEAVILY OPTIMIZED"""
        with self.get_connection() as conn:
            # Single complex query to get all stats at once
            cursor = conn.execute('''
                SELECT 
                    -- Basic counts by condition
                    SUM(CASE WHEN condition = 'Control' THEN 1 ELSE 0 END) as control_count,
                    SUM(CASE WHEN condition = 'Group A - Warning Label' THEN 1 ELSE 0 END) as warning_count,
                    COUNT(*) as total_participants,
                    
                    -- Completion counts by condition
                    SUM(CASE WHEN condition = 'Control' AND completed = 1 THEN 1 ELSE 0 END) as control_completed,
                    SUM(CASE WHEN condition = 'Group A - Warning Label' AND completed = 1 THEN 1 ELSE 0 END) as warning_completed,
                    
                    -- Get settings in same query
                    (SELECT value FROM study_metadata WHERE key = 'target_participants' LIMIT 1) as target_participants,
                    (SELECT value FROM study_metadata WHERE key = 'study_active' LIMIT 1) as study_active
                    
                FROM participants
            ''')
            
            result = cursor.fetchone()
            
            if not result:
                return {
                    'total_participants': 0,
                    'control_count': 0,
                    'warning_count': 0,
                    'completion_stats': {},
                    'balance_difference': 0,
                    'target_participants': 10,
                    'study_active': True
                }
            
            control_count = result['control_count'] or 0
            warning_count = result['warning_count'] or 0
            total_participants = result['total_participants'] or 0
            control_completed = result['control_completed'] or 0
            warning_completed = result['warning_completed'] or 0
            target_participants = int(result['target_participants']) if result['target_participants'] else 10
            study_active = result['study_active'] and result['study_active'].lower() == 'true'
            
            # Build completion stats
            completion_stats = {}
            if control_count > 0:
                completion_stats['Control'] = {
                    'total': control_count,
                    'completed': control_completed
                }
            if warning_count > 0:
                completion_stats['Group A - Warning Label'] = {
                    'total': warning_count,
                    'completed': warning_completed
                }
            
            return {
                'total_participants': total_participants,
                'control_count': control_count,
                'warning_count': warning_count,
                'completion_stats': completion_stats,
                'balance_difference': abs(control_count - warning_count),
                'target_participants': target_participants,
                'study_active': study_active
            }
    
    def get_participant_responses(self, participant_id: int) -> List[Dict]:
        """Get all responses for a specific participant"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM responses 
                WHERE participant_id = ?
                ORDER BY response_number
            ''', (participant_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Export all data to pandas DataFrames for analysis - OPTIMIZED"""
        with self.get_connection() as conn:
            # Use pandas read_sql for better performance
            participants_df = pd.read_sql_query('''
                SELECT id, condition, age, profession, completed,
                       datetime(timestamp, 'unixepoch') as assigned_at,
                       created_at
                FROM participants 
                ORDER BY id
            ''', conn)
            
            responses_df = pd.read_sql_query('''
                SELECT r.*, p.condition as participant_condition,
                       datetime(r.timestamp, 'unixepoch') as submitted_at
                FROM responses r
                JOIN participants p ON r.participant_id = p.id
                ORDER BY r.participant_id, r.response_number
            ''', conn)
            
            return participants_df, responses_df
    
    def get_study_progress(self, target_participants: Optional[int] = None) -> Dict:
        """Get study progress information - OPTIMIZED"""
        if target_participants is None:
            target_participants = self.get_target_participants()
        
        # Use already optimized get_assignment_stats
        stats = self.get_assignment_stats()
        
        return {
            'current_total': stats['total_participants'],
            'target_total': target_participants,
            'progress_percentage': (stats['total_participants'] / target_participants) * 100 if target_participants > 0 else 0,
            'remaining': max(0, target_participants - stats['total_participants']),
            'control_needed': max(0, (target_participants // 2 + target_participants % 2) - stats['control_count']),
            'warning_needed': max(0, (target_participants // 2) - stats['warning_count']),
            'is_complete': stats['total_participants'] >= target_participants,
            'study_active': stats['study_active']
        }
    
    def reset_database(self):
        """DANGER: Reset entire database - use only for testing!"""
        with self.get_connection() as conn:
            conn.execute('DROP TABLE IF EXISTS responses')
            conn.execute('DROP TABLE IF EXISTS participants') 
            conn.execute('DROP TABLE IF EXISTS study_metadata')
            conn.commit()
        self.init_database()

# Convenience functions for easy importing
def create_database() -> SurveyDatabase:
    """Create and return a SurveyDatabase instance"""
    return SurveyDatabase()

def get_condition_assignment() -> Tuple[str, int]:
    """Quick function to get next condition assignment"""
    db = create_database()
    return db.get_next_condition()

def save_survey_response(participant_id: int, response_data: Dict):
    """Quick function to save a response"""
    db = create_database()
    db.save_response(participant_id, response_data)

def get_statistics() -> Dict:
    """Quick function to get current statistics"""
    db = create_database()
    return db.get_assignment_stats()

# Admin utilities
class AdminUtils:
    """Administrative utilities for managing the study - OPTIMIZED"""
    
    def __init__(self):
        self.db = create_database()
    
    def show_detailed_stats(self) -> Dict:
        """Get comprehensive statistics for admin dashboard - OPTIMIZED"""
        # Use the already optimized functions
        stats = self.db.get_assignment_stats()
        progress = self.db.get_study_progress()
        
        # Simplified recent activity query
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT datetime(timestamp, 'unixepoch') as time,
                       'participant_joined' as event,
                       condition
                FROM participants
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (time.time() - 86400,))  # Last 24 hours
            recent_activity = [dict(row) for row in cursor.fetchall()]
        
        return {
            'basic_stats': stats,
            'progress': progress,
            'recent_activity': recent_activity
        }
    
    def export_for_analysis(self, filename_prefix: str = "survey_data"):
        """Export data to CSV files for analysis"""
        participants_df, responses_df = self.db.export_data()
        
        participants_file = f"{filename_prefix}_participants.csv"
        responses_file = f"{filename_prefix}_responses.csv"
        
        participants_df.to_csv(participants_file, index=False)
        responses_df.to_csv(responses_file, index=False)
        
        return participants_file, responses_file

if __name__ == "__main__":
    # Test the database
    print("Testing optimized database...")
    db = create_database()
    
    # Test condition assignment
    try:
        condition, pid = db.get_next_condition()
        print(f"Assigned participant {pid} to {condition}")
    except Exception as e:
        print(f"Assignment failed: {e}")
    
    # Test stats
    stats = db.get_assignment_stats()
    print(f"Current stats: {stats}")
    
    print("Database test complete!")