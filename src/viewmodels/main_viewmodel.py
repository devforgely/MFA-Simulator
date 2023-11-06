from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, QSystemTrayIcon
from configuration.app_settings import *
from configuration.resources_rc import *
from widgets.side_grip import SideGrip


# pyright: reportGeneralTypeIssues=false

class MainViewModel(QMainWindow):
    def __init__(self) -> None:
        QMainWindow.__init__(self)
        uic.loadUi("views/main_view.ui", self)

        # TOP BAR CONNECTIONS
        self.help_btn.clicked.connect(self.help)

        # LEFT MENUS CONNECTIONS
        self.play_btn.clicked.connect(self.buttonClick)
        self.learn_btn.clicked.connect(self.buttonClick)
        self.quiz_btn.clicked.connect(self.buttonClick)
        self.profile_btn.clicked.connect(self.buttonClick)
        self.manage_btn.clicked.connect(self.buttonClick)

        self.setup_ui()

        # SHOW APP
        self.show()
    
    def setup_ui(self) -> None:
        # USE CUSTOM TITLE BAR
        if Settings.ENABLE_CUSTOM_TITLE_BAR:
            self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)

            self.window_normal_status = True

            # MOVE WINDOW / MAXIMIZE / RESTORE
            def mousePressWindowEvent(event):
                if event.button() == Qt.LeftButton:
                    self.dragPos = event.globalPos() - self.pos()
                event.accept()
            
            def mouseMoveWindowEvent(event):
                if event.buttons() == Qt.LeftButton:
                    # If maximised window then change to normal window
                    if not self.window_normal_status:
                        x_ratio = self.stored_size.width() / self.width()
                        y_ratio = self.stored_size.height() / self.height()
                        self.maximise_restore_window()
                        # Move the window to the current mouse position
                        self.dragPos = QPoint(int(self.dragPos.x()*x_ratio), int(self.dragPos.y()*y_ratio))
    
                    # Move the window based on the mouse drag
                    self.move(event.globalPos() - self.dragPos)
                    event.accept()

            self.topBar.mousePressEvent = lambda event: mousePressWindowEvent(event)
            self.topBar.mouseMoveEvent = lambda event: mouseMoveWindowEvent(event)

            # TOP BAR CONNECTIONS
            self.minimise_btn.clicked.connect(self.showMinimized)
            self.maximise_restore_btn.clicked.connect(self.maximise_restore_window)
            self.close_btn.clicked.connect(self.close)

            # RESIZE WIDGETS
            self.gripSize = 5
            self.sideGrips = [
                SideGrip(self, QtCore.Qt.LeftEdge), 
                SideGrip(self, QtCore.Qt.TopEdge), 
                SideGrip(self, QtCore.Qt.RightEdge), 
                SideGrip(self, QtCore.Qt.BottomEdge), 
            ]
            self.cornerGrips = [QSizeGrip(self) for _ in range(4)]
            for grip in self.cornerGrips:
                grip.setStyleSheet("background-color: transparent;")

        else:
        # USE DEFAULT TITLE BAR
            self.setWindowTitle("MFA Simulator")
            self.rightSection.layout().removeWidget(self.minimise_btn)
            self.rightSection.layout().removeWidget(self.maximise_restore_btn)
            self.rightSection.layout().removeWidget(self.close_btn)
            self.minimise_btn.deleteLater()
            self.maximise_restore_btn.deleteLater()
            self.close_btn.deleteLater()
        
        # SET CUSTOM THEME
        if Settings.ENABLE_CUSTOM_THEME:
            self.styleSheet.setStyleSheet(open(Settings.THEME_FILE, 'r').read())

        #DROP SHADOW
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


    def help(self) -> None:
        pass

    def maximise_restore_window(self) -> None:
        if self.window_normal_status:
            self.stored_size = self.size()
            self.showMaximized()
            self.maximise_restore_btn.setToolTip("Restore")
            self.maximise_restore_btn.setIcon(QIcon(u":/resources/icons/window-restore-regular.svg"))

            for grip in self.cornerGrips:
                grip.hide()
            
            for grip in self.sideGrips:
                grip.hide()

            self.window_normal_status = False
        else:
            self.showNormal()
            self.maximise_restore_btn.setToolTip("Maximise")
            self.maximise_restore_btn.setIcon(QIcon(u":/resources/icons/square-regular.svg"))

            for grip in self.cornerGrips:
                grip.show()
            
            for grip in self.sideGrips:
                grip.show()

            self.window_normal_status = True
    
    def buttonClick(self) -> None:
        # GET BUTTON CLICKED
        btn_name = self.sender().objectName()

        match(btn_name):
            case "play_btn":
                print("play")
            case "learn_btn":
                print("learn")
            case "quiz_btn":
                print("quiz")
            case "profile_btn":
                print("profile")
            case "manage_btn":
                print("manage")
            case _:
                Exception("Undefined Button Behaviour")

    """
    =====================================================================================
    RESIZE FUNCTIONALITY
    =====================================================================================
    """

    def updateGrips(self) -> None:
        outRect = self.rect() # geometry includes the margin
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize,
            -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QtCore.QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QtCore.QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QtCore.QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QtCore.QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(), 
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(), 
            inRect.width(), self.gripSize)

    def resizeEvent(self, event) -> None:
        QMainWindow.resizeEvent(self, event)
        if Settings.ENABLE_CUSTOM_TITLE_BAR:
            self.updateGrips()