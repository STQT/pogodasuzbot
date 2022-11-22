import asyncio
import logging as log

from configs import i18n, OWM_TOKEN

from aiogram import Bot
from aiogram.utils import exceptions
from pyowm import OWM
from pyowm.weatherapi25.weather import Weather

from datetime import datetime

# ---------- FREE API KEY examples ---------------------

owm = OWM(OWM_TOKEN)
mgr = owm.weather_manager()


def get_today_weather_data(w_day: Weather, w_hourly_data: list):
    temp_c = w_day.temperature('celsius')
    status = {"Rain": "🌧",
              "light rain": "🌦",
              "None": "🌫️",
              "Thunderstorm": "⛈",
              "Drizzle": "🌧",
              "Snow": "🌨",
              "Mist": "🌫",
              "Clear": "☀️",
              "Clouds": "☁️",
              }

    # short = {'11d': "⛈",
    #          '10d': "🌦",
    #          '09d': "🌧",
    #          '13d': "🌨",
    #          '50d': "🌫️",
    #          '01d': "☀️",
    #          '01n': "☀️",
    #          '02d': "⛅️",
    #          '02n': "⛅️",
    #          '03d': "☁️",
    #          '03n': "☁️",
    #          '04d': "☁️",
    #          '04n': "☁️",
    #          }
    diction = {'min': temp_c['min'],
               'max': temp_c['max'],
               'namlik': w_day.humidity,
               'chiqish': datetime.fromtimestamp(w_day.sunrise_time()).strftime("%H:%M"),
               'botish': datetime.fromtimestamp(w_day.sunset_time()).strftime("%H:%M"),
               'current_day': datetime.fromtimestamp(w_day.reference_time()).strftime("%d %b"),
               'status_ico': status.get(w_day.status, "None"),
               'detailed_text': ((status.get(i.status, "None"), i.temperature('celsius')['temp'],
                                  i.temperature('celsius')['feels_like']) for i in w_hourly_data[:24]
                                 if datetime.fromtimestamp(i.ref_time).hour in (7, 13, 21))
               }
    return diction


# print(get_today_weather_data(w_first_day, w_hourly))

_ = i18n.gettext

cities = {
    "Tashkent": {"name": _("Toshkent"), "lon": 69.240562, "lat": 41.311081},
    "Samarkand": {"name": _("Samarqand"), "lon": 66.9596, "lat": 39.6459},
    "Navoiy": {"name": _("Navoiy"), "lon": 65.3834, "lat": 40.0752},
    "Nukus": {"name": _("Nukus"), "lon": 59.6022, "lat": 42.4566},
    "Xiva": {"name": _("Xiva"), "lon": 60.364, "lat": 41.3701},
    "Urgench": {"name": _("Urganch"), "lon": 60.6332, "lat": 41.542},
    "Fergana": {"name": _("Farg'ona"), "lon": 71.7864, "lat": 40.3782},
    "Andijan": {"name": _("Andijon"), "lon": 72.3501, "lat": 40.7584},
    "Namangan": {"name": _("Namangan"), "lon": 71.5667, "lat": 40.9584},
    "Termez": {"name": _("Termiz"), "lon": 67.2782, "lat": 37.2156},
    "Karshi": {"name": _("Qarshi"), "lon": 65.7999, "lat": 38.8582},
    "Bukhara": {"name": _("Buxoro"), "lon": 64.4836, "lat": 39.7663},
    "Jizzakh": {"name": _("Jizzax"), "lon": 67.8498, "lat": 40.1083},
}


async def get_current_user_weather_data(user_data):
    city = user_data.get('city')
    observation = mgr.one_call(cities[city]['lat'], cities[city]['lon'])
    w_hourly = observation.forecast_hourly
    w_first_day = observation.forecast_daily[0]
    user_data.update({'w_hourly_data': w_hourly, 'w_day': w_first_day})
    return user_data


async def get_all_city_weather_data(city_list):
    data = cities.copy()
    for city in city_list:
        city_dict = data[city]
        observation = mgr.one_call(city_dict['lat'], city_dict['lon'])
        w_hourly = observation.forecast_hourly
        w_first_day = observation.forecast_daily[0]
        city_dict.update({'w_hourly_data': w_hourly, 'w_day': w_first_day})
        await asyncio.sleep(0.1)
    return data


def get_text(w_day, w_hourly_data, user_data=None):
    dictionary = get_today_weather_data(w_day, w_hourly_data)
    morning, afternoon, nightly = dictionary['detailed_text']
    min_t = round(dictionary['min'])
    max_t = round(dictionary['max'])
    user_data = user_data.get('city') if user_data else ""
    data = {
        "cur_day": dictionary['current_day'],
        "sunrise": dictionary['chiqish'],
        "sunset": dictionary['botish'],
        "min_t": min_t,
        "max_t": max_t,
        "namlik": round(dictionary['namlik']),
        "status_ico": dictionary['status_ico'],
        "morning_smile": morning[0],
        "morning_cur": round(morning[1]),
        "morning2": round(morning[2]),
        "sign_morning": "+" if morning[1] > 0 else '',
        "sign_morning2": "+" if morning[2] > 0 else '',
        "afternoon_smile": afternoon[0],
        "afternoon_cur": round(afternoon[1]),
        "afternoon2": round(afternoon[2]),
        "sign_afternoon": "+" if afternoon[1] > 0 else '',
        "sign_afternoon2": "+" if afternoon[2] > 0 else '',
        "nightly_smile": nightly[0],
        "nightly_cur": round(nightly[1]),
        "nightly2": round(nightly[2]),
        "sign_nightly": "+" if nightly[1] > 0 else '',
        "sign_nightly2": "+" if nightly[2] > 0 else '',
        "sign_max": "+" if max_t > 0 else "",
        "sign_min": "+" if min_t > 0 else "",
        "city": user_data
    }
    uz_text = _("Bugun, {cur_day} {city}\n"
                "{status_ico} {sign_max}{max_t}°C  {sign_min}{min_t}°C\n"
                "{morning_smile} Tong {sign_morning}{morning_cur}°C "
                "({sign_morning2}{morning2} kabi seziladi)\n"
                "{afternoon_smile} Kun {sign_afternoon}{afternoon_cur}°C "
                "({sign_afternoon2}{afternoon2} kabi seziladi)\n"
                "{nightly_smile} Oqshom {sign_nightly}{nightly_cur}°C "
                "({sign_nightly2}{nightly2} kabi seziladi)\n"
                "Namlik: {namlik}%\n"
                "Quyosh chiqishi: {sunrise}\nQuyosh botishi: {sunset}\n@pogodas").format(**data)

    return uz_text


async def send_message(bot: Bot, user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param bot: Bot
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(bot, user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:

        log.info(f"Target [ID:{user_id}]: success")

        return True

    return False


def get_key_from_dict_value(val):
    city_key = [k for k, v in cities.items() if v['name'] == val]
    if city_key:
        city_key = city_key[0]
    else:
        city_key = "Tashkent"
    return city_key

SCHEDULED_HOURS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
