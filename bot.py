import asyncio
from aiogram import Dispatcher, types

from BotClass import Bot, ExpectedMessage, FormForOne

TOKEN = ""
users_file_name = "users.json"
TourBot = Bot(TOKEN, users_file_name)
admins = [558838836, 842921731, 442132164]


@TourBot.dp.message_handler(commands=['start'])
async def say_hello(message):
    await TourBot.print_special_message(message.chat.id, "start", message["from"])


@TourBot.dp.message_handler(commands=['admin'])
async def say_hello(message):
    if message.chat.id in admins:
        await TourBot.print_special_message(message.chat.id, "hi_admin", message["from"])
    else:
        await TourBot.print_special_message(message.chat.id, "perm_denied", message["from"])


@TourBot.dp.message_handler(commands=['menu'])
async def menu(message):
    await TourBot.print_special_message(message.chat.id, "menu", message["from"])


@TourBot.dp.message_handler(commands=['profile_info'])
async def profile_info(message):
    await TourBot.print_special_message(message.chat.id, "profile_info", message["from"])

@TourBot.dp.message_handler(commands=['info'])
async def info(message):
    await TourBot.print_special_message(message.chat.id, "info", message["from"])


@TourBot.dp.callback_query_handler()
async def reply_callback_query(call):
    await TourBot.reply_inline_call(call)


@TourBot.dp.message_handler(content_types=['text'])
async def answer(message):
    if TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.unexpected:
        pass
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.city_for_solo_tour:
        TourBot.chats[message["from"]["id"]].cur_tour.town = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 0)
        # if message.text.lower() != "питер" and message.text.lower() != "санкт-петербург":
        #     await TourBot.bot.send_message(message.chat.id, 'Пока доступны только маршруты в Санкт-Петербурге')
        # else:
        #     await TourBot.create_tour(message.text, message.chat.id, tour_type="solo")
        #     TourBot.chats[message["from"]["id"]].all_blocked = False
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_purpose:
        TourBot.chats[message["from"]["id"]].cur_tour.purpose_of_trip = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 1)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_duration_of_trip:
        TourBot.chats[message["from"]["id"]].cur_tour.duration_of_trip = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 2)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_company:
        TourBot.chats[message["from"]["id"]].cur_tour.company = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 3)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_budget:
        TourBot.chats[message["from"]["id"]].cur_tour.budget = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 4)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_lifestyle:
        TourBot.chats[message["from"]["id"]].cur_tour.lifestyle = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 5)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_count_visiting:
        TourBot.chats[message["from"]["id"]].cur_tour.count_visiting = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 6)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_transport:
        TourBot.chats[message["from"]["id"]].cur_tour.transport = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 7)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_contacts:
        TourBot.chats[message["from"]["id"]].cur_tour.contacts = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.form_tour_for_one(message.chat.id, message["from"], 8)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.cur_form_comment:
        TourBot.chats[message["from"]["id"]].cur_tour.comments = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        markup = types.InlineKeyboardMarkup()
        but_form = types.InlineKeyboardButton(text='Заполненная анкета', callback_data="cur_form_comment_no")
        markup.add(but_form)
        await TourBot.bot.send_message(message["from"]["id"], 'Просмотреть заполненную анкету перед отправкой', reply_markup=markup)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.age_for_reg:
        if message.text.isdigit():
            TourBot.chats[message["from"]["id"]].age = int(message.text)
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.registration(message.chat.id, message["from"], 1)
        else:
            await TourBot.bot.send_message(message.chat.id, 'Введите число полных лет, используйте только цифры')
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.change_age:
        if message.text.isdigit():
            TourBot.chats[message["from"]["id"]].age = int(message.text)
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
        else:
            await TourBot.bot.send_message(message.chat.id, 'Введите число полных лет, используйте только цифры')
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.sex_for_reg:
        if message.text.lower() == "мужской" or message.text.lower() == "м" or message.text.lower() == "муж":
            TourBot.chats[message["from"]["id"]].sex = True
        else:
            TourBot.chats[message["from"]["id"]].sex = False
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.registration(message.chat.id, message["from"], 2)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.change_sex:
        if message.text.lower() == "мужской" or message.text.lower() == "м" or message.text.lower() == "муж":
            TourBot.chats[message["from"]["id"]].sex = True
        else:
            TourBot.chats[message["from"]["id"]].sex = False
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.dl_for_reg:
        if message.text.lower() == "да":
            TourBot.chats[message["from"]["id"]].dl = True
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.registration(message.chat.id, message["from"], -1)
        elif message.text.lower() == "нет":
            TourBot.chats[message["from"]["id"]].dl = False
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.registration(message.chat.id, message["from"], -1)
        else:
            await TourBot.bot.send_message(message.chat.id, 'Введите да или нет')
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.change_dl:
        if message.text.lower() == "да":
            TourBot.chats[message["from"]["id"]].dl = True
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
        elif message.text.lower() == "нет":
            TourBot.chats[message["from"]["id"]].dl = False
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
        else:
            await TourBot.bot.send_message(message.chat.id, 'Введите да или нет')
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.name_for_reg:
        TourBot.chats[message["from"]["id"]].name = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.registration(message.chat.id, message["from"], 0)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.change_name:
        TourBot.chats[message["from"]["id"]].name = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.contacts_for_reg:
        TourBot.chats[message["from"]["id"]].contacts = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.registration(message.chat.id, message["from"], -1)
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.change_contacts:
        TourBot.chats[message["from"]["id"]].contacts = message.text
        TourBot.chats[message["from"]["id"]].all_blocked = False
        await TourBot.print_special_message(message["from"]["id"], "profile_info", message["from"])
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.wait_user_mes:
        if message.text == "отмена":
            TourBot.chats[message["from"]["id"]].all_blocked = False
            TourBot.chats[message["from"]["id"]].expect_mes = ExpectedMessage.unexpected
            await TourBot.print_special_message(message["from"]["id"], "hi_admin", message["from"])
        else:
            await TourBot.send_adm_mes(message.chat.id, message["from"], -1, message=message.text)


async def main():
    await TourBot.start()

if __name__ == "__main__":
    asyncio.run(main())
