import pymongo
import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


bot = telebot.TeleBot('6979419854:AAE2hMOTy2n8EBgLu1nehXVZUd4CTtO4FIE') 
keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
db_client = pymongo.MongoClient('mongodb://localhost:27017')
current_db = db_client['projectdb'] 
collection = current_db['songs'] 


def get_news():
    """Возвращает новости за последний месяц по ключу Oxxxymiron. Если их нет - выводит сообщение об отсутствии новостей

    :returns: новости или сообщение, что их нет
    :rtype: str
    .. note: требуются библиотеки request и модуль datetime"""

    current_date = datetime.now()
    month_ago = current_date - timedelta(days=30)
    current_date_str = current_date.strftime("%Y-%m-%d")
    month_ago_str = month_ago.strftime("%Y-%m-%d")

    keyword = 'Oxxxymiron'
    my_api = 'e3b155e0fc63466eb7c22c57823f8b9a'
    url = f"https://newsapi.org/v2/everything?q={keyword}&from={month_ago_str}&to={current_date_str}&sortBy=popularity&apiKey={my_api}"

    response = requests.get(url)
    data = response.json()
    news_articles = data['articles']

    if len(news_articles) == 0:
        return 'К сожалению, за последний месяц про Мирона нет новостей :('
    
    res = ''
    for article in news_articles:
        res += article['title'] + '\n'
    return res

def get_concerts():
    """Возвращает список предстоящих концертов Мирона (дата, время, город). Если их нет - выводит сообщение об отсутствии концертов.

    :returns: афиша концертов или сообщение, что их нет
    :rtype: str
    .. note: требуются библиотеки request, lxml и модуль bs4"""

    site_url = 'https://oxxymiron.com/events'
    responce = requests.get(site_url).text
    soup = BeautifulSoup(responce, 'lxml')

    list_block = [i for i in soup.find('div', id = 'content')]
    necessary_block = list_block[4]
    list_of_inf = str(necessary_block).split('-module--date--cfa68"')

    if len(list_of_inf) <= 1:
        return 'В ближайшее время концертов не будет :( \nВозвращайтесь позже!'

    inf_all_cities = ''
    for i in range(1, len(list_of_inf)):
        item = list_of_inf[i]
        date = item[1:15]
        time = item[75:80]
        city = item[206:][:item[206:].find('<')]
        inf_one_city = date + ' ' + time + ' ' + city
        inf_all_cities += inf_one_city + '\n'

    return inf_all_cities


@bot.message_handler(commands=['start']) 
def start(message):
    """Обрабатывает команду start и отправляет приветственное сообщение со списком доступных функций

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} \n \
                     \nВсе функции:\n-Открыть оффициальный сайт\n-Получить текст трека по названию\n-Получить ссылки на аккаунты Мирона\n-Получить афишу концертов')

@bot.message_handler(commands=['ofsite'])
def open_official_site(message):
    """Обрабатывает команду ofsite и отправляет гиперссылку на официальный сайт Мирона

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    link = '[Официальный сайт](https://oxxxymiron.com/)'
    bot.send_message(message.chat.id, link, parse_mode='Markdown')

@bot.message_handler(commands=['links'])
def send_links(message):
    """Обрабатывает команду links и отправляет ссылки на аккаунты Мирона в inst, tg и vk

    :param message: информация о боте, чате и пользователе
    :type x: dict"""
    
    links = "tg: @norimyxxxo \ninst: @norimyxxxo \nvk: @oxxxymiron"
    bot.send_message(message.chat.id, links)

@bot.message_handler(commands=['poster'])
def send_poster(message):
    """Обрабатывает команду poster и отправляет актуальную афишу концертов или сообщение, что предстоящих концертов нет

    :param message: информация о боте, чате и пользователе
    :type x: dict"""
    
    responce = get_concerts()
    bot.send_message(message.chat.id, responce)

@bot.message_handler(commands=['news'])
def send_news(message):
    """Обрабатывает команду news и отправляет новости за последний месяц по ключу Oxxxymiron. Если их нет - отправляет сообщение об отсутствии новостей

    :param message: информация о боте, чате и пользователе
    :type x: dict"""
    
    responce = get_news()
    bot.send_message(message.chat.id, responce)


@bot.message_handler(commands=['gettrack'])
def get_name_of_track(message):
    """Обрабатывает команду gettrack, просит пользователя ввести название трека, переходит к функциям отправки текста и отправки пояснений

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    track_name = bot.send_message(message.chat.id, 'Введите название трека: ', reply_markup = keyboard)
    bot.register_next_step_handler(track_name, send_inf_by_name)
    bot.register_next_step_handler(track_name, send_track_by_name)
    bot.register_next_step_handler(track_name, send_explanations_by_track)

def send_inf_by_name(message):
    """Получает от функции get_name_of_track() название трека и отправляет основную информацию о нем

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    key = message.text
    track = collection.find_one({'name': key})

    responce = track['date']

    if 'album' in (collection.find_one({'name': key})).keys():
        responce += '\n' + track['album']

    if 'feat' in (collection.find_one({'name': key})).keys():
        responce += '\n' + track['feat']

    bot.send_message(message.chat.id, responce)

def send_track_by_name(message):
    """Получает от функции get_name_of_track() название трека и отправляет его текст после обращения к бд

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    key = message.text
    responce = (collection.find_one({'name': key}))['text']
    bot.send_message(message.chat.id, responce)
    
def send_explanations_by_track(message):
    """Получает от функции get_name_of_track() название трека и отправляет пояснения к нему после обращения к бд

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    key = message.text
    responce = (collection.find_one({'name': key}))['explan']
    bot.send_message(message.chat.id, responce)


@bot.message_handler(commands=['getword'])
def get_word(message):
    """Обрабатывает команду getword, просит пользователя ввести слово или фразу, переходит к функции отправки списка треков

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    album_name = bot.send_message(message.chat.id, 'Введите слово или фразу, которую хотите найти: ', reply_markup = keyboard)
    bot.register_next_step_handler(album_name, send_tracks)

def send_tracks(message):
    """Получает от функции get_word() слово от пользователя и отправляет список треков, в названии или тексте которого есть данное слово

    :param message: информация о боте, чате и пользователе
    :type x: dict"""

    key = message.text
    res_album = collection.find({'name': {'$regex': f'.*{key}.*'}})
    res_text = collection.find({'text': {'$regex': f'.*{key}.*'}})

    responce = ''
    for record in res_album:
        responce += record['name'] + '\n'

    for record in res_text:
        responce += record['name'] + '\n'

    bot.send_message(message.chat.id, responce)
        

bot.polling(none_stop=True) 
