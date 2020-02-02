import pyttsx3, sys, os, time

engine = pyttsx3.Engine()
voices = engine.getProperty('voices')
engine.setProperty('voice', sys.argv[3])
engine.save_to_file(sys.argv[1], sys.argv[2])
engine.runAndWait()
while not os.path.isfile(sys.argv[2]) : time.sleep(0.01)
