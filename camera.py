import dxcam
from PIL import Image
# from pytesseract import pytesseract, image_to_string

from tessereact import image_to_text


# https://www.reddit.com/r/learnpython/comments/lyix7c/ocr_video_game_text/
# https://github.com/ra1nty/DXcam


lol_resolution = {'w': 1920, 'h': 1080}
screen_resolution = {'w': 2560, 'h': 1080}

screen_refresh_rate = 75

left, top = (screen_resolution['w'] - lol_resolution['w']) // 2, (screen_resolution['h'] - lol_resolution['h']) // 2
right, bottom = left + lol_resolution['w'], top + lol_resolution['h']
region = (left + lol_resolution['w'] - 140, top, right - 90, bottom - lol_resolution['h'] + 30)
# region_ = (left, top, right, bottom)

# pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_player_cs(camera, region):
    try:
        frame = camera.grab(region=region)
        image = Image.fromarray(frame)
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

    # camera.start(region=region, target_fps=screen_refresh_rate)
    # for i in range(1000):
    #     image = camera.get_latest_frame()  # Will block until new frame available
    #     cs = int(image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))
    # camera.stop()
