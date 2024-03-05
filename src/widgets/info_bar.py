from PyQt5.QtCore import QTimer, QPoint, QPropertyAnimation, QEasingCurve, QObject, pyqtSignal, QEvent, QParallelAnimationGroup, QSize, Qt
from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect, QFrame, QHBoxLayout, QToolButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from enum import Enum
import weakref
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false

class InfoBarIcon(Enum):
    SUCCESS = Settings.ICON_FILE_PATH+"success-icon.svg"
    WARNING = Settings.ICON_FILE_PATH+"warning-icon.svg"
    ERROR = Settings.ICON_FILE_PATH+"error-icon.svg"
    COIN = Settings.IMAGE_FILE_PATH+"coin.png"
    MEDAL = Settings.IMAGE_FILE_PATH+"star-medal.png"

class InfoBarPosition(Enum):
    """ Info bar position """
    TOP = 0

class InfoBar(QFrame):
    closedSignal = pyqtSignal()

    def __init__(self, icon: InfoBarIcon, content: str, duration=2000, parent=None):
        super().__init__(parent)

        self.icon = icon
        self.duration = duration

        self.iconLabel = QLabel(self)
        self.iconLabel.setPixmap(QIcon(icon.value).pixmap(20, 20))

        self.contentLabel = QLabel(content, self)

        self.closeButton = QToolButton(self)
        self.closeButton.setIcon(QIcon(Settings.ICON_FILE_PATH+"cross.svg"))
        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIconSize(QSize(12, 12))
        self.closeButton.setCursor(Qt.PointingHandCursor)
        self.closeButton.clicked.connect(self.close) # type: ignore

        self.hBoxLayout = QHBoxLayout(self)
        self.textLayout = QHBoxLayout()

        self.hBoxLayout.setContentsMargins(10, 3, 3, 3)
        self.hBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.textLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.textLayout.setContentsMargins(1, 5, 0, 5)

        self.hBoxLayout.addWidget(self.iconLabel, 0, Qt.AlignVCenter | Qt.AlignLeft)
        self.hBoxLayout.addSpacing(7)

        self.textLayout.addWidget(self.contentLabel, 1, Qt.AlignVCenter)
        self.textLayout.addSpacing(7)

        self.hBoxLayout.addLayout(self.textLayout)
        self.hBoxLayout.addWidget(self.closeButton, 0, Qt.AlignLeft)

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityEffect.setOpacity(1)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b'opacity', self)
    
        self.setGraphicsEffect(self.opacityEffect)
        self.setQss()

    def setQss(self):
        self.iconLabel.setStyleSheet("border: none;")
        self.contentLabel.setStyleSheet("border: none; color: #000; font-size: 9pt;")
        self.closeButton.setStyleSheet("""
                                          QToolButton { border: none; background: transparent; }
                                          QToolButton:hover { background-color: rgba(0, 0, 0, 6); }
                                          QToolButton:pressed { background-color: rgba(0, 0, 0, 9); }
                                       """)

        match(self.icon):
            case InfoBarIcon.SUCCESS:
                self.setStyleSheet("background-color: #dff5dd; border: 1px solid silver; border-radius: 7px")
            case InfoBarIcon.WARNING:
                self.setStyleSheet("background-color: #fef3ce; border: 1px solid silver; border-radius: 7px")
            case InfoBarIcon.ERROR:
                self.setStyleSheet("background-color: #fce6e8; border: 1px solid silver; border-radius: 7px")
            case InfoBarIcon.COIN | InfoBarIcon.MEDAL:
                self.setStyleSheet("background-color: #f2f3f5; border: 1px solid silver; border-radius: 7px")

    def __fadeOut(self):
        self.opacityAni.setDuration(self.duration)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.close) # type: ignore
        self.opacityAni.start()

    def showEvent(self, event):
        super().showEvent(event)

        if self.duration >= 0:
            QTimer.singleShot(self.duration, self.__fadeOut)

        manager = InfoBarManager.make(InfoBarPosition.TOP)
        manager.add(self)

    def closeEvent(self, event):
        self.closedSignal.emit()
        self.deleteLater()

