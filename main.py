import os
import logging
import csv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
from handlers import start_add, start, input_airdrop_name, input_status, input_type, input_tuyul, input_notes, input_result, check_progress, handle_next_button, handle_prev_button, start_edit, select_airdrop_to_edit, select_field_to_edit, input_new_value, start_remove, remove_airdrop, cancel
from constants import CSV_FILE, AIRDROP_NAME, STATUS, TYPE, TUYUL, NOTES, RESULT, EDIT_SELECT, EDIT_FIELD, EDIT_VALUE, COMMAND_OPTIONS, TUYUL_ACCOUNTS

load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Change this to DEBUG for more verbosity during development
)

# Ensure CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Airdrop Name", "Status", "Type"] + TUYUL_ACCOUNTS + ["Notes", "Result"])

def main():
    # Retrieve the bot token from an environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logging.error("Bot token not found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
        return

    application = Application.builder().token(bot_token).build()

    # Conversation Handler for /add
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_add)],
        states={
            AIRDROP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_airdrop_name)],
            STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_status)],
            TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_type)],
            TUYUL: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_tuyul)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_notes)],
            RESULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_result)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation Handler for /edit
    edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", start_edit)],
        states={
            EDIT_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_airdrop_to_edit)],
            EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_field_to_edit)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_new_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation Handler for /remove
    remove_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("remove", start_remove)],
        states={
            EDIT_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_airdrop)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers directly to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(remove_conv_handler)
    application.add_handler(CommandHandler("progress", check_progress))
    application.add_handler(CallbackQueryHandler(handle_next_button, pattern="^next$"))
    application.add_handler(CallbackQueryHandler(handle_prev_button, pattern="^prev$"))

    logging.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
