import asyncio
import io
import os
import time
import zipfile
from datetime import datetime as dt
from logging import INFO, basicConfig, getLogger
import shutil
import copy
import aiohttp
import yt_dlp
from telethon import Button, events

from .FastTelethon import download_file, upload_file
from .funcn import progress


UPLOAD_VIDEO_URL = os.environ.get("UPLOAD_VIDEO_URL")
UPLOAD_IMAGE_URL = os.environ.get("UPLOAD_IMAGE_URL")


basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=INFO)
logger = getLogger(__name__)
logger.info("Starting...")

if not os.path.isdir("input/"):
    os.mkdir("input/")
if not os.path.isdir("output/"):
    os.mkdir("output/")

FONTS = {
    1: "CenturySB-Bold",
    2: "CenturySB-Italic",
    3: "Futura-Bold",
    4: "Futura-Italic",
    5: "Garamond-Bold",
    6: "Garamond-Italic",
    7: "Helvetica-Bold",
    8: "Helvetica-Italic",
    9: "Mulish-Bold",
    10: "Mulish-Italic",
    11: "TimesRoman-Bold",
    12: "TimesRoman-Italic",
}


get_font_button = lambda num: Button.inline(
    text=f"{num}", data=f"change_font_type_{FONTS[num]}"
)

FONTS_BUTTONS = [
    [get_font_button(column_1), get_font_button(column_2), get_font_button(column_3)]
    for column_1, column_2, column_3 in zip(
        range(1, 13, 3), range(2, 13, 3), range(3, 13, 3)
    )
]

POSITIONS = [
    "left-top",
    "center-top",
    "right-top",
    "left-middle",
    "center-middle",
    "right-middle",
    "left-bottom",
    "center-bottom",
    "right-bottom",
]

get_position_button = lambda position: Button.inline(
    text=f"{POSITIONS[position]}", data=f"change_position_{POSITIONS[position]}"
)

POSITION_BUTTONS = [
    [
        get_position_button(column_1),
        get_position_button(column_2),
        get_position_button(column_3),
    ]
    for column_1, column_2, column_3 in zip(
        range(0, 9, 3),
        range(1, 9, 3),
        range(2, 9, 3),
    )
]


# COLORS = {
#     "black": "⬛️",
#     "white": "⬜️",
#     "red": "🟥",
#     "green": "🟩",
#     "blue": "🟦",
#     "yellow": "🟨",
#     "orange": "🟧",
#     "purple": "🟪",
# }

COLORS = {
    1: ["black", "⬛️"],
    2: ["white", "⬜️"],
    3: ["red", "🟥"],
    4: ["green", "🟩"],
    5: ["blue", "🟦"],
    6: ["yellow", "🟨"],
    7: ["orange", "🟧"],
    8: ["purple", "🟪"],
}


FONTS_COLORS_BUTTONS = [
    [Button.inline(text="Black ⬛️", data="change_font_color_black")],
    [Button.inline(text="White ⬜️", data="change_font_color_white")],
    [Button.inline(text="Red 🟥", data="change_font_color_red")],
    [Button.inline(text="Green 🟩", data="change_font_color_green")],
    [Button.inline(text="Blue 🟦", data="change_font_color_blue")],
    [Button.inline(text="Yellow 🟨", data="change_font_color_yellow")],
    [Button.inline(text="Orange 🟧", data="change_font_color_orange")],
    [Button.inline(text="Purple 🟪", data="change_font_color_purple")],
]

STROKE_COLORS_BUTTONS = [
    [Button.inline(text="Black ⬛️", data="change_stroke_color_black")],
    [Button.inline(text="White ⬜️", data="change_stroke_color_white")],
    [Button.inline(text="Red 🟥", data="change_stroke_color_red")],
    [Button.inline(text="Green 🟩", data="change_stroke_color_green")],
    [Button.inline(text="Blue 🟦", data="change_stroke_color_blue")],
    [Button.inline(text="Yellow 🟨", data="change_stroke_color_yellow")],
    [Button.inline(text="Orange 🟧", data="change_stroke_color_orange")],
    [Button.inline(text="Purple 🟪", data="change_stroke_color_purple")],
]

