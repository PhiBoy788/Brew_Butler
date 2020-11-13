#!/usr/bin/env python3

# import order per pep8 https://www.python.org/dev/peps/pep-0008/#imports
# standard library imports
import os
import datetime
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

# installed library imports
from gtts import gTTS
import speech_recognition as sr
import playsound

# module level imports
import grabber
import helper

# used for timer sound
import winsound
duration = 1000  # milliseconds
freq = 440  # Hz


class Tab1(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.timer_obj = ' '

        # Note that we are *in* the Tab1 class, so we use plain 'self' as the master
        lbl = ttk.Label(self, text ="Timer")
        lbl.grid(column = 0, row = 0, padx = 30, pady = 30)

        # 2 lines not strictly required if unless you need the object later
        # but 2 lines are always preferred for readability
        # name 'btn' is generic, reuseable, throwaway name that I use. Could be anything.
        btn = ttk.Button(self, text ="Voice Command", command = self.get_command)
        btn.grid(column = 1, row = 1, padx = 30, pady = 30)

        ttk.Label(self, text = "Notes").grid(column = 2, row = 0, padx = 30, pady = 30)

        # 2 lines required here, because we want to use the Entry object later to get a value
        time_frame = tk.Frame(self)
        self.time_min = ttk.Entry(time_frame, width=5)
        self.time_min.pack(side=tk.LEFT)
        lbl=tk.Label(time_frame, text=":")
        lbl.pack(side=tk.LEFT)
        self.time_sec = ttk.Entry(time_frame, width=5)
        self.time_sec.pack(side=tk.LEFT)
        time_frame.grid(column = 0, row = 1, padx = 30, pady = 30)

        #note = str(ttk.Entry.get(self))
        self.notes = ttk.Entry(self)
        self.notes.grid(column = 2, row = 1, padx = 30, pady = 30)
        #print("note = " + note)

        self.timer_btn = ttk.Button(self, text ="Start", command = self.start_pressed)
        self.timer_btn.grid(column = 0, row = 2, padx = 30, pady = 30)

        btn = ttk.Button(self, text ="Log", command = self.log_pressed)
        btn.grid(column = 2, row = 2, padx = 30, pady = 30)

    def get_command(self):
        helper.get_command()

    def start_pressed(self):
        try:
            seconds = int(self.time_sec.get() or 0)
            minutes = int(self.time_min.get() or 0)
            self.timer(seconds + minutes*60)
        except ValueError:
            showerror("Error", "Please enter an integer number of seconds")

    def timer(self, seconds_left=0):
        minutes, seconds = divmod(seconds_left, 60)
        self.time_min.delete(0, tk.END)
        self.time_min.insert(tk.END, minutes)
        self.time_sec.delete(0, tk.END)
        self.time_sec.insert(tk.END, f"{seconds:0>2}")
        self.after_cancel(self.timer_obj)
        if seconds_left > 0:
            self.timer_obj = self.after(1000, self.timer, seconds_left-1)
        else:
            winsound.Beep(freq, duration)

    def log_pressed(self):
        current_time = datetime.datetime.now()
        log_name = ("Brew day " + str(current_time.month) + "-" + str(current_time.day) + "-" + str(current_time.year))
        with open(log_name, 'a') as log:
            log.write(str(current_time.hour) + ":" + str(current_time.minute) + "    " + self.notes.get() + '\n')
            self.notes.delete(0,'end')
            print('Wrote note to log file')

#This is the tab for calculations 
class Tab2(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        #Labels line the left hand side of the program
        ttk.Label(self, text ="ABV").grid(column = 0, row = 0, padx = 15, pady = 30)
        ttk.Label(self, text = "DME -> LME").grid(column = 0, row = 1, padx = 30, pady = 20)
        ttk.Label(self, text = "LME -> DME").grid(column = 0, row = 2, padx = 30, pady = 30)

        #These next 3 blocks of code define the ABV calculator portion of this tab.
        #There are two entry tabs for the user to input the original and final gravity, 
        #Then when the calculate button is pressed, it feeds that info into a function 
        #that calculates the abv and displays it formatted in the third box
        #TODO prevent users from inputting data into the 3rd box. 

        abv_mainframe = tk.Frame(self)
        abv_mainframe.grid(column = 1, row = 0, padx = 30, pady = 0)

        abv_labels = tk.Frame(abv_mainframe)
        ttk.Label(abv_labels, text = "OG").pack(side=tk.LEFT, padx = 20)
        ttk.Label(abv_labels, text = "FG").pack(side=tk.LEFT, padx = 10)
        ttk.Label(abv_labels, text = "ABV").pack(side=tk.LEFT, padx = 20)
        abv_labels.grid(column = 0, row = 0, padx = 0, pady = 0)

        abv_frame = tk.Frame(abv_mainframe)
        self.original_gravity = ttk.Entry(abv_frame, width=5)
        self.original_gravity.pack(side=tk.LEFT)
        lbl=tk.Label(abv_frame, text="  ")
        lbl.pack(side=tk.LEFT)
        self.final_gravity = ttk.Entry(abv_frame, width=5)
        self.final_gravity.pack(side=tk.LEFT)
        lbl=tk.Label(abv_frame, text="  ")
        lbl.pack(side=tk.LEFT)
        self.abv = ttk.Entry(abv_frame, width = 7)
        self.abv.pack(side = tk.LEFT)
        abv_frame.grid(column = 0, row = 1, padx = 30, pady = 5)
        calc_abv_btn = tk.Button(self, text = "Calculate", command = self.calculate_abv_pressed)
        calc_abv_btn.grid(column = 2, row = 0, padx = 30, pady = 0)
        


    #This checks that the user input info into both tabs properly
    def calculate_abv_pressed(self):
        try: 
            og = float(self.original_gravity.get())
            fg = float(self.final_gravity.get())
            self.calculate_abv(og,fg)
        except ValueError:
            showerror("Error", "Please enter both OG and FG")

    #This takes the og and fg values from the calculate_abv_pressed
    #function and operates on them to find the abv. 
    #It then formats it and puts a percentage sign at the end
    #Finally it inserts it into the third entry tab in the GUI
    def calculate_abv(self, og,fg):
        abv = (og-fg) * 131.25
        abv = round(abv, 2)
        abv = str(abv)
        abv = abv + "%"
        print(abv)
        self.abv.insert(0, abv)
        return

        

        


        



class App(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("Brew Butler")

        self.tabControl = ttk.Notebook(self)

        self.tab1 = Tab1(self.tabControl)
        self.tab2 = Tab2(self.tabControl)

        self.tabControl.add(self.tab1, text ='Home')
        self.tabControl.add(self.tab2, text ='Calculations')
        self.tabControl.pack(expand = 1, fill ="both", padx = 5)

def main():
    command_thread = threading.Thread(target=command)
    app = App()
    app.mainloop() # blocking. Program will not pass this line until the GUI is closed.

    return

    #helper.speak(helper.greeting())
    time.sleep(1)
    # Has the listen function run in the background like siri and can be called with the phrase "Hey Brew Butler".
    #while True:
        #if helper.listen() == True:
            #new_command = helper.get_command()
            #helper.execute_command(new_command)
        #else:
            #pass

def command():
    command = helper.get_command()
    helper.execute_command(command)
    command = ""




if __name__ == '__main__':
    main()

