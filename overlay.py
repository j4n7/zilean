import tkinter as tk
# from PIL import Image, ImageTk

import ctypes
import win32gui
# import win32con
# import win32api

from datetime import datetime, timedelta
from pathlib import PurePath

from functions import get_base_dir, parse_time, format_time


# https://stackoverflow.com/questions/63047053/how-to-replace-a-background-image-in-tkinter
# https://stackoverflow.com/questions/59334733/resize-photoimage-using-zoom-or-subsample
# https://stackoverflow.com/questions/29641616/drag-window-when-using-overrideredirect


# Avoid Windows DPI sclaing
# https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
ctypes.windll.shcore.SetProcessDpiAwareness(2)


base_dir = get_base_dir()
path_img = PurePath(base_dir, 'img')


class CustomFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background_image = tk.PhotoImage(file=PurePath(path_img, 'overlay.png'))
        self.background = tk.Label(self, border=0, bg='grey15', image=self.background_image)
        self.background.pack(fill=tk.BOTH, expand=True)


class CustomText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure('red', foreground='#ff0000')
    text.highlight_pattern('this should be red', 'red')

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start='1.0', end='end',
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set('matchStart', start)
        self.mark_set('matchEnd', start)
        self.mark_set('searchLimit', end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, 'matchEnd', 'searchLimit',
                                count=count, regexp=regexp)
            if index == '':
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.mark_set('matchStart', index)
            self.mark_set('matchEnd', '%s+%sc' % (index, count.get()))
            self.tag_add(tag, 'matchStart', 'matchEnd')


class Overlay(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.overrideredirect(True)  # Deletes Windows' default title bar

        self.tk.call('tk', 'scaling', 1.0)

        self.wm_attributes('-alpha', 0.75)
        self.wm_attributes('-transparentcolor', 'grey15')  # str_a_ange color to avoid jagged borders
        self.wm_attributes("-topmost", True)

        self.frame = CustomFrame(self)
        self.frame.pack(side='top', fill='both', expand='True')

        self._padx = -6

        self._offsetx = 0
        self._offsety = 0

        self._terminate = False

        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)

        self.bind('<Escape>', self._close)
        self.geometry('212x212')
        self.eval('tk::PlaceWindow . center')

        # self.set_geometry()
        self.set_text_box()

        self.message = ''
        self.message_time = datetime.now()

    def _show(self, event):
        self.deiconify()

    def _hide(self, event):
        self.withdraw()

    def _close(self, event):
        self.quit()

    def drag(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry('+{x}+{y}'.format(x=x, y=y))

    def click(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def set_geometry(self):
        # WINDOW RECT
        # Origin (x = 0, y = 0) is left top corner of full screen
        # Margin left: distance from x = 0 to left side
        # Margin right: distance from x = 0 to right side
        # Margin top: distance from y = 0 to top side
        # Margin bottom: distance from y = 0 to bottom side

        window_name = 'League of Legends (TM) Client'  # 'League of Legends (TM) Client'
        window_handle = win32gui.FindWindow(None, window_name)
        window_rect = win32gui.GetWindowRect(window_handle)
        client_rect = win32gui.GetClientRect(window_handle)

        window_properties = {
            'margin_left': window_rect[0],
            'margin_top': window_rect[1],
            'margin_right': window_rect[2],
            'margin_bottom': window_rect[3],
            'width': window_rect[2] - window_rect[0],
            'height': window_rect[3] - window_rect[1],
        }

        # In relation to window
        client_properties = {
            'margin_left': client_rect[0],
            'margin_top': client_rect[1],
            'margin_right': client_rect[2],
            'margin_bottom': client_rect[3],
            'width': client_rect[2] - client_rect[0],
            'height': client_rect[3] - client_rect[1],
        }

        window_resolution = {'width': window_properties['width'], 'height': window_properties['height']}
        game_resolution = {'width': client_properties['width'], 'height': client_properties['height']}
        is_borderless = True if window_resolution == game_resolution else False

        # self.geometry('320x480')
        self.geometry(f"213x320+{window_properties['margin_left'] + window_properties['width'] - 228}+146")
        # self.geometry('160x240')

    def set_text_box(self):
        self.text = CustomText(self,
                            height=7,
                            width=16,
                            spacing1=10,
                            spacing2=5,
                            spacing3=10,
                            border=0,
                            font=('Tahoma', 21),
                            fg='white',
                            bg='#1F1F1F',
                            wrap=tk.WORD)
        self.text.place(x=17, y=14)
        self.text.tag_configure('blue', foreground='#72A7E8')
        self.text.tag_configure('red', foreground='#E87272')
        self.text.tag_configure('center', justify='center')
        self.text.bindtags((str(self.text), str(self), "all"))  # Disable text bindings
        self.text.config(cursor='arrow')

    def set_message(self, meessage):
        self.message = meessage
        self.message_time = datetime.now()

    def set_mockup(self):
        self.message = 'Mirar wavestate ¿Dónde esta el jungla?'

    def update_message(self):
        self.text.delete('1.0', 'end')

        time = datetime.now() - self.message_time
        if time.seconds <= 3:
            self.text.insert('end', self.message, 'center')
            self.text.highlight_pattern('-.+', 'blue', regexp=True)
            self.text.highlight_pattern('\+.+', 'red', regexp=True)

        self.after(1, self.update_message)

    def run(self):
        self.after(1, self.update_message)
        self.mainloop()


if __name__ == '__main__':

    overlay = Overlay()
    overlay.set_mockup()
    overlay.run()
