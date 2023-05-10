import aiogram
from aiogram import Dispatcher, types
from dataclasses import dataclass
from enum import Enum
from Tour import Tour


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


@dataclass
class Chat:
    age = 18
    expect_mes = ExpectedMessage.unexpected
    all_blocked = False
    sex = True

    # написать нужные параметры человека для маршрута


class Bot:
    def __init__(self, token):
        self.bot = aiogram.Bot(token)
        self.dp = Dispatcher(self.bot)
        self.chats = dict()
        self.expected_message_type = ExpectedMessage.unexpected

    async def print_special_message(self, chat_id, mes_type, user):
        if mes_type == 'start':
            # profiles.add_user(chat_id)
            self.chats[chat_id] = Chat()
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_y = types.InlineKeyboardButton(text='Да', callback_data='start_work')
            but_i = types.InlineKeyboardButton(text='Посмотреть справку', callback_data='help')
            markup.add(but_y, but_i)
            self.chats[user["id"]] = Chat()
            await self.bot.send_message(chat_id, 'Привет, Готов спланировать путешествие?', reply_markup=markup)
        elif mes_type == 'plug':
            await self.bot.send_message(chat_id, 'Эта функция еще не реализована')
            # заглушка для нереализованных функций
            await self.print_special_message(chat_id, "menu", user)
        elif mes_type == 'menu':
            self.chats[user["id"]].expect_mes = ExpectedMessage.unexpected
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_e = types.InlineKeyboardButton(text='Редактировать информацию о себе', callback_data='edit_profile')
            but_po = types.InlineKeyboardButton(text='Спланировать путешествие для меня', callback_data='tour_one')
            but_pm = types.InlineKeyboardButton(text='Спланировать путешествие для компании', callback_data='tour_many')
            markup.add(but_e, but_po, but_pm)
            await self.bot.send_message(chat_id, 'Чем могу помочь?', reply_markup=markup)
        elif mes_type == 'profile_info':
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_a = types.InlineKeyboardButton(text='Изменить возраст', callback_data='change_age')
            but_b = types.InlineKeyboardButton(text='Изменить пол', callback_data='change_sex')
            but_с = types.InlineKeyboardButton(text='Наличие прав', callback_data='change_dl')
            but_m = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')
            markup.add(but_a, but_b, but_с, but_m)
            await self.bot.send_message(chat_id, 'Информация профиля: '
                                                 '\nВозраст: {0}'
                                                 '\nПол: {1}'
                                                 '\nНаличие водительских прав: {2}'.format(str(self.chats[user["id"]].age),
                                                                     "Мужской" if self.chats[user["id"]].sex
                                                                     else "Женский",
                                                                     "Есть" if self.chats[user["id"]].dl else "Нет"),
                                        reply_markup=markup)
        elif mes_type == 'plan_solo_tour':
            markup = types.InlineKeyboardMarkup(row_width=1)
            but_m = types.InlineKeyboardButton(text='Возврат в меню', callback_data='back_to_menu')
            markup.add(but_m)
            await self.bot.send_message(chat_id, 'В какой город поедете?', reply_markup=markup)
            self.chats[user["id"]].expect_mes = ExpectedMessage.city_for_solo_tour
            self.chats[user["id"]].all_blocked = True
        elif mes_type == "change_age":
            pass
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
            await self.registration(call["from"], 0)
        elif call.data == 'help':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'plug', call["from"])
        elif call.data == 'edit_profile':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'profile_info', call["from"])
        elif call.data == 'tour_one':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'plan_solo_tour', call["from"])
        elif call.data == 'tour_many':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'plug', call["from"])
        elif call.data == 'back_to_menu':
            self.expected_message_type = ExpectedMessage.unexpected
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.print_special_message(chat_id, 'menu', call["from"])
        elif call.data == 'change_age':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], 'Каков ваш возраст?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_age
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == 'change_sex':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], 'Каков ваш пол(мужской/женский)?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_sex
            self.chats[call["from"]["id"]].all_blocked = True
        elif call.data == 'change_dl':
            await self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            await self.bot.send_message(call["from"]["id"], 'У вас есть водительские права(да/нет)?')
            self.chats[call["from"]["id"]].expect_mes = ExpectedMessage.change_dl
            self.chats[call["from"]["id"]].all_blocked = True

    async def registration(self, user, stage=0):
        if stage == 0:
            await self.bot.send_message(user["id"], 'Каков ваш возраст?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.age_for_reg
            self.chats[user["id"]].all_blocked = True
        elif stage == 1:
            await self.bot.send_message(user["id"], 'Каков ваш пол(Мужской/Женский)?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.sex_for_reg
            self.chats[user["id"]].all_blocked = True
        elif stage == 2:
            await self.bot.send_message(user["id"], 'У вас есть водительские права(да/нет)?')
            self.chats[user["id"]].expect_mes = ExpectedMessage.dl_for_reg
            self.chats[user["id"]].all_blocked = True
        else:
            await self.print_special_message(user["id"], "menu", user)

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

    async def print_info(self, chat_id):
        await self.bot.send_message(chat_id, f'Возраст: {self.chats[chat_id].age}')

    async def start(self):
        await self.dp.start_polling(self.bot)
