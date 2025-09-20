import time
import httpx
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from class_yapisi import DersProgramList, DersListesi
from database import DatabaseManager
from telegram_bot import TelegramBot
import os
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Veritabanı
db = DatabaseManager()

def parse_html_ders_list(html_text, branscode):
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        table = soup.find('table', id='dersProgramContainer')
        if table is None:
            return DersListesi(ders_program_list=[], guncellenme_saati="")
        tbody = table.find('tbody')
        if tbody is None:
            return DersListesi(ders_program_list=[], guncellenme_saati="")

        dersler = []
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) < 11:
                continue

            def td_text(idx):
                if idx >= len(tds):
                    return "-"
                return tds[idx].get_text(strip=True).replace('\r', ' ').replace('\n', ' ')

            crn_text = td_text(0)
            ders_kodu_text = tds[1].get_text(strip=True) if len(tds) > 1 else "-"
            ders_adi_text = td_text(2)
            ogretim_yontemi_text = td_text(3)
            ad_soyad_text = td_text(4)
            bina_kodu_text = tds[5].get_text(strip=True) if len(tds) > 5 else "-"
            gun_text = td_text(6)
            saat_text = td_text(7)
            derslik_text = td_text(8)
            kontenjan_text = td_text(9)
            ogrenci_sayisi_text = td_text(10)
            rezervasyon_text = td_text(11) if len(tds) > 11 else "-"
            programlar_text = td_text(12) if len(tds) > 12 else "-"
            on_sart_text = td_text(13) if len(tds) > 13 else "-"
            sinif_onsart_text = td_text(14) if len(tds) > 14 else "-"

            try:
                crn = int(crn_text) if crn_text.isdigit() else 0
            except Exception:
                crn = 0

            try:
                kontenjan = int(kontenjan_text) if kontenjan_text.isdigit() else 0
            except Exception:
                kontenjan = 0

            try:
                ogrenci_sayisi = int(ogrenci_sayisi_text) if ogrenci_sayisi_text.isdigit() else 0
            except Exception:
                ogrenci_sayisi = 0

            baslangic = "-"
            bitis = "-"
            if '/' in saat_text:
                parts = saat_text.split('/')
                if len(parts) >= 2:
                    baslangic = parts[0]
                    bitis = parts[1]

            ders = DersProgramList(
                ders_tanimi_id=0,
                akademik_donem_kodu=0,
                crn=crn,
                ders_kodu=ders_kodu_text,
                ders_brans_kodu_id=branscode,
                dil_kodu="",
                program_seviye_tipi="LS",
                ders_adi=ders_adi_text,
                ogretim_yontemi=ogretim_yontemi_text,
                ad_soyad=ad_soyad_text,
                mekan_adi=derslik_text,
                gun_adi_tr=gun_text,
                gun_adi_en="",
                baslangic_saati=baslangic,
                bitis_saati=bitis,
                webde_goster=True,
                bina_kodu=bina_kodu_text,
                kontenjan=kontenjan,
                ogrenci_sayisi=ogrenci_sayisi,
                program_seviye_tipi_id=2,
                rezervasyon=rezervasyon_text,
                sinif_program=programlar_text,
                on_sart=on_sart_text,
                sinif_onsart=sinif_onsart_text
            )
            dersler.append(ders)

        return DersListesi(ders_program_list=dersler, guncellenme_saati="")
    except Exception:
        return DersListesi(ders_program_list=[], guncellenme_saati="")

async def check_contenjan(derscode, derslistmy, branch_id):
    if derslistmy is None:
        return
    
    # Bu ders için bildirim alacak kullanıcıları bul
    users = db.get_users_by_course(derscode, branch_id)
    
    for i in derslistmy.ders_program_list:
        if (i.ders_kodu == derscode) and (i.ogrenci_sayisi != i.kontenjan):
            available_spots = i.kontenjan - i.ogrenci_sayisi
            message = f"🎓 **Kontenjan Açıldı!**\n\n" \
                     f"📚 **Ders:** {i.ders_adi}\n" \
                     f"🔢 **Ders Kodu:** {i.ders_kodu}\n" \
                     f"📊 **Mevcut Kontenjan:** {available_spots}\n" \
                     f"🏫 **CRN:** {i.crn}\n" \
                     f"👨‍🏫 **Öğretim Üyesi:** {i.ad_soyad}\n" \
                     f"📍 **Derslik:** {i.mekan_adi}\n" \
                     f"🕐 **Saat:** {i.baslangic_saati} - {i.bitis_saati}\n" \
                     f"📅 **Gün:** {i.gun_adi_tr}"
            
            # Tüm kullanıcılara bildirim gönder
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user['chat_id'], 
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"Bildirim gönderildi: {user['chat_id']} - {derscode}")
                except Exception as e:
                    logger.error(f"Bildirim gönderme hatası: {e} - {user['chat_id']}")
    

