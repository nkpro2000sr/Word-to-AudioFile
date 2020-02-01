import sys
if len(sys.argv) > 1 :
    p_data_file = sys.argv[1]
else :
    p_data_file = "words"

with open(p_data_file, 'r') as data_file :
    datas = data_file.read().split('\n')

datas_v0, datas_v1 = [], []
for data in datas :
    if data[0] == '0' :
        datas_v0.append(data.split(',')[1:])
    elif data[0] == '1' :
        datas_v1.append(data.split(',')[1:])

import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')

engine.setProperty('voice', voices[0].id)
for data in datas_v0 :
    engine.save_to_file(data[0], data[1])
engine.runAndWait()

engine.setProperty('voice', voices[1].id)
for data in datas_v1 :
    engine.save_to_file(data[0], data[1])
engine.runAndWait()

engine.stop()
