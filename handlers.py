import os
import csv
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from constants import CSV_FILE, STATUS_OPTIONS, TYPE_OPTIONS, TUYUL_OPTIONS, TUYUL_ACCOUNTS, COMMAND_OPTIONS, AIRDROP_NAME, STATUS, TYPE, TUYUL, NOTES, RESULT, EDIT_SELECT, EDIT_FIELD, EDIT_VALUE, EDIT_FIELD_OPTIONS

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Starting add process")
    await update.message.reply_text("📌 Input Airdrop Name:")
    return AIRDROP_NAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /start command")
    await update.message.reply_text(
        "Welcome! Please choose a command:",
        reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    )

async def input_airdrop_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received airdrop name")
    context.user_data["airdrop_name"] = update.message.text
    await update.message.reply_text("🔹 Select Status:", reply_markup=ReplyKeyboardMarkup(STATUS_OPTIONS, one_time_keyboard=True, resize_keyboard=True))
    return STATUS

async def input_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received status")
    context.user_data["status"] = update.message.text
    await update.message.reply_text("🔹 Select Type:", reply_markup=ReplyKeyboardMarkup(TYPE_OPTIONS, one_time_keyboard=True, resize_keyboard=True))
    return TYPE

async def input_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received type")
    context.user_data["type"] = update.message.text
    context.user_data["tuyul_status"] = []
    context.user_data["tuyul_index"] = 0
    return await ask_tuyul(update, context)

