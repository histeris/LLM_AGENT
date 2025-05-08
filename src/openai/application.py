import logging
import json
from telegram.ext import *
from telegram import Update, ReplyKeyboardMarkup
from crew import researcher
import asyncio
import pytz
from pytz import utc
import os 
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from memoryParser import parse_agent_text

import re

def remove_character(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

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
    
    keyboard = [
        ["Konsultasi"],
        ["history", "newchat"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Halo, selamat datang di aplikasi ini.\nSilahkan pilih menu yang tersedia:",
        reply_markup=reply_markup
    )
    
def run_crew_blocking(user_input, chat_history=None):
    history_context = ""
    if chat_history:
        for item in chat_history[-5:]:
            history_context += f"User: {item.get('user')}\nAgent: {item.get('agent')}\n"

    inputs = {
        "keluhan_user": f"{history_context}\nUser: {user_input}",
    }
    try:
        result = researcher().run(inputs)  # <- BUKAN .crew().kickoff() kalau kamu sudah pakai .run()
        return result  # JANGAN pakai f"{result}"
    except Exception as e:
        return {"error": f"Error saat menjalankan CrewAI: {e}"}


def format_agent_output(agent_data):
    try:
        if isinstance(agent_data, dict):
            if "error" in agent_data:
                return agent_data["error"]
            analisis = agent_data.get("analisis", "")
            rekomendasi = agent_data.get("rekomendasi_obat", "")
            return f"{analisis}\n\n{rekomendasi}"
        elif isinstance(agent_data, str):
            try:
                parsed = json.loads(agent_data)
                return format_agent_output(parsed)
            except:
                return agent_data
        else:
            return str(agent_data)
    except Exception as e:
        return f"Gagal memformat output: {e}"


        
async def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user_text = update.message.text
    memory = load_memory()
    
    if "started_users" not in memory or user_id not in memory["started_users"]:
        await update.message.reply_text("Ketik command terlebih dahulu sebelum memulai chat.")
        return
    
    if user_text.lower() in ["start", "konsultasi"]:
        await update.message.reply_text("Silakan ketik gejala yang anda alami.")
        return
    elif user_text == "history":
        await history(update, context)
        return
    elif user_text == "newchat":
        await new_chat(update,context)
        return
    
    await update.message.reply_text("Sedang memproses dengan CrewAI, tunggu sebentar...") 

    loop = asyncio.get_event_loop()
    last_history = []
    if user_id in memory and isinstance(memory[user_id], list) and memory[user_id]:
        last_history = memory[user_id][-1:]  # ambil satu item terakhir sebagai list
    else:
        last_history = []

    result = await loop.run_in_executor(executor, run_crew_blocking, user_text, last_history)

    formatted_result = format_agent_output(result)
    cleaned_result = remove_character(formatted_result)
    await update.message.reply_text(cleaned_result)
    memory = load_memory()
    
    if user_id not in memory:
        memory[user_id] = []
        
    memory[user_id].append({
        "user": user_text,
        "agent": parse_agent_text(cleaned_result)
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
        json.dump(memory,f,indent=4)

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
    logging.info("Running polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
