class CourseValidator:
    """Ders kodu doğrulama ve branş ID mapping"""
    
    # Branş kodları ve ID'leri
    BRANCH_MAPPING = {
        'EHB': 196,  # Elektronik ve Haberleşme Mühendisliği
        'MAT': 26,   # Matematik
        'FIZ': 28,   # Fizik
        'KIM': 30,   # Kimya
        'BIO': 30,   # Biyoloji
        'BIL': 32,   # Bilgisayar Mühendisliği
        'MAK': 34,   # Makine Mühendisliği
        'INS': 36,   # İnşaat Mühendisliği
        'ELE': 38,   # Elektrik Mühendisliği
        'END': 40,   # Endüstri Mühendisliği
        'GID': 42,   # Gıda Mühendisliği
        'CEV': 44,   # Çevre Mühendisliği
        'PET': 46,   # Petrol ve Doğalgaz Mühendisliği
        'MET': 48,   # Metalurji ve Malzeme Mühendisliği
        'MAD': 50,   # Maden Mühendisliği
        'JEO': 52,   # Jeoloji Mühendisliği
        'JEF': 54,   # Jeofizik Mühendisliği
        'GEM': 56,   # Gemi Mühendisliği
        'UCA': 58,   # Uçak Mühendisliği
        'UZA': 60,   # Uzay Mühendisliği
        'TEK': 62,   # Tekstil Mühendisliği
        'KON': 66,   # Kontrol Mühendisliği
        'KIM': 64,   # Kimya Mühendisliği
        'MIM': 68,   # Mimarlık
        'SEH': 70,   # Şehir ve Bölge Planlama
        'GEO': 72,   # Geomatik Mühendisliği
        'GID': 74,   # Gıda Mühendisliği
        'CEV': 76,   # Çevre Mühendisliği
        'PET': 78,   # Petrol ve Doğalgaz Mühendisliği
        'MET': 80,   # Metalurji ve Malzeme Mühendisliği
        'MAD': 82,   # Maden Mühendisliği
        'JEO': 84,   # Jeoloji Mühendisliği
        'JEF': 86,   # Jeofizik Mühendisliği
        'GEM': 88,   # Gemi Mühendisliği
        'UCA': 90,   # Uçak Mühendisliği
        'UZA': 92,   # Uzay Mühendisliği
        'TEK': 94,   # Tekstil Mühendisliği
    }
    
    @classmethod
    def validate_course_code(cls, course_code: str) -> tuple[bool, int, str]:
        """
        Ders kodunu doğrula
        Returns: (is_valid, branch_id, formatted_code)
        """
        if not course_code or not isinstance(course_code, str):
            return False, 0, ""
        
        # Boşlukları temizle ve büyük harfe çevir
        course_code = course_code.strip().upper()
        
        # Format kontrolü: "EHB 313E" veya "EHB313E" gibi
        parts = course_code.split()
        if len(parts) == 2:
            branch_code = parts[0]
            course_number = parts[1]
        elif len(parts) == 1 and len(course_code) >= 6:
            # "EHB313E" formatı
            branch_code = course_code[:3]
            course_number = course_code[3:]
        else:
            return False, 0, ""
        
        # Branş kodu kontrolü
        if branch_code not in cls.BRANCH_MAPPING:
            return False, 0, ""
        
        branch_id = cls.BRANCH_MAPPING[branch_code]
        formatted_code = f"{branch_code} {course_number}"
        
        return True, branch_id, formatted_code
    
    @classmethod
    def get_available_branches(cls) -> list:
        """Mevcut branş kodlarını getir"""
        return list(cls.BRANCH_MAPPING.keys())
    
    @classmethod
    def get_branch_name(cls, branch_code: str) -> str:
        """Branş adını getir"""
        branch_names = {
            'EHB': 'Elektronik ve Haberleşme Mühendisliği',
            'MAT': 'Matematik',
            'FIZ': 'Fizik',
            'KIM': 'Kimya',
            'BIO': 'Biyoloji',
            'BIL': 'Bilgisayar Mühendisliği',
            'MAK': 'Makine Mühendisliği',
            'INS': 'İnşaat Mühendisliği',
            'ELE': 'Elektrik Mühendisliği',
            'END': 'Endüstri Mühendisliği',
            'GID': 'Gıda Mühendisliği',
            'CEV': 'Çevre Mühendisliği',
            'PET': 'Petrol ve Doğalgaz Mühendisliği',
            'MET': 'Metalurji ve Malzeme Mühendisliği',
            'MAD': 'Maden Mühendisliği',
            'JEO': 'Jeoloji Mühendisliği',
            'JEF': 'Jeofizik Mühendisliği',
            'GEM': 'Gemi Mühendisliği',
            'UCA': 'Uçak Mühendisliği',
            'UZA': 'Uzay Mühendisliği',
            'TEK': 'Tekstil Mühendisliği',
            'KON': 'Kontrol Mühendisliği',
            'MIM': 'Mimarlık',
            'SEH': 'Şehir ve Bölge Planlama',
            'GEO': 'Geomatik Mühendisliği',
        }
        return branch_names.get(branch_code, branch_code)
