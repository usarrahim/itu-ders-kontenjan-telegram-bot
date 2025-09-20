import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını ve tabloları oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id TEXT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kullanıcı ders seçimleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_code TEXT NOT NULL,
                branch_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, course_code)
            )
        ''')
        
        # Ders kodları ve branş kodları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_branches (
                branch_code TEXT PRIMARY KEY,
                branch_id INTEGER NOT NULL,
                branch_name TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, chat_id: str, username: str = None, 
                 first_name: str = None, last_name: str = None) -> bool:
        """Yeni kullanıcı ekler"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, chat_id, username, first_name, last_name, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, chat_id, username, first_name, last_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Kullanıcı ekleme hatası: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Kullanıcı bilgilerini getirir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                user_data = dict(zip(columns, row))
                conn.close()
                return user_data
            conn.close()
            return None
        except Exception as e:
            print(f"Kullanıcı getirme hatası: {e}")
            return None
    
    def add_course_to_user(self, user_id: int, course_code: str, branch_id: int) -> bool:
        """Kullanıcıya ders ekler"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_courses 
                (user_id, course_code, branch_id)
                VALUES (?, ?, ?)
            ''', (user_id, course_code, branch_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ders ekleme hatası: {e}")
            return False
    
    def remove_course_from_user(self, user_id: int, course_code: str) -> bool:
        """Kullanıcıdan ders kaldırır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_courses 
                WHERE user_id = ? AND course_code = ?
            ''', (user_id, course_code))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ders kaldırma hatası: {e}")
            return False
    
    def get_user_courses(self, user_id: int) -> List[Dict]:
        """Kullanıcının ders listesini getirir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT course_code, branch_id FROM user_courses 
                WHERE user_id = ?
            ''', (user_id,))
            
            courses = []
            for row in cursor.fetchall():
                courses.append({
                    'course_code': row[0],
                    'branch_id': row[1]
                })
            
            conn.close()
            return courses
        except Exception as e:
            print(f"Ders listesi getirme hatası: {e}")
            return []
    
    def get_all_active_users(self) -> List[Dict]:
        """Aktif tüm kullanıcıları getirir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.user_id, u.chat_id, u.username, u.first_name, u.last_name,
                       uc.course_code, uc.branch_id
                FROM users u
                LEFT JOIN user_courses uc ON u.user_id = uc.user_id
                WHERE u.is_active = 1
            ''')
            
            users = {}
            for row in cursor.fetchall():
                user_id = row[0]
                if user_id not in users:
                    users[user_id] = {
                        'user_id': row[0],
                        'chat_id': row[1],
                        'username': row[2],
                        'first_name': row[3],
                        'last_name': row[4],
                        'courses': []
                    }
                
                if row[5]:  # course_code
                    users[user_id]['courses'].append({
                        'course_code': row[5],
                        'branch_id': row[6]
                    })
            
            conn.close()
            return list(users.values())
        except Exception as e:
            print(f"Aktif kullanıcılar getirme hatası: {e}")
            return []
    
    def get_users_by_course(self, course_code: str, branch_id: int) -> List[Dict]:
        """Belirli bir ders için bildirim alacak kullanıcıları getirir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.user_id, u.chat_id, u.username, u.first_name, u.last_name
                FROM users u
                JOIN user_courses uc ON u.user_id = uc.user_id
                WHERE uc.course_code = ? AND uc.branch_id = ? AND u.is_active = 1
            ''', (course_code, branch_id))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'chat_id': row[1],
                    'username': row[2],
                    'first_name': row[3],
                    'last_name': row[4]
                })
            
            conn.close()
            return users
        except Exception as e:
            print(f"Ders kullanıcıları getirme hatası: {e}")
            return []
    
    def update_user_activity(self, user_id: int, is_active: bool) -> bool:
        """Kullanıcı aktivite durumunu günceller"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (is_active, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Kullanıcı aktivite güncelleme hatası: {e}")
            return False
