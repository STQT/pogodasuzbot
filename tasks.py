import asyncio
import logging as log
import pytz

from datetime import datetime

from aiogram import Bot

from utils import _, get_all_city_weather_data, get_text, send_message
from db import get_all_active_users_with_hour


# Создаем функцию, в которой будет происходить запуск наших тасков.
async def send_message_every_hour(bot: Bot):
    hour = datetime.now(pytz.timezone('Asia/Tashkent')).hour
    users = await get_all_active_users_with_hour(hour)
    city_set = set([user['city'] for user in users])
    all_weather_data = await get_all_city_weather_data(city_list=city_set)
    count = 0
    try:
        for user in users:
            w_hourly = all_weather_data[user['city']]["w_hourly_data"]
            w_day = all_weather_data[user['city']]["w_day"]
            data_to_send = get_text(w_day, w_hourly)
            if await send_message(bot, user['_id'], data_to_send):
                count += 1
            await asyncio.sleep(.04)  # 25 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")
    return count


def set_scheduled_jobs(scheduler, bot, *args, **kwargs):
    # Добавляем задачи на выполнение
    # scheduler.add_job(send_message_every_hour, "interval", seconds=5, args=(bot,))
    scheduler.add_job(send_message_every_hour, 'cron', minute=0, args=(bot,))
    # scheduler.add_job(some_other_regular_task, "interval", seconds=100)
