# audible-split
Split audible mp3 in chapters.

# How To use
1. `main.py`
   1. Change the value of `AUDIO_FILE` at line 16.
   2. Run.
2. `podcast.py`
   1. Upload the splitted mp3 to dropbox.
   2. Go to: [url](https://www.dropbox.com/sh/2zbtmzxkk44qmgk/AACfbAgwyD0A9TAB3EdANO9ja?dl=0)
   3. Inspect the page and replace the value of `CONTENT` with this tag:
      ```html
      <table role="table" class="mc-table sl-list-container"></table>
      ```
   4. Run.

# vosk-api
https://github.com/alphacep/vosk-api/releases

Current version is: `0.3.50`

## Models
Download models with the script `scripts/get_models.sh`
Current versions are:
- vosk-model-small-en-us `0.15`
- vosk-model-small-it `0.22`

### Other models
https://alphacephei.com/vosk/models

## Source 
https://www.blisshq.com/music-library-management-blog/2021/01/22/splitting-audiobooks-chapters-ai/
