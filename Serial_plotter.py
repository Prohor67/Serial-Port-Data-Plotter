# serial_plotter.py
import sys
import csv
import time
from collections import deque
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import serial
import serial.tools.list_ports

class SerialReaderThread(QtCore.QThread):
    new_value = QtCore.pyqtSignal(float)
    status = QtCore.pyqtSignal(str)

    def __init__(self, port, baud=9600, parent=None):
        super().__init__(parent)
        self.port = "COM4"
        self.baud = baud
        self._running = False
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self._running = True
            self.status.emit(f"Opened {self.port} @ {self.baud}")
        except Exception as e:
            self.status.emit(f"Error opening port: {e}")
            return

        while self._running:
            try:
                if self.ser.in_waiting:
                    raw = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if raw:
                        
                        try:
                            parts = raw.split(',')
                            val = float(parts[0])
                            self.new_value.emit(val)
                        except Exception:
                            
                            self.status.emit(f"Bad data: {raw}")
    
                self.msleep(200)
            except Exception as e:
                self.status.emit(f"Serial read error: {e}")
                break

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.status.emit("Port closed")
        except Exception:
            pass

    def stop(self):
        self._running = False
        self.wait(1000)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Live Plotter")
        self.resize(900, 600)

        # Widgets
        self.port_combo = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("Refresh ports")
        self.baud_input = QtWidgets.QLineEdit("9600")
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.start_btn = QtWidgets.QPushButton("Start")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.export_btn = QtWidgets.QPushButton("Export CSV")
        self.status_label = QtWidgets.QLabel("Status: Idle")
        self.value_label = QtWidgets.QLabel("Latest: --")

        # Plot
        self.plot_widget = pg.PlotWidget(title="Live readings")
        self.plot_curve = self.plot_widget.plot([], pen=pg.mkPen(width=2))
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Sample')

        # Layout
        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(QtWidgets.QLabel("Port:"))
        top_row.addWidget(self.port_combo)
        top_row.addWidget(self.refresh_btn)
        top_row.addWidget(QtWidgets.QLabel("Baud:"))
        top_row.addWidget(self.baud_input)
        top_row.addWidget(self.connect_btn)
        top_row.addWidget(self.start_btn)
        top_row.addWidget(self.stop_btn)
        top_row.addWidget(self.export_btn)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.plot_widget)
        info_row = QtWidgets.QHBoxLayout()
        info_row.addWidget(self.value_label)
        info_row.addStretch()
        info_row.addWidget(self.status_label)
        main_layout.addLayout(info_row)

        container = QtWidgets.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Data buffer
        self.buffer = deque(maxlen=300)  # keep last 300 points
        self.running = False
        self.reader = None
        self.csv_file = None
        self.csv_writer = None

        # Connect signals
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.toggle_connect)
        self.start_btn.clicked.connect(self.start_plotting)
        self.stop_btn.clicked.connect(self.stop_plotting)
        self.export_btn.clicked.connect(self.export_csv)

        # initial
        self.refresh_ports()
        self.update_ui_state(disconnected=True)

        # Timer to refresh plot on UI thread (1Hz)
        self.ui_timer = QtCore.QTimer()
        self.ui_timer.setInterval(1000)  
        self.ui_timer.timeout.connect(self.refresh_plot)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)
        if self.port_combo.count() == 0:
            self.port_combo.addItem("No ports found")

    def toggle_connect(self):
        if self.reader and self.reader.isRunning():
            # disconnect
            self.stop_plotting()
            self.reader.stop()
            self.reader = None
            self.update_ui_state(disconnected=True)
        else:
            port = self.port_combo.currentText()
            try:
                baud = int(self.baud_input.text())
            except:
                baud = 9600
            self.reader = SerialReaderThread(port, baud)
            self.reader.new_value.connect(self.on_new_value)
            self.reader.status.connect(self.set_status)
            self.reader.start()
            self.update_ui_state(disconnected=False)

    def start_plotting(self):
        if not self.reader:
            self.set_status("Not connected")
            return
        self.running = True
        # open csv
        ts = int(time.time())
        filename = f"serial_readings_{ts}.csv"
        self.csv_file = open(filename, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["timestamp", "value"])
        self.set_status("Started plotting")
        self.ui_timer.start()

    def stop_plotting(self):
        self.running = False
        self.ui_timer.stop()
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
            self.set_status("Stopped plotting and saved CSV")
        else:
            self.set_status("Stopped plotting")

    def export_csv(self):
        if not self.buffer:
            self.set_status("No data to export")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "readings.csv", "CSV files (*.csv)")
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["index", "value"])
            for i, v in enumerate(self.buffer):
                w.writerow([i, v])
        self.set_status(f"Exported to {path}")

    @QtCore.pyqtSlot(float)
    def on_new_value(self, val):
        # called from reader thread via signal
        self.buffer.append(val)
        self.value_label.setText(f"Latest: {val:.3f}")
        if self.running and self.csv_writer:
            self.csv_writer.writerow([time.time(), val])

    def refresh_plot(self):
        data = list(self.buffer)
        if data:
            self.plot_curve.setData(data)

    @QtCore.pyqtSlot(str)
    def set_status(self, msg):
        self.status_label.setText("Status: " + msg)

    def update_ui_state(self, disconnected=False):
        self.connect_btn.setEnabled(disconnected)
        self.connect_btn.setText("Connect" if disconnected else "Disconnect")
        self.start_btn.setEnabled(not disconnected)
        self.stop_btn.setEnabled(not disconnected)
        self.refresh_btn.setEnabled(disconnected)
        self.port_combo.setEnabled(disconnected)
        self.baud_input.setEnabled(disconnected)

    def closeEvent(self, event):
        # clean up
        try:
            if self.reader and self.reader.isRunning():
                self.reader.stop()
        except:
            pass
        try:
            if self.csv_file:
                self.csv_file.close()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
