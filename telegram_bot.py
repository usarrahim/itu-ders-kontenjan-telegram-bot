import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import DatabaseManager
from course_validator import CourseValidator
from bot import check_list, check_contenjan
import os

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Veritabanı ve validator
db = DatabaseManager()
validator = CourseValidator()

# Bot token'ı environment variable'dan al
BOT_TOKEN = os.getenv('BOT_TOKEN', '8354560097:AAHifiQmARkiVHj4IUHtsvE3iNgIeT4BpuU')

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Bot komutlarını ayarlar"""
        # Komutlar
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("add_course", self.add_course_command))
        self.application.add_handler(CommandHandler("remove_course", self.remove_course_command))
        self.application.add_handler(CommandHandler("list_courses", self.list_courses_command))
        self.application.add_handler(CommandHandler("remove_all", self.remove_all_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Mesaj handler'ları
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot başlatma komutu"""
        user = update.effective_user
        
        # Kullanıcıyı veritabanına ekle
        db.add_user(
            user_id=user.id,
            chat_id=str(update.effective_chat.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
🎓 **ITU Ders Kontenjan Botu'na Hoş Geldiniz!**

Merhaba {user.first_name}! 👋

Bu bot, İTÜ ders programındaki kontenjan değişikliklerini takip eder ve size bildirim gönderir.

**Kullanılabilir Komutlar:**
• `/add_course` - Ders ekle
• `/remove_course` - Ders kaldır  
• `/list_courses` - Derslerimi listele
• `/remove_all` - Tüm dersleri kaldır
• `/status` - Bot durumu
• `/help` - Yardım

**Örnek ders kodu:** `EHB 313E`, `MAT 101`, `FIZ 101E`

Hemen bir ders eklemek için `/add_course` komutunu kullanabilirsiniz!
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yardım komutu"""
        help_text = """
📚 **Bot Kullanım Kılavuzu**

**Komutlar:**
• `/start` - Botu başlat
• `/add_course` - Yeni ders ekle
• `/remove_course` - Ders kaldır
• `/list_courses` - Mevcut derslerinizi görün
• `/remove_all` - Tüm dersleri kaldır
• `/status` - Bot durumu
• `/help` - Bu yardım mesajı

**Ders Kodu Formatı:**
Ders kodları şu formatta olmalıdır:
• `XXX XXX` (örn: MAT 101)
• `XXX XXXE` (örn: EHB 313E)

**Mevcut Branş Kodları:**
EHB, MAT, FIZ, KIM, BLG, ELK, MAK, MIM, INS, GID ve daha fazlası...

**Nasıl Çalışır:**
1. `/add_course` ile ders ekleyin
2. Bot her 4 dakikada bir kontenjan kontrol eder
3. Kontenjan açıldığında size bildirim gelir

**Örnek Kullanım:**
```
/add_course EHB 313E
/add_course MAT 101
/list_courses
```
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def add_course_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders ekleme komutu"""
        if not context.args:
            await update.message.reply_text(
                "❌ **Ders kodu gerekli!**\n\n"
                "Kullanım: `/add_course EHB 313E`\n"
                "Örnek: `/add_course MAT 101`",
                parse_mode='Markdown'
            )
            return
        
        course_code = ' '.join(context.args)
        user_id = update.effective_user.id
        
        # Ders kodunu doğrula
        is_valid, error_msg, branch_id = validator.validate_course_code(course_code)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ **Hata:** {error_msg}\n\n"
                "Doğru format: `XXX XXX` veya `XXX XXXE`\n"
                "Örnek: `EHB 313E`, `MAT 101`",
                parse_mode='Markdown'
            )
            return
        
        # Dersi kullanıcıya ekle
        success = db.add_course_to_user(user_id, course_code, branch_id)
        
        if success:
            await update.message.reply_text(
                f"✅ **Ders eklendi!**\n\n"
                f"📚 Ders: `{course_code}`\n"
                f"🏫 Branş ID: {branch_id}\n\n"
                f"Bu ders için kontenjan bildirimleri alacaksınız.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ **Hata:** Ders eklenirken bir sorun oluştu. Lütfen tekrar deneyin.",
                parse_mode='Markdown'
            )
    
    async def remove_course_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders kaldırma komutu"""
        if not context.args:
            # Kullanıcının derslerini listele ve seçim yapmasını sağla
            user_id = update.effective_user.id
            courses = db.get_user_courses(user_id)
            
            if not courses:
                await update.message.reply_text(
                    "📝 **Ders listeniz boş!**\n\n"
                    "Önce `/add_course` ile ders ekleyin.",
                    parse_mode='Markdown'
                )
                return
            
            # Ders listesi ile inline keyboard oluştur
            keyboard = []
            for course in courses:
                keyboard.append([InlineKeyboardButton(
                    f"❌ {course['course_code']}", 
                    callback_data=f"remove_{course['course_code']}"
                )])
            
            keyboard.append([InlineKeyboardButton("❌ Tümünü Kaldır", callback_data="remove_all")])
            keyboard.append([InlineKeyboardButton("❌ İptal", callback_data="cancel")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            course_list = "\n".join([f"• {course['course_code']}" for course in courses])
            
            await update.message.reply_text(
                f"📚 **Hangi dersi kaldırmak istiyorsunuz?**\n\n"
                f"**Mevcut dersleriniz:**\n{course_list}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        course_code = ' '.join(context.args)
        user_id = update.effective_user.id
        
        # Dersi kaldır
        success = db.remove_course_from_user(user_id, course_code)
        
        if success:
            await update.message.reply_text(
                f"✅ **Ders kaldırıldı!**\n\n"
                f"📚 Ders: `{course_code}`\n\n"
                f"Bu ders için artık bildirim almayacaksınız.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Hata:** `{course_code}` dersi bulunamadı veya kaldırılamadı.",
                parse_mode='Markdown'
            )
    
    async def list_courses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders listesi komutu"""
        user_id = update.effective_user.id
        courses = db.get_user_courses(user_id)
        
        if not courses:
            await update.message.reply_text(
                "📝 **Ders listeniz boş!**\n\n"
                "Ders eklemek için `/add_course` komutunu kullanın.\n"
                "Örnek: `/add_course EHB 313E`",
                parse_mode='Markdown'
            )
            return
        
        course_list = "\n".join([f"• {course['course_code']}" for course in courses])
        
        await update.message.reply_text(
            f"📚 **Ders Listeniz** ({len(courses)} ders)\n\n"
            f"{course_list}\n\n"
            f"Yeni ders eklemek için: `/add_course DERS_KODU`\n"
            f"Ders kaldırmak için: `/remove_course`",
            parse_mode='Markdown'
        )
    
    async def remove_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tüm dersleri kaldırma komutu"""
        user_id = update.effective_user.id
        courses = db.get_user_courses(user_id)
        
        if not courses:
            await update.message.reply_text(
                "📝 **Ders listeniz zaten boş!**",
                parse_mode='Markdown'
            )
            return
        
        # Onay için inline keyboard
        keyboard = [
            [InlineKeyboardButton("✅ Evet, Tümünü Kaldır", callback_data="confirm_remove_all")],
            [InlineKeyboardButton("❌ İptal", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        course_list = "\n".join([f"• {course['course_code']}" for course in courses])
        
        await update.message.reply_text(
            f"⚠️ **Tüm dersleri kaldırmak istediğinizden emin misiniz?**\n\n"
            f"**Kaldırılacak dersler:**\n{course_list}\n\n"
            f"Bu işlem geri alınamaz!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot durumu komutu"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        courses = db.get_user_courses(user_id)
        
        if not user_data:
            await update.message.reply_text(
                "❌ **Kullanıcı bulunamadı!**\n\n"
                "Lütfen `/start` komutunu kullanın.",
                parse_mode='Markdown'
            )
            return
        
        status_text = f"""
🤖 **Bot Durumu**

👤 **Kullanıcı Bilgileri:**
• Ad: {user_data.get('first_name', 'Bilinmiyor')}
• Kullanıcı Adı: @{user_data.get('username', 'Bilinmiyor')}
• Durum: {'✅ Aktif' if user_data.get('is_active') else '❌ Pasif'}

📚 **Ders Bilgileri:**
• Toplam ders sayısı: {len(courses)}
• Dersler: {', '.join([course['course_code'] for course in courses]) if courses else 'Yok'}

🔄 **Bot Özellikleri:**
• Kontrol sıklığı: Her 4 dakika
• Bildirim: Kontenjan açıldığında
• Desteklenen format: XXX XXX, XXX XXXE
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Genel mesaj handler'ı"""
        await update.message.reply_text(
            "🤖 **Merhaba!**\n\n"
            "Bot komutlarını kullanmak için `/help` yazın.\n"
            "Ders eklemek için `/add_course DERS_KODU` kullanın.",
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback query handler"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith("remove_"):
            if data == "remove_all":
                # Tüm dersleri kaldır
                courses = db.get_user_courses(user_id)
                for course in courses:
                    db.remove_course_from_user(user_id, course['course_code'])
                
                await query.edit_message_text(
                    f"✅ **Tüm dersler kaldırıldı!**\n\n"
                    f"Toplam {len(courses)} ders kaldırıldı.\n"
                    f"Yeni ders eklemek için `/add_course` kullanın.",
                    parse_mode='Markdown'
                )
            else:
                # Belirli bir dersi kaldır
                course_code = data.replace("remove_", "")
                success = db.remove_course_from_user(user_id, course_code)
                
                if success:
                    await query.edit_message_text(
                        f"✅ **Ders kaldırıldı!**\n\n"
                        f"📚 Ders: `{course_code}`\n"
                        f"Bu ders için artık bildirim almayacaksınız.",
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        f"❌ **Hata:** Ders kaldırılamadı.",
                        parse_mode='Markdown'
                    )
        
        elif data == "confirm_remove_all":
            # Tüm dersleri kaldır onayı
            courses = db.get_user_courses(user_id)
            for course in courses:
                db.remove_course_from_user(user_id, course['course_code'])
            
            await query.edit_message_text(
                f"✅ **Tüm dersler kaldırıldı!**\n\n"
                f"Toplam {len(courses)} ders kaldırıldı.\n"
                f"Yeni ders eklemek için `/add_course` kullanın.",
                parse_mode='Markdown'
            )
        
        elif data == "cancel":
            await query.edit_message_text(
                "❌ **İşlem iptal edildi.**",
                parse_mode='Markdown'
            )
    
    async def send_notification(self, chat_id: str, message: str):
        """Bildirim gönder"""
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Bildirim gönderme hatası: {e}")
    
    def run(self):
        """Botu çalıştır"""
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_async(self):
        """Botu async olarak çalıştır"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
