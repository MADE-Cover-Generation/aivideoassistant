import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AVAILABLE_POSITIONS = [
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

AVAILABLE_FONTS = [
    "CenturySB-Bold",
    "CenturySB-Italic",
    "Futura-Bold",
    "Futura-Italic",
    "Garamond-Bold",
    "Garamond-Italic",
    "Helvetica-Bold",
    "Helvetica-Italic",
    "Mulish-Bold",
    "Mulish-Italic",
    "TimesRoman-Bold",
    "TimesRoman-Italic",
]

COLORS_STR_RGB = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
}


DEFAULT_IMAGE_PARAMS = {
    "version": "simple",
    "position": "left-top",
    "font": "Futura-Bold",
    "font_size": 60,
    "font_color": "white",
    "stroke_color": "black",
    "stroke_width": 1,
}


def check_params():
    pass


class ImageText:
    def __init__(self, frame: np.ndarray, border_margin: int = 10):
        self.image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.initial_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.size = self.image.size
        self.draw = ImageDraw.Draw(self.image)
        self.border_margin = border_margin

    def _get_position_params(
        self, position: str, text: str, font: ImageFont
    ) -> list[tuple[int], str, str]:
        if "bottom" in position:
            bbox = self.draw.multiline_textbbox((0, 0), text, font=font)
            text_offset = bbox[-1] + bbox[1]
        match position:
            case "left-top":
                return [(self.border_margin, self.border_margin), "left", "la"]
            case "left-middle":
                return [(self.border_margin, self.size[1] // 2), "left", "lm"]
            case "left-bottom":
                return [
                    (
                        self.border_margin,
                        self.size[1] - self.border_margin - text_offset,
                    ),
                    "left",
                    "la",
                ]
            case "center-top":
                return [(self.size[0] // 2, self.border_margin), "center", "ma"]
            case "center-middle":
                return [(self.size[0] // 2, self.size[1] // 2), "center", "mm"]
            case "center-bottom":
                return [
                    (
                        self.size[0] // 2,
                        self.size[1] - self.border_margin - text_offset,
                    ),
                    "center",
                    "ma",
                ]
            case "right-top":
                return [
                    (self.size[0] - self.border_margin, self.border_margin),
                    "right",
                    "ra",
                ]
            case "right-middle":
                return [
                    (self.size[0] - self.border_margin, self.size[1] // 2),
                    "right",
                    "rm",
                ]
            case "right-bottom":
                return [
                    (
                        self.size[0] - self.border_margin,
                        self.size[1] - self.border_margin - text_offset,
                    ),
                    "right",
                    "ra",
                ]
        return [(self.border_margin, self.border_margin), "left", "la"]

    def add_text(
        self,
        text: str,
        position: str,
        font_path: str,
        font_size: int = 60,
        font_color: tuple[int] = (255, 255, 255),
        stroke_color: tuple[int] = (0, 0, 0),
        stroke_width: int = 1,
    ):
        img_font = ImageFont.truetype(font_path, font_size)
        xy, align, anchor = self._get_position_params(position, text, img_font)

        self.draw.multiline_text(
            xy,
            text,
            font=img_font,
            fill=font_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
            align=align,
            anchor=anchor,
        )

    def get_image(self, np_array: bool = True) -> (Image.Image | np.ndarray):
        return (
            cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            if np_array
            else self.image
        )

    def reset_image(self):
        self.image = self.initial_image.copy()
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self, filename: str = "img_text.png"):
        self.image.save(filename)


class ImageTextSmart(ImageText):
    def __init__(
        self,
        frame: np.ndarray,
        mask: np.ndarray,
        border_margin: int = 10,
        min_font_size: int = 20,
        max_font_size: int = 150,
    ):
        super().__init__(frame, border_margin)
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.mask = mask
        self.empty_area = self._get_empty_area()

    def _get_empty_area(self, bottom_min_treshold: float = 0.2) -> np.ndarray:
        empty_area = np.float32(self.mask > 0.85)
        empty_area = cv2.cvtColor(
            (empty_area * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR
        )
        img_w, img_h = self.size
        cv2.rectangle(
            empty_area,
            (0, int(img_h - img_h * bottom_min_treshold)),
            self.size,
            (0, 0, 0),
            -1,
        )
        cv2.rectangle(
            empty_area,
            (self.border_margin // 2, self.border_margin // 2),
            (
                img_w - self.border_margin // 2,
                img_h - self.border_margin // 2,
            ),
            (255, 255, 255),
            self.border_margin,
        )
        return np.uint8(cv2.cvtColor(empty_area, cv2.COLOR_BGR2GRAY) / 255)

    def _get_best_text_params(
        self, text: str, position: str, font_path: str
    ) -> (tuple[int, list[str]] | None):
        font_color = (255, 255, 255)
        cur_font_size = self.min_font_size
        prev_cur_size = self.min_font_size
        line_min_font_size = self.min_font_size
        line_max_font_size = self.max_font_size
        text_split = text.split()
        last_lines = [text_split]
        line_text = dict()
        for i in range(len(text_split)):
            pointer = 0 if i == 0 else 1
            last_lines = last_lines if line_text.get(i) is None else line_text[i][1]
            if len(last_lines[-1]) == 1 and i != 0:
                break
            for _ in range(10000):
                if pointer == 0:
                    lines = last_lines
                else:
                    lines = (
                        last_lines[:-1]
                        + [last_lines[-1][:pointer]]
                        + [last_lines[-1][pointer:]]
                    )
                text_lines = ["-".join(line) for line in lines if line]
                text = "\n".join(text_lines)
                for _ in range(100000):
                    empty_image = Image.new(
                        "RGB", self.empty_area.shape[::-1], color=(0, 0, 0)
                    )
                    draw = ImageDraw.Draw(empty_image)
                    img_font = ImageFont.truetype(font_path, cur_font_size)
                    xy, align, anchor = self._get_position_params(
                        position, text, img_font
                    )
                    draw.text(
                        xy,
                        text,
                        fill=font_color,
                        font=img_font,
                        align=align,
                        anchor=anchor,
                    )
                    e_i = np.uint8(
                        cv2.cvtColor(np.array(empty_image), cv2.COLOR_RGB2GRAY) / 255
                    )
                    # print(f"lines={len(lines)} pointer={pointer}, cur_size={cur_font_size}, prev_size={prev_cur_size}, lines_max_size={line_max_font_size}, lines_min_size={line_min_font_size}")
                    if (
                        e_i + np.uint8(self.empty_area)
                    ).max() == 2 or cur_font_size == self.max_font_size:
                        if cur_font_size == line_min_font_size:
                            break
                        elif cur_font_size - prev_cur_size > 2:
                            line_max_font_size = cur_font_size
                            cur_font_size = (
                                cur_font_size - (cur_font_size - prev_cur_size) // 2
                            )
                        else:
                            font_size = cur_font_size - 1
                            cur_font_size = font_size
                            prev_cur_size = cur_font_size
                            line_text[i + 1] = (font_size, lines)
                            line_min_font_size = font_size
                            break
                    else:
                        prev_cur_size = cur_font_size
                        step = (line_max_font_size - cur_font_size) // 2
                        cur_font_size += step if step else 1
                    line_max_font_size = self.max_font_size
                pointer += 1
                if i == 0 or pointer > len(last_lines[-1]) - 1:
                    last_lines = lines
                    break
        return line_text.get(max(line_text.keys()) if line_text.keys() else None)

    def add_text_smart(
        self,
        text: str,
        position: str,
        font_path: str,
        font_size: int = 80,
        font_color: tuple[int] = (255, 255, 255),
        stroke_color: tuple[int] = (0, 0, 0),
        stroke_width: int = 1,
    ):
        best_text_params = self._get_best_text_params(text, position, font_path)
        if best_text_params is not None:
            font_size_smart, lines = best_text_params
            text_lines = [" ".join(line) for line in lines if line]
            text_smart = "\n".join(text_lines)
            self.add_text(
                text_smart,
                position,
                font_path,
                font_size_smart,
                font_color,
                stroke_color,
                stroke_width,
            )
        else:
            self.add_text(
                text,
                position,
                font_path,
                font_size,
                font_color,
                stroke_color,
                stroke_width,
            )
