from gtts import gTTS
import speech_recognition as sr
import re
import time
import webbrowser
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
import requests
from pygame import mixer
import urllib.request
import urllib.parse
import json
import bs4


def talk(audio):
    "speaks audio passed as argument"

    print(audio)
    for line in audio.splitlines():
        text_to_speech = gTTS(text=audio, lang="en-uk")
        text_to_speech.save("audio.mp3")
        mixer.init()
        mixer.music.load("audio.mp3")
        mixer.music.play()


def myCommand():
    "listens for commands"
    # Initialize the recognizer
    # The primary purpose of a Recognizer instance is, of course, to recognize speech.
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("TARS is Ready...")
        r.pause_threshold = 1
        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source, duration=1)
        # listens for the user's input
        audio = r.listen(source)
        print("analyzing...")

    try:
        command = r.recognize_google(audio).lower()
        print("You said: " + command + "\n")
        time.sleep(2)

    # loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        print("Your last command couldn't be heard")
        command = myCommand()

    return command


def tars(command):
    errors = ["I don't know what you mean", "Excuse me?", "Can you repeat it please?"]
    "if statements for executing commands"

    # Search on Google
    if "open google and search" in command:
        reg_ex = re.search("open google and search (.*)", command)
        search_for = command.split("search", 1)[1]
        print(search_for)
        url = "https://www.google.com/"
        if reg_ex:
            subgoogle = reg_ex.group(1)
            url = url + "r/" + subgoogle
        talk("Okay!")
        driver = webdriver.Firefox(executable_path="/path/to/geckodriver")
        driver.get("http://www.google.com")
        search = driver.find_element_by_name("q")
        search.send_keys(str(search_for))
        search.send_keys(Keys.RETURN)  # hit return after you enter search text

    # Send Email
    elif "email" in command:
        talk("What is the subject?")
        time.sleep(3)
        subject = myCommand()
        talk("What should I say?")
        message = myCommand()
        content = "Subject: {}\n\n{}".format(subject, message)

        # init gmail SMTP
        mail = smtplib.SMTP("smtp.gmail.com", 587)

        # identify to server
        mail.ehlo()

        # encrypt session
        mail.starttls()

        # login
        mail.login("username_gmail", "password_gmail")

        # send message
        mail.sendmail("FROM", "TO", content)

        # end mail connection
        mail.close()

        talk("Email sent.")

    # search in wikipedia (e.g. Can you search in wikipedia apples)
    elif "wikipedia" in command:
        reg_ex = re.search("wikipedia (.+)", command)
        if reg_ex:
            query = command.split("wikipedia", 1)[1]
            response = requests.get("https://en.wikipedia.org/wiki/" + query)
            if response is not None:
                html = bs4.BeautifulSoup(response.text, "html.parser")
                title = html.select("#firstHeading")[0].text
                paragraphs = html.select("p")
                for para in paragraphs:
                    print(para.text)
                intro = "\n".join([para.text for para in paragraphs[0:3]])
                print(intro)
                mp3name = "speech.mp3"
                language = "en"
                myobj = gTTS(text=intro, lang=language, slow=False)
                myobj.save(mp3name)
                mixer.init()
                mixer.music.load("speech.mp3")
                mixer.music.play()
    elif 'stop' in command:
        mixer.music.stop()

    # Search videos on Youtube and play (e.g. Search in youtube believer)
    elif "youtube" in command:
        talk("Ok!")
        reg_ex = re.search("youtube (.+)", command)
        if reg_ex:
            domain = command.split("youtube", 1)[1]
            query_string = urllib.parse.urlencode({"search_query": domain})
            html_content = urllib.request.urlopen(
                "http://www.youtube.com/results?" + query_string
            )
            search_results = re.findall(
                r"href=\"\/watch\?v=(.{11})", html_content.read().decode()
            )
            # print("http://www.youtube.com/watch?v=" + search_results[0])
            webbrowser.open(
                "http://www.youtube.com/watch?v={}".format(search_results[0])
            )
            pass
    #  weather forecast in your city (e.g. weather in London)
    # please create and use your own API it is free
    elif "weather in" in command:
        city = command.split("in", 1)[1]   
        #openweathermap API
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=your_api_key&units=metric'.format(city)
        response = requests.get(url)
        data = response.json()
        #print(data)
        temp = data['main']['temp']
        round_temp = int(round(temp))
        talk('It is {} degree celcius in {}'.format(round_temp, city))
        time.sleep(3)


    elif "hello" in command:
        talk("Hello! I am TARS. How can I help you?")
        time.sleep(3)
    elif "who are you" in command:
        talk("I am one of four former U.S. Marine Corps tactical robots")
        time.sleep(3)
    else:
        error = random.choice(errors)
        talk(error)
        time.sleep(3)


talk("TARS activated!")

# loop to continue executing multiple commands
while True:
    time.sleep(4)
    tars(myCommand())
