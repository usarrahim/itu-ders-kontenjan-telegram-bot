from typing import Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class DersProgramList:
    ders_tanimi_id: int
    akademik_donem_kodu: int
    crn: int
    ders_kodu: str
    ders_brans_kodu_id: int
    dil_kodu: str
    program_seviye_tipi: str
    ders_adi: str
    ogretim_yontemi: str
    ad_soyad: str
    mekan_adi: str
    gun_adi_tr: str
    gun_adi_en: str
    baslangic_saati: str
    bitis_saati: str
    webde_goster: bool
    bina_kodu: str
    kontenjan: int
    ogrenci_sayisi: int
    program_seviye_tipi_id: int
    rezervasyon: str
    sinif_program: str
    on_sart: str
    sinif_onsart: str

    def __init__(self, ders_tanimi_id: int, akademik_donem_kodu: int, crn: int, ders_kodu: str, ders_brans_kodu_id: int, dil_kodu: str, program_seviye_tipi: str, ders_adi: str, ogretim_yontemi: str, ad_soyad: str, mekan_adi: str, gun_adi_tr: str, gun_adi_en: str, baslangic_saati: str, bitis_saati: str, webde_goster: bool, bina_kodu: str, kontenjan: int, ogrenci_sayisi: int, program_seviye_tipi_id: int, rezervasyon: str, sinif_program: str, on_sart: str, sinif_onsart: str) -> None:
        self.ders_tanimi_id = ders_tanimi_id
        self.akademik_donem_kodu = akademik_donem_kodu
        self.crn = crn
        self.ders_kodu = ders_kodu
        self.ders_brans_kodu_id = ders_brans_kodu_id
        self.dil_kodu = dil_kodu
        self.program_seviye_tipi = program_seviye_tipi
        self.ders_adi = ders_adi
        self.ogretim_yontemi = ogretim_yontemi
        self.ad_soyad = ad_soyad
        self.mekan_adi = mekan_adi
        self.gun_adi_tr = gun_adi_tr
        self.gun_adi_en = gun_adi_en
        self.baslangic_saati = baslangic_saati
        self.bitis_saati = bitis_saati
        self.webde_goster = webde_goster
        self.bina_kodu = bina_kodu
        self.kontenjan = kontenjan
        self.ogrenci_sayisi = ogrenci_sayisi
        self.program_seviye_tipi_id = program_seviye_tipi_id
        self.rezervasyon = rezervasyon
        self.sinif_program = sinif_program
        self.on_sart = on_sart
        self.sinif_onsart = sinif_onsart

    @staticmethod
    def from_dict(obj: Any) -> 'DersProgramList':
        assert isinstance(obj, dict)
        ders_tanimi_id = from_int(obj.get("dersTanimiId"))
        akademik_donem_kodu = int(from_str(obj.get("akademikDonemKodu")))
        crn = int(from_str(obj.get("crn")))
        ders_kodu = from_str(obj.get("dersKodu"))
        ders_brans_kodu_id = from_int(obj.get("dersBransKoduId"))
        dil_kodu = from_str(obj.get("dilKodu"))
        program_seviye_tipi = from_str(obj.get("programSeviyeTipi"))
        ders_adi = from_str(obj.get("dersAdi"))
        ogretim_yontemi = from_str(obj.get("ogretimYontemi"))
        ad_soyad = from_str(obj.get("adSoyad"))
        mekan_adi = from_str(obj.get("mekanAdi"))
        gun_adi_tr = from_str(obj.get("gunAdiTR"))
        gun_adi_en = from_str(obj.get("gunAdiEN"))
        baslangic_saati = from_str(obj.get("baslangicSaati"))
        bitis_saati = from_str(obj.get("bitisSaati"))
        webde_goster = from_bool(obj.get("webdeGoster"))
        bina_kodu = from_str(obj.get("binaKodu"))
        kontenjan = from_int(obj.get("kontenjan"))
        ogrenci_sayisi = from_int(obj.get("ogrenciSayisi"))
        program_seviye_tipi_id = from_int(obj.get("programSeviyeTipiId"))
        rezervasyon = from_str(obj.get("rezervasyon"))
        sinif_program = from_str(obj.get("sinifProgram"))
        on_sart = from_str(obj.get("onSart"))
        sinif_onsart = from_str(obj.get("sinifOnsart"))
        return DersProgramList(ders_tanimi_id, akademik_donem_kodu, crn, ders_kodu, ders_brans_kodu_id, dil_kodu, program_seviye_tipi, ders_adi, ogretim_yontemi, ad_soyad, mekan_adi, gun_adi_tr, gun_adi_en, baslangic_saati, bitis_saati, webde_goster, bina_kodu, kontenjan, ogrenci_sayisi, program_seviye_tipi_id, rezervasyon, sinif_program, on_sart, sinif_onsart)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dersTanimiId"] = from_int(self.ders_tanimi_id)
        result["akademikDonemKodu"] = from_str(str(self.akademik_donem_kodu))
        result["crn"] = from_str(str(self.crn))
        result["dersKodu"] = from_str(self.ders_kodu)
        result["dersBransKoduId"] = from_int(self.ders_brans_kodu_id)
        result["dilKodu"] = from_str(self.dil_kodu)
        result["programSeviyeTipi"] = from_str(self.program_seviye_tipi)
        result["dersAdi"] = from_str(self.ders_adi)
        result["ogretimYontemi"] = from_str(self.ogretim_yontemi)
        result["adSoyad"] = from_str(self.ad_soyad)
        result["mekanAdi"] = from_str(self.mekan_adi)
        result["gunAdiTR"] = from_str(self.gun_adi_tr)
        result["gunAdiEN"] = from_str(self.gun_adi_en)
        result["baslangicSaati"] = from_str(self.baslangic_saati)
        result["bitisSaati"] = from_str(self.bitis_saati)
        result["webdeGoster"] = from_bool(self.webde_goster)
        result["binaKodu"] = from_str(self.bina_kodu)
        result["kontenjan"] = from_int(self.kontenjan)
        result["ogrenciSayisi"] = from_int(self.ogrenci_sayisi)
        result["programSeviyeTipiId"] = from_int(self.program_seviye_tipi_id)
        result["rezervasyon"] = from_str(self.rezervasyon)
        result["sinifProgram"] = from_str(self.sinif_program)
        result["onSart"] = from_str(self.on_sart)
        result["sinifOnsart"] = from_str(self.sinif_onsart)
        return result


class DersListesi:
    ders_program_list: List[DersProgramList]
    guncellenme_saati: str

    def __init__(self, ders_program_list: List[DersProgramList], guncellenme_saati: str) -> None:
        self.ders_program_list = ders_program_list
        self.guncellenme_saati = guncellenme_saati

    @staticmethod
    def from_dict(obj: Any) -> 'DersListesi':
        assert isinstance(obj, dict)
        ders_program_list = from_list(DersProgramList.from_dict, obj.get("dersProgramList"))
        guncellenme_saati = from_str(obj.get("guncellenmeSaati"))
        return DersListesi(ders_program_list, guncellenme_saati)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dersProgramList"] = from_list(lambda x: to_class(DersProgramList, x), self.ders_program_list)
        result["guncellenmeSaati"] = from_str(self.guncellenme_saati)
        return result


def ders_listesi_from_dict(s: Any) -> DersListesi:
    return DersListesi.from_dict(s)


def ders_listesi_to_dict(x: DersListesi) -> Any:
    return to_class(DersListesi, x)
