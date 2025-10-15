import logging
import requests
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 로그 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

OPENWEATHERMAP_API_KEY = "81f0fca1547711d858d467e47754a65d"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
TELEGRAM_BOT_TOKEN = "8336834023:AAEhF9sh8V7NTZc8MAqlniU7dOlXSY0eEcY"

# 마지막 봇 메시지 ID 저장
last_bot_message_id = None

# ✅ 날씨 API 요청
def get_weather_data(city_name):
    params = {
        'q': city_name,
        'appid': OPENWEATHERMAP_API_KEY,
        'units': 'metric',
        'lang': 'kr'
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"날씨 정보 가져오기 오류: {e}")
        return None


# ✅ 2행 3열 버튼
def get_city_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("서울", callback_data="Seoul, KR"),
            InlineKeyboardButton("인천", callback_data="Incheon, KR"),
            InlineKeyboardButton("대구", callback_data="Daegu, KR")
        ],
        [
            InlineKeyboardButton("부산", callback_data="Busan, KR"),
            InlineKeyboardButton("대전", callback_data="Daejeon, KR"),
            InlineKeyboardButton("제주도", callback_data="Jeju City, KR")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bot_message_id

    chat_id = update.message.chat_id

    # 이전 메시지 버튼 제거
    if last_bot_message_id is not None:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=last_bot_message_id,
                reply_markup=None
            )
        except:
            pass
        
    msg = await update.message.reply_html(
        "🌤️ 안녕하세요! <b>날씨 안내 봇</b>입니다.\n"
        "도시를 선택하거나 영어로 도시를 입력해주세요.\n(예: Tokyo, London, New York)",
        reply_markup=get_city_keyboard()
    )
    last_bot_message_id = msg.message_id


# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bot_message_id

    chat_id = update.message.chat_id

    # 이전 메시지 버튼 제거
    if last_bot_message_id is not None:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=last_bot_message_id,
                reply_markup=None
            )
        except:
            pass

    text = (
        "📘 <b>사용법 안내</b>\n"
        "----------------------------------------\n"
        "/start - 도시 버튼 표시\n"
        "/help - 도움말 보기\n\n"
        "도시 입력 방법:\n"
        "• 한국 주요 도시 → 버튼 클릭\n"
        "• 해외 도시 → 영어로 입력 (예: Tokyo, London, New York)"
    )
    msg = await update.message.reply_html(text, reply_markup=get_city_keyboard())
    last_bot_message_id = msg.message_id


# 버튼 클릭 시 처리
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bot_message_id
    query = update.callback_query
    await query.answer()
    city = query.data
    chat_id = query.message.chat_id

    # 이전 메시지 버튼 제거
    if last_bot_message_id is not None:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=last_bot_message_id,
                reply_markup=None
            )
        except:
            pass

    # 날씨 API
    weather_data = get_weather_data(city)
    if weather_data and weather_data['cod'] == 200:
        weather = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']

        message = (
            f"📍 <b>{weather_data['name']}</b>의 현재 날씨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"날씨: {weather}\n"
            f"기온: {temp}°C\n"
            f"습도: {humidity}%\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            "도시를 선택하거나 영어로 도시를 입력해주세요.\n"
            "(예: Tokyo, London, New York)"
        )

        # 새 메시지 전송 + 버튼 유지
        msg = await query.message.reply_html(message, reply_markup=get_city_keyboard())
        last_bot_message_id = msg.message_id
    else:
        msg = await query.message.reply_text(
            "❌ 데이터를 가져올 수 없습니다.",
            reply_markup=get_city_keyboard()
        )
        last_bot_message_id = msg.message_id


# 영어 입력 처리
async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_bot_message_id
    user_message = update.message.text.strip()
    chat_id = update.message.chat_id

    # 이전 메시지 버튼 제거
    if last_bot_message_id is not None:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=last_bot_message_id,
                reply_markup=None
            )
        except:
            pass

    # 한글 입력 시 안내
    if any('가' <= ch <= '힣' for ch in user_message):
        msg = await update.message.reply_text(
            "⚠️ 영어로 입력해주세요. (예: Tokyo, New York, Paris)",
            reply_markup=get_city_keyboard()
        )
        last_bot_message_id = msg.message_id
        return

    # 날씨 API
    city = user_message
    weather_data = get_weather_data(city)

    if weather_data and weather_data['cod'] == 200:
        weather = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']

        message = (
            f"📍 <b>{weather_data['name']}</b>의 현재 날씨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"날씨: {weather}\n"
            f"기온: {temp}°C\n"
            f"습도: {humidity}%\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            "도시를 선택하거나 영어로 도시를 입력해주세요.\n"
            "(예: Tokyo, London, New York)"
        )

        msg = await update.message.reply_html(message, reply_markup=get_city_keyboard())
        last_bot_message_id = msg.message_id
    else:
        msg = await update.message.reply_text(
            "❌ 도시를 찾을 수 없거나 데이터를 가져오는 데 실패했습니다.",
            reply_markup=get_city_keyboard()
        )
        last_bot_message_id = msg.message_id


# 메인
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))
    application.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
