import csv
import sys
import os
import time
import logging
import RPi.GPIO as GPIO
from datetime import datetime
import nfc
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s", filename="/home/keitaro/Desktop/attendance/test_log.log")


class Attendance():
    def __init__(self):
        # GPIO settings
        self.ready_state_pin = 11
        self.attend_state_pin = 13
        self.buzzer = 15
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.ready_state_pin, GPIO.OUT)
        GPIO.setup(self.attend_state_pin, GPIO.OUT)
        GPIO.setup(self.buzzer, GPIO.OUT)

        self.admins = ["72047937"]
        
        today = datetime.now().date()
        self.log_file_path = "/home/keitaro/Desktop/attendance/log/{}.csv".format(today)
        if not os.path.exists(self.log_file_path):
            os.system(self.log_file_path)
        self.log = []
    
    def ready(self):
        GPIO.output(self.buzzer, 1)
        time.sleep(0.1)
        GPIO.output(self.buzzer, 0)
        GPIO.output(self.ready_state_pin, 1)

    def attend(self):
        GPIO.output(self.attend_state_pin, 1)
        GPIO.output(self.buzzer, 1)
        time.sleep(0.1)
        GPIO.output(self.attend_state_pin, 0)
        GPIO.output(self.buzzer, 0)

    def close_system(self):
        for i in range(3):
            GPIO.output(self.attend_state_pin, 1)
            GPIO.output(self.buzzer, 1)
            time.sleep(0.1)
            GPIO.output(self.attend_state_pin, 0)
            GPIO.output(self.buzzer, 0)
            time.sleep(0.05)
        GPIO.output(self.ready_state_pin, 0)

    def already_registered(self):
        for i in range(2):
            GPIO.output(self.attend_state_pin, 1)
            GPIO.output(self.buzzer, 1)
            time.sleep(0.1)
            GPIO.output(self.attend_state_pin, 0)
            GPIO.output(self.buzzer, 0)
            time.sleep(0.05)

    def on_connect(self, tag):
        sc = nfc.tag.tt3.ServiceCode(68, 0x0b)
        bc = nfc.tag.tt3.BlockCode(1, service=0)
        data_num = tag.read_without_encryption([sc], [bc])
        data_num = data_num.decode("shift_jis")
        student_id = data_num[:8]
        print(student_id)
        timestamp = datetime.now()
        if student_id in self.log:
            print("Already Registered")
            self.already_registered()
        else:
            with open(self.log_file_path, "a") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, student_id])
            print("attend")
            self.attend()
            self.log.append(student_id)

        if student_id in self.admins:
            print("exit")
            self.close_system()
            sys.exit(0)

        return True

    def battery_check(self):
        pass

    def main(self):
        while True:
            time.sleep(1)
            try:
                clf = nfc.ContactlessFrontend("usb")
                break
            except OSError:
                print("OSError")
                pass
        print("reader device found")
        self.ready()
        
        # mainloop
        while True:
            self.battery_check()
            logging.info("mainloop started")
            try:
                logging.info("tag found")
                tag = clf.connect(rdwr={'on-connect': self.on_connect})
            except nfc.tag.tt3.Type3TagCommandError:
                print("error")

if __name__ == "__main__":
    attendance = Attendance()
    attendance.main()