class InfoBarManager(QObject):
    """ Info bar manager """
    _instance = None
    managers = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InfoBarManager, cls).__new__(
                cls, *args, **kwargs)
            cls._instance.__initialized = False

        return cls._instance

    def __init__(self):
        super().__init__()
        if self.__initialized:
            return

        self.spacing = 16
        self.margin = 24
        self.infoBars = weakref.WeakKeyDictionary()
        self.aniGroups = weakref.WeakKeyDictionary()
        self.slideAnis = []
        self.dropAnis = []
        self.__initialized = True

    def add(self, infoBar: InfoBar):
 
        p = infoBar.parent()    # type:QObject
        if not p:
            return
   
        if p not in self.infoBars:
            p.installEventFilter(self)
            self.infoBars[p] = []
            self.aniGroups[p] = QParallelAnimationGroup(self)

        if infoBar in self.infoBars[p]:
            return

        # add drop animation
        if self.infoBars[p]:
            dropAni = QPropertyAnimation(infoBar, b'pos')
            dropAni.setDuration(200)

            self.aniGroups[p].addAnimation(dropAni)
            self.dropAnis.append(dropAni)

            infoBar.setProperty('dropAni', dropAni)

        # add slide animation
        self.infoBars[p].append(infoBar)
        slideAni = self._createSlideAni(infoBar)
        self.slideAnis.append(slideAni)

        infoBar.setProperty('slideAni', slideAni)
        infoBar.closedSignal.connect(lambda: self.remove(infoBar))

        slideAni.start()

    def remove(self, infoBar: InfoBar):
        p = infoBar.parent()
        if p not in self.infoBars:
            return

        if infoBar not in self.infoBars[p]:
            return

        self.infoBars[p].remove(infoBar)

        # remove drop animation
        dropAni = infoBar.property('dropAni')   # type: QPropertyAnimation
        if dropAni:
            self.aniGroups[p].removeAnimation(dropAni)
            self.dropAnis.remove(dropAni)

        # remove slider animation
        slideAni = infoBar.property('slideAni')
        if slideAni:
            self.slideAnis.remove(slideAni)

        # adjust the position of the remaining info bars
        self._updateDropAni(p)
        self.aniGroups[p].start()

    def _createSlideAni(self, infoBar: InfoBar):
        slideAni = QPropertyAnimation(infoBar, b'pos')
        slideAni.setEasingCurve(QEasingCurve.OutQuad)
        slideAni.setDuration(200)

        slideAni.setStartValue(self._slideStartPos(infoBar))
        slideAni.setEndValue(self._pos(infoBar))

        return slideAni

    def _updateDropAni(self, parent):
        for bar in self.infoBars[parent]:
            ani = bar.property('dropAni')
            if not ani:
                continue

            ani.setStartValue(bar.pos())
            ani.setEndValue(self._pos(bar))

    def _pos(self, infoBar: InfoBar, parentSize=None):
        raise NotImplementedError

    def _slideStartPos(self, infoBar: InfoBar):
        raise NotImplementedError

    def eventFilter(self, obj, e: QEvent):
        if obj not in self.infoBars:
            return False

        if e.type() in [QEvent.Resize, QEvent.WindowStateChange]:
            size = e.size() if e.type() == QEvent.Resize else None
            for bar in self.infoBars[obj]:
                bar.move(self._pos(bar, size))

        return super().eventFilter(obj, e)
    
    @classmethod
    def register(cls, name):
        """ register menu animation manager

        Parameters
        ----------
        name: Any
            the name of manager, it should be unique
        """
        def wrapper(Manager):
            if name not in cls.managers:
                cls.managers[name] = Manager

            return Manager

        return wrapper
    
    @classmethod
    def make(cls, position: InfoBarPosition):
        """ mask info bar manager according to the display position """
        if position not in cls.managers:
            raise ValueError(f'`{position}` is an invalid animation type.')

        return cls.managers[position]()
    
@InfoBarManager.register(InfoBarPosition.TOP)
class TopInfoBarManager(InfoBarManager):
    """ Top position info bar manager """

    def _pos(self, infoBar: InfoBar, parentSize=None):
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        x = (infoBar.parent().width() - infoBar.width()) // 2
        y = self.margin
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar):
        pos = self._pos(infoBar)
        return QPoint(pos.x(), pos.y() - 16)