import json
import io
import os
import shutil
import zipfile
import aiofiles
import asyncio
from logging import INFO, basicConfig, getLogger
from fastapi import FastAPI, File, UploadFile, Body, Request
from fastapi.responses import Response
from pydantic import BaseModel


INPUT_DIR = "input"
OUTPUT_DIR = "output"
MODEL = "casum"
DEVICE = "cuda"

app = FastAPI()

basicConfig(format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=INFO)
logger = getLogger(__name__)
logger.info("Start app")


def zipfiles(dir: str):
    filenames = sorted(os.listdir(dir))
    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fname in filenames:
        zf.write(f"{dir}/{fname}", fname)

    zf.close()
    zip_filename = "archive.zip"
    resp = Response(
        s.getvalue(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename={zip_filename}"},
    )

    return resp


class VideoParametrs(BaseModel):
    user_id: int
    video: str
    final_frame_length: int

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ImageParametrs(BaseModel):
    user_id: int
    image: str
    version: str
    text: str
    position: str
    font: str
    font_size: int
    font_color: str
    stroke_color: str
    stroke_width: int

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


@app.post("/uploadcheck")
def submit(params: VideoParametrs = Body(...), video: UploadFile = File(...)):
    return {"JSON Payload ": params, "Video": video.filename}


@app.post("/api/video/upload")
async def procces_upload_video(
    params: VideoParametrs = Body(...), video: UploadFile = File(...)
):
    logger.info("Recive video-post request")
    input_dir = f"{INPUT_DIR}/{params.user_id}"
    output_dir = f"{OUTPUT_DIR}/{params.user_id}"
    os.makedirs(input_dir, exist_ok=True)
    video_path = f"{input_dir}/{params.video}"
    logger.info("Download video")
    # Async writing:
    async with aiofiles.open(video_path, "wb") as out_file:
        while content := await video.read(1024):
            await out_file.write(content)
    logger.info("Run video processing")
    ncmd = f"cd app && python inference.py {MODEL} --source ../{video_path} --save-path ../{output_dir}/{params.video} --final-frame-length {params.final_frame_length} --device {DEVICE}"
    process = await asyncio.create_subprocess_shell(
        ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    logger.info(stdout.decode())
    logger.warning(stderr.decode())
    resp = zipfiles(output_dir)
    shutil.rmtree(input_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    logger.info("Response zip file")
    return resp


@app.post("/api/image/upload")
async def procces_upload_image(
    params: ImageParametrs = Body(...), image: UploadFile = File(...)
):
    logger.info("Recive image-post request")
    input_dir = f"{INPUT_DIR}/{params.user_id}"
    output_dir = f"{OUTPUT_DIR}/{params.user_id}"
    os.makedirs(input_dir, exist_ok=True)
    image_path = f"{input_dir}/{params.image}"
    logger.info("Download image")
    # Async writing:
    async with aiofiles.open(image_path, "wb") as out_file:
        while content := await image.read(1024):
            await out_file.write(content)
    logger.info("Run image processing")
    ncmd = f'cd app && python cover_gen.py {params.version} --source ../{image_path} --save-path ../{output_dir}/cover.png --text "{params.text}" --position {params.position} --font-path fonts/{params.font}.ttf --font-size {params.font_size} --font-color {params.font_color} --stroke-color {params.stroke_color if params.stroke_color else "white"} --stroke-width {params.stroke_width if params.stroke_color else 0}'
    process = await asyncio.create_subprocess_shell(
        ncmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    logger.info(stdout.decode())
    logger.warning(stderr.decode())
    with open(f"{output_dir}/cover.png", "rb") as img:
        cover = img.read()
    resp = Response(content=cover, media_type="image/png")
    shutil.rmtree(input_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    logger.info("Response cover image")
    return resp


@app.post("/echo")
async def echo(request: Request):
    print(request)
    return {"Result": "OK"}
