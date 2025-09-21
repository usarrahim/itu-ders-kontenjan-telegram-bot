import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import DatabaseManager
from course_validator import CourseValidator

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.db = DatabaseManager()
        self.validator = CourseValidator()
        
        # Application oluştur
        self.application = Application.builder().token(bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Komut işleyicilerini ayarla"""
        # Komutlar
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("add", self.add_course_command))
        self.application.add_handler(CommandHandler("remove", self.remove_course_command))
        self.application.add_handler(CommandHandler("list", self.list_courses_command))
        self.application.add_handler(CommandHandler("removeall", self.remove_all_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Callback query handler (inline keyboard için)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Mesaj handler (ders kodu eklemek için)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komutu"""
        user = update.effective_user
        
        # Kullanıcıyı veritabanına ekle
        self.db.add_user(
            user_id=user.id,
            chat_id=update.effective_chat.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
🎓 **İTÜ Ders Kontenjan Takip Botu'na Hoş Geldiniz!**

Merhaba {user.first_name}! 👋

Bu bot ile İTÜ derslerinin kontenjan değişikliklerini takip edebilirsiniz.

**📋 Kullanılabilir Komutlar:**
• `/add <ders_kodu>` - Ders ekle (örn: /add EHB 313E)
• `/remove <ders_kodu>` - Ders kaldır
• `/list` - Takip ettiğiniz dersleri listele
• `/removeall` - Tüm dersleri kaldır
• `/status` - Bot durumunuzu görüntüle
• `/help` - Yardım

**🚀 Başlamak için:**
`/add EHB 313E` yazarak ilk dersinizi ekleyebilirsiniz!
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yardım komutu"""
        help_text = """
📚 **İTÜ Ders Kontenjan Takip Botu - Yardım**

**🎯 Bot Ne Yapar?**
Bu bot, İTÜ OBS'deki ders kontenjanlarını sürekli kontrol eder ve kontenjan açıldığında size bildirim gönderir.

**📋 Komutlar:**

**➕ Ders Ekleme:**
`/add EHB 313E` - EHB 313E dersini takip listesine ekler
`/add MAT 101` - MAT 101 dersini takip listesine ekler

**➖ Ders Kaldırma:**
`/remove EHB 313E` - Belirtilen dersi listeden kaldırır
`/removeall` - Tüm dersleri kaldırır

**📊 Bilgi Komutları:**
`/list` - Takip ettiğiniz dersleri gösterir
`/status` - Bot durumunuzu gösterir

**💡 Örnek Kullanım:**
1. `/add EHB 313E` - Ders ekle
2. `/add MAT 101` - Başka ders ekle
3. `/list` - Derslerinizi kontrol et
4. Bot otomatik olarak kontenjan değişikliklerini takip eder

**⚠️ Not:** Bot her 4 dakikada bir kontrol yapar. Kontenjan açıldığında anında bildirim alırsınız.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def add_course_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders ekleme komutu"""
        if not context.args:
            await update.message.reply_text(
                "❌ **Hata:** Ders kodu belirtmelisiniz.\n\n"
                "**Kullanım:** `/add EHB 313E`\n"
                "**Örnek:** `/add MAT 101`",
                parse_mode='Markdown'
            )
            return
        
        course_code = ' '.join(context.args)
        user_id = update.effective_user.id
        
        # Ders kodunu doğrula
        is_valid, branch_id, formatted_code = self.validator.validate_course_code(course_code)
        
        if not is_valid:
            available_branches = ', '.join(self.validator.get_available_branches()[:10])
            await update.message.reply_text(
                f"❌ **Geçersiz ders kodu:** `{course_code}`\n\n"
                f"**Doğru format:** `EHB 313E` veya `MAT 101`\n"
                f"**Mevcut branşlar:** {available_branches}...\n\n"
                f"**Örnek:** `/add EHB 313E`",
                parse_mode='Markdown'
            )
            return
        
        # Dersi kullanıcıya ekle
        success = self.db.add_course_to_user(user_id, formatted_code, branch_id)
        
        if success:
            branch_name = self.validator.get_branch_name(formatted_code.split()[0])
            await update.message.reply_text(
                f"✅ **Ders eklendi!**\n\n"
                f"📚 **Ders:** {formatted_code}\n"
                f"🏫 **Branş:** {branch_name}\n\n"
                f"Bu ders için kontenjan değişikliklerini takip edeceğim! 🔍",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"⚠️ **Ders zaten ekli!**\n\n"
                f"`{formatted_code}` dersi zaten takip listenizde.",
                parse_mode='Markdown'
            )
    
    async def remove_course_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders kaldırma komutu"""
        if not context.args:
            # Kullanıcının derslerini listele ve inline keyboard ile seçim yap
            user_id = update.effective_user.id
            courses = self.db.get_user_courses(user_id)
            
            if not courses:
                await update.message.reply_text(
                    "📝 **Takip ettiğiniz ders bulunmuyor.**\n\n"
                    "Ders eklemek için `/add EHB 313E` komutunu kullanın.",
                    parse_mode='Markdown'
                )
                return
            
            keyboard = []
            for course in courses:
                keyboard.append([InlineKeyboardButton(
                    f"❌ {course['course_code']}", 
                    callback_data=f"remove_{course['course_code']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🗑️ **Kaldırmak istediğiniz dersi seçin:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        course_code = ' '.join(context.args)
        user_id = update.effective_user.id
        
        # Ders kodunu formatla
        is_valid, _, formatted_code = self.validator.validate_course_code(course_code)
        if not is_valid:
            formatted_code = course_code.upper()
        
        # Dersi kaldır
        self.db.remove_course_from_user(user_id, formatted_code)
        
        await update.message.reply_text(
            f"✅ **Ders kaldırıldı!**\n\n"
            f"`{formatted_code}` dersi takip listenizden çıkarıldı.",
            parse_mode='Markdown'
        )
    
    async def list_courses_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ders listesi komutu"""
        user_id = update.effective_user.id
        courses = self.db.get_user_courses(user_id)
        
        if not courses:
            await update.message.reply_text(
                "📝 **Takip ettiğiniz ders bulunmuyor.**\n\n"
                "Ders eklemek için `/add EHB 313E` komutunu kullanın.",
                parse_mode='Markdown'
            )
            return
        
        course_list = "\n".join([f"• {course['course_code']}" for course in courses])
        
        await update.message.reply_text(
            f"📚 **Takip Ettiğiniz Dersler:**\n\n{course_list}\n\n"
            f"**Toplam:** {len(courses)} ders\n\n"
            f"**Ders eklemek için:** `/add DERS_KODU`\n"
            f"**Ders kaldırmak için:** `/remove DERS_KODU`",
            parse_mode='Markdown'
        )
    
    async def remove_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tüm dersleri kaldırma komutu"""
        user_id = update.effective_user.id
        courses = self.db.get_user_courses(user_id)
        
        if not courses:
            await update.message.reply_text(
                "📝 **Kaldırılacak ders bulunmuyor.**",
                parse_mode='Markdown'
            )
            return
        
        keyboard = [
            [InlineKeyboardButton("✅ Evet, Tümünü Kaldır", callback_data="confirm_remove_all")],
            [InlineKeyboardButton("❌ İptal", callback_data="cancel_remove_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        course_list = "\n".join([f"• {course['course_code']}" for course in courses])
        
        await update.message.reply_text(
            f"⚠️ **Tüm dersleri kaldırmak istediğinizden emin misiniz?**\n\n"
            f"**Kaldırılacak dersler:**\n{course_list}\n\n"
            f"**Toplam:** {len(courses)} ders",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Durum komutu"""
        user_id = update.effective_user.id
        user_info = self.db.get_user(user_id)
        courses = self.db.get_user_courses(user_id)
        
        if not user_info:
            await update.message.reply_text(
                "❌ **Kullanıcı bulunamadı.**\n\n"
                "Önce `/start` komutunu kullanın.",
                parse_mode='Markdown'
            )
            return
        
        status_text = f"""
🤖 **Bot Durumunuz**

👤 **Kullanıcı:** {user_info['first_name']} {user_info.get('last_name', '')}
🆔 **ID:** {user_info['user_id']}
📱 **Chat ID:** {user_info['chat_id']}
✅ **Durum:** {'Aktif' if user_info['is_active'] else 'Pasif'}

📚 **Takip Edilen Dersler:** {len(courses)}
        """
        
        if courses:
            course_list = "\n".join([f"• {course['course_code']}" for course in courses])
            status_text += f"\n\n**Dersler:**\n{course_list}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Genel mesaj işleyici"""
        text = update.message.text.strip()
        
        # Eğer mesaj ders kodu gibi görünüyorsa, otomatik ekle
        if len(text.split()) <= 2 and any(char.isdigit() for char in text):
            await update.message.reply_text(
                f"💡 **Ders eklemek için komut kullanın:**\n\n"
                f"`/add {text}`\n\n"
                f"**Örnek:** `/add EHB 313E`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❓ **Anlamadım.**\n\n"
                "Yardım için `/help` komutunu kullanın.",
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback query işleyici"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data.startswith("remove_"):
            course_code = data.replace("remove_", "")
            self.db.remove_course_from_user(user_id, course_code)
            
            await query.edit_message_text(
                f"✅ **Ders kaldırıldı!**\n\n"
                f"`{course_code}` dersi takip listenizden çıkarıldı.",
                parse_mode='Markdown'
            )
        
        elif data == "confirm_remove_all":
            courses = self.db.get_user_courses(user_id)
            for course in courses:
                self.db.remove_course_from_user(user_id, course['course_code'])
            
            await query.edit_message_text(
                f"✅ **Tüm dersler kaldırıldı!**\n\n"
                f"**Kaldırılan ders sayısı:** {len(courses)}\n\n"
                f"Yeni ders eklemek için `/add DERS_KODU` komutunu kullanın.",
                parse_mode='Markdown'
            )
        
        elif data == "cancel_remove_all":
            await query.edit_message_text(
                "❌ **İşlem iptal edildi.**\n\n"
                "Dersleriniz korundu.",
                parse_mode='Markdown'
            )
    
    async def send_notification(self, chat_id: int, message: str):
        """Bildirim gönder"""
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Bildirim gönderme hatası: {e}")
    
    async def run_async(self):
        """Bot'u asenkron çalıştır"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Bot çalışırken bekle
        try:
            await asyncio.Future()  # Sonsuz döngü
        except KeyboardInterrupt:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
