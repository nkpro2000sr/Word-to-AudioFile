import os, sys, shutil, subprocess

from gtts import gTTS 
from pydub import AudioSegment as As

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))

def wta(infile= "infile.txt", outdir= "output",
        seq= [1,1,1], normalizer= [1,1,1],      #gtts,pyttsx3.v[0],pyttsx3.v[1]
        duer= 2000, rmold= False, max_AF_per_process= None, log_level= 20) :
    """ 
    to generate audio files for given words in $infile
    and save audio files in $outdir with subdirs names as words
    and each subdirs have files f.mp3, m.mp3, f1.mp3 based on $seq

    ### this function only works for MAC bacause of lack of support pyttsx3 in Windows & Linux
    ###> still you can use $seq[0] for f.mp3 in all platform

    $seq[0] : enable for f.mp3 (audio generated from google test-to-speach API)
    $seq[1] : enable for m.mp3 (audio genereted form system text-to-speach API)
    $seq[2] : enable for f1.mp3 (same as before(m.mp3) but have different voice)

    $normalizer is for making each audio files in same duration
    by adding silence at ends based on given total_duration_of_each_file $duer

    $normalizer : enable for noramalizing f.mp3 => F.mp3
    $normalizer : enable for noramalizing m.mp3 => M.mp3
    $normalizer : enable for noramalizing f1.mp3 => F1.mp3

    $rmold : enable to remove old files f.mp3, m.mp3, f1.mp3
    > best pratice is to call rmold function seperatly after normalizing is done

    $max_AF_per_process = max audio files can be created by singe process using pyttsx3 engine
    > this may vary for computers (100 may work for all systems)
    """
    if seq :
        with open(infile,"r") as words_file :
            words = words_file.read().replace('\n',' ').split()
            words = [''.join(filter(str.isalnum,x)) for x in words]
            words = list(filter(len,words))
        words = list(set(words))
        log.debug(words)
        log.info("no. of words = "+str(len(words)))
        words2 = []

        c_pyttsx3 = []
        p_python = "python3"
        p_pyttsx3_AFgen = "generate_AFs.py"
        p_words_file = "words"

        if max_AF_per_process == None :
            max_AF_per_process = subprocess.call([p_python, "test_pyttsx3_engine_inMAC.py"])
            max_AF_per_process-=2

        language = 'en' #language assignment
        for word in words :
            try:
                os.makedirs(os.path.join(outdir,word), exist_ok=True)
                if seq[0]==1 : #TODO add request_over exception
                    audio = gTTS(text=word, lang=language, slow=False)
                    audio.save(os.path.join(outdir,word,"f.mp3"))
                if seq[1]==1 :
                    c_pyttsx3.append(','.join(['0', word, os.path.join(outdir,word,"m.mp3")]))
                if seq[2]==1 :
                    c_pyttsx3.append(','.join(['1', word, os.path.join(outdir,word,"f1.mp3")]))
                if len(c_pyttsx3)==max_AF_per_process :
                    log.debug("calling",p_pyttsx3_AFgen,"with",str(len(c_pyttsx3)),"words")
                    with open(p_words_file,'w') as c_file :
                        c_file.write("\n".join(c_pyttsx3))
                    c_pyttsx3 = []
                    return_code = subprocess.call([p_python, p_pyttsx3_AFgen, p_words_file])
                    log.debug(p_pyttsx3_AFgen,"returned with",str(return_code))
            except FileExistsError:
                pass
            except :
                log.error("form audio generating",sys.exc_info())
            else:
                words2.append(word)
        if len(c_pyttsx3) :
            log.debug("calling",p_pyttsx3_AFgen,"with",str(len(c_pyttsx3)),"words")
            with open(p_words_file,'w') as c_file :
                c_file.write("\n".join(c_pyttsx3))
            c_pyttsx3 = []
            return_code = subprocess.call([p_python, p_pyttsx3_AFgen, p_words_file])
            log.debug(p_pyttsx3_AFgen,"returned with",str(return_code))

        log.debug(words2)
        log.info(len(words2))

    if type(normalizer)==str :
        words = os.listdir(normalizer)
        for word in words :
            audios = os.listdir(os.path.join(normalizer,word))
            for audio in audios :
                try:
                    sound = As.from_mp3(os.path.join(normalizer,word,audio))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        new_audio = audio.split('.')
                        new_audio[0] = new_audio[0].upper()
                        new_audio = '.'.join(new_audio)
                        sound.export(os.path.join(normalizer,word,new_audio), format='mp3')
                        if rmold : os.remove(os.path.join(normalizer,word,audio))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving", os.path.join(normalizer,word,audio), os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(normalizer,word,audio), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing", sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving", os.path.join(normalizer,word,audio), os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(normalizer,word,audio), os.path.join(outdir,"~Defects",word))

    elif type(normalizer)==list :
        if normalizer[0] :
            for word in words2:
                try:
                    sound=As.from_mp3(os.path.join(outdir,word,"f.mp3"))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(outdir,word,"F.mp3"), format='mp3')
                        if rmold : os.remove(os.path.join(outdir,word,"f.mp3"))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving", os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing f.mp3", sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving", os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~Defects",word))
            log.info("done normalizing all f.mp3")
        if normalizer[1] :
            for word in words2:
                try:
                    sound=As.from_mp3(os.path.join(outdir,word,"m.mp3"))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(outdir,word,"M.mp3"), format='mp3')
                        if rmold : os.remove(os.path.join(outdir,word,"m.mp3"))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving", os.path.join(outdir,word,"m.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,"m.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing m.mp3", sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving", os.path.join(outdir,word,"m.mp3"), os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,"m.mp3"), os.path.join(outdir,"~Defects",word))
            log.info("done normalizing all f.mp3")
        if normalizer[2] :
            for word in words2:
                try:
                    sound=As.from_mp3(os.path.join(outdir,word,"f1.mp3"))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(outdir,word,"F1.mp3"), format='mp3')
                        if rmold : os.remove(os.path.join(outdir,word,"f1.mp3"))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving", os.path.join(outdir,word,"f1.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,"f1.mp3"), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing f1.mp3", sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving", os.path.join(outdir,word,"f1.mp3"), os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,"f1.mp3"), os.path.join(outdir,"~Defects",word))
            log.info("done normalizing all f.mp3")

def rmold (outdir= "output", files =["f.mp3","m.mp3","f1.mp3"], move= False):
    """
    to remove each files (elements of $files)
    form all subdirs of $outdir
    """
    words = os.listdir(outdir)
    for word in words:
        if not os.path.isdir(os.path.join(outdir,word)) :
            log.error(outdir,word,"is not a dir")
            continue
        for file in files:
            if not move:
                try:
                    os.remove(os.path.join(outdir,word,file))
                except:
                    log.error("not able to delete",outdir,word,file)
            else:
                try:
                    os.makedirs(os.path.join(move,word), exist_ok=True)
                    shutil.move(os.path.join(outdir,word,file), os.path.join(move,word))
                except:
                    log.error("not able to move",outdir,word,file)

def rmempty (outdir= "output"):
    """
    to remove all empty subdirs of $oudir
    """
    words = os.listdir(outdir)
    for word in words:
        if not os.path.isdir(os.path.join(outdir,word)) :
            log.error(outdir,word,"is not a dir")
            continue
        try:
            os.rmdir(os.path.join(outdir,word))
        except:
            pass

