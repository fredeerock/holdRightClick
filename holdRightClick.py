from pynput import mouse, keyboard
import time
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QStyle
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread

class ClickTracker:
    def __init__(self):
        self.click_count = 0
        self.last_click = 0
        self.is_holding = False
        self.mouse_controller = mouse.Controller()
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.running = True

    def on_click(self, x, y, button, pressed):
        if not pressed:
            return

        current_time = time.time()

        if button == mouse.Button.left:
            if self.is_holding:
                self.mouse_controller.release(mouse.Button.right)
                self.is_holding = False
                return

            if current_time - self.last_click < 0.3:
                self.click_count += 1
                if self.click_count == 3:
                    self.click_count = 0
                    self.mouse_controller.press(mouse.Button.right)
                    self.is_holding = True
            else:
                self.click_count = 1

            self.last_click = current_time

        elif button == mouse.Button.right and self.is_holding:
            self.mouse_controller.release(mouse.Button.right)
            self.is_holding = False

    def on_press(self, key):
        if key == keyboard.Key.esc and self.is_holding:
            self.mouse_controller.release(mouse.Button.right)
            self.is_holding = False

    def stop(self):
        self.running = False
        if self.is_holding:
            self.mouse_controller.release(mouse.Button.right)
            self.is_holding = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

class ClickTrackerThread(QThread):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker

    def run(self):
        self.tracker.start()

    def stop(self):
        self.tracker.stop()
        self.quit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tracker = ClickTracker()
        self.tracker_thread = ClickTrackerThread(self.tracker)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hold Right Click")
        self.setGeometry(100, 100, 300, 200)

        # Create buttons
        self.toggle_button = QPushButton("Start", self)
        self.toggle_button.clicked.connect(self.toggle_tracker)

        self.tray_button = QPushButton("Send to Tray", self)
        self.tray_button.clicked.connect(self.send_to_tray)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.tray_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up system tray icon
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "clicker.ico")
        else:
            icon_path = "clicker.ico"

        if not QIcon(icon_path).isNull():
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            print("Icon not found, using default icon.")
            self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), self)

        # Set up system tray menu
        tray_menu = QMenu()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_program)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def exit_program(self):
        self.tracker_thread.stop()
        QApplication.quit()

    def toggle_tracker(self):
        if self.tracker_thread.isRunning():
            self.tracker_thread.stop()
            self.toggle_button.setText("Start")
        else:
            self.tracker_thread = ClickTrackerThread(self.tracker)  # Create a new thread instance
            self.tracker_thread.start()
            self.toggle_button.setText("Stop")

    def send_to_tray(self):
        self.tray_icon.show()
        self.hide()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.raise_()

    def closeEvent(self, event):
        self.tracker_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
