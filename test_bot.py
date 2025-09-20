#!/usr/bin/env python3
"""
ITU Ders Kontenjan Bot Test Suite
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from course_validator import CourseValidator
from database import DatabaseManager

class TestCourseValidator(unittest.TestCase):
    """Course validator testleri"""
    
    def setUp(self):
        self.validator = CourseValidator()
    
    def test_valid_course_codes(self):
        """Geçerli ders kodlarını test et"""
        valid_codes = [
            "EHB 313E",
            "MAT 101",
            "FIZ 101E",
            "KIM 101",
            "BLG 101"
        ]
        
        for code in valid_codes:
            is_valid, error, branch_id = self.validator.validate_course_code(code)
            self.assertTrue(is_valid, f"Code {code} should be valid")
            self.assertIsNotNone(branch_id, f"Branch ID should not be None for {code}")
    
    def test_invalid_course_codes(self):
        """Geçersiz ders kodlarını test et"""
        invalid_codes = [
            "INVALID 123",
            "EHB313E",  # Boşluk yok
            "EHB 313",  # E eksik
            "123 456",  # Sayısal branş kodu
            "",         # Boş
            "EHB",      # Eksik
        ]
        
        for code in invalid_codes:
            is_valid, error, branch_id = self.validator.validate_course_code(code)
            self.assertFalse(is_valid, f"Code {code} should be invalid")
    
    def test_format_course_code(self):
        """Ders kodu formatlamasını test et"""
        test_cases = [
            ("ehb 313e", "EHB 313E"),
            ("  MAT 101  ", "MAT 101"),
            ("fiz 101e", "FIZ 101E"),
        ]
        
        for input_code, expected in test_cases:
            result = self.validator.format_course_code(input_code)
            self.assertEqual(result, expected)

class TestDatabaseManager(unittest.TestCase):
    """Database manager testleri"""
    
    def setUp(self):
        # Test için geçici veritabanı
        self.db = DatabaseManager("test_users.db")
    
    def tearDown(self):
        # Test veritabanını temizle
        if os.path.exists("test_users.db"):
            os.remove("test_users.db")
    
    def test_add_user(self):
        """Kullanıcı ekleme testi"""
        success = self.db.add_user(
            user_id=12345,
            chat_id="12345",
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        self.assertTrue(success)
    
    def test_get_user(self):
        """Kullanıcı getirme testi"""
        # Önce kullanıcı ekle
        self.db.add_user(12345, "12345", "testuser", "Test", "User")
        
        # Kullanıcıyı getir
        user = self.db.get_user(12345)
        self.assertIsNotNone(user)
        self.assertEqual(user['user_id'], 12345)
        self.assertEqual(user['username'], 'testuser')
    
    def test_add_course_to_user(self):
        """Kullanıcıya ders ekleme testi"""
        # Önce kullanıcı ekle
        self.db.add_user(12345, "12345", "testuser", "Test", "User")
        
        # Ders ekle
        success = self.db.add_course_to_user(12345, "EHB 313E", 196)
        self.assertTrue(success)
        
        # Dersleri kontrol et
        courses = self.db.get_user_courses(12345)
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]['course_code'], "EHB 313E")
    
    def test_remove_course_from_user(self):
        """Kullanıcıdan ders kaldırma testi"""
        # Önce kullanıcı ve ders ekle
        self.db.add_user(12345, "12345", "testuser", "Test", "User")
        self.db.add_course_to_user(12345, "EHB 313E", 196)
        
        # Dersi kaldır
        success = self.db.remove_course_from_user(12345, "EHB 313E")
        self.assertTrue(success)
        
        # Derslerin boş olduğunu kontrol et
        courses = self.db.get_user_courses(12345)
        self.assertEqual(len(courses), 0)

def run_tests():
    """Testleri çalıştır"""
    print("🧪 ITU Ders Kontenjan Bot Test Suite")
    print("=" * 50)
    
    # Test suite oluştur
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTest(unittest.makeSuite(TestCourseValidator))
    suite.addTest(unittest.makeSuite(TestDatabaseManager))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Sonuçları yazdır
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Tüm testler başarılı!")
        return True
    else:
        print(f"❌ {len(result.failures)} test başarısız, {len(result.errors)} hata")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
