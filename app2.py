import datetime  # Импортируем модуль для работы с датой и временем
import pytz  # Импортируем модуль для работы с часовыми поясами
import schedule  # Импортируем модуль для планирования задач
import pandas_market_calendars as mcal  # Импортируем модуль для получения календаря рынка
import pandas as pd  # Импортируем pandas для работы с данными
import time  # Импортируем модуль для работы со временем
import requests  # Импортируем модуль для отправки HTTP-запросов

# Управление токенами OAuth 2.0
CLIENT_ID = 'YOUR_CLIENT_ID'  # Замените на ваш фактический Client ID  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ CLIENT_ID]
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'  # Замените на ваш фактический Client Secret  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ CLIENT_SECRET]
REDIRECT_URI = 'YOUR_REDIRECT_URI'  # Замените на ваш фактический Redirect URI  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ REDIRECT_URI]
TOKEN_URL = 'https://api.schwab.com/token'  # URL для получения токена Schwab
AUTHORIZATION_URL = 'https://api.schwab.com/authorize'  # URL для авторизации Schwab

ACCESS_TOKEN = ''  # Переменная для хранения Access Token
REFRESH_TOKEN = ''  # Переменная для хранения Refresh Token
TOKEN_EXPIRY = datetime.datetime.now()  # Время истечения токена

ACCOUNT_ID = 'YOUR_ACCOUNT_ID'  # Замените на ваш фактический ID счета Schwab  #-#-#-#-#-#-#[ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ ACCOUNT_ID]

# Настройки стратегии
MAX_POSITION_SIZE = 1000  # Максимальный размер позиции в долларах  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ СУММУ ВХОДА]
TAKE_PROFIT_PERCENT = 0.06 / 100  # Уровень фиксации прибыли в процентах  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ УРОВЕНЬ TAKE PROFIT]
STOP_LOSS_PERCENT = 0.08 / 100  # Уровень стоп-лосса в процентах  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ УРОВЕНЬ STOP LOSS]
PARTIAL_TAKE_PROFIT_PERCENT = 0.03 / 100  # Уровень частичной фиксации прибыли в процентах  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ УРОВЕНЬ ЧАСТИЧНОГО TAKE PROFIT]

# Торговые часы (время Нью-Йорка)
ny_tz = pytz.timezone('America/New_York')  # Устанавливаем часовой пояс Нью-Йорка
START_TIME = datetime.time(10, 0)  # Время начала торговли (10:00)  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ ВРЕМЯ НАЧАЛА]
END_TIME = datetime.time(15, 50)  # Время окончания торговли (15:50)  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ ВРЕМЯ ОКОНЧАНИЯ]

# Переменные для отслеживания результатов
trades_count = 0  # Количество сделок
profitable_trades = 0  # Количество прибыльных сделок
loss_trades = 0  # Количество убыточных сделок
capital_growth = 0  # Рост капитала

