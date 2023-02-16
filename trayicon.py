import os

import pystray

from PIL import Image
from pathlib import Path


# https://stackoverflow.com/questions/54835399/running-a-tkinter-window-and-pystray-icon-together
# https://stackoverflow.com/questions/9494739/how-to-build-a-systemtray-app-for-windows


class TrayIcon():

    def __init__(self, overlay):
        self.overlay = overlay

        self.image = Image.open(Path(Path(__file__).parent, 'img', 'clock.png'))
        self.menu = (
            pystray.MenuItem('Quit', self.quit_window),
            )

        self.icon = pystray.Icon('tray_icon', self.image, 'Zilean', self.menu)
        self.icon.run()

    def quit_window(self):
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

    overlay = Overlay_()
    tray_icon = TrayIcon(overlay)

    while True:
        pass
