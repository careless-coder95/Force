import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import config
from database import db
from handlers import admin_handler, user_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # User handlers
    app.add_handler(CommandHandler("start", user_handler.start))
    app.add_handler(CommandHandler("admin", admin_handler.admin_panel))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(admin_handler.handle_admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(user_handler.verify_callback, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(user_handler.handle_menu_button, pattern="^menu_btn_"))
    
    # Message handler for admin input
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, admin_handler.handle_input))

    logger.info("Bot started!")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
