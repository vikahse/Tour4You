import aiogram
from aiogram import Dispatcher, types
import uuid
from dataclasses import dataclass
from enum import Enum
from Tour import Tour
import copy
import json
from db import *

admins = [558838836, 842921731, 442132164]

class ExpectedMessage(Enum):
    unexpected = 0
    city_for_solo_tour = 1
    city_for_group_tour = 2
    age_for_reg = 3
    change_age = 4
    sex_for_reg = 5
    change_sex = 6
    dl_for_reg = 7
    change_dl = 8
    name_for_reg = 9
    change_name = 10
    contacts_for_reg = 11
    change_contacts = 12
    cur_form_purpose = 13
    cur_duration_of_trip = 14
    cur_form_company = 15
    cur_form_budget = 16
    cur_form_lifestyle = 17
    cur_form_count_visiting = 18
    cur_form_transport = 19
    cur_form_contacts = 20
    cur_form_comment = 21
    wait_user_mes = 22
    user_id = 23


class FormForOne:
    # При изменении класса надо также менять Users Encoder
    town = "Not filled"
    purpose_of_trip = "Not filled"
    duration_of_trip = "Not filled"
    company = "Not filled"
    budget = "Not filled"
    lifestyle = "Not filled"
    count_visiting = "Not filled"
    transport = "Not filled"
    contacts = "Not filled"
    comments = "Not filled"


@dataclass
class Chat:
    # При изменении класса надо также менять Users Encoder
    registration = False
    filling_the_form = False
    age = 18
    expect_mes = ExpectedMessage.unexpected
    all_blocked = False
    sex = True
    dl = False
    name = "User Name"
    contacts = "None"
    tour_count = 0
    tours = []
    cur_tour = FormForOne()  # текущая анкета для заполнения


class UsersEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Chat):
            return {"AGE": o.age, "EXPECT_MES": o.expect_mes, "ALL_BLOCKED": o.all_blocked, "SEX": o.sex, "DL": o.dl,
                    "NAME": o.name, "CONTACTS": o.contacts, "TOUR_COUNT": o.tour_count, "TOURS": o.tours,
                    "CUR_TOUR": o.cur_tour, "REGISTRATION": o.registration, "FILLING_THE_FORM": o.filling_the_form}
        elif isinstance(o, ExpectedMessage):
            return o.value
        elif isinstance(o, FormForOne):
            return {"town": o.town, "purpose_of_trip": o.purpose_of_trip, "duration_of_trip": o.duration_of_trip,
                    "company": o.company, "budget": o.budget, "lifestyle": o.lifestyle,
                    "count_visiting": o.count_visiting, "transport": o.transport, "contacts": o.contacts,
                    "comments": o.comments}
        return json.JSONEncoder.default(self, o)


def tour_maker(dic):
    res = FormForOne()
    res.town = dic["town"]
    res.purpose_of_trip = dic["purpose_of_trip"]
    res.duration_of_trip = dic["duration_of_trip"]
    res.company = dic["company"]
    res.budget = dic["budget"]
    res.lifestyle = dic["lifestyle"]
    res.count_visiting = dic["count_visiting"]
    res.transport = dic["transport"]
    res.contacts = dic["contacts"]
    res.comments = dic["comments"]
    return res


def chat_maker(dic):
    res = dict()
    for i in dic:
        res[int(i)] = Chat()
        res[int(i)].filling_the_form = bool(dic[i]["FILLING_THE_FORM"])
        res[int(i)].registration = bool(dic[i]["REGISTRATION"])
        res[int(i)].age = int(dic[i]["AGE"])
        res[int(i)].expect_mes = dic[i]["EXPECT_MES"]
        res[int(i)].all_blocked = bool(dic[i]["ALL_BLOCKED"])
        res[int(i)].sex = bool(dic[i]["SEX"])
        res[int(i)].dl = bool(dic[i]["DL"])
        res[int(i)].name = dic[i]["NAME"]
        res[int(i)].contacts = dic[i]["CONTACTS"]
        res[int(i)].tour_count = dic[i]["TOUR_COUNT"]
        res[int(i)].cur_tour = tour_maker(dic[i]["CUR_TOUR"])
        res[int(i)].tours = []
        for tour in dic[i]["TOURS"]:
            res[int(i)].tours.append(tour_maker(tour))
    return res