# AVAILABLE_COLORS = list(COLORS.keys())

# get_color_button = lambda color, param: Button.inline(
#     text=f"{COLORS[color]}", data=f"change_{param}_{color}"
# )

# get_color_button = lambda num, param: Button.inline(
#     text=f"{COLORS[num][1]}", data=f"change_{param}_{COLORS[num][0]}"
# )

# FONTS_COLORS_BUTTONS = [
#     [[get_color_button(column_1, "font_color")], [get_color_button(column_2, "font_color")]]
#     for column_1, column_2 in zip(range(1, 9, 2), range(2, 9, 2))
# ]

# FONTS_COLORS_BUTTONS = [
#         Button.inline(text=f"{color} {COLORS[color]}", data=f"change_font_color_{color}") for color in COLORS
# ]


# STROKE_COLORS_BUTTONS = [
#     [
#         get_color_button(column_1, "stroke_color"),
#         get_color_button(column_2, "stroke_color"),
#     ]
#     for column_1, column_2 in zip(AVAILABLE_COLORS[::2], AVAILABLE_COLORS[1::2])
# ]

# STROKE_COLORS_BUTTONS = [
#     [get_color_button(column_1, "stroke_color")], [get_color_button(column_2, "stroke_color")]
#     for column_1, column_2 in zip(range(1, 9, 2), range(2, 9, 2))
# ]

# STROKE_COLORS_BUTTONS = [
#         Button.inline(text=f"{color} {COLORS[color]}", data=f"change_stroke_color_{color}")
#     for color in COLORS
# ]

START_IMAGE_PROCESSING_BUTTON = [
    Button.inline(f"Start processing!", data=f"start_image_processing")
]

DEFAULT_VIDEO_PARAMS = {
    "user_id": "",
    "video": "",
    "final_frame_length": 27,
}

DEFAULT_IMAGE_PARAMS = {
    "user_id": "",
    "image": "",
    "version": "",
    "text": "",
    "position": "",
    "font": "",
    "font_size": 0,
    "font_color": "",
    "stroke_color": "",
    "stroke_width": 0,
}

PARAMS_DECODE = {
    "version": "Version",
    "text": "Title",
    "position": "Position",
    "font": "Font",
    "font_size": "Font size",
    "font_color": "Font color",
    "stroke_color": "Stroke color",
    "stroke_width": "Stroke width",
}

PROCESS_PARAMS = [*DEFAULT_IMAGE_PARAMS][2:]


DB = {}
INPUT_DIR = "input"
OUTPUT_DIR = "output"


def get_params_report(key):
    params = DB[key]  # decode(key)
    html_params = "\n".join(
        [
            f" <b>{PARAMS_DECODE[param]}:</b> {params[param]}"
            for param in PROCESS_PARAMS
            if params[param]
        ]
    )
    params_report = "<b>Current parameters:</b>\n" + html_params + "\n"
    return params_report


######## CMDS HANDLERS ########
async def start(event):
    welcome_answer = [
        "Hello!\n",
        "I'm the AI video assistant bot!\n",
        "I'm able to create awesome previews and thumbnails (covers) for your video.\n"
        "Upload your video as a file or via YouTube-URL or send me image:",
    ]
    await event.reply("".join(welcome_answer))
    # buttons=[
    #     [
    #         Button.url("SOURCE CODE", url="github.com/1Danish-00/"),
    #         # Button.url("DEVELOPER", url="t.me/danish_00"),
    #     ],
    # ],


######## CMDS HANDLERS ########
async def test(event):
    font_message = ""
    await event.reply(font_message)


