from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSizeGrip, QButtonGroup
from widgets.side_grip import SideGrip
from widgets.info_bar import InfoBarIcon, InfoBar
from views.simulate_views import SimulateView
from views.learn_view import LearnView
from views.quiz_views import QuizView
from views.profile_view import ProfileView
from views.manage_view import ManageView
from viewmodels.simulate_viewmodels import SimulateViewModel
from viewmodels.learn_viewmodel import LearnViewModel
from viewmodels.quiz_viewmodels import QuizViewModel
from viewmodels.profile_viewmodel import ProfileViewModel
from viewmodels.manage_viewmodel import ManageViewModel
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false


class MainView(QMainWindow):
    def __init__(self, viewmodel) -> None:
        super().__init__()
        uic.loadUi("views_ui/main_view.ui", self)

        self._viewmodel = viewmodel
        self._viewmodel.fact_changed.connect(self.fact_label.setText)
        self._viewmodel.coin_count_changed.connect(self.coin_count.setText)
        self._viewmodel.badge_count_changed.connect(self.badge_count.setText)
        self._viewmodel.info_bar_added.connect(self.show_notification)

        self.setWindowTitle("MFA Simulator")

        # PAGES
        self.simulate_page = SimulateView(SimulateViewModel(), parent=self.stackedWidget)
        self.learn_page = LearnView(LearnViewModel(), parent=self.stackedWidget)
        self.quiz_page = QuizView(QuizViewModel(), parent=self.stackedWidget)
        self.profile_page = ProfileView(ProfileViewModel(), parent=self.stackedWidget)
        self.manage_page = ManageView(ManageViewModel(), parent=self.stackedWidget)
        self.stackedWidget.addWidget(self.simulate_page)
        self.stackedWidget.addWidget(self.learn_page)
        self.stackedWidget.addWidget(self.quiz_page)
        self.stackedWidget.addWidget(self.profile_page)
        self.stackedWidget.addWidget(self.manage_page)

        # Data LOAD
        self._viewmodel.fact()
        self._viewmodel.coin_count()
        self._viewmodel.badge_count()

        # LEFT MENUS CONNECTIONS
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.simulate_btn)
        self.button_group.addButton(self.learn_btn)
        self.button_group.addButton(self.quiz_btn)
        self.button_group.addButton(self.profile_btn)
        self.button_group.addButton(self.manage_btn)
        self.button_group.buttonClicked.connect(self.highlight_menu)
        self.simulate_btn.clicked.connect(self.button_click)
        self.learn_btn.clicked.connect(self.button_click)
        self.quiz_btn.clicked.connect(self.button_click)
        self.profile_btn.clicked.connect(self.button_click)
        self.manage_btn.clicked.connect(self.button_click)

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

            self.top_bar.mousePressEvent = lambda event: mousePressWindowEvent(event)
            self.top_bar.mouseMoveEvent = lambda event: mouseMoveWindowEvent(event)

            # TOP BAR CONNECTIONS
            self.minimise_btn.clicked.connect(self.showMinimized)
            self.maximise_restore_btn.clicked.connect(self.maximise_restore_window)
            self.close_btn.clicked.connect(self.close)

            # RESIZE WIDGETS
            self.gripSize = 5
            self.sideGrips = [
                SideGrip(self, Qt.LeftEdge), 
                SideGrip(self, Qt.TopEdge), 
                SideGrip(self, Qt.RightEdge), 
                SideGrip(self, Qt.BottomEdge), 
            ]
            self.cornerGrips = [QSizeGrip(self) for _ in range(4)]
            for grip in self.cornerGrips:
                grip.setStyleSheet("background-color: transparent;")

        else:
        # USE DEFAULT TITLE BAR
            self.rightSection.layout().removeWidget(self.minimise_btn)
            self.rightSection.layout().removeWidget(self.maximise_restore_btn)
            self.rightSection.layout().removeWidget(self.close_btn)
            self.minimise_btn.deleteLater()
            self.maximise_restore_btn.deleteLater()
            self.close_btn.deleteLater()
        
        # SET CUSTOM THEME
        if Settings.ENABLE_CUSTOM_THEME:
            self.styleSheet.setStyleSheet(open(Settings.THEME_FILE, 'r').read())
        
        # HELP
        self.help_btn.clicked.connect(self._viewmodel.help)

        # PAGE INIT
        self.stackedWidget.setCurrentIndex(self._viewmodel.get_system_startup())

        button = self.button_group.buttons()[self._viewmodel.get_system_startup()]
        button.setChecked(True)
        self.highlight_menu(button)

    
    def maximise_restore_window(self) -> None:
        if self.window_normal_status:
            self.stored_size = self.size()
            self.showMaximized()
            self.maximise_restore_btn.setToolTip("Restore")
            self.maximise_restore_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "window-restore-regular.svg"))

            for grip in self.cornerGrips:
                grip.hide()
            
            for grip in self.sideGrips:
                grip.hide()

            self.window_normal_status = False
        else:
            self.showNormal()
            self.maximise_restore_btn.setToolTip("Maximise")
            self.maximise_restore_btn.setIcon(QIcon(Settings.ICON_FILE_PATH + "square-regular.svg"))

            for grip in self.cornerGrips:
                grip.show()
            
            for grip in self.sideGrips:
                grip.show()

            self.window_normal_status = True
    
    def button_click(self) -> None:
        # GET BUTTON CLICKED
        btn_name = self.sender().objectName()

        match(btn_name):
            case "simulate_btn":
                self.stackedWidget.setCurrentWidget(self.simulate_page)
            case "learn_btn":
                self.stackedWidget.setCurrentWidget(self.learn_page)
            case "quiz_btn":
                self.stackedWidget.setCurrentWidget(self.quiz_page)
            case "profile_btn":
                self.stackedWidget.setCurrentWidget(self.profile_page)
            case "manage_btn":
                self.stackedWidget.setCurrentWidget(self.manage_page)
            case _:
                Exception("Undefined Button Behaviour")
    
    def highlight_menu(self, button) -> None:
        btn_name = button.objectName()
        for btn in self.button_group.buttons():
            if btn.objectName() == btn_name:
                match(btn.objectName()):
                    case "simulate_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"button-play-blue.svg"))
                    case "learn_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"book-reading-blue.svg"))
                    case "quiz_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"task-list-blue.svg"))
                    case "profile_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"user-circle-single-blue.svg"))
                    case "manage_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"cog-blue.svg"))
                    case _:
                        Exception("Undefined Button Behaviour")
            else:
                match(btn.objectName()):
                    case "simulate_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"button-play.png"))
                    case "learn_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"book-reading.svg"))
                    case "quiz_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"task-list.png"))
                    case "profile_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"user-circle-single.png"))
                    case "manage_btn":
                        btn.setIcon(QIcon(Settings.ICON_FILE_PATH+"cog.png"))
                    case _:
                        Exception("Undefined Button Behaviour")

    def show_notification(self, icon: InfoBarIcon, content: str):
        infobar = InfoBar(icon, content, parent=self)
        infobar.show()

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
            QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

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