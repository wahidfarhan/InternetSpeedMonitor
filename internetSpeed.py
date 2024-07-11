import sys
import os
import psutil
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon  # Import QIcon for setting the window icon


class DataUsageMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.setWindowTitle("Internet Data Usage Monitor")
        self.setWindowIcon(QIcon('icon.png'))  # Set custom icon (replace 'icon.png' with your icon file)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(170, 80)

        # Set transparent background
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: white; border-radius: 10px;")
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Add labels for displaying data sent, received, and total download
        self.label_sent_kbps = QLabel("Upload Speed: 0.00 Kbps")
        self.main_layout.addWidget(self.label_sent_kbps)

        self.label_recv_kbps = QLabel("Download Speed: 0.00 Kbps")
        self.main_layout.addWidget(self.label_recv_kbps)

        self.label_total_recv = QLabel("Total Downloaded: 0.00 MB")
        self.main_layout.addWidget(self.label_total_recv)

        self.total_received = 0

        self.data_folder = os.path.join(os.path.expanduser("~"), "data")

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.load_saved_data()
        self.start_monitoring()

    def load_saved_data(self):
        data_file = os.path.join(self.data_folder, 'data_usage.txt')
        try:
            with open(data_file, 'r') as file:
                self.total_received = float(file.read().strip())
                self.label_total_recv.setText(f"Total Downloaded: {self.total_received:.2f} MB")
        except FileNotFoundError:
            print("No saved data found. Starting with initial values.")

    def save_data(self):
        data_file = os.path.join(self.data_folder, 'data_usage.txt')
        with open(data_file, 'w') as file:
            file.write(f"{self.total_received:.2f}")

    def get_network_usage(self):
        net_io = psutil.net_io_counters()
        return net_io.bytes_sent, net_io.bytes_recv

    def update_usage(self):
        last_sent, last_recv = self.get_network_usage()

        while True:
            time.sleep(1)
            current_sent, current_recv = self.get_network_usage()
            data_sent = current_sent - last_sent
            data_recv = current_recv - last_recv

            data_sent_kbps = (data_sent * 8) / 1024  # Convert to Kbps
            data_recv_kbps = (data_recv * 8) / 1024  # Convert to Kbps

            self.total_received += data_recv / 1_024 / 1_024  # Convert bytes to MB

            last_sent, last_recv = current_sent, current_recv

            # Debugging print statements


            # Update labels with new data
            self.label_sent_kbps.setText(self.format_speed(data_sent_kbps, "Upload"))
            self.label_recv_kbps.setText(self.format_speed(data_recv_kbps, "Download"))
            self.label_total_recv.setText(f"Total Downloaded: {self.total_received:.2f} MB")

    def format_speed(self, speed_kbps, label):
        if speed_kbps > 1000:
            speed_mbps = speed_kbps / 1000
            return f"{label} Speed: {speed_mbps:.2f} Mbps"
        else:
            return f"{label} Speed: {speed_kbps:.2f} Kbps"

    def start_monitoring(self):
        monitoring_thread = threading.Thread(target=self.update_usage)
        monitoring_thread.daemon = True
        monitoring_thread.start()

    def closeEvent(self, event):
        self.save_data()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DataUsageMonitor()
    main_window.show()
    sys.exit(app.exec_())