######## MESSAGE HANDLERS ########
async def encod(event):
    try:
        if not event.is_private:
            return
        if not event.media:
            return
        if hasattr(event.media, "document"):
            if not event.media.document.mime_type.startswith(
                ("video", "application/octet-stream")
            ):
                return
        elif not (hasattr(event.media, "webpage") or hasattr(event.media, "photo")):
            return

        key = event.chat_id
        download_message = await event.reply("`Downloading...`")
        if len(DB) > 9:
            return await download_message.edit(
                "Too many requests, try later.",
                # buttons=[Button.inline("BACK", data="start_back")],
            )
        if key in DB:
            return await download_message.edit(
                "Currently, your previous video is being processed.\nPlease wait."
            )
        DB[key] = ""

        input_dir = f"{INPUT_DIR}/{key}/"
        if not os.path.isdir(input_dir):
            os.mkdir(input_dir)
        if hasattr(event.media, "photo"):
            params = copy.copy(DEFAULT_IMAGE_PARAMS)
            img_path = await event.client.download_media(event.media, input_dir)
            logger.info(f"Recive image {img_path}")
            params["user_id"] = key
            params["image"] = img_path.split("/")[-1]
            DB[key] = params
            await download_message.delete()
            await event.client.send_message(
                event.chat_id,
                f"Photo was uploaded successfully!\nIt is possible to choose a <b>simple version</b> of the text overlay process with the specified parameters for the selected position, or a more intelligent - <b>smart version</b> when the font size and text splitting are optimally selected taking into account the objects in the image:",
                buttons=[
                    [Button.inline("Simple", data=f"change_version_simple")],
                    [Button.inline("Smart", data=f"change_version_smart")],
                ],
            )
        else:
            if hasattr(event.media, "webpage"):
                logger.info("Recive URL")
                message = event.message
                text = event.message.message
                item = event.message.entities[0]
                try:
                    url = text[item.offset : item.offset + item.length]
                    ydl_opts = {
                        "outtmpl": input_dir + "%(id)s.%(ext)s",
                        "noplaylist": True,
                        "format": "bestvideo[ext=mp4]+bestaudio[ext=mp4]/mp4+best[height<=720]",
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        assert (
                            info["duration"] <= 1500
                        ), "Video duration exceeds the limit (25 min)"
                        ydl.download(url)
                        filename = info["id"] + ".mp4"
                except AssertionError as dur_limit:
                    await download_message.edit(str(dur_limit))
                    logger.info(str(dur_limit))
                    DB.pop(key, None)
                    return shutil.rmtree(input_dir, ignore_errors=True)
                except Exception as er:
                    if "Video unavailable" in str(er):
                        await download_message.edit(
                            "Video unavailable. This content is not available in the host country of the server (Russia)."
                        )
                    else:
                        await download_message.edit(
                            "There were problems while downloading the video, try again"
                        )
                    logger.info(er)
                    DB.pop(key, None)
                    return shutil.rmtree(input_dir, ignore_errors=True)
            else:
                logger.info("Recive video")
                ttt = time.time()
                try:
                    if hasattr(event.media, "document"):
                        assert (
                            event.file.duration <= 1500
                        ), "Video duration exceeds the limit (25 min)"
                        file = event.media.document
                        filename = event.file.name
                        if not filename:
                            filename = (
                                "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
                            )
                        dl = input_dir + filename
                        with open(dl, "wb") as f:
                            ok = await download_file(
                                client=event.client,
                                location=file,
                                out=f,
                                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                                    progress(
                                        d,
                                        t,
                                        download_message,
                                        ttt,
                                        "Downloading",
                                    )
                                ),
                            )
                    else:
                        dl = await event.client.download_media(
                            event.media,
                            input_dir,
                            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                                progress(d, t, download_message, ttt, "Downloading")
                            ),
                        )
                except AssertionError as dur_limit:
                    await download_message.edit(str(dur_limit))
                    logger.info(str(dur_limit))
                    DB.pop(key, None)
                    return shutil.rmtree(input_dir, ignore_errors=True)
                except Exception as er:
                    await download_message.edit(
                        "There were problems while downloading the video, try again"
                    )
                    logger.info(er)
                    DB.pop(key, None)
                    return shutil.rmtree(input_dir, ignore_errors=True)

            params = copy.copy(DEFAULT_VIDEO_PARAMS)
            params["user_id"] = key
            params["video"] = filename
            DB[key] = params
            await download_message.delete()
            await event.client.send_message(
                event.chat_id,
                f"Video was uploaded successfully!\nThe final preview will be 30 seconds long. You can change the duration to a longer version (2 min).",
                buttons=[
                    [Button.inline("Change to 2 min", data=f"change_length")],
                    [Button.inline(f"Start processing!", data=f"start_processing")],
                ],
            )
    except BaseException as er:
        logger.info(er)
        return DB.pop(key, None)


