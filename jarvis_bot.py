"""
🤖 JARVIS - Tu Asistente Personal vía Telegram
Powered by Claude AI (Anthropic)

Instalación:
    pip install python-telegram-bot anthropic python-dotenv

Uso:
    1. Crea un bot en Telegram con @BotFather → obtienes TELEGRAM_TOKEN
    2. Obtén tu ANTHROPIC_API_KEY en console.anthropic.com
    3. Crea archivo .env con las claves (ver .env.example)
    4. python jarvis_bot.py
"""

import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

# ── Configuración ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Solo estos usuarios pueden hablar con JARVIS (deja vacío para permitir todos)
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")  # ej: "123456789,987654321"

JARVIS_PERSONALITY = """Eres JARVIS, el asistente personal de inteligencia artificial del usuario.
Tu estilo es:
- Formal pero cálido, como un mayordomo británico de alto nivel
- Eficiente, preciso y proactivo
- Usas "señor" o "señora" ocasionalmente (según el usuario)
- Tienes ligero humor sutil e inteligente
- Siempre dispuesto a ayudar con cualquier tarea: preguntas, análisis, redacción, código, etc.
- Puedes recordar el contexto de la conversación actual

Al iniciar siempre saludas de forma breve y preguntas en qué puedes asistir.
Responde siempre en el idioma que use el usuario."""

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Clientes ───────────────────────────────────────────────────
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Memoria de conversaciones por usuario {user_id: [messages]}
conversation_history: dict[int, list] = {}

MAX_HISTORY = 20  # Máximo de mensajes a recordar por usuario


# ── Helpers ────────────────────────────────────────────────────
def is_authorized(user_id: int) -> bool:
    if not ALLOWED_USERS or ALLOWED_USERS == [""]:
        return True  # Sin restricciones
    return str(user_id) in ALLOWED_USERS


def get_history(user_id: int) -> list:
    return conversation_history.get(user_id, [])


def add_to_history(user_id: int, role: str, content: str):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": role, "content": content})
    # Limitar historial
    if len(conversation_history[user_id]) > MAX_HISTORY:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY:]


async def ask_jarvis(user_id: int, user_message: str) -> str:
    add_to_history(user_id, "user", user_message)
    
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=JARVIS_PERSONALITY,
        messages=get_history(user_id),
    )
    
    reply = response.content[0].text
    add_to_history(user_id, "assistant", reply)
    return reply


# ── Handlers de Telegram ───────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        await update.message.reply_text("⛔ Acceso no autorizado.")
        return

    conversation_history.pop(user.id, None)  # Reset al iniciar
    
    welcome = await ask_jarvis(
        user.id,
        f"El usuario {user.first_name} acaba de iniciar una nueva sesión. Salúdale."
    )
    await update.message.reply_text(f"🤖 *JARVIS en línea*\n\n{welcome}", parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        return
    conversation_history.pop(user.id, None)
    await update.message.reply_text("🔄 Memoria borrada. Nueva sesión iniciada, señor.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        return
    msgs = len(get_history(user.id))
    await update.message.reply_text(
        f"📊 *Estado de JARVIS*\n"
        f"• Mensajes en memoria: {msgs}/{MAX_HISTORY}\n"
        f"• Estado: Operativo ✅\n"
        f"• Modelo: Claude (Anthropic)",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user.id):
        await update.message.reply_text("⛔ No autorizado.")
        return

    user_text = update.message.text
    logger.info(f"[{user.id}] {user.first_name}: {user_text[:50]}...")

    # Indicador de "escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        reply = await ask_jarvis(user.id, user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "⚠️ Disculpe señor, he encontrado un error temporal. Por favor intente de nuevo."
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder para mensajes de voz (requiere Whisper API)"""
    await update.message.reply_text(
        "🎙️ Mensajes de voz en desarrollo. Por favor use texto por ahora, señor."
    )


# ── Main ───────────────────────────────────────────────────────
def main():
    if not TELEGRAM_TOKEN or not ANTHROPIC_API_KEY:
        raise ValueError("❌ Faltan TELEGRAM_TOKEN o ANTHROPIC_API_KEY en .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("status", status))

    # Mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("🤖 JARVIS iniciado. Esperando mensajes...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
