import nfc
import csv
import sys
import os
import time
from datetime import datetime
from gtts import gTTS
import tkinter as tk

class Attendance():
    def __init__(self):
        while True:
            time.sleep(1)
            try:
                self.clf = nfc.ContactlessFrontend("usb")
                break
            except OSError:
                pass # try again

        print("found reader device")
        self.logs = []
        # read log.csv and add todays logs
        today = datetime.now().date()
        # create log file
        self.log_file_path = "/media/keitaro/attendance/{}.csv".format(today)
        os.system("touch {}".format(self.log_file_path))
        with open(self.log_file_path, "r") as f:
            for row in csv.reader(f):
                timestamp = row[0].strip(" ")
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").date()
                if timestamp == today:
                    self.logs.append(row[1])

    def unmount(self):
        path = "/media/keitaro/attendance"
        os.system("sudo umount {}".format(path))
        os.system("sudo shutdown now")
         
    def student_number_to_mp3(self, student_number):
        # ask for data
        table = {}
        try:
            name = table[student_number]
        except KeyError:
            name = ""
        speech_text = "good morning {}".format(name)
        engine = gTTS(text=speech_text, lang="en", slow=False)
        engine.save("greeting.mp3")

    # with other card, dump data will be different and occur errors and die
    # need to check if scanned card is correct one
    def main(self):
        #f = open(self.log_file_path, "a") # even if exception occurs, data will be saved
        #writer = csv.writer(f)
        while True:
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
                target = tag.dump()[33]
                target = target.split("|")[1]
                student_number = target.split("002062")[0]

                # close attendance
                """
                if student_number == "72047937":
                    print("close ID found")
                    break
                """

                if not student_number in self.logs:
                    timestamp = datetime.now()
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    f = open(self.log_file_path, "a")
                    writer = csv.writer(f)
                    writer.writerow([timestamp, student_number])
                    f.close()
                    #self.student_number_to_mp3(student_number)
                    self.logs.append(student_number)
                    print(student_number)
                    os.system("mpg123 /home/keitaro/Desktop/attendance/ok.mp3 > /dev/null")
                else:
                    print("already registered")
                    os.system("mpg123 /home/keitaro/Desktop/attendance/already_registered.mp3 > /dev/null")
            except nfc.tag.tt3.Type3TagCommandError:
                print("error")

if __name__ == "__main__":
    media_path = "/media/keitaro/attendance"
    print("wait for removal media...")
    while True:
        media_check = os.path.exists(media_path)
        if media_check:
            break
    print("media found")
    os.system("mpg123 /home/keitaro/Desktop/attendance/ok.mp3")
        
    attendance = Attendance()
    attendance.main()
