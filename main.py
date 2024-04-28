from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from methods import *
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone='Europe/London')

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer("турн зе музик ОН")


@dp.message(Command(commands=["help"]))
async def help_command(Message):
    await Message.answer(
        "команды:\nПоиск ИМЯИСПОЛНИТЕЛЯ - выводит айди исполнителя\nАльбомы ИМЯИСПОЛНИТЕЛЯ - выводит альбомы исполнителя\nсаб/ансаб ИМЯИСПОЛНИТЕЛЯ - подписывает/отписывает от обновлений музыканта\nмои сабки - показывает все актуальные подписки"
    )


@dp.message(F.text[0:5].lower() == "поиск")
async def searchartist(Message):
    otvet = spotysearch(Message.text[6:], spotoken)
    print(otvet)
    await Message.answer(otvet)


@dp.message(F.text[0:7].lower() == "альбомы")
async def searchalbums(Message):
    await Message.answer('\n\n'.join('\n'.join(i) for i in spotysearchalbums(name=Message.text[8:], include = 'album', spotoken=spotoken)))

@dp.message(F.text[0:6].lower() == "релизы")
async def searchalbums(Message):
    await Message.answer('\n\n'.join('\n'.join(i) for i in spotysearchalbums(name=Message.text[7:],spotoken=spotoken, include = 'album%2Csingle%2Cappears_on%2Ccompilation')))

@dp.message(F.text.lower() == "мои сабки" or F.text.lower() == "сабки" )
async def showsubs(Message):
    await Message.answer(showsubsmethod(Message.from_user.id))


@dp.message(F.text[0:3].lower() == "саб")
async def sub2artist(Message):
    msgansw = bdsubs(Message.text[4:].lower(), True, Message.from_user.id, spotoken)

    await Message.answer(msgansw)
    if "такого исполнителя нету: " not in msgansw:
        await dailyupdatecheck(singlecheck=True, artistname=spotysearchnameid(Message.text[6:].lower(), spotoken)[0])


@dp.message(F.text[0:5].lower() == "ансаб")
async def unsubartist(Message):
    msgansw = bdsubs(Message.text[6:].lower(), False, Message.from_user.id, spotoken)

    await Message.answer(msgansw)
    if "такого исполнителя нету: " not in msgansw:
        await dailyupdatecheck(singlecheck=True, artistname=spotysearchnameid(Message.text[6:].lower(), spotoken)[0])

async def dailyupdatecheck(singlecheck=False, artistname = 'artistname'):
    releases = checkupdates(spotoken,singlecheck,artistname)
    for i in releases.keys():
        print(i)
        await bot.send_message(i, ('ОБНОВОЧКИ\n' + '\n\n'.join(releases[i])))
def gettoken():
    spotoken = getsptfytoken()
    global spotoken
    tokenupdatetime = datetime.now() + timedelta(minutes=int(50))
    scheduler.add_job(gettoken, 'date', run_date=tokenupdatetime)
if __name__ == "__main__":
    gettoken()
    dailyupdatecheck()
    dp.run_polling(bot)