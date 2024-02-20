from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QPoint, QSize, pyqtSlot
from PyQt5.QtWidgets import QLabel, QLineEdit, QToolButton, QHBoxLayout, QFrame, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon, QPen, QBrush, QPainter, QColor, QFont
from configuration.app_configuration import Settings

# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false

class BorderedImageLabel(QLabel):
    clicked = pyqtSignal(QLabel)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = ""
    
    def set_image(self, image) -> None:
        self.image = image
    
    def mousePressEvent(self, event):
        self.clicked.emit(self)
    
    def show_border(self) -> None:
        self.setStyleSheet('border: 3px solid blue;')
    
    def hide_border(self) -> None:
        self.setStyleSheet('border: none;')


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder: str, visibility: bool, maxlength: int, icon: str):
        super(CustomLineEdit, self).__init__()

        self.setFrame(False)
        self.setStyleSheet("""
            QLineEdit {
                height: 52px;
                margin: 7px 0;
                padding: 0px 15px;
                padding-left: 35px;
                border-bottom: 2px solid #bbbdbf;
                font-size: 10pt;
                font-weight: 400;
                color: #333;
            }

            QLineEdit:focus {
                border-color: #4070f4;
            }
        """)

        self.setPlaceholderText(placeholder)
        self.setMaxLength(maxlength)
        # Create a layout for the QLineEdit
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        self.icon = QLabel(self)
        self.icon.setFixedSize(24, 24)
        self.icon.setScaledContents(True)
        self.icon.setPixmap(QPixmap(f"{Settings.ICON_FILE_PATH}{icon}.svg"))
        layout.addWidget(self.icon)
        # Add a stretchable space in the middle
        layout.addStretch()

        if not visibility:        
            self.setEchoMode(QLineEdit.Password)
            self.eye_button = QToolButton(self)
            self.eye_button.setCursor(Qt.PointingHandCursor)
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye.svg"))

            self.eye_button.setStyleSheet("""
                QToolButton {
                    border: none;
                    alignment: 5px 0px 5px 200px;
                }
            """)

            # Add the eye button to the right
            layout.addWidget(self.eye_button)
            self.eye_button.clicked.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self):
        if self.echoMode() == QLineEdit.Password:
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye-off.svg"))
            self.setEchoMode(QLineEdit.Normal)
        else:
            self.eye_button.setIcon(QIcon(f"{Settings.ICON_FILE_PATH}eye.svg"))
            self.setEchoMode(QLineEdit.Password)

#credit: RexBarker
class ToggleSwitch(QCheckBox):
    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)
    _black_pen = QPen(Qt.black)

    def __init__(self, 
                 parent=None, 
                 bar_color=Qt.gray, 
                 checked_color="#00B0FF",
                 handle_color=Qt.white, 
                 h_scale=1.0,
                 v_scale=1.0,
                 fontSize=10):
             
        super().__init__(parent)

        # Save our properties on the object via self, so we can access them later
        # in the paintEvent.
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())

        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget.

        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0
        self._h_scale = h_scale
        self._v_scale = v_scale
        self._fontSize = fontSize

        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self):
        return QSize(58, 45)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):

        contRect = self.contentsRect()
        width =  contRect.width() * self._h_scale
        height = contRect.height() * self._v_scale
        handleRadius = round(0.24 * height)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(0, 0, width - handleRadius, 0.40 * height)
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width()*self._h_scale - 2 * handleRadius
        xLeft = contRect.center().x() - (trailLength + handleRadius)/2 
        xPos = xLeft + handleRadius + trailLength * self._handle_position

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)

            p.setPen(self._black_pen)
            p.setFont(QFont('Helvetica', self._fontSize, 75))
            p.drawText(QPointF(xLeft + handleRadius / 2, contRect.center().y() + 
                       handleRadius / 2),"ON")

        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.setPen(self._light_grey_pen)
        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @pyqtSlot(int)
    def handle_state_change(self, value):
        self._handle_position = 1 if value else 0

    def handle_position(self, pos):
        """change the property
           we need to trigger QWidget.update() method, either by:
           1- calling it here [ what we're doing ].
           2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    def setH_scale(self,value):
        self._h_scale = value
        self.update()

    def setV_scale(self,value):
        self._v_scale = value
        self.update()

    def setFontSize(self,value):
        self._fontSize = value
        self.update()