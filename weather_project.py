import logging
import requests
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 로그 설정 (디버깅에 유용)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 여기에 당신의 OpenWeatherMap API 키를 입력하세요.
OPENWEATHERMAP_API_KEY = "81f0fca1547711d858d467e47754a65d"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# 여기에 당신의 텔레그램 봇 토큰을 입력하세요.
TELEGRAM_BOT_TOKEN = "8336834023:AAEhF9sh8V7NTZc8MAqlniU7dOlXSY0eEcY"

def get_weather_data(city_name):
    """
    OpenWeatherMap API로부터 날씨 데이터를 가져오는 함수
    """
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

# /start 명령어에 응답하는 함수
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "안녕하세요! 저는 날씨를 알려주는 봇입니다.\n"
        "예시) <b>대구</b> 또는 <b>대구 날씨</b> 라고 입력해주세요."
    )

# 사용자의 메시지에 응답하는 함수
async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower().strip()
    
    # 사용자의 메시지에 '날씨'라는 단어가 포함되어 있거나, 도시 이름만 입력했을 경우
    if '대구' in user_message or user_message == '대구':
        city = 'Daegu, KR'
    elif '서울' in user_message or user_message == '서울':
        city = 'Seoul, KR'
    else:
        await update.message.reply_text("죄송합니다. 아직 대구와 서울 날씨만 알려드릴 수 있습니다.")
        return
    
    weather_data = get_weather_data(city)

    if weather_data and weather_data['cod'] == 200:
        weather = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        
        message = (
            f"📍 <b>{weather_data['name']}</b>의 현재 날씨\n"
            f"----------------------------------------\n"
            f"날씨: {weather}\n"
            f"현재 기온: {temp}°C\n"
            f"습도: {humidity}%"
        )
        await update.message.reply_html(message)
    else:
        await update.message.reply_text("도시를 찾을 수 없거나 데이터를 가져오는 데 실패했습니다.")

def main():
    """봇을 실행하는 메인 함수."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

    application.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()