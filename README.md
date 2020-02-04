# Word-to-AudioFile
this is to generate audio files from given words

this module is for generating audio files for given list of words
helpful for generating dataset for training model for set of words

##### example
```python3
import WordToAudioFile as wta
wta.wta(infile= "words_file.txt", outdir= "dataset", seq= [0,...])
```

## Normalizing
we can also making all audio files for same duration
```python3
import WordToAudioFile as wta
wta.wta(infile= "words_file.txt", outdir= "dataset",
        seq= [0,...], normalize= [0,...],
        duer= 1000) # in miliseconds
wta.rmold(outdir= "dataset", seq= [0,...])
```
## Modifying
we can change duration of audio files by changing its frame_rate and frame_count other than adding silence
```python3
import WordToAudioFile as wta
wta.wta(infile= "words_file.txt", outdir= "dataset",
        seq= [0,...], normalize= False, modify= [0,...],
        duer= 1000)
wta.rmold(outdir= "dataset", seq= [0,...])
```

# Voice_recorder
this is to record human voices as audio files for given words

##### example
```python3
import voice_recorder
voice_recorder.record(infile= "words_file.txt", outdir= "dataset",
                      duer= 1000)
```
