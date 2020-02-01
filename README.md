# Word-to-AudioFile
this is to generate audio files from given words

this module is for generating audio files for given list of words
helpful for generating dataset for training model for set of words

##### example
```python3
import WordToAudioFile as wta
wta.wta(infile= "words_file.txt", seq= [1,1,1])
```

## Normalizing
we can also making all audio files for same duration
```python3
import WordToAudioFile as wta
wta.wta(infile= "words_file.txt",
        seq= [1,1,1], normalizer= [1,1,1],
        duer= 1000 # in miliseconds
        )
```