class Bot:
    def __init__(self, token, users_file_name):
        self.bot = aiogram.Bot(token)
        self.dp = Dispatcher(self.bot)
        with open(users_file_name, "r") as ufn:
            self.chats = json.load(ufn)
        self.user_file = users_file_name
        self.expected_message_type = ExpectedMessage.unexpected

    async def print_special_message(self, chat_id, mes_type, user):
        if mes_type == 'start':
            # profiles.add_user(chat_id)
            if chat_id in self.chats:
                if not self.chats[user["id"]].filling_the_form:
                    await self.print_special_message(chat_id, "menu", user)
                else:
                    self.chats[user["id"]].all_blocked = False
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_y = types.InlineKeyboardButton(text='Выйти', callback_data='exit_from_form_start')
                    but_n = types.InlineKeyboardButton(text='Продолжить заполнять',
                                                       callback_data='continue_filling_the_form')
                    markup.add(but_y, but_n)
                    await self.bot.send_message(chat_id,
                                                'Вы уверены, что хотите прекратить заполнять форму ? Ответы не будут сохранены ❌',
                                                reply_markup=markup)
            else:
                self.chats[chat_id] = Chat()
                markup = types.InlineKeyboardMarkup(row_width=1)
                but_y = types.InlineKeyboardButton(text='Да', callback_data='start_work')
                but_i = types.InlineKeyboardButton(text='Посмотреть справку', callback_data='help')
                markup.add(but_y, but_i)
                self.chats[user["id"]] = Chat()
                await self.bot.send_message(chat_id,
                                            'Приветствуем 👋 Команда Tour4You очень рада, что Вы заглянули к нам! '
                                            'Чтобы больше узнать о нас, Вы можете просмотреть справку ⬇ '
                                            '\nА если Вы уже готовы, то давайте спланируем Ваше путешествие ? 🤩',
                                            reply_markup=markup)
        elif mes_type == 'start_after_info':
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_y = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='start_work')
            but_i = types.InlineKeyboardButton(text='Посмотреть справку', callback_data='help')
            markup.add(but_y, but_i)
            await self.bot.send_message(chat_id, 'Прежде, чем приступить, пройдите, пожалуйста, быструю анкету 🙏',
                                        reply_markup=markup)
        elif mes_type == 'plug':
            await self.bot.send_message(chat_id, 'Эта функция еще не реализована')
            # заглушка для нереализованных функций
            await self.print_special_message(chat_id, "menu", user)
        elif mes_type == 'menu':
            if chat_id in self.chats:
                if not self.chats[user["id"]].registration:
                    await self.print_special_message(chat_id, "start_after_info", user)
                elif self.chats[user["id"]].filling_the_form:
                    self.chats[user["id"]].all_blocked = False
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_y = types.InlineKeyboardButton(text='Выйти', callback_data='exit_from_form_menu')
                    but_n = types.InlineKeyboardButton(text='Продолжить заполнять',
                                                       callback_data='continue_filling_the_form')
                    markup.add(but_y, but_n)
                    await self.bot.send_message(chat_id,
                                                'Вы уверены, что хотите прекратить заполнять форму ? Ответы не будут сохранены ❌',
                                                reply_markup=markup)
                else:
                    self.chats[user["id"]].expect_mes = ExpectedMessage.unexpected
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_e = types.InlineKeyboardButton(text='Редактировать информацию о себе',
                                                       callback_data='edit_profile')
                    but_po = types.InlineKeyboardButton(text='Спланировать путешествие для меня',
                                                        callback_data='tour_one')
                    # but_pm = types.InlineKeyboardButton(text='Спланировать путешествие для компании', callback_data='tour_many')
                    but_pt = types.InlineKeyboardButton(text='Покажи мои прошлые путешествия',
                                                        callback_data='prev_tours')
                    but_inf = types.InlineKeyboardButton(text='Справка о компании', callback_data='comp_info')
                    markup.add(but_e, but_po, but_pt, but_inf)
                    await self.bot.send_message(chat_id, '🔮 Чем могу помочь? 🔮', reply_markup=markup)
            else:
                await self.print_special_message(chat_id, "start", user)
        elif mes_type == 'profile_info':
            if chat_id in self.chats:
                if not self.chats[user["id"]].registration:
                    await self.print_special_message(chat_id, "start_after_info", user)
                elif self.chats[user["id"]].filling_the_form:
                    self.chats[user["id"]].all_blocked = False
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_y = types.InlineKeyboardButton(text='Выйти', callback_data='exit_from_form_profile_info')
                    but_n = types.InlineKeyboardButton(text='Продолжить заполнять',
                                                       callback_data='continue_filling_the_form')
                    markup.add(but_y, but_n)
                    await self.bot.send_message(chat_id,
                                                'Вы уверены, что хотите прекратить заполнять форму ? Ответы не будут сохранены ❌',
                                                reply_markup=markup)
                else:
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_n = types.InlineKeyboardButton(text='Изменить имя', callback_data='change_name')
                    but_a = types.InlineKeyboardButton(text='Изменить возраст', callback_data='change_age')
                    but_b = types.InlineKeyboardButton(text='Изменить пол', callback_data='change_sex')
                    but_c = types.InlineKeyboardButton(text='Наличие прав', callback_data='change_dl')
                    but_d = types.InlineKeyboardButton(text='Изменить контакты', callback_data='change_contacts')
                    but_m = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')
                    markup.add(but_n, but_a, but_b, but_c, but_d, but_m)
                    await self.bot.send_message(chat_id, 'Информация профиля:'
                                                         '\n⭐ Имя: {0}'
                                                         '\n⭐ Возраст: {1}'
                                                         '\n⭐ Пол: {2}'
                                                         '\n⭐ Наличие водительских прав: {3}'
                                                         '\n⭐ Контакты: {4}'.format(str(self.chats[user["id"]].name),
                                                                                    str(self.chats[user["id"]].age),
                                                                                    "Мужской" if self.chats[
                                                                                        user["id"]].sex
                                                                                    else "Женский",
                                                                                    "Есть" if self.chats[
                                                                                        user["id"]].dl else "Нет",
                                                                                    str(self.chats[
                                                                                            user["id"]].contacts)),
                                                reply_markup=markup)
            else:
                await self.print_special_message(chat_id, "start", user)
        elif mes_type == 'plan_solo_tour':
            self.chats[user["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[user["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[user["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[user["id"]].cur_tour.company = "Not Filled"
            self.chats[user["id"]].cur_tour.budget = "Not Filled"
            self.chats[user["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[user["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[user["id"]].cur_tour.transport = "Not Filled"
            self.chats[user["id"]].cur_tour.comments = "Not Filled"
            self.chats[user["id"]].cur_tour.contacts = "Not Filled"

            await self.bot.send_message(chat_id, '🗺 Давайте спланируем Вам незабываемое путешествие 🗺',
                                        reply_markup=None)
            self.chats[user["id"]].filling_the_form = True
            await self.bot.send_message(chat_id, '📍 В какой город Вы поедете?', reply_markup=None)
            self.chats[user["id"]].expect_mes = ExpectedMessage.city_for_solo_tour
            self.chats[user["id"]].all_blocked = True
        elif mes_type == "info":
            if chat_id in self.chats:
                if not self.chats[user["id"]].registration:
                    await self.print_special_message(chat_id, "start_after_info", user)
                elif self.chats[user["id"]].filling_the_form:
                    self.chats[user["id"]].all_blocked = False
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    but_y = types.InlineKeyboardButton(text='Выйти', callback_data='exit_from_form_info')
                    but_n = types.InlineKeyboardButton(text='Продолжить заполнять',
                                                       callback_data='continue_filling_the_form')
                    markup.add(but_y, but_n)
                    await self.bot.send_message(chat_id,
                                                'Вы уверены, что хотите прекратить заполнять форму ? Ответы не будут сохранены ❌',
                                                reply_markup=markup)
                else:
                    await self.bot.send_message(chat_id,
                                                '💟 Мы стартап Tour4You 💟 Отвечаем за Ваш насыщенный и интересный отдых, '
                                                'составляя за Вас программу путешествия и прокладывая маршрут 🗺'
                                                '\n\n✈️ Сейчас мы предлагаем Вам познакомиться с предлагаемыми возможностями и '
                                                'оценить качество предложенной услуги. Для этого Вам необходимо заполнить первоначальную анкету, '
                                                'указав информацию о себе в нашем телеграмм боте @Tour4You_Bot. Затем Вы можете заполнить анкету для составления путешествий, указав свои интересы, '
                                                'намерения и пожелания на Вашу ближайшую поездку. После отправки, в течение суток, Вы получите подробный план путешествия, отвечающий всем Вашим пожеланиям. '
                                                'А так же мы будем рады получить Ваш фидбек.'
                                                '\n\n💰Стоимость одного плана путешествия: 200 рублей'
                                                '\n💰Способ оплаты: онлайн перевод'
                                                '\n\n☎ Контакты для связи ☎'
                                                '\n➡ Светлана: @Svetlana_Gi'
                                                '\n➡ Виктория: @at_one_day'
                                                '\n➡ Даниил: @Daniilklo'
                                                '\n\n📩 Наша почта 📩 Tour4You@yandex.ru'
                                                '\n\n❓Функционал бота ❓'
                                                '\n📌 Вкладка «Редактировать информацию о себе» - в любое удобное время, Вы можете '
                                                'изменить информацию о себе'
                                                '\n📌 Вкладка «Спланировать путешествия для меня» - нажав на нее Вы сможете заполнить анкету '
                                                'для планирования нового путешествия'
                                                '\n📌 Вкладка «Покажи мои прошлые путешествия» - в любое время Вы сможете возвращаться к уже '
                                                'созданным планам Ваших путешествий')
                    await self.print_special_message(chat_id, "menu", user)
            else:
                await self.print_special_message(chat_id, "start", user)
        elif mes_type == "hi_admin":
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_m = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')
            but_e = types.InlineKeyboardButton(text='Завершить работу программы', callback_data='end')
            but_s = types.InlineKeyboardButton(text='Сохранить данные о пользователях', callback_data='save')
            but_uo = types.InlineKeyboardButton(text='Посмотреть невыполненные заказы', callback_data='uncomp_orders')
            but_po = types.InlineKeyboardButton(text='Посмотреть выполненные заказы', callback_data='comp_orders')
            but_st = types.InlineKeyboardButton(text='Статистика', callback_data='stat')
            but_sp = types.InlineKeyboardButton(text='Отправить план', callback_data='send_plan')
            but_sm = types.InlineKeyboardButton(text='Отправить сообщение пользователю', callback_data='send_mes')
            markup.add(but_m, but_e, but_s, but_uo, but_po, but_sp, but_st, but_sm)
            await self.bot.send_message(chat_id, 'Привет админ', reply_markup=markup)
        elif mes_type == "perm_denied":
            await self.bot.send_message(chat_id, 'Нет доступа')
            await self.print_special_message(chat_id, "menu", user)
        else:
            await self.bot.send_message(chat_id, 'Я тебя не понял :(')

    async def reply_inline_call(self, call):
        chat_id = call.message.chat.id
        if chat_id not in self.chats:
            self.chats[chat_id] = Chat()
        if self.chats[call["from"]["id"]].all_blocked:
            pass
        elif call.data == 'start_work':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.registration(chat_id, call["from"], 3)
        elif call.data == 'help':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call.message.chat.id,
                                        '💟 Мы стартап Tour4You 💟 Отвечаем за Ваш насыщенный и интересный отдых, '
                                        'составляя за Вас программу путешествия и прокладывая маршрут 🗺'
                                        '\n\n✈️ Сейчас мы предлагаем Вам познакомиться с предлагаемыми возможностями и '
                                        'оценить качество предложенной услуги. Для этого Вам необходимо заполнить первоначальную анкету, '
                                        'указав информацию о себе в нашем телеграмм боте @Tour4You_Bot. Затем Вы можете заполнить анкету для составления путешествий, указав свои интересы, '
                                        'намерения и пожелания на Вашу ближайшую поездку. После отправки, в течение суток, Вы получите подробный план путешествия, отвечающий всем Вашим пожеланиям. '
                                        'А так же мы будем рады получить Ваш фидбек.'
                                        '\n\n💰Стоимость одного плана путешествия: 200 рублей'
                                        '\n💰Способ оплаты: онлайн перевод'
                                        '\n\n☎ Контакты для связи ☎'
                                        '\n➡ Светлана: @Svetlana_Gi'
                                        '\n➡ Виктория: @at_one_day'
                                        '\n➡ Даниил: @Daniilklo'
                                        '\n\n📩 Наша почта 📩 Tour4You@yandex.ru'
                                        '\n\n❓Функционал бота ❓'
                                        '\n📌 Вкладка «Редактировать информацию о себе» - в любое удобное время, Вы можете '
                                        'изменить информацию о себе'
                                        '\n📌 Вкладка «Спланировать путешествия для меня» - нажав на нее Вы сможете заполнить анкету '
                                        'для планирования нового путешествия'
                                        '\n📌 Вкладка «Покажи мои прошлые путешествия» - в любое время Вы сможете возвращаться к уже '
                                        'созданным планам Ваших путешествий')
            await self.print_special_message(chat_id, "start_after_info", call["from"])
            # await self.print_special_message(chat_id, 'plug', call["from"])
        elif call.data == 'edit_profile':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.print_special_message(chat_id, 'profile_info', call["from"])
        elif call.data == 'tour_one':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.print_special_message(chat_id, 'plan_solo_tour', call["from"])
        elif call.data == 'tour_many':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'plug', call["from"])
        elif call.data == 'back_to_menu':
            # await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            self.expected_message_type = ExpectedMessage.unexpected
            # self.chats[call["from"]["id"]].all_blocked = False
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'menu', call["from"])
        elif call.data == 'change_age':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], '🟣 Каков ваш возраст?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_age
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == 'change_sex':
            markup = types.InlineKeyboardMarkup()
            but_m = types.InlineKeyboardButton(text='Мужской', callback_data="change_sex_male")
            but_w = types.InlineKeyboardButton(text='Женский', callback_data="change_sex_female")
            markup.add(but_m, but_w)
            await self.bot.send_message(call.message.chat.id, '🟣 Каков Ваш пол?', reply_markup=markup)
        elif call.data == 'change_dl':
            markup = types.InlineKeyboardMarkup()
            but_yes = types.InlineKeyboardButton(text='Да', callback_data="change_dl_yes")
            but_no = types.InlineKeyboardButton(text='Нет', callback_data="change_dl_no")
            markup.add(but_yes, but_no)
            await self.bot.send_message(call.message.chat.id, '🟣 У Вас есть водительские права?', reply_markup=markup)
        elif call.data == 'registration_sex_male':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call.message.chat.id, 'Пол: Мужской', reply_markup=None)
            self.chats[call["from"]["id"]].sex = True
            await self.registration(chat_id, call["from"], 2)
        elif call.data == 'registration_sex_female':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call.message.chat.id, 'Пол: Женский', reply_markup=None)
            self.chats[call["from"]["id"]].sex = False
            await self.registration(chat_id, call["from"], 2)
        elif call.data == 'change_sex_male':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call.message.chat.id, 'Пол: Мужской', reply_markup=None)
            self.chats[call["from"]["id"]].sex = True
            await self.print_special_message(call["from"]["id"], "profile_info", call["from"])
        elif call.data == 'change_sex_female':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call.message.chat.id, 'Пол: Женский', reply_markup=None)
            self.chats[call["from"]["id"]].sex = False
            await self.print_special_message(call["from"]["id"], "profile_info", call["from"])
        elif call.data == 'registration_dl_yes':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id, 'Наличие водительских прав: Есть', reply_markup=None)
            self.chats[call["from"]["id"]].dl = True
            await self.registration(chat_id, call["from"], 4)
        elif call.data == 'registration_dl_no':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id, 'Наличие водительских прав: Нет', reply_markup=None)
            self.chats[call["from"]["id"]].dl = False
            await self.registration(chat_id, call["from"], 4)
        elif call.data == 'change_dl_yes':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id, 'Наличие водительских прав: Есть', reply_markup=None)
            self.chats[call["from"]["id"]].dl = True
            await self.print_special_message(call["from"]["id"], "profile_info", call["from"])
        elif call.data == 'change_dl_no':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id, 'Наличие водительских прав: Нет', reply_markup=None)
            self.chats[call["from"]["id"]].dl = False
            await self.print_special_message(call["from"]["id"], "profile_info", call["from"])
        elif call.data == 'change_name':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], '🟣 Как Вас зовут?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_name
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == 'change_contacts':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], '🟣 Как еще можно с Вами связаться (телефон/почта/...) ?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_contacts
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == 'prev_tours':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            if len(self.chats[call["from"]["id"]].tours) == 0:
                await self.bot.send_message(call["from"]["id"], 'У Вас еще нет планов путешествий 🥺')
                await self.print_special_message(call["from"]["id"], "menu", call["from"])
            else:
                for i in range(len(self.chats[call["from"]["id"]].tours)):
                    await self.bot.send_message(call["from"]["id"], '✈️ Поездка № {0}'
                                                                    '\n📍 Куда: {1}'
                                                                    '\n📍 Дата поездки: {2}'
                                                                    '\n📍 Ссылка на план путешествия: \n\n'.format(
                        str(i + 1),
                        self.chats[call["from"]["id"]].tours[i].town,
                        self.chats[call["from"]["id"]].tours[i].duration_of_trip))
                await self.print_special_message(call["from"]["id"], "menu", call["from"])
        elif call.data == "comp_info":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.print_special_message(chat_id, 'info', call["from"])
        elif call.data == "cur_form_comment_yes":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], 'Напишите Ваш комментарий:')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.cur_form_comment
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == "cur_form_comment_no":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_s = types.InlineKeyboardButton(text='Отправить анкету', callback_data="send_cur_form")
            but_a = types.InlineKeyboardButton(text='Заполнить анкету заново', callback_data="fill_form_again")
            markup.add(but_s, but_a)
            await self.bot.send_message(call["from"]["id"], '⬇ Ваши ответы ⬇'
                                                            '\n\n🔘 Город, куда планируете поехать: {0}'
                                                            '\n\n🔘 Цель поездки: {1}'
                                                            '\n\n🔘Период пребывания в этом городе и дата поездки: {2}'
                                                            '\n\n🔘В каком составе планируете поехать: {3}'
                                                            '\n\n🔘Бюджет поездки (сегмент заведений): {4}'
                                                            '\n\n🔘Ваш образ жизни: {5}'
                                                            '\n\n🔘Который раз посещаете этот город: {6}'
                                                            '\n\n🔘На каком транспорте добираетесь до города: {7}'
                                                            '\n\n🔘Комментарий: {8}'
                                                            '\n\n🔘Ваши контакты: {9}'.format(
                self.chats[call["from"]["id"]].cur_tour.town,
                self.chats[call["from"]["id"]].cur_tour.purpose_of_trip,
                self.chats[call["from"]["id"]].cur_tour.duration_of_trip,
                self.chats[call["from"]["id"]].cur_tour.company,
                self.chats[call["from"]["id"]].cur_tour.budget,
                self.chats[call["from"]["id"]].cur_tour.lifestyle,
                self.chats[call["from"]["id"]].cur_tour.count_visiting,
                self.chats[call["from"]["id"]].cur_tour.transport,
                self.chats[call["from"]["id"]].cur_tour.comments,
                self.chats[call["from"]["id"]].cur_tour.contacts), reply_markup=markup)
        elif call.data == "send_cur_form":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

            # добавили в db 
            copy_cur_tour = copy.copy(self.chats[call["from"]["id"]].cur_tour)
            list_parametrs = [str(uuid.uuid4()), call.message.chat.id, copy_cur_tour.town, copy_cur_tour.purpose_of_trip,
                              copy_cur_tour.duration_of_trip,
                              copy_cur_tour.company, copy_cur_tour.budget, copy_cur_tour.lifestyle,
                              copy_cur_tour.count_visiting,
                              copy_cur_tour.transport, copy_cur_tour.contacts, copy_cur_tour.comments]
            cur_user_form = [tuple(list_parametrs)]
            with con:
                con.executemany(sql, cur_user_form)

            # self.chats[call["from"]["id"]].tours.append(copy.copy(self.chats[call["from"]["id"]].cur_tour))
            # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"
            await self.bot.send_message(call["from"]["id"], 'Ваша анкета отправлена ✅ Скоро с Вами свяжутся!'
                                                            '\n☎ Контакты для связи ☎'
                                                            '\n➡ Светлана: @Svetlana_Gi'
                                                            '\n➡ Виктория: @at_one_day'
                                                            '\n➡ Даниил: @Daniilklo'
                                                            '\n📩 Наша почта 📩 Tour4You@yandex.ru')
            self.chats[call["from"]["id"]].filling_the_form = False

            # отправить уведомления админам
            for admin in admins:
                await self.bot.send_message(admin, "🆘 User {0} заполнил анкету, просмотрите в незаконченных "
                                                   "заказах 🆘".format(call["from"]["id"]))

            await self.print_special_message(chat_id, 'menu', call["from"])
        elif call.data == "fill_form_again":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"
            await self.print_special_message(chat_id, 'plan_solo_tour', call["from"])
        elif call.data == "save":
            with open(self.user_file, "w") as fd:
                json.dump(self.chats, fd, cls=UsersEncoder)
            await self.print_special_message(chat_id, 'hi_admin', call["from"])
        elif call.data == "end":
            with open(self.user_file, "w") as fd:
                json.dump(self.chats, fd, cls=UsersEncoder)
            x = 42 / 0
        elif call.data == "uncomp_orders":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id, "Админ, по этой ссылке ты можешь открыть файл с незаконченными "
                                                              "заказами: https://sqliteviewer.app")
            await self.bot.send_document(chat_id=call.message.chat.id, document=open('not_finished_forms.db', 'rb'))
            # await self.print_special_message(chat_id, "plug", call["from"])
        elif call.data == "comp_orders":
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call.message.chat.id,
                                        "Админ, по этой ссылке ты можешь открыть файл с выполненными "
                                        "заказами: https://sqliteviewer.app")
            await self.bot.send_document(chat_id=call.message.chat.id, document=open('finished_forms.db', 'rb'))
            # await self.print_special_message(chat_id, "plug", call["from"])
        elif call.data == "stat":
            await self.print_special_message(chat_id, "plug", call["from"])
        elif call.data == "send_plan":
            await self.bot.send_message(call.message.chat.id, 'Напишите уникальный номер заказа, user_id, town, ссылку, кому собираетесь отправлять план через один пробел!!', reply_markup=None)
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.user_id
            self.chats[call["from"]["id"]].all_blocked = True
            # await self.print_special_message(chat_id, "plug", call["from"])
        elif call.data == "send_mes":
            await self.send_adm_mes(chat_id, call["from"], 0)
        elif call.data == "exit_from_form_start":
            self.chats[call["from"]["id"]].all_blocked = False
            self.chats[call["from"]["id"]].filling_the_form = False
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"

            await self.bot.send_message(call["from"]["id"], 'Вы вышли из формы 🔚', reply_markup=None)
            await self.print_special_message(chat_id, 'start', call["from"])
        elif call.data == "exit_from_form_menu":
            self.chats[call["from"]["id"]].all_blocked = False
            self.chats[call["from"]["id"]].filling_the_form = False
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"

            await self.bot.send_message(call["from"]["id"], 'Вы вышли из формы 🔚', reply_markup=None)
            await self.print_special_message(chat_id, 'menu', call["from"])
        elif call.data == "exit_from_form_profile_info":
            self.chats[call["from"]["id"]].all_blocked = False
            self.chats[call["from"]["id"]].filling_the_form = False
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"

            await self.bot.send_message(call["from"]["id"], 'Вы вышли из формы 🔚', reply_markup=None)
            await self.print_special_message(chat_id, 'profile_info', call["from"])
        elif call.data == "exit_from_form_info":
            self.chats[call["from"]["id"]].all_blocked = False
            self.chats[call["from"]["id"]].filling_the_form = False
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.chats[call["from"]["id"]].cur_tour.town = "Not Filled"  # обнулила текущую анкету
            self.chats[call["from"]["id"]].cur_tour.purpose_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.duration_of_trip = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.company = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.budget = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.lifestyle = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.count_visiting = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.transport = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.comments = "Not Filled"
            self.chats[call["from"]["id"]].cur_tour.contacts = "Not Filled"

            await self.bot.send_message(call["from"]["id"], 'Вы вышли из формы 🔚', reply_markup=None)
            await self.print_special_message(chat_id, 'info', call["from"])
        elif call.data == "continue_filling_the_form":
            self.chats[call["from"]["id"]].all_blocked = True
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.bot.send_message(call["from"]["id"], 'Жду ответ на последний вопрос ⌛', reply_markup=None)

    async def registration(self, chat_id, user, stage=0):
        if stage == 0:
            await self.bot.send_message(user["id"], '🟣 Каков Ваш возраст?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.age_for_reg
            self.chats[user["id"]].all_blocked = True
        elif stage == 1:
            markup = types.InlineKeyboardMarkup()
            but_m = types.InlineKeyboardButton(text='Мужской', callback_data="registration_sex_male")
            but_w = types.InlineKeyboardButton(text='Женский', callback_data="registration_sex_female")
            markup.add(but_m, but_w)
            await self.bot.send_message(user["id"], '🟣 Каков Ваш пол?', reply_markup=markup)
        elif stage == 2:
            markup = types.InlineKeyboardMarkup()
            but_yes = types.InlineKeyboardButton(text='Да', callback_data="registration_dl_yes")
            but_no = types.InlineKeyboardButton(text='Нет', callback_data="registration_dl_no")
            markup.add(but_yes, but_no)
            await self.bot.send_message(user["id"], '🟣 У Вас есть водительские права?', reply_markup=markup)
        elif stage == 3:
            await self.bot.send_message(user["id"], '🟣 Как Вас зовут?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.name_for_reg
            self.chats[user["id"]].all_blocked = True
        elif stage == 4:
            await self.bot.send_message(user["id"], '🟣 Как еще можно с Вами связаться (телефон/почта/...) ?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.contacts_for_reg
            self.chats[user["id"]].all_blocked = True
        else:
            self.chats[user["id"]].registration = True
            await self.print_special_message(user["id"], "menu", user)

    async def form_tour_for_one(self, chat_id, user, stage=0):
        if stage == 0:
            await self.bot.send_message(chat_id, '📍 Цель поездки ?'
                                                 '\n\nВозможные варианты:'
                                                 '\n⭐ Максимально окунуться в историческую составляющую города'
                                                 '\n⭐ Прочувствовать вечернюю и ночную жизнь города'
                                                 '\n⭐ Тур по самым молодежным местам города'
                                                 '\n⭐ Гастротур'
                                                 '\n⭐ Активный/спортивный отдых'
                                                 '\n⭐ Романтическая поездка'
                                                 '\n⭐ Семейное путешествие')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_purpose
            self.chats[user["id"]].all_blocked = True
        elif stage == 1:
            await self.bot.send_message(chat_id, '📍 Период пребывания в этом городе и дата поездки')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_duration_of_trip
            self.chats[user["id"]].all_blocked = True
        elif stage == 2:
            await self.bot.send_message(chat_id, '📍 В каком составе планируете поехать?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_company
            self.chats[user["id"]].all_blocked = True
        elif stage == 3:
            await self.bot.send_message(chat_id, '📍 Бюджет поездки (сегмент заведений)')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_budget
            self.chats[user["id"]].all_blocked = True
        elif stage == 4:
            await self.bot.send_message(chat_id, '📍 Опишите Ваш образ жизни'
                                                 '\n\nВозможные варианты:'
                                                 '\n⭐ Девочка с патриков'
                                                 '\n⭐ На рэпе на трепе'
                                                 '\n⭐ Тусовщик'
                                                 '\n⭐ Культурный обозреватель'
                                                 '\n⭐ На свэге'
                                                 '\n⭐ Ленивец')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_lifestyle
            self.chats[user["id"]].all_blocked = True
        elif stage == 5:
            await self.bot.send_message(chat_id, '📍 Который раз посещаете этот город ?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_count_visiting
            self.chats[user["id"]].all_blocked = True
        elif stage == 6:
            await self.bot.send_message(chat_id, '📍 На каком транспорте планируете добираться до города ?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_transport
            self.chats[user["id"]].all_blocked = True
        elif stage == 7:
            await self.bot.send_message(chat_id, '📍 Как с Вами связаться (email/telegram/phone ...) ?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.cur_form_contacts
            self.chats[user["id"]].all_blocked = True
        elif stage == 8:
            markup = types.InlineKeyboardMarkup()
            but_y = types.InlineKeyboardButton(text='Да', callback_data="cur_form_comment_yes")
            but_n = types.InlineKeyboardButton(text='Нет', callback_data="cur_form_comment_no")
            markup.add(but_y, but_n)
            await self.bot.send_message(chat_id, '📍 Хотите что-нибудь добавить ?', reply_markup=markup)

    async def create_tour(self, city, chat_id, tour_type='solo'):
        if tour_type == 'solo':
            tour = Tour(city, [self.chats[chat_id]])
        else:
            tour = "Nothing"
            pass
        markup = types.InlineKeyboardMarkup(row_width=1)
        but_m = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')
        markup.add(but_m)
        await self.bot.send_message(chat_id, str(tour), reply_markup=markup)

    async def send_adm_mes(self, chat_id, admin, stage, message=""):
        if stage == 0:
            self.chats[admin["id"]].expect_mes = ExpectedMessage.wait_user_mes
            self.chats[admin["id"]].all_blocked = True
            await self.bot.send_message(chat_id,
                                        "Введите айди пользователя и через символ * сообщение или напишите отмена")
        else:
            user_id, mes = message.split("*")
            await self.bot.send_message(int(user_id), mes)
            await self.print_special_message(admin["id"], "hi_admin", admin)

    async def print_info(self, chat_id):
        await self.bot.send_message(chat_id, f'Возраст: {self.chats[chat_id].age}')

    async def start(self):
        await self.dp.start_polling(self.bot)
