import nfc
import csv
import os
from datetime import datetime
from gtts import gTTS
import tkinter as tk

class Attendance():
    def __init__(self):
        self.logs = []
        # read log.csv and add todays logs
        today = datetime.now().date()
        # create log file
        self.log_file_path = "{}.csv".format(today)
        os.system("touch {}".format(self.log_file_path))
        with open(self.log_file_path, "r") as f:
            for row in csv.reader(f):
                timestamp = row[0].strip(" ")
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").date()
                if timestamp == today:
                    self.logs.append(row[1])

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

    def on_connect(self, tag):
        # Service一覧の出力
        # for i in range(0x10000):
        #     area_or_service = tag.search_service_code(i)
        #     if area_or_service is None:
        #         break
        #     elif len(area_or_service) == 1:
        #         sc = area_or_service[0]
        #         print(nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f))
        #     elif len(area_or_service) == 2:
        #         area_code, area_last = area_or_service
        #         print("Area {0:04x}--{0:04x}".format(area_code, area_last))
        #         #    Random Service 68: write with key & read w/o key (0x1108 0x110B)
        #         #    Random Service 72: write with key & read w/o key (0x1208 0x120B)
        #         #    Random Service 76: write with key & read w/o key (0x1308 0x130B)

        # dump実行結果の出力
        # dumped = tag.dump()
        # for row in dumped:
        #     print(row)

        # read_without_encryptionを使えば特定アドレスだけdumpできそう
        # https://nfcpy.readthedocs.io/en/latest/modules/tag.html#nfc.tag.tt3.Type3Tag.read_without_encryption
        # sc1 = nfc.tag.tt3.ServiceCode(76, 0x1308)
        # print(tag.read_without_encryption([sc1]))

        target = tag.dump()[33]
        target = target.split("|")[1]
        student_number = target.split("002062")[0]
        if not student_number in self.logs:
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file_path, "a") as f:  # even if exception occurs, data will be saved
                writer = csv.writer(f)
                writer.writerow([timestamp, student_number])
            # self.student_number_to_mp3(student_number)
            # os.system("afplay greeting.mp3")
            self.logs.append(student_number)
            print(student_number)
            os.system("afplay ok.mp3")
        else:
            print("already registered")
            os.system("afplay already_registered.mp3")

    # with other card, dump data will be different and occur errors and die
    # need to check if scanned card is correct one
    def main(self):
        with nfc.ContactlessFrontend("usb") as clf:
            while True:
                try:
                    clf.connect(rdwr={'on-connect': self.on_connect})
                except nfc.tag.tt3.Type3TagCommandError:
                    print("error")

if __name__ == "__main__":
    attendance = Attendance()
    attendance.main()
