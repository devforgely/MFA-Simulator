from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QRect

# pyright: reportAttributeAccessIssue=false

class DraggableCard(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        self.dragging = False
        self.original_pos = self.pos()
        self.collision_widget = None
        self.trigger = None

    def set_collision(self, widget) -> None:
        self.collision_widget = widget

    def set_collision_call(self, func) -> None:
        self.trigger = func

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.setCursor(Qt.ClosedHandCursor)
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            parent_rect = self.parent().rect()
            if parent_rect.contains(QRect(new_pos, self.size())):
                self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)
            self.check_collision()
            if not self.parent().rect().contains(self.geometry()):
                self.move(self.original_pos)

    def check_collision(self):
        if self.collision_widget is not None and self.trigger is not None \
            and self.geometry().intersects(self.collision_widget.geometry()):
            self.trigger()
            self.deleteLater()