import time
import random
import argparse
import serial

def run(port, baudrate):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        print(f"Sending to {port} @ {baudrate}bps. Ctrl+C to stop.")
        try:
            while True:
                
                value = random.uniform(0, 100)
                line = f"{value:.3f}\n"
                ser.write(line.encode('utf-8'))
                
                print("Sent:", line.strip())
                time.sleep(1)  
        except KeyboardInterrupt:
            print("Stopped sender.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port to write to (e.g. COM4 or /dev/pts/4)")
    parser.add_argument("--baud", default=9600, type=int)
    args = parser.parse_args()
    run(args.port, args.baud)