######## CALLBACKQUERYS HANDLERS ########
async def change_length(event):
    key = event.chat_id
    params = DB[key]
    params["final_frame_length"] = 117
    DB[key] = params
    await start_processing(event)


async def change_version(event):
    key = event.chat_id
    version = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    params["version"] = version
    DB[key] = params
    await change_title(event)


async def change_title(event):
    key = event.chat_id
    param = "text"
    params = DB[key]
    cur_params = get_params_report(key)
    change_message = await event.edit(
        f"{cur_params}\nEnter a value for the <b>{PARAMS_DECODE[param]}</b>:"
    )
    chat = event.sender_id
    async with event.client.conversation(chat) as cv:
        reply = await cv.wait_event(events.NewMessage(from_users=chat))
        params[param] = reply.text
        DB[key] = params
        await change_message.delete()
        await reply.delete()
        cur_params = get_params_report(key)
        await cv.send_message(
            cur_params + "\nChoose a position:",
            buttons=POSITION_BUTTONS,
        )


async def change_position(event):
    key = event.chat_id
    position = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    params["position"] = position
    DB[key] = params
    cur_params = get_params_report(key)
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        cur_params + "\nChoose a font:",
        file="aivideoassistantbot/public/fonts.png",
        buttons=FONTS_BUTTONS,
    )


async def change_font(event):
    key = event.chat_id
    font = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    params["font"] = font
    DB[key] = params
    await change_font_size(event)


async def change_font_size(event):
    key = event.chat_id
    param = "font_size"
    params = DB[key]
    cur_params = get_params_report(key)
    change_message = await event.edit(
        f"{cur_params}\nEnter a value for the <b>{PARAMS_DECODE[param]}</b>:"
    )
    chat = event.sender_id
    async with event.client.conversation(chat) as cv:
        reply = await cv.wait_event(events.NewMessage(from_users=chat))
        params[param] = int(reply.text)
        await change_message.delete()
        await reply.delete()
        cur_params = get_params_report(key)
        await cv.send_message(
            cur_params + "\nChoose a font color:", buttons=FONTS_COLORS_BUTTONS
        )


async def change_font_color(event):
    key = event.chat_id
    font_color = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    params["font_color"] = font_color
    DB[key] = params
    cur_params = get_params_report(key)

    change_message = await event.edit(
        cur_params + "\nChoose a stroke color or start processing without stroke:",
        buttons=STROKE_COLORS_BUTTONS + [START_IMAGE_PROCESSING_BUTTON],
    )


async def change_stroke_color(event):
    key = event.chat_id
    stroke_color = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    params["stroke_color"] = stroke_color
    DB[key] = params
    await change_stroke_width(event)


async def change_stroke_width(event):
    key = event.chat_id
    param = "stroke_width"
    params = DB[key]
    cur_params = get_params_report(key)
    change_message = await event.edit(
        f"{cur_params}\nEnter a value for the <b>{PARAMS_DECODE[param]}</b>:"
    )
    chat = event.sender_id
    async with event.client.conversation(chat) as cv:
        reply = await cv.wait_event(events.NewMessage(from_users=chat))
        params[param] = int(reply.text)
        await change_message.delete()
        await reply.delete()
        cur_params = get_params_report(key)
        await cv.send_message(cur_params, buttons=START_IMAGE_PROCESSING_BUTTON)


