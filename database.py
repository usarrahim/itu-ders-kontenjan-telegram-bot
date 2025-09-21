import sqlite3
import json
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kullanıcı dersleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_code TEXT,
                branch_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, chat_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None):
        """Kullanıcı ekle veya güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, chat_id, username, first_name, last_name, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (user_id, chat_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Kullanıcı bilgilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'chat_id': result[1],
                'username': result[2],
                'first_name': result[3],
                'last_name': result[4],
                'is_active': result[5],
                'created_at': result[6]
            }
        return None
    
    def add_course_to_user(self, user_id: int, course_code: str, branch_id: int):
        """Kullanıcıya ders ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aynı ders zaten ekli mi kontrol et
        cursor.execute('''
            SELECT id FROM user_courses 
            WHERE user_id = ? AND course_code = ?
        ''', (user_id, course_code))
        
        if cursor.fetchone():
            conn.close()
            return False  # Ders zaten ekli
        
        cursor.execute('''
            INSERT INTO user_courses (user_id, course_code, branch_id)
            VALUES (?, ?, ?)
        ''', (user_id, course_code, branch_id))
        
        conn.commit()
        conn.close()
        return True
    
    def remove_course_from_user(self, user_id: int, course_code: str):
        """Kullanıcıdan ders kaldır"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM user_courses 
            WHERE user_id = ? AND course_code = ?
        ''', (user_id, course_code))
        
        conn.commit()
        conn.close()
    
    def get_user_courses(self, user_id: int) -> List[Dict]:
        """Kullanıcının derslerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT course_code, branch_id FROM user_courses 
            WHERE user_id = ?
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'course_code': row[0], 'branch_id': row[1]} for row in results]
    
    def get_all_active_users(self) -> List[Dict]:
        """Tüm aktif kullanıcıları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.chat_id, uc.course_code, uc.branch_id
            FROM users u
            JOIN user_courses uc ON u.user_id = uc.user_id
            WHERE u.is_active = 1
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'user_id': row[0],
            'chat_id': row[1],
            'course_code': row[2],
            'branch_id': row[3]
        } for row in results]
    
    def get_users_by_course(self, course_code: str, branch_id: int) -> List[Dict]:
        """Belirli bir dersi takip eden kullanıcıları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.chat_id, u.first_name
            FROM users u
            JOIN user_courses uc ON u.user_id = uc.user_id
            WHERE uc.course_code = ? AND uc.branch_id = ? AND u.is_active = 1
        ''', (course_code, branch_id))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'user_id': row[0],
            'chat_id': row[1],
            'first_name': row[2]
        } for row in results]
