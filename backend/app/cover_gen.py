import os
import logging
import cv2

from src.helpers import init_helper
from src.helpers.cover_helper import ImageText, ImageTextSmart, COLORS_STR_RGB
from src.helpers.sod_helper import U2NETHelper

U2NET_PATH = "models/u2net_human_seg.pth"

logger = logging.getLogger()


def main():
    args = init_helper.get_cover_arguments()

    init_helper.init_logger(args.log_dir, args.log_file)
    init_helper.set_random_seed(args.seed)

    try:
        save_dir = os.path.dirname(args.save_path)
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"Read image {args.source}")
        image = cv2.imread(args.source)
        logger.info(f"Complete")
        if args.version == "simple":
            logger.info(f"Add text with simple version")
            image_text = ImageText(image)
            image_text.add_text(
            text = args.text,
            position = args.position,
            font_path = args.font_path,
            font_size = args.font_size,
            font_color = args.font_color_rgb if args.font_color_rgb is not None else COLORS_STR_RGB[args.font_color],
            stroke_color = args.stroke_color_rgb if args.stroke_color_rgb is not None else COLORS_STR_RGB[args.stroke_color],
            stroke_width = args.stroke_width,
            )
            logger.info(f"Save image with text")
            image_text.save_image(args.save_path)
            logger.info(f"Complete")
        elif args.version == "smart":
            logger.info(f"Add text with smart version")
            logger.info(f"Load SOD-model from {U2NET_PATH}")
            net = U2NETHelper(U2NET_PATH)
            logger.info(f"Get image mask")
            mask = net.inference(image)
            image_text = ImageTextSmart(image, mask)
            image_text.add_text_smart(
            text = args.text,
            position = args.position,
            font_path = args.font_path,
            font_color = args.font_color_rgb if args.font_color_rgb is not None else COLORS_STR_RGB[args.font_color],
            stroke_color = args.stroke_color_rgb if args.stroke_color_rgb is not None else COLORS_STR_RGB[args.stroke_color],
            stroke_width = args.stroke_width,
            )
            logger.info(f"Save image with text")
            image_text.save_image(args.save_path)
            logger.info(f"Complete")
    except BaseException as err:
        logger.warning(err)

if __name__ == '__main__':
    main()


