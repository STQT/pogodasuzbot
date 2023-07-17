from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import SchedulerMiddleware
from tasks import set_scheduled_jobs

from configs import i18n, TOKEN
from db import collusers, insert_new_user, get_current_user_col, update_notify_hours_by_user_id, \
    update_city_hours_by_user_id, user_counts
from utils import get_current_user_weather_data, get_text, SCHEDULED_HOURS, cities, get_key_from_dict_value

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Setup i18n middleware
dp.middleware.setup(i18n)
_ = i18n.lazy_gettext

# Setup schedulers
scheduler = AsyncIOScheduler()
dp.middleware.setup(SchedulerMiddleware(scheduler))

main_menu_kbs = types.ReplyKeyboardMarkup(
    [
        [
            types.KeyboardButton(_("📅 Bugungi ob-havo"))
        ],
        [
            types.KeyboardButton(_("⚙️ Sozlamalar"))
        ]
    ],
    resize_keyboard=True
)

settings_kbs = types.ReplyKeyboardMarkup(
    [
        [
            types.KeyboardButton(_("📍 Shaharni o'zgartirish"))
        ],
        [
            types.KeyboardButton(_("⏰ Obuna o'zgartirish"))
        ],
        [
            types.KeyboardButton(_("⬅️ Ortga qaytish"))
        ]
    ],
    resize_keyboard=True
)

schedule_kbs_list = types.ReplyKeyboardMarkup(
    [
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[:3]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[3:6]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[6:9]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[9:12]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[12:15]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[15:18]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[18:21]],
        [types.KeyboardButton(f'{i}:00') for i in SCHEDULED_HOURS[21:24]],
        [types.KeyboardButton(_("⬅️ Ortga qaytish"))]
    ]
)

city_adding_emoji = "🌆 "

city_list_kb = types.ReplyKeyboardMarkup(
    [
        [types.KeyboardButton(city_adding_emoji + cities[i]['name'])] for i in cities.keys()
    ]
)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    count = await collusers.count_documents({'_id': message.from_user.id})
    if count == 0:
        await insert_new_user(message.from_user.id)
    await message.answer(_("Bot ishlab turipti"),
                         reply_markup=main_menu_kbs)


@dp.message_handler(lambda msg: msg.text == _("📅 Bugungi ob-havo"))
async def language_echo(msg: types.Message):
    user_data = await get_current_user_col(msg.from_user.id)
    if user_data is not None:
        weather_data = await get_current_user_weather_data(user_data)
        w_hourly = weather_data["w_hourly_data"]
        w_day = weather_data["w_day"]
        data_to_send = get_text(w_day, w_hourly, user_data)
        await msg.answer(data_to_send)
    else:
        await insert_new_user(msg.from_user.id)
        await language_echo(msg)


@dp.message_handler(lambda msg: msg.text == _("⚙️ Sozlamalar"))
async def settings_echo(msg: types.Message):
    user_data = await get_current_user_col(msg.from_user.id)
    if user_data is not None:
        text_dict = user_data
        text_dict.update({"city_name": cities.get(text_dict['city'])['name']})
        await msg.answer(
            _("Hozirgi sozlamalaringiz\n"
              "Shahar: {city_name}\n"
              "Obuna: Har kuni {notify_hours}:00 da").format(**text_dict),
            reply_markup=settings_kbs
        )
    else:
        await insert_new_user(msg.from_user.id)
        await settings_echo(msg)


@dp.message_handler(lambda msg: msg.text == _("⏰ Obuna o'zgartirish"))
async def notification_echo(msg: types.Message):
    await msg.answer(_("Qachon ob-havo ma'lumotini olishni istaysiz?"), reply_markup=schedule_kbs_list)


@dp.message_handler(lambda msg: msg.text == _("⬅️ Ortga qaytish"))
async def back_button(msg: types.Message):
    await start(msg)


@dp.message_handler(lambda msg: msg.text.find(city_adding_emoji) == 0)
async def city_setting_button(msg: types.Message):
    city_name = msg.text.split(city_adding_emoji)[1]
    city_key = get_key_from_dict_value(city_name)
    await update_city_hours_by_user_id(msg.from_user.id, city_key)
    await msg.answer(_("{city_name} shahri tanlandi").format(city_name=city_name), reply_markup=main_menu_kbs)


@dp.message_handler(lambda msg: msg.text == "/users_count")
async def get_users_count(msg: types.Message):
    await msg.answer("Users count: {}".format(await user_counts()))


@dp.message_handler(lambda msg: msg.text == _("📍 Shaharni o'zgartirish"))
async def city_change_button(msg: types.Message):
    await msg.answer(_("Iltimos, shahringizni tanlang."), reply_markup=city_list_kb)


@dp.message_handler(regexp="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
async def hours_setting_button(msg: types.Message):
    hour = int(msg.text.split(":")[0])
    await update_notify_hours_by_user_id(msg.from_user.id, hour)
    await msg.answer(_("Endi men sizga har kuni soat {hour}:00 da ob-havo ma'lumotini jo'nataman.").format(hour=hour),
                     reply_markup=main_menu_kbs)


@dp.message_handler()
async def echo(msg: types.Message):
    await msg.answer(msg.text)


async def on_startup(dp):
    scheduler.start()
    set_scheduled_jobs(scheduler, bot)
    print(await dp.bot.get_me())


if __name__ == "__main__":
    print("Bot ishga tushirilmoqda...")
    executor.start_polling(dp, on_startup=on_startup)
