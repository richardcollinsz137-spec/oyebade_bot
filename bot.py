import os
import io
import logging
import asyncio
from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from pdf_handler import extract_text_from_pdf

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Professional greeting and usage prompt."""
    welcome_text = (
        "🤖 *Welcome to oyebade_bot! Your PDF-to-Text Assistant.*\n\n"
        "I am designed to parse native documents and extract textual content from "
        "scanned images seamlessly.\n\n"
        "📥 *How to use:*\n"
        "Drop any `.pdf` document file directly into our chat window. I will "
        "process it and return your text layer safely."
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catches document objects, filters by extension, processes via thread pool."""
    incoming_doc: Document = update.message.document
    
    if not incoming_doc.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Refused. Please attach a file that explicitly carries a `.pdf` suffix.")
        return

    # Deliver immediate responsive placeholder acknowledgement
    processing_notice = await update.message.reply_text("⏳ Processing your file... Please hold on.")
    local_temp_disk_target = f"track_{incoming_doc.file_id}.pdf"
    
    try:
        logger.info(f"Downloading stream sequence for file target: {incoming_doc.file_name}")
        telegram_file_object = await context.bot.get_file(incoming_doc.file_id)
        await telegram_file_object.download_to_drive(local_temp_disk_target)
        
        # Offload structural extraction to prevent loop starvation on massive files
        text_dataset = await asyncio.to_thread(extract_text_from_pdf, local_temp_disk_target)
        
        if not text_dataset or not text_dataset.strip():
            await processing_notice.edit_text("⚠️ Processing ended without resolving recognizable character data layers.")
            return

        # Delivery Route Calculation (Telegram text message limit cap threshold is 4096)
        if len(text_dataset) <= 3500:
            success_output = (
                "📝 *PDF Converted Successfully*\n"
                "Here is your extracted text:\n\n"
                f"{text_dataset}"
            )
            await processing_notice.delete()
            await update.message.reply_text(text=success_output, parse_mode="Markdown")
        else:
            await processing_notice.edit_text("📦 Processing complete. Dataset exceeds message caps. Exporting text file document...")
            
            byte_stream = io.BytesIO(text_dataset.encode('utf-8'))
            cleaned_file_title = incoming_doc.file_name.rsplit('.', 1)[0]
            byte_stream.name = f"Extracted_{cleaned_file_title}.txt"
            
            await update.message.reply_document(
                document=byte_stream,
                caption="✅ *PDF Converted Successfully*\nYour complete extracted text structure is ready above."
            )
            await processing_notice.delete()

    except Exception as workflow_fault:
        logger.error(f"Exception broken in worker handler workflow loop: {str(workflow_fault)}")
        await processing_notice.edit_text("❌ An unexpected processing error derailed document transcription layouts.")
        
    finally:
        if os.path.exists(local_temp_disk_target):
            os.remove(local_temp_disk_target)

# --- Python 3.14 Concurrent Polling Daemon ---
async def start_application_daemon() -> None:
    if not BOT_TOKEN:
        raise ValueError("System Environment variable assignment 'BOT_TOKEN' is missing.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("oyebade_bot core running. Native asynchronous lifecycle engine active.")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main() -> None:
    asyncio.run(start_application_daemon())

if __name__ == "__main__":
    main()
