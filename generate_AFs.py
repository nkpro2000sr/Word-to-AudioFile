import pyttsx3, sys, os, time

engine = pyttsx3.init()
if len(sys.argv)>3 :
    try :
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[int(sys.argv[3])].id)
    except ValueError :
        engine.setProperty('voice', sys.argv[3])
dir_ = os.path.split(sys.argv[2])
if len(dir_[0]) :
    os.makedirs(dir_[0], exist_ok=True)
engine.save_to_file(sys.argv[1], sys.argv[2])
engine.runAndWait()

timeout = 1 # 1 sec
while not os.path.isfile(sys.argv[2]) and timeout > 0 :
    time.sleep(0.01)
    timeout -= 0.01
engine.stop()
if timeout <= 0 : exit(1)
