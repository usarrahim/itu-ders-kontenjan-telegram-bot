import json
import re
from typing import Dict, List, Optional, Tuple

class CourseValidator:
    def __init__(self):
        # Ders kodları ve branş kodları mapping'i
        self.branch_mapping = {
            "AKM": 42, "ALM": 227, "ARB": 305, "ARC": 302, "ATA": 43,
            "BBF": 310, "BEB": 200, "BED": 149, "BEN": 165, "BIL": 38,
            "BIO": 30, "BLG": 3, "BLS": 180, "BUS": 155, "CAB": 127,
            "CEN": 304, "CEV": 7, "CHA": 169, "CHE": 137, "CHZ": 81,
            "CIE": 142, "CIN": 245, "CMP": 146, "COM": 208, "CVH": 168,
            "DAN": 243, "DEN": 10, "DFH": 163, "DGH": 181, "DNK": 44,
            "DUI": 32, "EAS": 141, "ECN": 232, "ECO": 154, "EEE": 289,
            "EEF": 294, "EFN": 297, "EHA": 182, "EHB": 196, "EHN": 241,
            "EKO": 39, "ELE": 59, "ELH": 2, "ELK": 1, "ELT": 178,
            "END": 15, "ENE": 183, "ENG": 179, "ENR": 207, "ENT": 225,
            "ESL": 140, "ESM": 164, "ETK": 110, "EUT": 22, "FIZ": 28,
            "FRA": 226, "FZK": 175, "GED": 138, "GEM": 11, "GEO": 74,
            "GID": 4, "GLY": 162, "GMI": 46, "GMK": 176, "GMZ": 109,
            "GSB": 53, "GSN": 173, "GUV": 31, "GVT": 177, "GVZ": 111,
            "HSS": 256, "HUK": 41, "IAD": 301, "ICM": 63, "ILT": 253,
            "IML": 112, "IND": 300, "ING": 33, "INS": 8, "ISE": 153,
            "ISH": 231, "ISL": 14, "ISP": 228, "ITA": 255, "ITB": 50,
            "JDF": 9, "JEF": 19, "JEO": 18, "JPN": 202, "KIM": 27,
            "KMM": 6, "KMP": 125, "KON": 58, "LAT": 156, "MAD": 16,
            "MAK": 12, "MAL": 48, "MAR": 148, "MAT": 26, "MCH": 160,
            "MDN": 293, "MEK": 47, "MEN": 258, "MET": 5, "MIM": 20,
            "MKN": 184, "MMD": 290, "MOD": 150, "MRE": 157, "MRT": 158,
            "MST": 257, "MTH": 143, "MTK": 174, "MTM": 260, "MTO": 23,
            "MTR": 199, "MUH": 29, "MUK": 40, "MUT": 126, "MUZ": 128,
            "MYZ": 309, "NAE": 259, "NTH": 263, "ODS": 161, "PAZ": 151,
            "PEM": 64, "PET": 17, "PHE": 262, "PHY": 147, "PREP": 203,
            "RES": 36, "ROS": 307, "RUS": 237, "SBP": 21, "SEC": 308,
            "SED": 288, "SEN": 171, "SES": 124, "SGI": 291, "SNT": 193,
            "SPA": 172, "STA": 37, "STI": 159, "TDW": 261, "TEB": 121,
            "TEK": 13, "TEL": 57, "TER": 49, "TES": 269, "THO": 129,
            "TRN": 65, "TRS": 215, "TRZ": 170, "TUR": 34, "UCK": 25,
            "ULP": 195, "UZB": 24, "VBA": 306, "X100": 198, "YTO": 213,
            "YZV": 221
        }
    
    def validate_course_code(self, course_code: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Ders kodunu doğrular
        Format: XXX XXX (örn: EHB 313E, MAT 101)
        Returns: (is_valid, error_message, branch_id)
        """
        if not course_code:
            return False, "Ders kodu boş olamaz", None
        
        # Boşlukları temizle ve büyük harfe çevir
        course_code = course_code.strip().upper()
        
        # Format kontrolü: XXX XXX veya XXX XXXE
        pattern = r'^([A-Z]{2,4})\s+(\d{3}[A-Z]?)$'
        match = re.match(pattern, course_code)
        
        if not match:
            return False, "Geçersiz ders kodu formatı. Örnek: EHB 313E, MAT 101", None
        
        branch_code = match.group(1)
        course_number = match.group(2)
        
        # Branş kodunu kontrol et
        if branch_code not in self.branch_mapping:
            available_branches = list(self.branch_mapping.keys())[:10]  # İlk 10'u göster
            return False, f"Geçersiz branş kodu: {branch_code}. Mevcut branşlar: {', '.join(available_branches)}...", None
        
        branch_id = self.branch_mapping[branch_code]
        
        return True, None, branch_id
    
    def get_available_branches(self) -> List[str]:
        """Mevcut branş kodlarını döndürür"""
        return list(self.branch_mapping.keys())
    
    def get_branch_name(self, branch_code: str) -> Optional[str]:
        """Branş kodunun açıklamasını döndürür"""
        # Bu fonksiyon ileride genişletilebilir
        return branch_code
    
    def format_course_code(self, course_code: str) -> str:
        """Ders kodunu standart formata çevirir"""
        if not course_code:
            return ""
        
        # Boşlukları temizle ve büyük harfe çevir
        formatted = course_code.strip().upper()
        
        # Tek boşluk bırak
        formatted = re.sub(r'\s+', ' ', formatted)
        
        return formatted
    
    def is_valid_course_format(self, course_code: str) -> bool:
        """Sadece format kontrolü yapar, branş kodunu kontrol etmez"""
        if not course_code:
            return False
        
        course_code = course_code.strip().upper()
        pattern = r'^([A-Z]{2,4})\s+(\d{3}[A-Z]?)$'
        return bool(re.match(pattern, course_code))
