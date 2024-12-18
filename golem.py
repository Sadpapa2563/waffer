import os
import telebot
import logging
import asyncio
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import certifi
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import threading  # Import threading module

# Sensitive info
TOKEN = '7549081732:AAEBqij1-k0vghXRHnMtk_xe1aOxJ0UZYNY'
MONGO_URI = 'mongodb+srv://Bishal:Bishal@bishal.dffybpx.mongodb.net/?retryWrites=true&w=majority&appName=Bishal'

# Configuration
FORWARD_CHANNEL_ID = -1002280848259
CHANNEL_ID = -1002280848259
error_channel_id = -1002280848259

REQUEST_INTERVAL = 1  # Interval for asyncio tasks
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Database connection
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['zoya']
users_collection = db.users

# Initialize bot
bot = telebot.TeleBot(TOKEN)
loop = asyncio.get_event_loop()

# Helper flag and state
bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0

# Proxy updater
def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"

        # Add more proxies as needed
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    try:
        update_proxy()
        bot.send_message(message.chat.id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to update proxy: {e}")

# Background asyncio tasks
async def background_tasks():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Approval/Disapproval logic
def is_user_admin(user_id, chat_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not is_user_admin(user_id, CHANNEL_ID):
        bot.send_message(chat_id, "*🚫 You are not authorized to use this command.*", parse_mode='Markdown')
        return

    cmd_parts = message.text.split()
    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*⚠️ Invalid format! Use:*\n"
                                   "`/approve <user_id> <plan> <days>`\n"
                                   "`/disapprove <user_id>`", parse_mode='Markdown')
        return

    action, target_user_id = cmd_parts[0], int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == '/approve':
        if plan == 1 and users_collection.count_documents({"plan": 1}) >= 99:
            bot.send_message(chat_id, "*🚫 Instant Plan limit reached (99 users).*", parse_mode='Markdown')
            return
        if plan == 2 and users_collection.count_documents({"plan": 2}) >= 499:
            bot.send_message(chat_id, "*🚫 Instant++ Plan limit reached (499 users).*", parse_mode='Markdown')
            return

        valid_until = (datetime.now() + timedelta(days=days)).isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"user_id": target_user_id, "plan": plan, "valid_until": valid_until}},
            upsert=True
        )
        bot.send_message(chat_id, f"User {target_user_id} approved for Plan {plan} ({days} days).", parse_mode='Markdown')

    elif action == '/disapprove':
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": None}},
            upsert=True
        )
        bot.send_message(chat_id, f"User {target_user_id} disapproved.", parse_mode='Markdown')

# Attack command
@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    if not user_data or user_data['plan'] == 0:
        bot.send_message(message.chat.id, "*🚫 You are not authorized to perform attacks.*", parse_mode='Markdown')
        return

    bot.send_message(message.chat.id, "*Enter target IP, port, and duration (e.g., `1.2.3.4 8080 120`):*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack)

def process_attack(message):
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "*❗ Invalid format! Use `IP PORT DURATION`.*", parse_mode='Markdown')
        return

    target_ip, target_port, duration = args[0], int(args[1]), int(args[2])
    if target_port in blocked_ports:
        bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked. Choose another.*", parse_mode='Markdown')
        return
    if duration > 300:
        bot.send_message(message.chat.id, "*⏳ Duration cannot exceed 300 seconds.*", parse_mode='Markdown')
        return

    # Start attack (dummy implementation)
    bot.attack_in_progress = True
    bot.attack_duration = duration
    bot.attack_start_time = time.time()
    bot.send_message(message.chat.id, f"*🚀 Attack started on {target_ip}:{target_port} for {duration}s!*", parse_mode='Markdown')

@bot.message_handler(commands=['myinfo'])
def myinfo_command(message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    if user_data:
        response = f"*👤 User ID:* {user_id}\n*💸 Plan:* {user_data.get('plan', 'N/A')}\n*⏳ Valid Until:* {user_data.get('valid_until', 'N/A')}"
    else:
        response = "*❌ You are not registered.*"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Start bot
def start_asyncio_thread():
    loop.run_until_complete(background_tasks())

# Create and start the asyncio thread
asyncio_thread = threading.Thread(target=start_asyncio_thread, daemon=True)
asyncio_thread.start()

# Start the bot polling
bot.polling(none_stop=True)
