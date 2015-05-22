import os
import sys
import time
import threading

try:
    from PyQt5.QtCore import (
        QFile, QFileInfo,
        QPoint, QRect, QRectF,
        QSettings, QSize, Qt, QTextStream
    )
    from PyQt5.QtGui import (
        QIcon, QKeySequence, QPainterPath,
        QPainter, QLinearGradient,
        QPen, QColor, QImage
    )
    from PyQt5.QtWidgets import (
        QAction, QApplication, QFileDialog,
        QMainWindow, QMessageBox, QTextEdit,
        QWidget, QPushButton
    )
    # from PyQt5 import Qt
except ImportError:
    print('PyQt5 is needed')
    sys.exit(-1)

from asec.rom import Loader


class Timer(threading.Thread):
    def __init__(self, interval, function, args=None, kwargs={}):
        if not args:
            args = []

        super(Timer, self).__init__()

        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self._loop = True

    def run(self):
        while self._loop:
            self.function(*self.args, **self.kwargs)
            time.sleep(self.interval)

    def stop(self):
        self._loop = False


class ViewQImage(QImage):
    def __init__(self, screen):
        super(ViewQImage, self).__init__(
            screen.toImage().tostring(),
            screen.width, screen.height,
            QImage.Format_RGB32
        )


class Screen(QWidget):
    def __init__(self, parent):
        super(Screen, self).__init__(parent)
        self.screenX = self.width()
        self.screenY = self.height()
        self.screen = None
        self.paused = False

        self._fps = 0
        self._image = None
        self._last_redraw = time.time()
        # self._redraw_timer = Timer(.03, lambda: self.repaint())
        # self._redraw_timer.start()

        self._repainting = False

    def setEmulator(self, emulator):
        self.emulator = emulator
        self.setScreen(self.emulator.GPU.screen)
        self.emulator.GPU.renderScreen.connect(self.redraw)
        self.emulator.start()

    def setScreen(self, screen):
        self.screenX = screen.width
        self.screenY = screen.height
        self.resize(self.screenX, self.screenY)

    def redraw(self, screen):
        current = int(time.time() * 1000)
        self._fps = 1000/(current - self._last_redraw)
        self._image = ViewQImage(screen)
        self._last_redraw = current
        # self.update()
        self.repaint()

    def repaint(self):
        if hasattr(self, '_repainting') and not self._repainting:
            super(Screen, self).repaint()

    def paintEvent(self, event):
        self._repainting = True
        painter = QPainter(self)

        if self._image:
            painter.drawImage(0, 0, self._image)
            painter.drawText(5, 15, "FPS: %-05i" % self._fps)

        if self.paused:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.gray)
            painter.drawRoundedRect(0, 0, 20, 60, 5.0, 5.0)
            painter.drawRoundedRect(40, 0, 20, 60, 5.0, 5.0)
        self._repainting = False

    def keyPressEvent(self, event):
        self.emulator.KEY.press(event.key())
        if event.key() == Qt.Key_Escape:
            self.pause()
        print(event.key(), self.emulator.KEY.colidX, self.emulator.KEY.keys)

    def keyReleaseEvent(self, event):
        self.emulator.KEY.release(event.key())
        if event.key() == Qt.Key_Escape:
            self.play()
        print(event.key(), self.emulator.KEY.colidX, self.emulator.KEY.keys)

    def pause(self):
        if not self.paused:
            self.emulator.pause()
            self.paused = True

    def play(self):
        if self.paused:
            self.emulator.play()
            self.paused = False

    def focusOutEvent(self, event):
        self.pause()
        event.accept()

    def focusInEvent(self, event):
        self.play()
        event.accept()

    def closeEvent(self, event):
        self.pause()
        # self.emulator._loop = False
        # self.emulator._stop()
        # self._redraw_timer.stop()
        # self._redraw_timer.join()
        # del self._redraw_timer
        del self.emulator


class ROMChooser(QWidget):
    def __init__(self, parent):
        super(ROMChooser, self).__init__(parent)
        self.setMinimumSize(300, 200)
        self.file_over = False
        self.setAcceptDrops(True)

    def paintEvent(self, event):
        painter = QPainter(self)

        drawColor = Qt.gray if not self.file_over else Qt.blue

        pen = QPen()
        pen.setDashPattern([4, 2])
        pen.setWidth(3)
        pen.setColor(drawColor)
        painter.setPen(pen)

        painter.setRenderHint(QPainter.Antialiasing)

        # Rounded dashed rect
        painter.translate(self.width()/2-60, self.height()/2-60)
        painter.drawRoundedRect(0, 0, 120, 120, 25.0, 25.0)

        # Arrow
        painter.translate(22, 30)
        arrow = QPainterPath()
        arrow.moveTo(20, 40)
        arrow.lineTo(30, 40)
        arrow.lineTo(30, 1)
        arrow.lineTo(50, 1)
        arrow.lineTo(50, 40)
        arrow.lineTo(60, 40)
        arrow.lineTo(40, 60)
        arrow.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.setBrush(drawColor)
        painter.drawPath(arrow)

    # Drag & drop events
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.file_over = True
            self.update()
        else:
            event.ignore()
            self.file_over = False
            self.update()

    def dragLeaveEvent(self, event):
        self.file_over = False
        event.ignore()
        self.update()

    def dropEvent(self, event):
        self.file_over = False
        self.update()

        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                self.parentWidget().setCurrentFile(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.curFile = ''

        self.rom_chooser = ROMChooser(self)
        self.setCentralWidget(self.rom_chooser)

        self.screens = []

        self.readSettings()

        self.setCurrentFile(self.curFile)

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def readSettings(self):
        settings = QSettings("AlexSnet", "Emulator Collection")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QSettings("AlexSnet", "Emulator Collection")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.setWindowModified(False)

        if fileName:
            loader = Loader(self.curFile)
            loader.read()

            emulator = loader.loader.emulator()
            screen = Screen(None)
            screen.info = loader
            screen.setEmulator(emulator)
            # emulator.GPU.setRedrawCallback(screen.redraw)
            screen.show()
            screen.setWindowTitle(loader.name)
            self.screens.append(screen)

        else:
            self.setWindowTitle("Choose game ROM - ASEC")


def main():
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s\t%(levelname)-10s\t"
               "%(name)-20s\t%(process)-5d\t%(message)s"
    )

    application = QApplication(sys.argv)
    mw = MainWindow()

    if len(sys.argv) == 2:
        mw.setCurrentFile(sys.argv[1])
    else:
        mw.show()

    sys.exit(application.exec_())

if __name__ == '__main__':
    main()