async def change_params(event):
    key = event.chat_id
    param = event.pattern_match.group(1).decode("UTF-8")
    params = DB[key]
    await event.edit(f"Enter a value for the <b>{PARAMS_DECODE[param]}</b>:")
    chat = event.sender_id
    async with event.client.conversation(chat) as cv:
        reply = cv.wait_event(events.NewMessage(from_users=chat))
        repl = await reply
        params[param] = repl.text
        DB[key] = params
        await repl.reply(
            f"The <b>{PARAMS_DECODE[param]}</b> value is set to: <b>{params[param]}</b>",
            buttons=[
                [
                    Button.inline(
                        f"Change the value of the {PARAMS_DECODE[param]}",
                        data=f"change_params_{param}",
                    )
                ],
                [Button.inline("NEXT", data=f"preprocessing")],
            ],
        )


async def preprocessing(event):
    key = event.chat_id
    process_params = PROCESS_PARAMS
    params_report = get_params_report(key)
    get_param_button = lambda param: Button.inline(
        text=PARAMS_DECODE[param], data=f"change_params_{param}"
    )
    params_buttons = [
        [get_param_button(param_1), get_param_button(param_2)]
        for param_1, param_2 in zip(process_params[::2], process_params[1::2])
    ]
    full_buttons = params_buttons + [
        [Button.inline(f"Start processing!", data=f"start_processing_image")]
    ]
    await event.edit(
        params_report + "Do you want to change parameters or start processing?",
        buttons=full_buttons,
    )


async def start_processing(event):
    key = event.chat_id
    await event.delete()
    wait_message = await event.client.send_message(
        event.chat_id, "Processing has started.\nIt will take a few minutes."
    )
    params = DB[key]
    input_dir = f'{INPUT_DIR}/{params["user_id"]}/'
    output_dir = f'{OUTPUT_DIR}/{params["user_id"]}/'
    video_path = input_dir + params["video"]
    try:
        data = aiohttp.FormData()
        data.add_field("video", open(video_path, "rb"))
        data.add_field("params", str(params).replace("'", '"'))
        # default value is 5 minutes, set to `None` for unlimited timeout
        timeout = aiohttp.ClientTimeout(total=20 * 60)
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.post(url=UPLOAD_VIDEO_URL, data=data) as response:
                zip_bin = await response.read()

        zip = zipfile.ZipFile(io.BytesIO(zip_bin))

        zip.extractall(output_dir)
        ttt = time.time()
        await wait_message.delete()
        uploading_message = await event.client.send_message(
            event.chat_id, "`Uploading...`"
        )

        media_group = []
        for file in zip.namelist():
            path = output_dir + file
            with open(path, "rb") as f:
                media_file = await upload_file(
                    client=event.client,
                    file=f,
                    name=path,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, uploading_message, ttt, f"uploading {file}...")
                    ),
                )
                media_group.append(media_file)
        ds = await event.client.send_file(
            event.chat_id,
            file=media_group,
            force_document=False,
        )

    except BaseException as er:
        await uploading_message.edit(
            "There were problems while processing the video, try again"
        )
        logger.info(er)
        await asyncio.sleep(5)
    await uploading_message.delete()
    DB.pop(key, None)
    logger.info(f"User data delete {DB.get(key) is None}")
    shutil.rmtree(input_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)


async def start_image_processing(event):
    key = event.chat_id
    await event.delete()
    wait_message = await event.client.send_message(
        event.chat_id, "Processing has started.\nIt will take a few minutes."
    )
    params = DB[key]
    input_dir = f'{INPUT_DIR}/{params["user_id"]}/'
    image_path = input_dir + params["image"]
    try:
        data = aiohttp.FormData()
        data.add_field("image", open(image_path, "rb"))
        data.add_field("params", str(params).replace("'", '"'))
        # default value is 5 minutes, set to `None` for unlimited timeout
        timeout = aiohttp.ClientTimeout(total=20 * 60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url=UPLOAD_IMAGE_URL, data=data) as response:
                image_bin = await response.read()
        await event.client.send_file(
            event.chat_id,
            file=image_bin,
        )
    except BaseException as er:
        await wait_message.edit(
            "There were problems while processing the video, try again"
        )
        logger.info(er)
        await asyncio.sleep(5)
    await wait_message.delete()
    DB.pop(key, None)
    logger.info(f"User data delete {DB.get(key) is None}")
    shutil.rmtree(input_dir, ignore_errors=True)
