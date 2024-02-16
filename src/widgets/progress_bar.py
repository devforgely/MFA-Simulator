from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QImage, QPen, QPainter, QBrush, QPalette, QColor

# pyright: reportAttributeAccessIssue=false

class QRoundProgressBar(QWidget):
    PositionLeft = 180
    PositionTop = 90
    PositionRight = 0
    PositionBottom = -90

    UF_VALUE = 1
    UF_PERCENT = 2
    UF_MAX = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.min = 0
        self.max = 100
        self.value = 25

        self.nullPosition = self.PositionTop
        self.outlinePenWidth = 10
        self.dataPenWidth = 10
        self.rebuildBrush = False
        self.format = "%p%"
        self.decimals = 0
        self.updateFlags = self.UF_PERCENT
        self.brushColor = QColor(0,0,0)

    def setRange(self, min, max):
        self.min = min
        self.max = max

        if self.max < self.min:
            self.max, self.min = self.min, self.max

        if self.value < self.min:
            self.value = self.min
        elif self.value > self.max:
            self.value = self.max

        self.update()

    def setMinimun(self, min):
        self.setRange(min, self.max)

    def setMaximun(self, max):
        self.setRange(self.min, max)

    def setValue(self, val):
        if self.value != val:
            if val < self.min:
                self.value = self.min
            elif val > self.max:
                self.value = self.max
            else:
                self.value = val
            self.update()

    def setNullPosition(self, position):
        if position != self.nullPosition:
            self.nullPosition = position
            self.update()

    def setOutlinePenWidth(self, penWidth):
        if penWidth != self.outlinePenWidth:
            self.outlinePenWidth = penWidth
            self.update()

    def setDataPenWidth(self, penWidth):
        if penWidth != self.dataPenWidth:
            self.dataPenWidth = penWidth
            self.update()

    def setBrushColor(self, color):
        if color != self.brushColor:
            self.brushColor = color
            self.rebuildBrush = True
            self.update()

    def setFormat(self, format):
        if format != self.format:
            self.format = format
            self.valueFormatChanged()

    def resetFormat(self):
        self.format = ''
        self.valueFormatChanged()

    def setDecimals(self, count):
        if count >= 0 and count != self.decimals:
            self.decimals = count
            self.valueFormatChanged()

    def paintEvent(self, event):
        outerRadius = min(self.width(), self.height())
        baseRect = QRectF(1, 1, outerRadius-2, outerRadius-2)

        buffer = QImage(outerRadius, outerRadius, QImage.Format_ARGB32)
        buffer.fill(0)

        p = QPainter(buffer)
        p.setRenderHint(QPainter.Antialiasing)

        # data brush
        self.rebuildDataBrushIfNeeded()

        # background
        self.drawBackground(p, buffer.rect())

        # base circle
        self.drawBase(p, baseRect)

        # data circle
        arcStep = 360.0 / (self.max - self.min) * self.value
        self.drawValue(p, baseRect, self.value, arcStep)

        # center circle
        innerRect, innerRadius = self.calculateInnerRect(outerRadius)

        # text
        self.drawText(p, innerRect, innerRadius, self.value)

        # finally draw the bar
        p.end()

        painter = QPainter(self)
        painter.drawImage(0, 0, buffer)

    def drawBackground(self, p, baseRect):
        p.fillRect(baseRect, self.palette().window())

    def drawBase(self, p, baseRect):
        p.setPen(QPen(QColor(239,241,240), self.outlinePenWidth))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2))

    def drawValue(self, p, baseRect, value, arcLength):
        # nothing to draw
        if value == self.min:
            return

        p.setPen(QPen(self.palette().highlight().color(), self.dataPenWidth))
        p.setBrush(Qt.NoBrush)
        p.drawArc(baseRect.adjusted(self.outlinePenWidth/2, self.outlinePenWidth/2, -self.outlinePenWidth/2, -self.outlinePenWidth/2),
                    int(self.nullPosition * 16),
                    int(-arcLength * 16))

    def calculateInnerRect(self, outerRadius):
        innerRadius = outerRadius - self.outlinePenWidth

        delta = (outerRadius - innerRadius) / 2.
        innerRect = QRectF(delta, delta, innerRadius, innerRadius)
        return innerRect, innerRadius

    def drawText(self, p, innerRect, innerRadius, value):
        if not self.format:
            return

        text = self.valueToText(value)

        if len(text) >= 1:
            f = self.font()
            f.setPixelSize(int(innerRadius * 0.8 / len(text[0])))
            p.setFont(f)

            p.setPen(self.palette().text().color())
            innerRect = QRectF(innerRect.left(), innerRect.top()-10, innerRect.width(), innerRect.height())
            p.drawText(innerRect, Qt.AlignCenter, text[0])

        if len(text) == 2:
            f = self.font()
            f.setPixelSize(int(innerRadius * 0.7 / len(text[1])))
            p.setFont(f)

            p.setPen(self.palette().text().color())
            rect_adjusted = QRectF(innerRect.left(), innerRect.top()+10, innerRect.width(), innerRect.height() * 0.85)  # Adjust the rectangle
            p.drawText(rect_adjusted, Qt.AlignCenter | Qt.AlignBottom, text[1])

    def valueToText(self, value):
        textToDraw = self.format.split("|")
        if len(textToDraw) > 2: return []

        format_string = f"{{:.{self.decimals}f}}"

        for i in range(len(textToDraw)):
            if self.updateFlags & self.UF_VALUE:
                textToDraw[i] = textToDraw[i].replace("%v", str(value))

            if self.updateFlags & self.UF_PERCENT:
                percent = (value - self.min) / (self.max - self.min) * 100.0
                textToDraw[i] = textToDraw[i].replace("%p", format_string.format(percent))

            if self.updateFlags & self.UF_MAX:
                m = self.max - self.min
                textToDraw[i] = textToDraw[i].replace("%m", str(m))

        return textToDraw

    def valueFormatChanged(self):
        self.updateFlags = 0

        if "%v" in self.format:
            self.updateFlags |= self.UF_VALUE

        if "%p" in self.format:
            self.updateFlags |= self.UF_PERCENT

        if "%m" in self.format:
            self.updateFlags |= self.UF_MAX

        self.update()

    def rebuildDataBrushIfNeeded(self):
        if self.rebuildBrush:
            self.rebuildBrush = False

            p = self.palette()
            p.setBrush(QPalette.Highlight, self.brushColor)
            self.setPalette(p)