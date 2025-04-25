import logging
import json
import nest_asyncio
from telegram.ext import *
from telegram import Update
from crew import researcher
import asyncio
import pytz
from pytz import utc
import os 
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

MEMORY_FILE = "memory.json"

MAX_MESSAGE_LENGTH = 4096

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('Starting Bot...')

executor = ThreadPoolExecutor()
 
async def start_command(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    memory = load_memory()
    
    if "started_users" not in memory:
        memory["started_users"] = []
    
    if user_id not in memory["started_users"]:
        memory["started_users"].append(user_id)
        save_memory(memory)
    await update.message.reply_text("Halo Silahkan ketik gejala apa yang ada alami maka kami akan rekomendasikan obatnya untuk anda.")

def run_crew_blocking(user_input):
    inputs = {
        "gejala_user": user_input,
    }
    try:
        result = researcher().crew().kickoff(inputs=inputs)
        return f"{result}"
    except Exception as e:
        return f"Error saat menjalankan CrewAI: {e}"

async def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_text = update.message.text
    memory = load_memory()
    
    if "started_users" not in memory or user_id not in memory["started_users"]:
        await update.message.reply_text("Ketik command terlebih dahulu sebelum memulai chat.")
        return
    
    await update.message.reply_text("Sedang memproses dengan CrewAI, tunggu sebentar...") 

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_crew_blocking, user_text)

    await update.message.reply_text(result)
    memory = load_memory()
    
    if user_id not in memory:
        memory[user_id] = []
        
    memory[user_id].append({
        "user": user_text,
        "agent": result
    })
    save_memory(memory)

async def error(update: Update, context: CallbackContext):
    print(f"Error terjadi: {context.error}")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    memory = load_memory()
    
    if user_id in memory and memory[user_id]:
        history_text = memory[user_id][-10:]
        formatted_history = ""
        for item in history_text:
            if isinstance(item, dict) and "user" in item and "agent" in item:
                formatted_history += f"User: {item['user']}\nAgent: {item['agent']}\n\n"
            else:
                formatted_history += f"[Format tidak valid]: {str(item)}\n\n"
        try:
            if len(formatted_history) > MAX_MESSAGE_LENGTH:
                for i in range(0, len(formatted_history), MAX_MESSAGE_LENGTH):
                    await update.message.reply_text(formatted_history[i:i+MAX_MESSAGE_LENGTH])
            else:
                await update.message.reply_text(f"Histori: \n{formatted_history.strip()}")
        # await update.message.reply_text(f"Histori: \n{history_text}", parse_mode="Markdown")
        # await update.message.reply_text(f"Histori: \n{formatted_history.strip()}")
        except Exception as e:
            await update.message.reply_text("Pesan terlalu panjang untuk dikirim.")
    else:
        await update.message.reply_text("Belum ada histori percakapan.")
            
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Gagal membaca memory.json: {e}")
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory,f)

async def new_chat(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    memory = load_memory()
    
    if "history_backup" not in memory:
        memory["history_backup"] = {}
        
    if user_id in memory and isinstance(memory[user_id], list):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_key = f"{user_id}_{timestamp}"
        memory["history_backup"][backup_key] = memory[user_id]

    memory[user_id] = []
    
    save_memory(memory)

    await update.message.reply_text("Obrolan baru telah dimulai.")
    
def main():
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("newchat", new_chat))
    # application.add_handler(CommandHandler("custom", custom_command))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    # asyncio.run(main())
    main()
