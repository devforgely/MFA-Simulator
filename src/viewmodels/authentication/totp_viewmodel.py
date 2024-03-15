from viewmodels.authentication.authentication_base import *
from models.authentication.authentication import Method
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from widgets.timer import TimeThread
import time
import qrcode
import random
import string
from io import BytesIO
from datetime import datetime, timezone

# pyright: reportAttributeAccessIssue=false

class TOTPRegisterViewModel(AuthenticationBaseViewModel):
    qr_signal = pyqtSignal(QPixmap)
    qr_scan_signal = pyqtSignal(str, str, str, str)

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()

    def make_qr(self) -> None:
        self.authentication_service.register("")

        qr = qrcode.QRCode()
        qr.add_data(self.authentication_service.get_session_stored()["shared_key"])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')

        # Create a QPixmap from the BytesIO object
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), 'PNG')
        pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)

        self.qr_signal.emit(pixmap)

    def generate_ip(self):
        return ".".join([str(random.randint(100, 999)), str(random.randint(10, 99)), str(random.randint(10, 99)), str(random.randint(100, 999))])

    def generate_user_id(self):
        letters = string.ascii_lowercase
        return random.choice(letters) + ''.join(random.choices(string.digits, k=5)) + ''.join(random.choices(letters, k=2))

    def scan_qr(self) -> None:
        location = "Manchester, ENG, GB"
        time = datetime.now(timezone.utc).strftime("%H:%M %Z")
        ip = self.generate_ip()
        user_id = self.generate_user_id()
        self.qr_scan_signal.emit(location, time, ip, user_id)

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        return data

    def send(self) -> None:
        if self.authentication_service.register("Confirm Key"):
            self.state_change.emit("Account is linked.", 0)
            self.state_data_change.emit(self.state_data(), 0)
            self.message_service.send(self, "Registered")
        else:
            self.state_change.emit("Registration Fail", 1)


class TOTPAuthenticateViewModel(AuthenticationBaseViewModel):
    time_changed = pyqtSignal(int)
    code_changed = pyqtSignal(str, str)
    clear_code_signal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.display_details = self.authentication_service.get_display_details()
        
        # thread for timer
        self.max_time = 30
        self.threading = TimeThread(self.max_time)
        self.step_count = self.threading.max_val
        self.threading._signal.connect(self.signal_update)
        self.allow_code = True
        self.started = False

    def subscribe(self, type) -> None:
        self.message_service.subscribe(self, type, self.on_message)

    def on_message(self, message_title: str, *args)  -> None:
        if message_title == "Change View":
            if self.started:
                if args[0] == Method.TOTP:
                    self.allow_code = True
                    self.authentication_service.authenticate("GENERATE", ignore_limit=True)
                    self.code_changed.emit(self.authentication_service.get_session_stored()["totp"], datetime.now(timezone.utc).strftime("%H:%M %Z"))
                else:
                    self.allow_code = False
    
    def get_code(self) -> None:
        # generate new totp
        if self.allow_code:
            self.authentication_service.authenticate("GENERATE", ignore_limit=True)
            self.code_changed.emit(self.authentication_service.get_session_stored()["totp"], datetime.now(timezone.utc).strftime("%H:%M %Z"))

    def start_totp(self) -> None:
        self.started = True
        self.get_code()
        if self.threading is not None:
            self.threading.set_max(int(self.max_time - (time.time() % self.max_time))) # remaining time before totp expire
            self.threading.start()

    def signal_update(self, val: int):
        self.time_changed.emit(val)
        
        if val == 0:
            # Stop the old thread
            if hasattr(self, 'threading') and self.threading is not None:
                self.threading.quit()
                self.threading.wait()
                self.threading = None

            self.threading = TimeThread(self.max_time) # Now we are in sync
            self.threading._signal.connect(self.signal_update)
            self.threading.start()

            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.get_code)
            self.timer.start(1000) # add delay to account for synchronisation
            

    def state_data(self) -> dict:
        data = self.authentication_service.get_session_stored().copy()
        return data

    def send(self, code: str) -> None:
        flag = self.authentication_service.authenticate(code)

        if not flag:
            self.allow_code = False
            self.clean_up()
            self.state_change.emit("The user has been authenticated.", flag)
            self.message_service.send(self, "Authenticated")
        elif flag == 1:
            self.clear_code_signal.emit()
            self.state_change.emit("The TOTP does not match.", flag)
        elif flag == 2:
            self.state_change.emit("Locked for 10 seconds.", flag)
        
        self.state_data_change.emit(self.state_data(), flag)

    def bypass(self) -> None:
        self.state_data_change.emit(self.state_data(), 0)
        self.clean_up()

    def clean_up(self) -> None:
        self.message_service.unsubscribe(self)
        if hasattr(self, 'threading') and self.threading is not None:
            self.threading.stop()
            self.threading.quit()
            self.threading.wait()
            self.threading = None
        if hasattr(self, 'timer') and self.timer is not None:
            if self.timer.isActive():
                self.timer.stop()
            self.timer.deleteLater()
            self.timer = None