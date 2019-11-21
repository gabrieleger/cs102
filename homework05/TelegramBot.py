import requests
import config
import telebot
from bs4 import BeautifulSoup
import datetime
import time

telebot.apihelper.proxy = {'https': 'socks5://veryshit:dude@proxy.prokhn.ru:1080'}
bot = telebot.TeleBot(config.access_token)

DAY_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain='http://www.ifmo.ru/ru/schedule/0',
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page


def parse_schedule_for_day(web_page, day_name):
    soup = BeautifulSoup(web_page, "html5lib")
    schedule_table = soup.find("table", attrs={"id": f"{DAY_NAMES.index(day_name) + 1}day"})
    if schedule_table is None:
        return

    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info])
                    for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list

@bot.message_handler(commands=DAY_NAMES)
def get_schedule(message):
    """ Получить расписание на указанный день """
    day, week, group = message.text.split()
    day = day[1:]

    web_page = get_page(group, week)
    schedule_for_day = parse_schedule_for_day(web_page, day)
    if schedule_for_day is None:
        bot.send_message(message.chat.id, 'No lessons')
    else:
        resp = ''
        times_lst, locations_lst, lessons_lst = schedule_for_day
        for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    """ Получить ближайшее занятие """
    _, group = message.text.split()
    current_day = datetime.date.today().weekday()
    if current_day == 7:
        current_day = 0

    web_page = get_page(group)
    not_found = True
    today = True
    while not_found:
        if today:
            today = False
            schedule_for_day = parse_schedule_for_day(web_page, DAY_NAMES[current_day])
            if schedule_for_day is None:
                continue
            else:
                times_lst, locations_lst, lessons_lst = schedule_for_day
                now_time = time.strptime(time.strftime('%H:%M'), '%H:%M')
                for time_comarison in range(len(times_lst)):
                    if now_time < time.strptime(times_lst[time_comarison].split('-')[0], '%H:%M'):
                        bot.send_message(message.chat.id, f'Nearest lesson today at:{times_lst[time_comarison]}\n'
                                                          f'Lesson: {lessons_lst[time_comarison]} at'
                                                          f' {locations_lst[time_comarison]}')
                        not_found = False
                        break
        else:
            current_day += 1
            if current_day == 7:
                current_day = 0
            schedule_for_day = parse_schedule_for_day(web_page, DAY_NAMES[current_day])
            if schedule_for_day is None:
                continue
            else:
                times_lst, locations_lst, lessons_lst = schedule_for_day
                bot.send_message(message.chat.id, f'Nearest lesson on {DAY_NAMES[current_day].capitalize()} at:'
                                                  f'{times_lst[0]}\n'
                                                  f'Lesson: {lessons_lst[0]} in '
                                                  f'{locations_lst[0]}')
                not_found = False


@bot.message_handler(commands=['tomorrow'])
def get_tomorrow(message):
    """ Получить расписание на следующий день """
    tmrw_day = datetime.date.today().weekday() + 1
    if tmrw_day == 7:
        tmrw_day = 0
    tmrw_day = DAY_NAMES[tmrw_day]

    _, group = message.text.split()
    web_page = get_page(group)
    schedule_for_day = parse_schedule_for_day(web_page, tmrw_day)

    if schedule_for_day is None:
        bot.send_message(message.chat.id, 'No lessons')
    else:
        resp = f'Tomorrow Day: {tmrw_day.capitalize()}\n'
        times_lst, locations_lst, lessons_lst = schedule_for_day
        for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    _, group = message.text.split()

    for day in DAY_NAMES:
        resp = f'{day.capitalize()} lessons:\n'
        web_page = get_page(group)
        schedule_for_day = parse_schedule_for_day(web_page, day)
        if schedule_for_day is None:
            bot.send_message(message.chat.id, resp + 'No lessons')
        else:
            times_lst, locations_lst, lessons_lst = schedule_for_day
            for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
                resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
            bot.send_message(message.chat.id, resp, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)
