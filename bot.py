import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types, apihelper
import content.strings as cs
import content.buttons as bt
import config

# bot settings
api_key = config.api_key
logs_ch = config.logs_ch
web_app_link = config.web_app_link
set_info = config.set_info
local_bot_api = config.local_bot_api

if local_bot_api:
    local_api = 'http://localhost:8081/'
    link_for_api_helper = f"{local_api}" + "bot{0}/{1}"
    apihelper.API_URL = link_for_api_helper
bot = AsyncTeleBot(api_key)

# /start command handler
@bot.message_handler(commands=['start'])
async def start(message) -> None:
    await bot.send_message(message.chat.id, cs.text_intro,
                           reply_markup=msg_buttons('start'),
                           parse_mode='HTML', 
                           disable_web_page_preview=True)
    await logs(message, "start")

# inline buttons handler
@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call):
    print(f"{call.data} - {call.message.chat.id}")
    if call.data == 'intro':
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.id,
                                            reply_markup=navigate_buttons(call.data))

    if 'info_' in call.data:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    text=cs.text_strings_info[call.data],
                                    message_id=call.message.id,
                                    reply_markup=navigate_buttons(call.data),
                                    parse_mode='HTML')
    await callback_logs(call, call.data)

# inline buttons
def msg_buttons(msg_type):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton(text=bt.button_info, callback_data='intro')
    itembtn2 = types.InlineKeyboardButton(text=bt.button_to_web_app, web_app=types.WebAppInfo(web_app_link))

    if msg_type == 'start':
        keyboard.add(itembtn1, itembtn2)
    elif msg_type == 'intro':
        keyboard.add(itembtn2)

    return keyboard

def navigate_buttons(navigate_button):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for key, value in bt.buttons_dict.items():
        itembtn = types.InlineKeyboardButton(text=value, callback_data=key)
        keyboard.add(itembtn)

    itembtn0 = types.InlineKeyboardButton(text=bt.button_to_web_app, web_app=types.WebAppInfo(web_app_link))
    keyboard.add(itembtn0)

    return keyboard

# bot mini log
async def logs(message, query):
    log_text = f'''
#{query} | user #u{message.chat.id} :
<blockquote expandable>first_name: <b><a href='tg://user?id={message.chat.id}'>{message.chat.first_name}</a></b>
last_name: <b>{message.chat.last_name}</b>
username: @{message.chat.username}
language_code: <b>{message.from_user.language_code}</b>
bio: <b>{message.chat.bio}</b>
personal_chat: {message.chat.personal_chat}
</blockquote>
'''
    await bot.send_message(chat_id=logs_ch, text=log_text, parse_mode="HTML")

# inline buttons log
async def callback_logs(call, query):
    log_text = f'''
#{query} | <a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name} ({call.from_user.id})</a>
'''
    await bot.send_message(chat_id=logs_ch, text=log_text, parse_mode="HTML")

# setup bot description and bot info
if set_info:
    set_description = bot.set_my_description(description=cs.description, language_code=None)
    print(f"set_description = {set_description}")

    set_description_short = bot.set_my_short_description(short_description=cs.description_short, language_code=None)
    print(f"set_description_short = {set_description_short}")

async def main():
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())
