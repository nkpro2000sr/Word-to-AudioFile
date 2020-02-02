import os, sys, shutil, subprocess, logging

from gtts import gTTS
import pyttsx3
from pydub import AudioSegment as As

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.INFO)

def _get_voices(seq):
    seq = list(seq)
    if 0 in seq :
        gtts = True
        seq.remove(0)
    else :
        gtts = False
    voices = [voice.id for voice in pyttsx3.Engine().getProperty("voices")]
    if ... in seq :
        id_ns = list(range(1,len(voices)+1))
        seq.remove(...)
        seq = list(filter(lambda x:x>=len(voices)+1, seq))
        for i in seq :
           id_ns.remove(i)
    else :
        seq = list(filter(lambda x:x>=len(voices)+1, seq))
        id_ns = seq
    return gtts, [voices[i-1] for i in id_ns]

def wta(infile= "infile.txt", outdir= "output",
        seq= [0,...], normalize= [0,...],
        duer= 2000, rmold= False) :
    """ 
    to generate audio files for given words in $infile
    and save audio files in $outdir with subdirs names as words
    and each subdirs have files *.mp3 based on $seq

    if 0 in $seq => gtts.mp3 in audio_files_in_each_subdirs
    if $seq has numbers => all_(number-1)th_voices in voices are generated
    if $seq has ... => all voices are generated
    if $seq has both ... and numbers => all voices except all_(number-1)th_voices are generated

    $normaliz is for making each audio files in same duration
    by adding silence at ends based on given total_duration_of_each_file $duer

    $rmold : enable to remove old files f.mp3, m.mp3, f1.mp3
    > best pratice is to call rmold function seperatly after normalizing is done
    """
    if type(seq)==list :
        gtts, voices = _get_voices(seq)

        with open(infile,"r") as words_file :
            words = words_file.read().replace('\n',' ').split()
            words = [''.join(filter(str.isalnum,x)) for x in words]
            words = list(filter(len,words))
        words = list(set(words))
        log.debug(words)
        log.info("no. of words = "+str(len(words)))
        err_free_words = []

        p_python = "python3"
        p_pyttsx3_AFgen = "generate_AFs.py"

        language = 'en' #language assignment
        for word in words :
            try:
                os.makedirs(os.path.join(outdir,word), exist_ok=True)
                sequence = list(seq)
                if gtts : #TODO add request_limit_exided exception
                    sequence.remove(0)
                    audio = gTTS(text=word, lang=language, slow=False)
                    audio.save(os.path.join(outdir,word,"gtts.mp3"))
                if len(voices) :
                    for voice in voices :
                        log.debug("calling "+p_pyttsx3_AFgen+' '+word+' '+os.path.join(outdir,word,voice+".mp3")+' '+voice)
                        return_code = subprocess.call([p_python, p_pyttsx3_AFgen, word, os.path.join(outdir,word,voice+".mp3"), voice])
                        log.debug("return_code = "+str(return_code))
                        if return_code != 0 : log.error(p_pyttsx3_AFgen+" returned "+str(return_code))
            except FileExistsError:
                pass
            except :
                log.error("form audio generating "+sys.exc_info())
            else:
                err_free_words.append(word)

        log.debug(err_free_words)
        log.info("final no. of words "+str(len(err_free_words)))

    if type(normalize)==str and os.path.isdir(normalize):
        words = os.listdir(normalize)
        for word in words :
            audios = os.listdir(os.path.join(normalize,word))
            for audio in audios :
                try:
                    sound = As.from_mp3(os.path.join(normalize,word,audio))
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
                        sound.export(os.path.join(normalize,word,new_audio), format='mp3')
                        if rmold : os.remove(os.path.join(normalize,word,audio))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(normalize,word,audio)+' '+os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(normalize,word,audio), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing "+sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(normalize,word,audio)+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(normalize,word,audio), os.path.join(outdir,"~Defects",word))
        log.info("normalizing done "+normalize)

    elif type(normalize)==list :
        gtts, voices = _get_voices(normalize)
        audio_files = [voice+'.mp3' for voice in voices]
        if gtts : audio_files.append("gtts.mp3")

        if 'err_free_words' in locals().keys() :
             words = err_free_words
        else :
            with open(infile,"r") as words_file :
                words = words_file.read().replace('\n',' ').split()
            words = [''.join(filter(str.isalnum,x)) for x in words]
            words = list(filter(len,words))

        log.debug(str(words)+'\n'+str(audio_files))
        for word in words:
            for audio_file in audio_files :
                try:
                    sound=As.from_mp3(os.path.join(outdir,word,audio_file))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(outdir,word,"N"+audio_file), format='mp3')
                        if rmold : os.remove(os.path.join(outdir,word,audio_file))
                    else:
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing "+os.path.join(word,audio_file)+' '+sys.exc_info())
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(outdir,word,"f.mp3")+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~Defects",word))
        log.info("normalizing done "+str(normalize))

def rmold (outdir= "output", seq= [0,...], move= False):
    """
    to remove each files (depending on elements of $seq)
    form all subdirs of $outdir
    """
    gtts, voices = _get_voices(seq)
    audio_files = [voice+'.mp3' for voice in voices]
    if gtts : audio_files.append("gtts.mp3")

    words = os.listdir(outdir)
    for word in words:
        if not os.path.isdir(os.path.join(outdir,word)) :
            log.error(outdir+' '+word+" is not a dir")
            continue
        for audio_file in audio_files:
            if not move:
                try:
                    os.remove(os.path.join(outdir,word,audio_file))
                except:
                    log.error("not able to delete "+os.path.join(outdir,word,audio_file))
            else :
                try:
                    os.makedirs(os.path.join(move,word), exist_ok=True)
                    shutil.move(os.path.join(outdir,word,audio_file), os.path.join(move,word))
                except:
                    log.error("not able to move "+os.path.join(outdir,word,audio_file))

def rmempty (outdir= "output"):
    """
    to remove all empty subdirs of $oudir
    """
    words = os.listdir(outdir)
    for word in words:
        if not os.path.isdir(os.path.join(outdir,word)) :
            log.error(os.path.join(outdir,word)+" is not a dir")
            continue
        try:
            os.rmdir(os.path.join(outdir,word))
        except:
            pass
