from gtts import gTTS
import os
import speech_recognition as sr
import datetime
import helper
import time
import playsound
import threading
import grabber


def main():
    command_thread = threading.Thread(target=command)
    log_name = datetime.datetime.now()
    log_name = ("Brew day " + str(log_name.month) + "-" + str(log_name.day) + "-" + str(log_name.year))
    log = open(log_name, 'a')
    command_thread.start()
    #helper.speak(helper.greeting())

    





    log.close()

def command():
    command = helper.get_command()
    helper.execute_command(command)
    command = ""


main()