##This file contains the helper functions for brew_butler
from gtts import gTTS
import playsound
import datetime
import speech_recognition as sr
import os
import time
from tika import parser
import threading
import wget
import grabber
from requests import get
from bs4 import BeautifulSoup
import sys
import webbrowser
import urllib.parse
import urllib.request 




#sets up the mic for voice commands
r = sr.Recognizer()
mic = sr.Microphone()

#When called, uses a string input to create a gTTS file, codes that into an mp3 and then plays it.
def speak(text):
    tts = gTTS(text = text, lang = "en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
    

# Uses the datetime module to provide a greeting to user based on the time of day.
def greeting():
    now = datetime.datetime.now()
    current_time = now.hour
    if current_time > 16:
        text = "Good Evening, Henry."
        return text
    elif current_time > 12:
        text = "Good Afternoon, Henry."
        return text
    else:
        text = "Good Morning, Henry."
        return text

# prompts the user for a command and returns it as a string for the execute command function
def get_command():
    trys = 1
    try:
        print("trying")
        with mic as source:
            
            while True:
                try:
                    speak("What can I do for you?")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    print(command)
                    execute_command(command)
                    break
                except:
                    print("got the issue " + str(trys))
                    trys += 1
            return command
    except:
        if trys == 3:
            speak("I'm having trouble hearing you, please try again later.")
            return 1
        else:
            speak("I'm sorry, I didn't hear you. Please try again.")
            trys = trys + 1
            return 0

# parses the command given and operates on it based on what key words it finds. 
def execute_command(command):
    #sets the log name in case of a new note being added
    log = datetime.datetime.now()
    log_name = ("Brew day " + str(log.month) + "-" + str(log.day) + "-" + str(log.year))
    if "note" in command:
        with open(log_name, 'a') as notes:
            with mic as source:
                speak("Ok, you need me to take a note. Ready.")
                audio = r.listen(source)
                audio = r.recognize_google(audio)
                notes.write(str(log.hour) + ":" + str(log.minute) + "    " + str(audio) + "\n")

    # If the user input contains the word "timer"
    # Prompts user for how long timer will be, in minutes, and uses get_timer function
    # to decide how long to sleep then alerts user when timer has expired.  
    elif "timer" in command:
        with mic as source:
            speak("Ok you need a timer. Please state how long you'd like the timer to be.")
            audio = r.listen(source)
            audio = r.recognize_google(audio)
            timer_length = get_timer(audio)
        timer(timer_length)

    #uses grabber.py to scrape the url of the kit, downloads the pdf then saves it with the first two words of the recipe input to keep naming conventional for future parsing/manipulation.
    elif "recipe" in command or "instructions" in command:
        with mic as source:
            speak ("Alright, lets look up a recipe. Please give me the full name of the kit you'd like me to get the instructions for.")
            audio = r.listen(source)
            audio = r.recognize_google(audio)
            recipe = audio
            title = recipe.split()[0:2]
            title = "_".join(title)
            print("recipe: \n")
            print(recipe)
            kit_url = grabber.extract_or_all_grain(recipe)
            print("url \n")
            print(kit_url)
            response = get(kit_url)
            print("get url")
            print(response)
            page = response.text
            soup = BeautifulSoup(page, 'html.parser')
            link = soup.find("td", text = "Beer Recipe Kit Instructions").find_next_sibling("td")
            link_string = str(link)
            print(link_string)
            recipe_url = grabber.recipe_url_grabber(link_string)
            print("Downloading %s" % recipe_url)
            wget.download(recipe_url, (title + ".pdf"))
    elif "quit program" in command:
        sys.exit()
    elif "abv" in command:
        abv_calculator()           
# assists the execute_command function's timer elif
# by processing user's voice input and returning the length of time to sleep         
def get_timer(audio):
    words = audio.split()
    time = 0
    minutes = 0
    seconds = 0
    for word in words:
        if word == "minutes":
            index_of_minutes = words.index("minutes")
            minutes += int(words[index_of_minutes - 1])
            time += minutes * 60
        elif word == "one":
            minutes += 1
            time += 60
        elif word == "seconds":
            index_of_seconds = words.index("seconds")
            seconds += int(words[index_of_seconds - 1])
            time += seconds
        elif words == None:
            speak("Sorry I couldn't understand you, please try again.")
    speak("Ok your timer is set for " + str(minutes) + "minutes and " + str(seconds) + "seconds.")
    return time
    

# Controls the timer and prints the elapsed time to the console
# TODO: reverse it and make it print out remaining time? 
def timer(timer_length):
    seconds = 0
    minutes = 0
    original_time = timer_length
    while timer_length > -1:
        if minutes < 10 and seconds < 10:
            print("0" + str(minutes) + ":" + "0" + str(seconds))
        elif minutes >= 10 and seconds >= 10:
            print(str(minutes) + ":" + str(seconds))
        elif minutes >= 10 and seconds < 10:
            print(str(minutes) + ":0" + str(seconds))
        elif minutes < 10 and seconds >= 10:
            print("0" + str(minutes) + ":" + str(seconds))
        seconds += 1
        timer_length -= 1
        time.sleep(1)
        if seconds == 60:
            minutes += 1
            seconds = 0
    speak("Your" + str(int(original_time / 60)) + " minute and " +str(seconds - 1) + " second timer is complete")
    
#listens in the background for the user to
#call upon the voice command function then calls it for them.
#currently WIP 
def listen ():
    print("listen function start")
    print("trying")
    with mic as source:
        audio = r.listen(source)
        words = r.recognize_google_cloud(audio)
        words = words.lower()
        print(words)
        if "hey" in words:
            print("returning true")
            return True
        else:
            print("sleeping...")
            return False



#calculates abv and returns a string like (abv_total%ABV)
def abv_calculator():
    og = float(input("What is the original gravity?\n"))
    fg = float(input("What is the final gravity\n"))
    abv = (og-fg) * 131.25
    abv = round(abv, 2)
    abv = str(abv)
    abv = (abv + "% ABV")
    return abv

#These two equations allow the user to convert Liquid Malt Extract and Dry Malt Extract if they have to substitute.
#They return an int so it can be formatted elsewhere.
def lme_to_dme(lme):
    dme = lme * (36/43)
    dme = int(round(dme, 2))
    return dme
def dme_to_lme(dme):
    lme = dme * (43/36)
    lme = int(round(lme, 2))
    return lme

# Enters notes into brew log via the GUI

def gui_notes(note):
    log = datetime.datetime.now()
    log_name = ("Brew day " + str(log.month) + "-" + str(log.day) + "-" + str(log.year))
    with open(log_name, 'a') as notes:
        notes.write(str(log.hour) + ":" + str(log.minute) + "    " + str(note) + "\n")