# Функция для получения Access Token с использованием authorization code
def get_access_token(authorization_code):
    global ACCESS_TOKEN, REFRESH_TOKEN, TOKEN_EXPIRY  # Объявляем глобальные переменные
    data = {
        'grant_type': 'authorization_code',  # Тип grant для получения токена
        'code': authorization_code,  # Authorization code из OAuth 2.0  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ AUTHORIZATION_CODE]
        'redirect_uri': REDIRECT_URI,  # Redirect URI для приложения
        'client_id': CLIENT_ID,  # Client ID приложения
        'client_secret': CLIENT_SECRET,  # Client Secret приложения
    }
    response = requests.post(TOKEN_URL, data=data)  # Отправляем POST-запрос для получения токена
    if response.status_code == 200:  # Проверяем успешность запроса
        token_data = response.json()  # Получаем данные токена в формате JSON
        ACCESS_TOKEN = token_data['access_token']  # Сохраняем Access Token
        REFRESH_TOKEN = token_data['refresh_token']  # Сохраняем Refresh Token
        expires_in = token_data.get('expires_in', 3600)  # Получаем время истечения токена
        TOKEN_EXPIRY = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)  # Устанавливаем время истечения токена
        print('Access Token успешно получен')  # Выводим сообщение об успешном получении токена
    else:
        print(f"Не удалось получить Access Token: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке

# Функция для обновления Access Token с использованием Refresh Token
def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN, TOKEN_EXPIRY  # Объявляем глобальные переменные
    data = {
        'grant_type': 'refresh_token',  # Тип grant для обновления токена
        'refresh_token': REFRESH_TOKEN,  # Текущий Refresh Token
        'client_id': CLIENT_ID,  # Client ID приложения
        'client_secret': CLIENT_SECRET,  # Client Secret приложения
    }
    response = requests.post(TOKEN_URL, data=data)  # Отправляем POST-запрос для обновления токена
    if response.status_code == 200:  # Проверяем успешность запроса
        token_data = response.json()  # Получаем данные токена в формате JSON
        ACCESS_TOKEN = token_data['access_token']  # Обновляем Access Token
        REFRESH_TOKEN = token_data['refresh_token']  # Обновляем Refresh Token
        expires_in = token_data.get('expires_in', 3600)  # Получаем новое время истечения токена
        TOKEN_EXPIRY = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)  # Устанавливаем новое время истечения токена
        print('Access Token успешно обновлен')  # Выводим сообщение об успешном обновлении токена
    else:
        print(f"Не удалось обновить Access Token: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке

# Убедиться, что Access Token действителен
def ensure_access_token():
    if datetime.datetime.now() >= TOKEN_EXPIRY:  # Проверяем, истек ли токен
        refresh_access_token()  # Обновляем токен, если он истек

# Функция для вычисления RSI (Relative Strength Index)
def get_rsi(data, window=14):
    delta = data['close'].diff()  # Вычисляем изменения цены закрытия
    gain = (delta.where(delta > 0, 0)).fillna(0)  # Вычисляем прибыль
    loss = (-delta.where(delta < 0, 0)).fillna(0)  # Вычисляем убытки
    avg_gain = gain.rolling(window=window, min_periods=1).mean()  # Вычисляем среднюю прибыль
    avg_loss = loss.rolling(window=window, min_periods=1).mean()  # Вычисляем средние убытки
    rs = avg_gain / avg_loss  # Вычисляем отношение прибыли к убыткам
    rsi = 100 - (100 / (1 + rs))  # Вычисляем RSI
    return rsi  # Возвращаем RSI

# Функция для получения исторических данных
def get_historical_data(symbol):
    ensure_access_token()  # Убеждаемся, что токен действителен
    url = f'https://api.schwab.com/v1/marketdata/{symbol}/pricehistory'  # URL для получения исторических данных
    params = {
        'periodType': 'day',  # Тип периода (день)
        'period': 2,  # Количество периодов
        'frequencyType': 'minute',  # Тип частоты (минута)
        'frequency': 1,  # Частота
    }
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}  # Заголовки с Access Token
    response = requests.get(url, params=params, headers=headers)  # Отправляем GET-запрос
    if response.status_code == 200:  # Проверяем успешность запроса
        data = response.json()  # Получаем данные в формате JSON
        df = pd.DataFrame(data['candles'])  # Преобразуем данные в DataFrame
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')  # Конвертируем время
        df.set_index('datetime', inplace=True)  # Устанавливаем индекс DataFrame
        return df  # Возвращаем DataFrame с историческими данными
    else:
        print(f"Не удалось получить исторические данные: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке
        return None  # Возвращаем None при ошибке

# Функция для получения текущей цены
def get_current_price(symbol):
    ensure_access_token()  # Убеждаемся, что токен действителен
    url = f'https://api.schwab.com/v1/marketdata/{symbol}/quotes'  # URL для получения текущей цены
    params = {'symbol': symbol}  # Параметры запроса с символом
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}  # Заголовки с Access Token
    response = requests.get(url, params=params, headers=headers)  # Отправляем GET-запрос
    if response.status_code == 200:  # Проверяем успешность запроса
        data = response.json()  # Получаем данные в формате JSON
        price_data = data['quotes'][0]  # Извлекаем данные по котировкам
        return price_data['lastPrice']  # Возвращаем последнюю цену
    else:
        print(f"Не удалось получить текущую цену: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке
        return None  # Возвращаем None при ошибке

# Функция для размещения рыночного ордера
def place_market_order(symbol, side, quantity):
    ensure_access_token()  # Убеждаемся, что токен действителен
    url = f'https://api.schwab.com/v1/accounts/{ACCOUNT_ID}/orders'  # URL для размещения ордера  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ ACCOUNT_ID]
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'}  # Заголовки запроса
    order = {
        'orderType': 'MARKET',  # Тип ордера (рыночный)
        'session': 'NORMAL',  # Сессия (обычная)
        'duration': 'DAY',  # Длительность ордера (в течение дня)
        'orderStrategyType': 'SINGLE',  # Тип стратегии ордера (одиночная)
        'orderLegCollection': [
            {
                'instruction': side.upper(),  # Инструкция (BUY или SELL)
                'quantity': quantity,  # Количество акций
                'instrument': {
                    'symbol': symbol,  # Символ актива
                    'assetType': 'EQUITY'  # Тип актива (акции)
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=order)  # Отправляем POST-запрос для размещения ордера
    if response.status_code in [200, 201]:  # Проверяем успешность запроса
        print(f"Ордер размещен: {side} {quantity} акций {symbol}")  # Выводим сообщение об успешном размещении ордера
        return response.json()  # Возвращаем ответ сервера
    else:
        print(f"Не удалось разместить ордер: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке
        return None  # Возвращаем None при ошибке

# Функция для открытия позиции
def open_position(symbol):
    global trades_count, profitable_trades, loss_trades, capital_growth  # Объявляем глобальные переменные

    data = get_historical_data(symbol)  # Получаем исторические данные
    if data is None or len(data) < 2:  # Проверяем, достаточно ли данных
        print("Недостаточно данных для принятия решения.")  # Выводим сообщение
        return  # Выходим из функции

    data['rsi'] = get_rsi(data)  # Вычисляем RSI и добавляем в данные

    previous_candle = data.iloc[-2]  # Получаем предыдущую свечу
    current_price = data.iloc[-1]['close']  # Получаем текущую цену закрытия
    rsi = previous_candle['rsi']  # Получаем RSI предыдущей свечи

    # Условия для открытия позиции
    if previous_candle['close'] > previous_candle['open'] and rsi > 50:  # Если свеча бычья и RSI > 50
        entry_price = previous_candle['open'] + (previous_candle['close'] - previous_candle['open']) / 2  # Вычисляем цену входа
    elif previous_candle['close'] < previous_candle['open'] and rsi < 50:  # Если свеча медвежья и RSI < 50
        entry_price = previous_candle['close']  # Цена входа равна цене закрытия
    else:
        print("Не выполнены подходящие условия.")  # Выводим сообщение
        return  # Выходим из функции

    quantity = int(MAX_POSITION_SIZE / current_price)  # Вычисляем количество акций для покупки  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ MAX_POSITION_SIZE]
    if quantity * current_price > MAX_POSITION_SIZE:  # Проверяем, не превышает ли сумма максимальный размер позиции
        quantity -= 1  # Уменьшаем количество акций на 1

    if quantity <= 0:  # Проверяем, что количество акций положительное
        print("Недостаточно средств для открытия позиции.")  # Выводим сообщение
        return  # Выходим из функции

    # Размещение рыночного ордера на покупку
    order_response = place_market_order(symbol, 'BUY', quantity)  # Размещаем ордер на покупку
    if order_response:
        send_telegram_notification(f"Ордер размещен: КУПЛЕНО {quantity} акций {symbol} по цене {current_price}")  # Отправляем уведомление
    else:
        return  # Выходим из функции, если не удалось разместить ордер

    # Установка уровней фиксации прибыли и стоп-лосса
    take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENT)  # Цена для фиксации прибыли  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ TAKE_PROFIT_PERCENT]
    stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENT)  # Цена для стоп-лосса  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ STOP_LOSS_PERCENT]
    partial_take_profit_price = entry_price * (1 + PARTIAL_TAKE_PROFIT_PERCENT)  # Цена для частичной фиксации прибыли  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ PARTIAL_TAKE_PROFIT_PERCENT]

    stop_loss_count = [0]  # Счетчик для контроля стоп-лосса

    # Мониторинг цены
    while should_run():  # Пока стратегия должна работать
        current_price = get_current_price(symbol)  # Получаем текущую цену
        if current_price is None:  # Если не удалось получить цену
            time.sleep(60)  # Ждем 60 секунд
            continue  # Переходим к следующей итерации

        # Проверка на фиксацию прибыли
        if current_price >= take_profit_price:  # Если достигли цели по прибыли
            place_market_order(symbol, 'SELL', quantity)  # Размещаем ордер на продажу
            send_telegram_notification(f"Достигнут уровень фиксации прибыли: ПРОДАНО {quantity} акций {symbol} по цене {current_price}")  # Отправляем уведомление
            trades_count += 1  # Увеличиваем счетчик сделок
            profitable_trades += 1  # Увеличиваем счетчик прибыльных сделок
            capital_growth += quantity * (take_profit_price - entry_price)  # Обновляем рост капитала
            return  # Выходим из функции

        # Проверка на частичную фиксацию прибыли
        if current_price >= partial_take_profit_price:  # Если достигли уровня частичной фиксации прибыли
            partial_quantity = int(quantity * 0.7)  # Количество акций для продажи  ##-#-#-#-#-#-# [КОММЕНТАРИЙ: МОЖНО ИЗМЕНЯТЬ ДОЛЮ ЧАСТИЧНОЙ ПРОДАЖИ]
            place_market_order(symbol, 'SELL', partial_quantity)  # Размещаем ордер на частичную продажу
            send_telegram_notification(f"Достигнут уровень частичной фиксации прибыли: ПРОДАНО {partial_quantity} акций {symbol} по цене {current_price}")  # Отправляем уведомление

        # Проверка на стоп-лосс
        if current_price <= stop_loss_price:  # Если достигли стоп-лосса
            stop_loss_count[0] += 1  # Увеличиваем счетчик стоп-лосса
            if stop_loss_count[0] == 2:  # Если стоп-лосс сработал дважды
                place_market_order(symbol, 'SELL', quantity)  # Размещаем ордер на продажу
                send_telegram_notification(f"Сработал стоп-лосс: ПРОДАНО {quantity} акций {symbol} по цене {current_price}")  # Отправляем уведомление
                trades_count += 1  # Увеличиваем счетчик сделок
                loss_trades += 1  # Увеличиваем счетчик убыточных сделок
                capital_growth -= quantity * (entry_price - stop_loss_price)  # Обновляем рост капитала
                return  # Выходим из функции
        else:
            stop_loss_count[0] = 0  # Сбрасываем счетчик стоп-лосса

        time.sleep(60)  # Ждем 60 секунд

# Функция для проверки, должна ли стратегия работать
def should_run():
    now = datetime.datetime.now(ny_tz).time()  # Получаем текущее время
    return START_TIME <= now <= END_TIME  # Проверяем, находится ли текущее время в торговых часах

# Функция для отправки уведомления в Telegram
def send_telegram_notification(message):
    bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'  # Замените на ваш фактический токен бота  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ TELEGRAM_BOT_TOKEN]
    chat_id = 'YOUR_CHAT_ID'  # Замените на ваш фактический ID чата  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ CHAT_ID]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"  # URL для отправки сообщения
    data = {'chat_id': chat_id, 'text': message}  # Данные запроса
    response = requests.post(url, data=data)  # Отправляем POST-запрос
    if response.status_code == 200:  # Проверяем успешность запроса
        print('Уведомление успешно отправлено')  # Выводим сообщение об успешной отправке
    else:
        print(f"Не удалось отправить уведомление: {response.status_code} - {response.text}")  # Выводим сообщение об ошибке

# Функция для отправки уведомления в конце дня
def send_notification():
    global trades_count, profitable_trades, loss_trades, capital_growth  # Объявляем глобальные переменные
    message = (f"Всего сделок: {trades_count}, "
               f"Прибыльных: {profitable_trades}, "
               f"Убыточных: {loss_trades}, "
               f"Рост капитала: {capital_growth} долларов")  # Формируем сообщение
    send_telegram_notification(message)  # Отправляем уведомление

# Основной цикл стратегии
def run_strategy():
    while should_run():  # Пока стратегия должна работать
        open_position('NYCB')  # Открываем позицию по символу 'NYCB'  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ СИМВОЛ ИНСТРУМЕНТА]
        time.sleep(60)  # Ждем 60 секунд

# Задание для планировщика
def job():
    today = datetime.datetime.now(ny_tz).date()  # Получаем текущую дату
    nyse = mcal.get_calendar('NYSE').schedule(start_date=today, end_date=today)  # Проверяем расписание NYSE
    nasdaq = mcal.get_calendar('NASDAQ').schedule(start_date=today, end_date=today)  # Проверяем расписание NASDAQ
    amex = mcal.get_calendar('AMEX').schedule(start_date=today, end_date=today)  # Проверяем расписание AMEX

    if not nyse.empty or not nasdaq.empty or not amex.empty:  # Если сегодня торговый день
        run_strategy()  # Запускаем стратегию
    else:
        print("Сегодня не торговый день.")  # Выводим сообщение

# Планируем ежедневный запуск стратегии
schedule.every().day.at("10:00").do(job)  # Планируем запуск стратегии в 10:00

# Планируем ежедневное уведомление
schedule.every().day.at("16:00").do(send_notification)  # Планируем отправку уведомления в 16:00

# Запускаем планировщик
if __name__ == "__main__":
    # Убедитесь, что токены получены перед началом работы
    # Необходимо отдельно получить authorization_code и вызвать get_access_token(authorization_code)
    # Пример:
    # authorization_code = 'YOUR_AUTHORIZATION_CODE'  ##-#-#-#-#-#-# [ЗЕЛЕНЫЙ КОММЕНТАРИЙ: ВСТАВЬТЕ СВОЙ AUTHORIZATION_CODE]
    # get_access_token(authorization_code)  # Получаем Access Token

    while True:
        schedule.run_pending()  # Выполняем запланированные задачи
        time.sleep(1)  # Ждем 1 секунду



##########################################


########## Объяснение изменений: ##########

# Комментарии для каждой строки кода:
# Добавлены подробные комментарии на русском языке к каждой строке кода для лучшего понимания.
# Зеленые комментарии для ключей и идентификаторов:
# Места в коде, где необходимо вставить свои ключи или идентификаторы (CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID, TELEGRAM_BOT_TOKEN, CHAT_ID, AUTHORIZATION_CODE), помечены зелеными комментариями. Это поможет вам быстро найти и заменить эти значения на ваши собственные.
# Отметки для изменяемых параметров стратегии:
# Параметры, такие как суммы для разных ордеров (MAX_POSITION_SIZE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, PARTIAL_TAKE_PROFIT_PERCENT), отмечены комментариями. Вы можете изменить эти значения в соответствии с вашими предпочтениями.
# Отметки для символа торгуемого инструмента:
# Место, где указывается символ инструмента для торговли ('NYCB'), отмечено зеленым комментарием. Замените 'NYCB' на символ инструмента, которым вы хотите торговать.
# Инструкции по использованию кода:
# Добавлены комментарии с инструкциями по настройке и запуску стратегии, включая необходимость получения authorization_code и вставки ваших собственных значений в соответствующие места в коде.
# Пожалуйста, убедитесь, что вы заменили все плейсхолдеры (например, YOUR_CLIENT_ID, YOUR_ACCOUNT_ID) на реальные значения перед запуском кода.


########################################


########## Ответ на первый вопрос:##########

# Если я хочу изменить акцию, которой торгую, должен ли я менять символ везде или только в одном месте?

# Вы можете изменить символ торгуемой акции, заменив его в одном месте в коде. 
# Конкретно, вам нужно изменить символ в вызове функции open_position() в основном цикле стратегии. 


# В коде это выглядит так:

# python
# Copy code
# def run_strategy():
#     while should_run():
#         open_position('NYCB')  # Замените 'NYCB' на символ акции, которой вы хотите торговать
#         time.sleep(60)
# Замените 'NYCB' на символ нужной вам акции, например 'AAPL' для Apple или 'TSLA' для Tesla. 
# После этого стратегия будет торговать выбранным вами инструментом. 
# Вам не нужно менять символ в других местах кода, так как все функции используют этот символ, переданный в open_position().




###########################################



########## Ответ на второй вопрос: ##########

# Объясните мне стратегию, как она работает, шаг за шагом.

# Стратегия, реализованная в коде, основана на комбинации анализа свечных паттернов и индикатора RSI (Relative Strength Index). 
# Вот подробное объяснение каждого шага стратегии:

# Получение исторических данных:
# Стратегия запрашивает исторические данные цен акций с интервалом в 1 минуту за последние 2 дня с помощью функции get_historical_data(symbol).
# Эти данные необходимы для расчета индикатора RSI и анализа последних свечей.
# Расчет индикатора RSI:
# Используется функция get_rsi(data, window=14), которая рассчитывает RSI на основе цен закрытия за заданное количество периодов (по умолчанию 14).
# RSI измеряет скорость и изменение ценовых движений и колеблется между 0 и 100.
# Значения RSI выше 70 обычно считаются перекупленными, а ниже 30 – перепроданными.
# Анализ предыдущей свечи:
# Из исторических данных выбирается предыдущая свеча (предпоследняя запись в данных), обозначенная как previous_candle.
# Также определяется текущая цена закрытия, обозначенная как current_price.
# Извлекается значение RSI для предыдущей свечи.
# Условия для открытия позиции:
# Бычий сценарий:
# Если предыдущая свеча бычья (цена закрытия выше цены открытия) и RSI больше 50:
# Рассчитывается цена входа как середина тела свечи: entry_price = previous_candle['open'] + (previous_candle['close'] - previous_candle['open']) / 2.
# Это указывает на продолжение восходящего тренда.
# Медвежий сценарий:
# Если предыдущая свеча медвежья (цена закрытия ниже цены открытия) и RSI меньше 50:
# Цена входа устанавливается как цена закрытия предыдущей свечи: entry_price = previous_candle['close'].
# Это указывает на продолжение нисходящего тренда.
# Если ни одно из условий не выполнено:
# Стратегия не открывает позицию, считая, что нет явного тренда.
# Расчет количества акций для покупки:
# Рассчитывается максимальное количество акций, которое можно купить, исходя из MAX_POSITION_SIZE и current_price.
# Пример: если MAX_POSITION_SIZE = 1000 долларов и current_price = 50 долларов, то quantity = int(1000 / 50) = 20 акций.
# Если полученная сумма превышает MAX_POSITION_SIZE, количество акций уменьшается на 1.
# Размещение рыночного ордера на покупку:
# Если условия выполнены и количество акций больше 0, размещается рыночный ордер на покупку с помощью функции place_market_order(symbol, 'BUY', quantity).
# Отправляется уведомление в Telegram о размещении ордера.
# Установка уровней фиксации прибыли и стоп-лосса:
# Take Profit (фиксация прибыли):
# Уровень устанавливается на определенный процент выше цены входа: take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENT).
# По умолчанию TAKE_PROFIT_PERCENT = 0.06 / 100, то есть 0.06%.
# Partial Take Profit (частичная фиксация прибыли):
# Уровень для частичной продажи устанавливается: partial_take_profit_price = entry_price * (1 + PARTIAL_TAKE_PROFIT_PERCENT).
# По умолчанию PARTIAL_TAKE_PROFIT_PERCENT = 0.03 / 100, то есть 0.03%.
# Stop Loss:
# Уровень устанавливается на определенный процент ниже цены входа: stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENT).
# По умолчанию STOP_LOSS_PERCENT = 0.08 / 100, то есть 0.08%.
# Мониторинг позиции:
# Стратегия периодически (каждую минуту) проверяет текущую цену акций с помощью функции get_current_price(symbol).
# Проверка условий для выхода из позиции:
# Take Profit достигнут:
# Если текущая цена выше или равна take_profit_price, стратегия закрывает всю позицию, продавая все купленные акции.
# Отправляется уведомление в Telegram о фиксации прибыли.
# Partial Take Profit достигнут:
# Если текущая цена выше или равна partial_take_profit_price, стратегия продает часть позиции (например, 70% от количества акций).
# Отправляется уведомление в Telegram о частичной фиксации прибыли.
# Stop Loss достигнут:
# Если текущая цена ниже или равна stop_loss_price, увеличивается счетчик stop_loss_count.
# Если цена дважды подряд коснулась уровня стоп-лосса (то есть stop_loss_count == 2), стратегия закрывает всю позицию, продавая все оставшиеся акции.
# Отправляется уведомление в Telegram о срабатывании стоп-лосса.
# Счетчик используется для предотвращения случайного закрытия позиции при кратковременном снижении цены.
# Обновление статистики:
# После закрытия позиции обновляются статистические данные:
# trades_count — общее количество сделок увеличивается на 1.
# profitable_trades или loss_trades увеличиваются в зависимости от результата сделки.
# capital_growth обновляется на величину прибыли или убытка от сделки.
# Завершение мониторинга:
# Если позиция закрыта (по одному из условий), функция open_position() завершается.
# Стратегия возвращается к основному циклу и может искать новые возможности для открытия позиции.
# Планирование работы стратегии:
# Стратегия работает только в определенные часы, заданные переменными START_TIME и END_TIME.
# Функция should_run() проверяет, находится ли текущее время в заданном диапазоне.
# Планировщик schedule используется для запуска стратегии в нужное время и для отправки уведомлений в конце торгового дня.
# Ежедневное уведомление о результатах:
# В конце дня (в 16:00 по времени Нью-Йорка) функция send_notification() отправляет сводку о количестве сделок, прибыльных и убыточных сделках, а также о росте капитала.
# Итоговое описание стратегии:

# Цель стратегии — воспользоваться краткосрочными движениями цены акций, основываясь на последних свечных паттернах и значениях индикатора RSI.
# Вход в позицию осуществляется при подтверждении направления тренда:
# В длинную позицию (покупка) при восходящем тренде и RSI > 50.
# В короткую позицию (продажа) стратегия не реализует, но можно расширить функционал для этого.
# Выход из позиции происходит при достижении целей по прибыли или при срабатывании стоп-лосса.
# Управление рисками обеспечивается через ограничения по максимальному размеру позиции, установку стоп-лосса и фиксацию прибыли.
# Автоматизация достигается с помощью периодических проверок и автоматических действий (покупка, продажа, отправка уведомлений).
# Замечания:

# Настройка параметров стратегии:
# Вы можете изменить параметры MAX_POSITION_SIZE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, PARTIAL_TAKE_PROFIT_PERCENT для адаптации стратегии под ваши предпочтения и рыночные условия.
# Расширение функционала:
# Стратегия может быть расширена для работы с несколькими акциями, дополнительными индикаторами или условиями входа/выхода.
# Тестирование:
# Рекомендуется протестировать стратегию на исторических данных или в демо-среде перед применением на реальном рынке.
# Важно: Всегда помните о рисках, связанных с торговлей на финансовых рынках. Убедитесь, что вы полностью понимаете стратегию и ее возможные последствия перед использованием ее в реальной торговле.