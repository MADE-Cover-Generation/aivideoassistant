import os
import re
from telethon import TelegramClient, events
from aivideoassistantbot.handlers import *


APP_ID = int(os.environ.get('APP_ID'))
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def main():
    try:
        cbot = TelegramClient("bot", APP_ID, API_HASH).start(bot_token=BOT_TOKEN)
        cbot.parse_mode = "html"
    except Exception as e:
        logger.info("Environment vars are missing! Kindly recheck.")
        logger.info("Bot is quiting...")
        logger.info(str(e))
        exit()

    ####### GENERAL CMDS ########
    @cbot.on(events.NewMessage(pattern="/start"))
    async def _(e):
        await start(e)

    @cbot.on(events.NewMessage(pattern="/test"))
    async def _(e):
        await test(e)

    ######## Callbacks #########
    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_length")
        )
    )
    async def _(e):
        await change_length(e)


    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_version_(\S*)")
        )
    )
    async def _(e):
        await change_version(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_title")
        )
    )
    async def _(e):
        await change_title(e)


    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_position_(\S*)")
        )
    )
    async def _(e):
        await change_position(e)


    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_font_type_(\S*)")
        )
    )
    async def _(e):
        await change_font(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_font_size")
        )
    )
    async def _(e):
        await change_font_size(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_font_color_(\S*)")
        )
    )
    async def _(e):
        await change_font_color(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_stroke_color_(\S*)")
        )
    )
    async def _(e):
        await change_stroke_color(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"change_stroke_width")
        )
    )
    async def _(e):
        await change_stroke_width(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"start_processing")
        )
    )
    async def _(e):
        await start_processing(e)

    @cbot.on(
        events.callbackquery.CallbackQuery(
            data=re.compile(b"start_image_processing")
        )
    )
    async def _(e):
        await start_image_processing(e)

    ########## AUTO ###########
    @cbot.on(events.NewMessage(incoming=True))
    async def _(e):
        await encod(e)

    logger.info("Bot has started.")
    cbot.run_until_disconnected()


if __name__ == "__main__":
    main()
