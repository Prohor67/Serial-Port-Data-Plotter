# Serial Data Streamer & Live Plotter

A Python‑based **real‑time serial data visualization system** that generates, transmits, and plots sensor‑like data using **PyQt5** and **PyQtGraph**.  

This project demonstrates a full pipeline — from **data generation** and **serial communication** to **graphical live plotting** and **CSV logging**.

***

## ⚙️ Project Overview

This repository contains two main Python scripts:

1. **`Data_sender.py`** – simulates live sensor data and transmits it via a serial port.  
2. **`Serial_plotter.py`** – receives, plots, and logs the incoming serial data through a PyQt5 GUI dashboard.

Together, they simulate how data flows between a sensor node and a visualization dashboard.

***

## 🧠 How It Works

### 1. `Data_sender.py`
This script acts as a **virtual sensor** that sends random numeric values (within 0–100) every second to a specified serial port.

**Main Components:**
- **Serial Connection**: Opens a serial port using the `pyserial` library.  
- **Random Data Generation**: Uses `random.uniform()` to generate continuous floating‑point numbers.  
- **Data Transmission**: Writes each new reading to the serial buffer as a line (`{value}\n`).  
- **Command-Line Arguments**:  
  - `--port`: Specify the COM or virtual serial port (e.g., `COM4`, `/dev/pts/4`).  
  - `--baud`: Define the baud rate (default: `9600`).  

**Core Function:**
- `run(port, baudrate)`: Handles initialization, data writing, and error handling.

**Loop Behavior:**
Each second:
1. Generates a random float →  
2. Encodes and sends over serial →  
3. Prints the value in the terminal →  
4. Waits 1 second before sending the next reading.

📟 Example execution:
```bash
python Data_sender.py --port COM4 --baud 9600
```

***

### 2. `Serial_plotter.py`
This GUI-based application dynamically plots the incoming serial data stream.

**Primary Libraries Used:**
- **PyQt5** – Handles GUI structure, widgets, and multi‑threading.  
- **PyQtGraph** – For fast and responsive data plotting.  
- **PySerial** – For serial communication.  
- **CSV module** – For saving readings.

***

### 2.1 Serial Reader (Background Thread)
Class: `SerialReaderThread(QThread)`  
- Runs in a dedicated thread to avoid GUI freezing.  
- Constantly listens to the specified serial port for new lines.  
- Emits each valid reading (`float`) to the main GUI thread using PyQt signals.  
- Gracefully handles serial connection errors and closes safely on exit.

**Key Signals:**
- `new_value`: Sends the parsed float value to UI.  
- `status`: Updates the status label with connection logs or errors.

***

### 2.2 GUI Dashboard (MainWindow)

**Features:**
- Real‑time plotting of the latest serial readings.  
- Start/Stop recording functions.  
- Export data to CSV.  
- Dynamic port listing and baud rate selection.  
- Live numeric display of the most recent reading.  
- Automatic refresh every 1 second.

**UI Components:**
- Top row: Port selection, baud rate, refresh, connect/disconnect buttons.  
- Center: PyQtGraph live chart.  
- Bottom: Real‑time status updates and latest value display.

**Core Methods:**
- `refresh_ports()`: Detects available COM ports.  
- `toggle_connect()`: Connects/disconnects to serial reader threads.  
- `start_plotting()`: Starts updating both the graph and the CSV file.  
- `stop_plotting()`: Stops live updates and closes the CSV file safely.  
- `export_csv()`: Manually export the buffer to a chosen CSV file.  
- `on_new_value()`: Receives each emitted float from the reader and adds it to the buffer.  
- `refresh_plot()`: Updates the graph curve every second using the buffered data.  

All signals, buttons, and connections ensure that user interaction never stalls the serial reading process.

***

### 2.3 Data Recording and Storage
- Data is stored in both memory (a **deque** buffer of 300 latest points) and in a **CSV log file**.
- Each CSV file is timestamped (e.g., `serial_readings_1729779672.csv`).
- Every line contains:
  ```
  timestamp, value
  ```

***

## 🧩 Project Flow Summary

| Step | Action | Script |
|------|--------|--------|
| 1 | Simulate sensor data | `Data_sender.py` |
| 2 | Send values over serial port | `Data_sender.py` |
| 3 | Read data via serial connection | `Serial_plotter.py` |
| 4 | Display values and live plot | `Serial_plotter.py` |
| 5 | Save logs as `.csv` | `Serial_plotter.py` |

***

## 📊 Example Output

Below is a sample output:
- **Graph Window:**
- 
  <img width="898" height="629" alt="image" src="https://github.com/user-attachments/assets/463f2ce5-2643-4aae-91f0-1ec940d0baf2" />

- **CSV File:**
- 
<img width="357" height="491" alt="image" src="https://github.com/user-attachments/assets/99794af0-2009-44d9-a8a1-cc183b61d39a" />


```
serial_readings_1729779672.csv
timestamp,value
1729779673.321,72.483
1729779674.325,68.194
1729779675.330,75.919
...
```

***

## 🔧 Requirements

Install dependencies before running:

```bash
pip install pyqt5 pyqtgraph pyserial
```

***

## 🚀 Running the System

1. Start the data sender:
   ```bash
   python Data_sender.py --port COM4 --baud 9600
   ```

2. Launch the plotter GUI:
   ```bash
   python Serial_plotter.py
   ```

3. Select the same COM port (`COM4`) and press **Connect** → **Start**.  
   You’ll instantly see live data updates in the graph.

4. Press **Stop** to end logging, or **Export CSV** to manually save data.

***

## 💡 Concepts Demonstrated
- Thread‑safe serial communication in PyQt5.  
- Handling GUI updates with signals and slots.  
- Real‑time data visualization using PyQtGraph.  
- Proper resource cleanup (serial port, file handles).  
- Modular code design separating sender, receiver, and visualization logic.

***

## 🖼️ Files Included
- `Data_sender.py` – random data source via serial.  
- `Serial_plotter.py` – GUI visualizer and logger.  
