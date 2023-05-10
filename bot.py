import asyncio

from BotClass import Bot, ExpectedMessage

TOKEN = ""
TourBot = Bot(TOKEN)


@TourBot.dp.message_handler(commands=['start'])
async def say_hello(message):
    await TourBot.print_special_message(message.chat.id, "start", message["from"])


@TourBot.dp.callback_query_handler()
async def reply_callback_query(call):
    await TourBot.reply_inline_call(call)


@TourBot.dp.message_handler(content_types=['text'])
async def answer(message):
    if TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.unexpected:
        pass
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.city_for_solo_tour:
        if message.text.lower() != "питер" and message.text.lower() != "санкт-петербург":
            await TourBot.bot.send_message(message.chat.id, 'Пока доступны только маршруты в Санкт-Петербурге')
        else:
            await TourBot.create_tour(message.text, message.chat.id, tour_type="solo")
            TourBot.chats[message["from"]["id"]].all_blocked = False
    elif TourBot.chats[message["from"]["id"]].expect_mes == ExpectedMessage.age_for_reg:
        if message.text.isdigit():
            TourBot.chats[message["from"]["id"]].age = int(message.text)
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.registration(message["from"], 1)
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
        await TourBot.registration(message["from"], 2)
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
            await TourBot.registration(message["from"], -1)
        elif message.text.lower() == "нет":
            TourBot.chats[message["from"]["id"]].dl = False
            TourBot.chats[message["from"]["id"]].all_blocked = False
            await TourBot.registration(message["from"], -1)
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


async def main():
    await TourBot.start()

if __name__ == "__main__":
    asyncio.run(main())