async def ask_tuyul(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data["tuyul_index"] < len(TUYUL_ACCOUNTS):
        tuyul_name = TUYUL_ACCOUNTS[context.user_data["tuyul_index"]]
        logging.info(f"Asking for {tuyul_name} status")
        await update.message.reply_text(f"🤖 {tuyul_name} (✅ Yes / ❌ No):", reply_markup=ReplyKeyboardMarkup(TUYUL_OPTIONS, one_time_keyboard=True, resize_keyboard=True))
        return TUYUL
    else:
        await update.message.reply_text("📝 Input Notes:")
        return NOTES

async def input_tuyul(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received tuyul status")
    context.user_data["tuyul_status"].append(update.message.text)
    context.user_data["tuyul_index"] += 1
    return await ask_tuyul(update, context)

async def input_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received notes")
    context.user_data["notes"] = update.message.text
    await update.message.reply_text("🏁 Input Result:")
    return RESULT

async def input_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Received result")
    context.user_data["result"] = update.message.text

    # Save data to CSV with UTF-8 encoding
    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([context.user_data["airdrop_name"], context.user_data["status"], context.user_data["type"], *context.user_data["tuyul_status"], context.user_data["notes"], context.user_data["result"]])
        await update.message.reply_text(
            "✅ Airdrop data added successfully!",
            reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
        )
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")
        await update.message.reply_text("An error occurred while saving the data.")
    
    return ConversationHandler.END

async def check_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received /progress command")
    if not os.path.exists(CSV_FILE):
        await update.message.reply_text("No data available yet. Add an airdrop using /add.")
        return

    # Load CSV with UTF-8 encoding
    try:
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = list(csv.reader(file))
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        await update.message.reply_text("An error occurred while reading the data.")
        return

    if not reader:
        await update.message.reply_text("No airdrop progress found.")
        return

    # Pagination: calculate the range of records for the current page
    current_page = context.user_data.get("page", 0)
    start_index = current_page * 5  # Skip previous records
    end_index = start_index + 5

    # Slice the list to get the current page's data
    airdrop_data = reader[start_index:end_index]

    if not airdrop_data:
        await update.message.reply_text("No more results.")
        return

    result_text = "📊 *Airdrop Progress:*\n\n"
    for row in airdrop_data:
        try:
            airdrop_name, status, type_, *tuyul_progress, notes, result = row
        except ValueError as e:
            logging.error(f"Error unpacking row: {row} - {e}")
            continue

        # Format Tuyul completion
        tuyul_status = " | ".join(tuyul_progress)

        result_text += (
            f"📌 *{airdrop_name}*\n"
            f"🟢 Status: {status}\n"
            f"🔹 Type: {type_}\n"
            f"🤖 Tuyul: {tuyul_status}\n"
            f"📝 Notes: {notes if notes else '-'}\n"
            f"🏁 Result: {result if result else '-'}\n"
            f"----------------------\n"
        )

    # Add the "Prev" and "Next" buttons if there are more results
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton("Prev", callback_data="prev"))
    if end_index < len(reader):
        buttons.append(InlineKeyboardButton("Next", callback_data="next"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

    # Ensure we're replying to the correct message
    if update.callback_query:
        # Acknowledge the callback and update the message
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        # In case the initial message is used (for first-time message or /progress)
        await update.message.reply_text(result_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_next_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received next button press")
    # Acknowledge the callback
    await update.callback_query.answer()

    # Retrieve the current page number
    current_page = context.user_data.get("page", 0)  # Default to page 0
    # Increase the page number for the next results
    next_page = current_page + 1

    # Update the page number in user_data
    context.user_data["page"] = next_page

    # Call the check_progress function to show the next set of results
    await check_progress(update, context)

async def handle_prev_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Received prev button press")
    # Acknowledge the callback
    await update.callback_query.answer()

    # Retrieve the current page number
    current_page = context.user_data.get("page", 0)  # Default to page 0
    # Decrease the page number for the previous results
    prev_page = max(current_page - 1, 0)

    # Update the page number in user_data
    context.user_data["page"] = prev_page

    # Call the check_progress function to show the previous set of results
    await check_progress(update, context)

async def start_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Starting edit process")
    await update.message.reply_text("📌 Input Airdrop Name to Edit:")
    return EDIT_SELECT

async def select_airdrop_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Selecting airdrop to edit")
    context.user_data["edit_airdrop_name"] = update.message.text
    await update.message.reply_text("🔹 Select Field to Edit:", reply_markup=ReplyKeyboardMarkup(EDIT_FIELD_OPTIONS, one_time_keyboard=True, resize_keyboard=True))
    return EDIT_FIELD

async def select_field_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Selecting field to edit")
    context.user_data["edit_field"] = update.message.text
    await update.message.reply_text(f"🔹 Input New Value for {context.user_data['edit_field']}:")
    return EDIT_VALUE

async def input_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Inputting new value")
    new_value = update.message.text
    airdrop_name = context.user_data["edit_airdrop_name"]
    field = context.user_data["edit_field"]

    # Load CSV with UTF-8 encoding
    try:
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = list(csv.reader(file))
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        await update.message.reply_text("An error occurred while reading the data.")
        return ConversationHandler.END

    # Find and update the record
    updated = False
    for row in reader:
        if row[0] == airdrop_name:
            if field == "Status":
                row[1] = new_value
            elif field == "Type":
                row[2] = new_value
            elif field in TUYUL_ACCOUNTS:
                tuyul_index = TUYUL_ACCOUNTS.index(field) + 3
                row[tuyul_index] = new_value
            elif field == "Notes":
                row[-2] = new_value
            elif field == "Result":
                row[-1] = new_value
            updated = True
            break

    if updated:
        # Save updated data to CSV with UTF-8 encoding
        try:
            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(reader)
            await update.message.reply_text(
                "✅ Airdrop data updated successfully!",
                reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
            )
        except Exception as e:
            logging.error(f"Error writing to CSV file: {e}")
            await update.message.reply_text("An error occurred while saving the data.")
    else:
        await update.message.reply_text("❌ Airdrop not found.",
            reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True))

    return ConversationHandler.END

async def start_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Starting remove process")
    await update.message.reply_text("📌 Input Airdrop Name to Remove:")
    return EDIT_SELECT

async def remove_airdrop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Removing airdrop")
    airdrop_name = update.message.text

    # Load CSV with UTF-8 encoding
    try:
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = list(csv.reader(file))
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        await update.message.reply_text("An error occurred while reading the data.")
        return ConversationHandler.END

    # Find and remove the record
    updated_reader = [row for row in reader if row[0] != airdrop_name]

    if len(updated_reader) == len(reader):
        await update.message.reply_text("❌ Airdrop not found.")
    else:
        # Save updated data to CSV with UTF-8 encoding
        try:
            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(updated_reader)
            await update.message.reply_text(
                "✅ Airdrop data removed successfully!",
                reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
            )
        except Exception as e:
            logging.error(f"Error writing to CSV file: {e}")
            await update.message.reply_text("An error occurred while saving the data.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info("Process canceled")
    await update.message.reply_text("❌ Process canceled.",
        reply_markup=ReplyKeyboardMarkup(COMMAND_OPTIONS, one_time_keyboard=True, resize_keyboard=True))
    return ConversationHandler.END
