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

def _change_duer(p_af, p_maf, duer, fr= None) :
    """$p_af is path of input audio file
    $p_maf is path for output audio file
    $duer = output audio file duration
    $fr = output audio file frame rate"""
    with open(p_af, 'rb') as af :
        sound = As.from_file(af)
    new_fr = int(sound.frame_count() / duer)
    m_sound = sound._spawn(sound.raw_data, #modified_sound
                           overrides={'frame_rate':new_fr})
    m_sound = m_sound.set_frame_rate(fr if fr else sound.frame_rate)
    m_sound.export(p_maf, format=os.path.splitext(p_maf)[1])
    return len(m_sound), m_sound.frame_count(), m_sound.frame_rate

def wta(infile= "infile.txt", outdir= "output",
        seq= [0,...], normalize= [0,...], modify= False,
        duer= 2000, rmold= False) :
    """ 
    to generate audio files for given words in $infile
    and save audio files in $outdir with subdirs names as words
    and each subdirs have files *.mp3 based on $seq

    if 0 in $seq => gtts.mp3 in audio_files_in_each_subdirs
    if $seq has numbers => all_(number-1)th_voices in voices are generated
    if $seq has ... => all voices are generated
    if $seq has both ... and numbers => all voices except all_(number-1)th_voices are generated

    $normalize is for making each audio files have same duration
    by adding silence at ends based on given total_duration_of_each_file $duer

    $modify is for making each audio files have same duration by modifying frame_count

    $rmold : enable to remove old files f.mp3, m.mp3, f1.mp3
    > best pratice is to call rmold function seperatly after normalizing is done

    > don't enable both normalize and modify if rmold is True
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
                log.error("form audio generating "+str(sys.exc_info()))
            else:
                err_free_words.append(word)

        log.debug(err_free_words)
        log.info("final no. of words "+str(len(err_free_words)))

    if type(normalize)==str and os.path.isdir(normalize):
        words = os.listdir(normalize)
        log.debug(str(words))
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
                        sound.export(os.path.join(normalize,word,"N"+audio), format='mp3')
                        if rmold : os.remove(os.path.join(normalize,word,audio))
                    else:
                        log.error("from normalizing "+os.path.join(word,audio)+" duration greater than "+str(duer))
                        os.makedirs(os.path.join(normalize,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(normalize,word,audio)+' '+os.path.join(normalize,"~LargerThan_duer",word))
                        shutil.move(os.path.join(normalize,word,audio), os.path.join(normalize,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing "+str(sys.exc_info()))
                    os.makedirs(os.path.join(normalize,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(normalize,word,audio)+' '+os.path.join(normalize,"~Defects",word))
                    shutil.move(os.path.join(normalize,word,audio), os.path.join(normalize,"~Defects",word))
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
        words = list(set(words))

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
                        log.error("from normalizing "+os.path.join(word,audio_file)+" duration greater than "+str(duer))
                        os.makedirs(os.path.join(outdir,"~LargerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~LargerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~LargerThan_duer",word))
                except:
                    log.error("form normalizing "+os.path.join(word,audio_file)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(outdir,word,"f.mp3")+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,"f.mp3"), os.path.join(outdir,"~Defects",word))
        log.info("normalizing done "+str(normalize))

    if type(modify)==str and os.path.isdir(modify):
        words = os.listdir(modify)
        for word in words :
            audios = os.listdir(os.path.join(modify,word))
            for audio in audios :
                try:
                    log.debug("modifing "+os.path.join(modify,word,audio)+" to "+os.path.join(modify,word,"M"+audio))
                    retrn = _change_duer(os.path.join(modify,word,audio), os.path.join(modify,word,"M"+audio), duer)
                    if retrn[0] == duer :
                        log.debug("modifier returned with "+str(retrn))
                    else :
                        log.error("modifier not able to change dueration for this audio")
                        raise Exception("modifier not able to change dueration")
                except:
                    log.error("form modifier "+os.path.join(word,audio)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(modify,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(modify,word,audio)+' '+os.path.join(modify,"~Defects",word))
                    shutil.move(os.path.join(modify,word,audio), os.path.join(modify,"~Defects",word))

    elif type(modify)==list :
        gtts, voices = _get_voices(modify)
        audio_files = [voice+'.mp3' for voice in voices]
        if gtts : audio_files.append("gtts.mp3")

        if 'err_free_words' in locals().keys() :
             words = err_free_words
        else :
            with open(infile,"r") as words_file :
                words = words_file.read().replace('\n',' ').split()
            words = [''.join(filter(str.isalnum,x)) for x in words]
            words = list(filter(len,words))
        words = list(set(words))

        log.debug(str(words)+'\n'+str(audio_files))
        for word in words:
            for audio_file in audio_files :
                try:
                    log.debug("modifing "+os.path.join(outdir,word,audio_file)+" to "+os.path.join(outdir,word,"M"+audio_file))
                    retrn = _change_duer(os.path.join(outdir,word,audio_file), os.path.join(outdir,word,"M"+audio_file), duer)
                    if retrn[0] == duer :
                        log.debug("modifier returned with "+str(retrn))
                    else :
                        log.error("modifier not able to change dueration for this audio")
                        raise Exception("modifier not able to change dueration")
                except:
                    log.error("form modifier "+os.path.join(word,audio_file)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~Defects",word))

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
