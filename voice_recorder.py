import os, sys, time, pynput, pyaudio, wave
import pyttsx3; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

def say_0(word): #pyttsx3 #default

    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()

def say_1(word): #gtts

    import gtts, io, pygame; pygame.mixer.init()
    tts = gtts.gTTS(text=word, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()

def record_audio(word, duer, outdir, name):

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 24000
    CHUNK = 1024
    RECORD_SECONDS = duer/1000
    WAVE_OUTPUT_FILENAME = os.path.join(outdir,word,name+".wav")

    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)) :
        print("|>",end='')
        data = stream.read(CHUNK)
        frames.append(data)
    print("\nfinished recording")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    os.makedirs(os.path.split(WAVE_OUTPUT_FILENAME)[0], exist_ok=True)
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def get_words(p_words_file, sep):

    with open(p_words_file, 'r') as words_file :
        if sep == -1 : words = words_file.read().split()
        else : words = words_file.read().split(sep)
    words = list(filter(len, words))
    words = list(filter(lambda x:x.isalnum(), words))
    return words

def get_unfinished_words(outdir, words, name):

    unfinished_words = []
    for word in words :
        if not os.path.exists(os.path.join(outdir, word, name+".wav")) :
            unfinished_words.append(word)
    return unfinished_words

def record(infile= "infile.txt", outdir= "output", duer= 2000, sep= -1, speech= 0):
    """
    $infile : file contains words to be recorded
    $outdir : directory where the voices are stored
    $duer : duration of each words to be recorded (in milliseconds)
    $sep : sep for spliting words from infile (-1 => sep = AllWhiteSpaces)
    """

    global words, index, updated
    words = get_words(infile, sep)
    index = 0
    updated = False #whether words list is updated or not
    if os.path.isfile("index") :
        with open("index",'r') as kept :
            index = int(kept.read())
            print("index",index,"is restored")
        os.remove("index")

    print("""Welcome to continous_WordRecorder !
and thanking you for giving your voice for dataset collection.
this app supports diffent key events :
1. 's' : if you don't know pronunciation you can ask for help by pressing this key
2. 'r' : for start recording and save to file
3. 'n' : to proceed next word
4. 'k' : to save current index for later use (it will be restored automatically once)
5. 'p' : to repeat previous word
6. 'u' : to automatically update words list with unfinished words
7. 'i' : to manually set index
8. 'd' : to disable key event listener
         you can enable it by pressing enter in this window
9. 'e' : to exit

<<Important>>
(:0) please disable key event listener while doing other jobs (see 8. <above>).
(:0) since it listens globally it may responce for your key events in other windows.
""")

    name = input("please enter your name : ")
    print()
    print(str(index)+". Say>",words[index])
    print("press r for start recording")

    def on_press(key):
        try : char = key.char
        except : char = None
        global words, index, updated
        if char == 's' : # say for me
            if speech == 1 : say_1(words[index])
            else : say_0(words[index])
        elif char == 'r' : # record
            record_audio(words[index], duer, outdir, name)
        elif char == 'n' : # go to next word
            if index+1 >= len(words) :
                print("you reached the END ;)")
                unfinished_words = get_unfinished_words(outdir, words, name)
                if len(unfinished_words):
                    print("you have some unfinished words.")
                    print("press `u` to update words list with unfinished words")
                else:
                    print("you done all your recordings succefully :)")
                return
            index += 1
            print()
            print(str(index)+". Say>",words[index])
            print("press r for start recording")
        elif char == 'k' : # keep index for later
            if updated :
                print("since words list is updated keep_index is disabled")
                print("your current index in updated words list is",index)
                return
            with open("index",'w') as keep :
                keep.write(str(index))
            print("index",index,"saved in index file")
        elif char == 'p' : # go to previous word
            """
            if abs(index) >= len(words) :
                print("you reached the END ;)")
                unfinished_words = get_unfinished_words(outdir, words, name)
                if len(unfinished_words):
                    print("you have some unfinished words.")
                    print("press `u` to update words list with unfinished words")
                else:
                    print("you done all your recordings succefully :)")
                return
            """
            if index == 0 :
                print("you reached top `^^^^^`")
                return
            
            index -= 1
            print()
            print(str(index)+". Say>",words[index])
            print("press r for start recording")
        elif char == 'u' : # to update unfinished words
            unfinished_words = get_unfinished_words(outdir, words, name)
            if len(unfinished_words):
                words =  unfinished_words
                index = 0
                updated = True
                print("words list is updated.")
                print("currently you have only",len(words),"words.")
            else:
                print("you finished all the words :)")
            print()
            print(str(index)+". Say>",words[index])
            print("press r for start recording")
        elif char == 'i' : # to manually set index
            sys.stdin.flush()
            index = int(input("index >"))
            print()
            print(str(index)+". Say>",words[index])
            print("press r for start recording")
        elif char == 'd' :
            sys.stdin.flush()
            input()
        elif char == 'e' : # to exit
            sys.stdin.flush()
            if input("type 'exit\\n' to EXIT\nor 'dont\\n' to skip\n").find("exit") != -1 :
                sys.exit(0)
            else :
                return

    key_listener = pynput.keyboard.Listener(on_press= on_press)
    key_listener.start()
    key_listener.join()

if __name__ == '__main__' :
    record(speech=0)
#pyinstaller -F voice_recorder.py --hidden-import pyttsx3.drivers --hidden-import pyttsx3.drivers.sapi5 --exclude pygame -i icon.ico
