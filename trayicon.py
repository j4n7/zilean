import os

import pystray

from PIL import Image
from pathlib import Path
from threading import Thread


# https://stackoverflow.com/questions/54835399/running-a-tkinter-window-and-pystray-icon-together
# https://stackoverflow.com/questions/9494739/how-to-build-a-systemtray-app-for-windows


class TrayIcon():

    def __init__(self, overlay, start):
        self.overlay = overlay

        self.start = start
        self.blue = True

        self.image = Image.open(Path(Path(__file__).parent, 'img', 'clock.png'))
        self.menu = (
            pystray.MenuItem('Blue', self.set_blue, checked=lambda item: self.blue),
            pystray.MenuItem('Red', self.set_red, checked=lambda item: not self.blue),
            pystray.MenuItem('Quit', self.quit),
            )

        self.icon = pystray.Icon('tray_icon', self.image, 'Zilean', self.menu)
        self.icon.run()

    def set_blue(self, icon, item):
        self.blue = True
        self.start.color = 'blue'

    def set_red(self, icon, item):
        self.blue = False
        self.start.color = 'red'

    def quit(self, icon, item):
        icon.visible = False  # Avoid phantom icons
        os._exit(0)

    def show_window(self):
        self.icon.stop()
        self.overlay.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.overlay.after(0, self.overlay.deiconify)


if __name__ == '__main__':
    class Overlay_:
        def __init__(self):
            pass

        def destroy(self):
            pass

    class Start:
        def __init__(self):
            self.color = 'blue'

    overlay = Overlay_()
    tray_icon = TrayIcon(overlay, Start())

    while True:
        pass