async def check_list(branscode):
    try:
        async with httpx.AsyncClient() as client:
            link = f"https://obs.itu.edu.tr/public/DersProgram/DersProgramSearch?ProgramSeviyeTipiAnahtari=LS&dersBransKoduId={branscode}"
            response = await client.get(link)
            print(f"API Status Code: {response.status_code}")
            print(f"Response Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                # Response içeriğini kontrol et
                response_text = response.text
                print(f"Response Length: {len(response_text)}")
                print(f"First 200 chars: {response_text[:200]}")
                
                # JSON parsing'i dene
                try:
                    response_json = response.json()
                    print("JSON parsing başarılı")
                    derslist = DersListesi.from_dict(response_json)
                    return derslist
                except Exception as json_error:
                    print(f"JSON parsing hatası: {json_error}")
                    # HTML parse fallback
                    derslist = parse_html_ders_list(response_text, branscode)
                    print(f"HTML parse ile {len(derslist.ders_program_list)} ders bulundu")
                    return derslist
            else:
                print(f"Hata: {response.status_code} hatası aldınız.")
                print(f"Response text: {response.text}")
                await bot.send_message(chat_id=CHAT_ID, text=f"Hata: {response.status_code} hatası aldınız.")
                return None
    except Exception as e:
        print(f"API çağrısında hata: {e}")
        await bot.send_message(chat_id=CHAT_ID, text=f"API çağrısında hata: {e}")
        return None
  




# Telegram bot API token
API_TOKEN = os.getenv('BOT_TOKEN', '8354560097:AAHifiQmARkiVHj4IUHtsvE3iNgIeT4BpuU')

# Bot oluşturma
bot = Bot(token=API_TOKEN)

async def main():
    """Ana kontrol fonksiyonu - tüm kullanıcıların derslerini kontrol eder"""
    try:
        logger.info("Ders programı kontrol ediliyor...")
        
        # Tüm aktif kullanıcıları ve derslerini al
        users = db.get_all_active_users()
        
        if not users:
            logger.info("Aktif kullanıcı bulunamadı.")
            return
        
        # Dersleri branş koduna göre grupla
        courses_by_branch = {}
        for user in users:
            for course in user.get('courses', []):
                branch_id = course['branch_id']
                course_code = course['course_code']
                
                if branch_id not in courses_by_branch:
                    courses_by_branch[branch_id] = set()
                courses_by_branch[branch_id].add(course_code)
        
        # Her branş için kontrol yap
        for branscode, ders_kodlari in courses_by_branch.items():
            logger.info(f"Branş {branscode} kontrol ediliyor: {list(ders_kodlari)}")
            derslistmy = await check_list(branscode=branscode)
            
            if derslistmy:
                for ders_kodu in ders_kodlari:
                    await check_contenjan(derscode=ders_kodu, derslistmy=derslistmy, branch_id=branscode)
        
        logger.info("Kontrol tamamlandı.")
        
    except Exception as e:
        logger.error(f"Ana fonksiyonda hata: {e}")

async def run_monitoring():
    """Kontenjan kontrol döngüsü"""
    logger.info("Kontenjan kontrol botu başlatıldı.")
    
    while True:
        try:
            await main()
            await asyncio.sleep(240)  # 4 dakika bekle
        except KeyboardInterrupt:
            logger.info("Bot durduruldu.")
            break
        except Exception as e:
            logger.error(f"Bot çalışırken hata: {e}")
            await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle

async def run_telegram_bot():
    """Telegram bot'u çalıştır"""
    telegram_bot = TelegramBot()
    await telegram_bot.run_async()

async def main_async():
    """Ana async fonksiyon - hem Telegram bot hem de monitoring"""
    # İki görevi paralel çalıştır
    await asyncio.gather(
        run_monitoring(),
        run_telegram_bot()
    )

if __name__ == "__main__":
    asyncio.run(main_async())
