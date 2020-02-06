import os, time, wave, pynput, pyttsx3, pyaudio

def say(word) :

    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()

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
    print("\nfinished recording\n")

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

def record(infile= "infile.txt", outdir= "output", duer= 2000, sep= -1):
    """
    $infile : file contains words to be recorded
    $outdir : directory where the voices are stored
    $duer : duration of each words to be recorded (in milliseconds)
    $sep : sep for spliting words from infile (-1 => sep = AllWhiteSpaces)
    """

    words = get_words(infile, sep)
    global index
    index = 0
    if os.path.isfile("index") :
        with open("index",'r') as kept :
            index = int(kept.read())
            print("index",index,"is restored")
        os.remove("index")

    print("""
welcome to continous_WordRecorder !
and thanking you for giving your voice for dataset collection.
this app supports diffent key events :
1. 's' : if you don't know pronunciation you can ask for help by pressing this key
2. 'r' : for start recording and save to file
3. 'n' : to proceed next word
4. 'k' : to save current index for later use (it will be restored automatically once)
5. 'p' : to repeat previous word
6. 'e' : to exit
7. 'i' : to manually set index
""")

    name = input("please enter your name : ")
    print(str(index)+". Say>",words[index])
    print("press r for start recording")

    def on_press(key):
        try : char = key.char
        except : char = None
        global index
        if char == 's' : # say for me
            say(words[index])
        elif char == 'r' : # record
            record_audio(words[index], duer, outdir, name)
        elif char == 'n' : # go to next next
            if index+1 >= len(words) :
                print("you done all your recordings succefully :)")
                return
            index += 1
            print(str(index)+". Say>",words[index])
            print("press r for start recording")
        elif char == 'k' : # keep index for later
            with open("index",'w') as keep :
                keep.write(str(index))
            print("index",index,"saved in index file")
        elif char == 'p' : # re record previous word
            index -= 1
            print("Say>",words[index])
            print("press r for start recording")
        elif char == 'e' : # to exit
            exit(0)
        elif char == 'i' : # to manually set index
            index = int(input("index >"))

    key_listener = pynput.keyboard.Listener(on_press= on_press)
    key_listener.start()
    key_listener.join()

if __name__ == '__main__' :
    record()
