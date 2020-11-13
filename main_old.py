from gtts import gTTS
import os
import speech_recognition as sr
import datetime
import helper
import time
import playsound
import threading
import grabber
import tkinter as tk
from tkinter import ttk


class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title("TBD")
        self.tabControl = ttk.Notebook(self.root) 
  
        self.tab1 = ttk.Frame(self.tabControl) 
        self.tab2 = ttk.Frame(self.tabControl) 
  
        self.tabControl.add(self.tab1, text ='Home') 
        self.tabControl.add(self.tab2, text ='Calculations') 
        self.tabControl.pack(expand = 1, fill ="both", padx = 5) 
  
        ttk.Label(self.tab1,  
                text ="Timer").grid(column = 0, row = 0, padx = 30, pady = 30)
                   
        ttk.Button(self.tab1, 
                text ="Voice Command", command = helper.get_command).grid(column = 1, row = 1, padx = 30, pady = 30)

        ttk.Label(self.tab1,
        text = "Notes").grid(column = 2, row = 0, padx = 30, pady = 30)

        ttk.Entry(self.tab1).grid(column = 0, row = 1, padx = 30, pady = 30)

        #time = int(ttk.Entry.get(self))
        #print("time = " + time)

        ttk.Entry(self.tab1).grid(column = 2, row = 1, padx = 30, pady = 30)
        
        #note = str(ttk.Entry.get(self))

        #print("note = " + note)
        
        ttk.Button(self.tab1, 
                text ="Start", command = lambda:[ttk.Entery.get(), helper.timer(time)]).grid(column = 0, row = 2, padx = 30, pady = 30)

        ttk.Button(self.tab1, 
                text ="Log", command = lambda: [helper.gui_notes(note)]).grid(column = 2, row = 2, padx = 30, pady = 30)

        self.root.mainloop()


app = App()
def main():
    command_thread = threading.Thread(target=command)
    log_name = datetime.datetime.now()
    log_name = ("Brew day " + str(log_name.month) + "-" + str(log_name.day) + "-" + str(log_name.year))
    log = open(log_name, 'a')
    
    #helper.speak(helper.greeting())
    time.sleep(1)
    # Has the listen function run in the background like siri and can be called with the phrase "Hey Brew Butler".
    #while True:
        #if helper.listen() == True:
            #new_command = helper.get_command()
            #helper.execute_command(new_command)
        #else:
            #pass

    





    log.close()

def command():
    command = helper.get_command()
    helper.execute_command(command)
    command = ""



main()
