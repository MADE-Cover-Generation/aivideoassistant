import time
import subprocess
import math
import json


def stdr(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    dur = (
        ((str(hours) + ":") if hours else "00:")
        + ((str(minutes) + ":") if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )
    return dur


def ts(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]


def hbs(size: float) -> str:
    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


async def progress(current, total, event, start, type_of_ps, file=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "`[{0}{1}] {2}%`\n\n".format(
            "".join(["●" for i in range(math.floor(percentage / 5))]),
            "".join(["○" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )
        tmp = (
            progress_str
            + "`{0} of {1}`\n\n`✦ Speed: {2}/s`\n\n`✦ ETA: {3}`\n\n".format(
                hbs(current),
                hbs(total),
                hbs(speed),
                ts(time_to_completion),
            )
        )
        if file:
            await event.edit(
                "`✦ {}`\n\n`File Name: {}`\n\n{}".format(type_of_ps, file, tmp)
            )
        else:
            await event.edit("`✦ {}`\n\n{}".format(type_of_ps, tmp))


async def genss(file):
    process = subprocess.Popen(
        ["mediainfo", file, "--Output=JSON"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = process.communicate()
    out = stdout.decode().strip()
    z = json.loads(out)
    p = z["media"]["track"][0]["Duration"]
    return int(p.split(".")[-2])


async def duration_s(file):
    tsec = await genss(file)
    x = round(tsec / 5)
    y = round(tsec / 5 + 30)
    pin = stdr(x)
    if y < tsec:
        pon = stdr(y)
    else:
        pon = stdr(tsec)
    return pin, pon
