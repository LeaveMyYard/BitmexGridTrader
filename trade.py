import asyncio
import threading

import qdarkstyle
from sourse.ui.mainwindow import MainWindow
from PyQt5 import QtWidgets


def main():
    loop = asyncio.new_event_loop()

    def spin_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # asyncio.get_child_watcher().attach_loop(loop)
    threading.Thread(target=spin_loop, daemon=True).start()

    QtWidgets.QApplication.setStyle('Fusion')
    app = QtWidgets.QApplication([])
    window = MainWindow(loop)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.exec_()


if __name__ == "__main__":
    main()

