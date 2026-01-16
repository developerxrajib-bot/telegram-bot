import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
MessageHandler,
ContextTypes,
filters,
)

================= CONFIG =================

BOT_TOKEN = "8359632531:AAFBthz9YN-ggk2sVV7zAyco5TgLczJZ5Qk"
ADMIN_ID =  7403460145 # <-- নিজের Telegram ID বসাও

PAYMENT_TEXT = """
🔷 টাকা সেন্ড করার নিয়ম
👉 মোট টাকার সাথে +1% চার্জ যোগ করে সেন্ড মানি করবেন।

💳 পেমেন্ট অপশন:
🅱 bKash : +8801704635232
🆖 Nagad : +8801339597482
🚀 Rocket : +8801339597482

⏭️ টাকা সেন্ড করার পর
Transaction ID (TrxID) পাঠান।
"""

================= DATABASE =================

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
username TEXT,
premium_until TEXT
)
""")
db.commit()

================= HELPERS =================

def is_premium(user_id: int):
cur.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,))
row = cur.fetchone()
if not row or not row[0]:
return False
return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") > datetime.now()

================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
cur.execute(
"INSERT OR IGNORE INTO users (user_id, username, premium_until) VALUES (?, ?, ?)",
(user.id, user.username, None),
)
db.commit()

await update.message.reply_text(    
    "👋 Welcome!\n\n"    
    "💎 Premium নিতে 👉 /pay\n"    
    "🧾 TrxID পাঠান, Admin verify করবে"    
)

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(PAYMENT_TEXT)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text.strip()
if len(text) >= 8:
await update.message.reply_text(
"✅ TrxID Received\n⏳ Admin Verify Pending"
)
else:
await update.message.reply_text("❌ সঠিক TrxID দিন")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id != ADMIN_ID:
return

try:    
    user_id = int(context.args[0])    
    days = context.args[1]    

    if days.lower() == "permanent":    
        premium_until = datetime.now() + timedelta(days=3650)    
    else:    
        premium_until = datetime.now() + timedelta(days=int(days))    

    cur.execute(    
        "UPDATE users SET premium_until=? WHERE user_id=?",    
        (premium_until.strftime("%Y-%m-%d %H:%M:%S"), user_id),    
    )    
    db.commit()    

    await context.bot.send_message(    
        chat_id=user_id,    
        text=f"🎉 Premium Activated!\n⏳ Valid till: {premium_until}"    
    )    
    await update.message.reply_text("✅ Premium Activated")    

except Exception as e:    
    await update.message.reply_text("❌ Format:\n/verify user_id days")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
if is_premium(update.effective_user.id):
await update.message.reply_text("✅ আপনি Premium User")
else:
await update.message.reply_text("❌ Premium নেই")

================= MAIN =================

def main():
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))    
app.add_handler(CommandHandler("pay", pay))    
app.add_handler(CommandHandler("verify", verify))    
app.add_handler(CommandHandler("premium", premium))    
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))    

print("🤖 Bot Running...")    
app.run_polling()

if name == "main":
main()
