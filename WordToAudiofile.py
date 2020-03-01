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
        seq= [0,...], add_silence= [0,...], fill_fit= False,
        duer= 2000, rmold= False) :
    """ 
    to generate audio files for given words in $infile
    and save audio files in $outdir with subdirs names as words
    and each subdirs have files *.mp3 based on $seq

    if 0 in $seq => gtts.mp3 in audio_files_in_each_subdirs
    if $seq has numbers => all_(number-1)th_voices in voices are generated
    if $seq has ... => all voices are generated
    if $seq has both ... and numbers => all voices except all_(number-1)th_voices are generated

    $add_silence : boolean, enable to making each audio files have same duration
    by adding silence at ends based on given total_duration_of_each_file $duer

    $fill_fit : boolean, enable to making each audio files have same duration by stretch or shrink the audio

    $rmold : boolean, enable to remove old files
    > best pratice is to call rmold function seperatly after wta is done

    $return[0] = list of successfully audio file generated words
    $return[1] = no. of words classified as longer than given dureation $duer
    $return[2] = no. of words classified as defects while doing add_silence or fill_fit

    > don't enable both add_silence and fill_fit if rmold is True
    """
    longer, defects = 0, 0

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
                    log.debug("calling gTTS(text="+str(word)+", lang="+str(language)+", slow=False)")
                    audio = gTTS(text=word, lang=language, slow=False)
                    audio.save(os.path.join(outdir,word,"gtts.mp3"))
                    log.debug(os.path.join(outdir,word,"gtts.mp3")+" saved")
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

    if type(add_silence)==str and os.path.isdir(add_silence):
        words = os.listdir(add_silence)
        log.debug(str(words))
        for word in words :
            audios = os.listdir(os.path.join(add_silence,word))
            for audio in audios :
                try:
                    sound = As.from_mp3(os.path.join(add_silence,word,audio))
                    log.debug("adding silence to "+os.path.join(add_silence,word,audio))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(add_silence,word,"S"+audio), format='mp3')
                        if rmold : os.remove(os.path.join(add_silence,word,audio))
                    else:
                        longer += 1
                        log.error("from add_silence"+os.path.join(word,audio)+" duration greater than "+str(duer))
                        os.makedirs(os.path.join(add_silence,"~LongerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(add_silence,word,audio)+' '+os.path.join(add_silence,"~LongerThan_duer",word))
                        shutil.move(os.path.join(add_silence,word,audio), os.path.join(add_silence,"~LongerThan_duer",word))
                except:
                    defects += 1
                    log.error("form add_silence "+str(sys.exc_info()))
                    os.makedirs(os.path.join(add_silence,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(add_silence,word,audio)+' '+os.path.join(add_silence,"~Defects",word))
                    shutil.move(os.path.join(add_silence,word,audio), os.path.join(add_silence,"~Defects",word))
        log.info("add_silence done "+add_silence)

    elif type(add_silence)==list :
        gtts, voices = _get_voices(add_silence)
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
                    log.debug("adding silence to "+os.path.join(outdir,word,audio_file))
                    if len(sound)<duer:
                        remaining = duer - len(sound)
                        rem = remaining//2
                        if rem == remaining/2 :
                            sound = As.silent(duration=rem)+sound+As.silent(duration=rem)
                        else :
                            sound = As.silent(duration=rem+1)+sound+As.silent(duration=rem)
                        sound.export(os.path.join(outdir,word,"S"+audio_file), format='mp3')
                        if rmold : os.remove(os.path.join(outdir,word,audio_file))
                    else:
                        longer += 1
                        log.error("from add_silence "+os.path.join(word,audio_file)+" duration greater than "+str(duer))
                        os.makedirs(os.path.join(outdir,"~LongerThan_duer",word), exist_ok=True)
                        log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~LongerThan_duer",word))
                        shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~LongerThan_duer",word))
                except:
                    defects += 1
                    log.error("form add_silence "+os.path.join(word,audio_file)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~Defects",word))
        log.info("add_silence done "+str(add_silence))

    if type(fill_fit)==str and os.path.isdir(fill_fit):
        words = os.listdir(fill_fit)
        log.debug(str(words))
        for word in words :
            audios = os.listdir(os.path.join(fill_fit,word))
            for audio in audios :
                try:
                    log.debug("fill_fitting "+os.path.join(fill_fit,word,audio)+" to "+os.path.join(fill_fit,word,"F"+audio))
                    retrn = _change_duer(os.path.join(fill_fit,word,audio), os.path.join(fill_fit,word,"F"+audio), duer)
                    if retrn[0] == duer :
                        log.debug("change_duer returned with "+str(retrn))
                    else :
                        log.error("change_duer not able to change dueration for this audio")
                        raise Exception("change_duer not able to change dueration")
                except:
                    defects += 1
                    log.error("form fill_fitter "+os.path.join(word,audio)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(fill_fit,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(fill_fit,word,audio)+' '+os.path.join(fill_fit,"~Defects",word))
                    shutil.move(os.path.join(fill_fit,word,audio), os.path.join(fill_fit,"~Defects",word))

    elif type(fill_fit)==list :
        gtts, voices = _get_voices(fill_fit)
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
                    log.debug("fill_fitting "+os.path.join(outdir,word,audio_file)+" to "+os.path.join(outdir,word,"F"+audio_file))
                    retrn = _change_duer(os.path.join(outdir,word,audio_file), os.path.join(outdir,word,"F"+audio_file), duer)
                    if retrn[0] == duer :
                        log.debug("change_duer returned with "+str(retrn))
                    else :
                        log.error("change_duer not able to change dueration for this audio")
                        raise Exception("change_duer not able to change dueration")
                except:
                    defects += 1
                    log.error("form fill_fitter "+os.path.join(word,audio_file)+' '+str(sys.exc_info()))
                    os.makedirs(os.path.join(outdir,"~Defects",word), exist_ok=True)
                    log.debug("moving "+os.path.join(outdir,word,audio_file)+' '+os.path.join(outdir,"~Defects",word))
                    shutil.move(os.path.join(outdir,word,audio_file), os.path.join(outdir,"~Defects",word))

    log.info("wta all done.")
    return err_free_words, longer, defects

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
    log.info("rmold all done.")

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
    log.info("rmempty all done.")
