import os, time, wave, pynput, pyttsx3, pyaudio

def say(word) :

    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()

def record(word):

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 24000
    CHUNK = 1024
    RECORD_SECONDS = 2
    WAVE_OUTPUT_FILENAME = word+".wav"
	 
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
    print("finished recording\n")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def get_words(p_words_file):

    with open(p_words_file, 'r') as words_file :
        words = words_file.read().split('\n')
    words = list(filter(len, words))
    words = list(filter(lambda x:x.isalnum(), words))
    return words

def main(p_words_file):

    words = get_words(p_words_file)
    global index
    if os.path.isfile("index") :
        with open("index",'r') as kept :
            index = int(kept.read())
        os.remove("index")
    index = 0

    def on_press(key):
        try : char = key.char
        except : char = None
        global index
        if char == 's' : # say for me
            say(words[index])
        elif char == 'r' : # record
            record(words[index])
        elif char == 'n' : # go to next next
            if index+1 >= len(words) :
                print("you done all your recordings succefully ")
                return
            index += 1
            print("Say>",words[index])
            print("press r for start recording")
        elif char == 'k' : # keep index for later
            with open("index",'w') as keep :
                keep.write(str(index))
        elif char == 'p' : # re record previous word
            index -= 1
            print("Say>",words[index])
            print("press r for start recording")
        elif char == 'e' : # to exit 
            exit(0)
        elif char == 'i' : # to manually set index
            index = int(input("index >"))

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
    print("Say>",words[index])
    print("press r for start recording")
    key_listener = pynput.keyboard.Listener(on_press= on_press)
    key_listener.start()
    key_listener.join()

if __name__ == '__main__' :
    main("infile.txt")
