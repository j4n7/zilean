import ctypes
import dxcam
from PIL import Image, ImageOps
# from pytesseract import pytesseract, image_to_string

from tessereact import image_to_text


# https://www.reddit.com/r/learnpython/comments/lyix7c/ocr_video_game_text/
# https://github.com/ra1nty/DXcam


user32 = ctypes.windll.user32

lol_resolution = {'w': 1920, 'h': 1080}
screen_resolution = {'w': user32.GetSystemMetrics(0), 'h': user32.GetSystemMetrics(1)}

screen_refresh_rate = 75

left, top = (screen_resolution['w'] - lol_resolution['w']) // 2, (screen_resolution['h'] - lol_resolution['h']) // 2
right, bottom = left + lol_resolution['w'], top + lol_resolution['h']
region = (left + lol_resolution['w'] - 140, top, right - 115, bottom - lol_resolution['h'] + 30)
# region_ = (left, top, right, bottom)

# pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_player_cs(camera, region):
    try:
        frame = camera.grab(region=region)
        image = Image.fromarray(frame)

        # https://stackoverflow.com/questions/9506841/using-pil-to-turn-a-rgb-image-into-a-pure-black-and-white-image
        threshold = 200
        image = image.convert('L').point(lambda x : 255 if x > threshold else 0, mode='1')
        image = ImageOps.invert(image)  # Invert black and white

        # image.show()

        # cs = int(image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))
        cs = int(image_to_text(image))
        return cs
    except ValueError:
        '''No CS available'''
    except AttributeError:
        '''No frame'''
    return 777


if __name__ == '__main__':
    camera = dxcam.create(output_color='RGBA')
    cs = get_player_cs(camera, region)
    print('cs:', cs)
