#this is to find how many audio files can be generated using pyttsx3
## by a single process at a single call
#this return <how_many_files>+2
#if return value is 1 or 0 => error

import sys

if len(sys.argv) == 1 :

    import subprocess

    # path for python.exe in windows and python.so in linux or environmental path
    python_path = "python3"

    count = 2
    max_count = -1

    while count < max_count or max_count == -1 :

        return_code = subprocess.call([python_path, sys.argv[0], str(count)])

        if return_code == 1 :
            #print("This can generate only",count,"audio files")
            exit(count+2)

        elif return_code-2 == count :
            #print("#> can generate",count,"audio files")
            count+=1

        elif return_code-2 < count :
            #print("This can generate only",return_code-2,"audio files")
            exit(return_code)

        else :
            exit(1)

count = int(sys.argv[1])

import pyttsx3, shutil, os
engine = pyttsx3.init()
try : shutil.rmtree("audios")
except FileNotFoundError : pass
os.mkdir("audios")

for i in range(count):
    engine.save_to_file("say something", os.path.join("audios",str(i)+'.mp3'))

engine.runAndWait()
engine.stop()

if len(os.listdir("audios")) == count :
    return_code = count+2
    for i, audio_file_name in enumerate(sorted(os.listdir("audios"))) :
        if os.path.getsize(os.path.join("audios",audio_file_name)) == 0 : # is null bytes
            return_code = i+2
            break
else :
    return_code = 1

exit(return_code)

