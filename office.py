import lib
from time import sleep

class Office(object):
    def __init__(self):
        self.media  = lib.media             # Library for media related functions such as downloading, playing
        self.llm    = lib.llm               # Library for language related functions such as chat, translation, transcription


if __name__ == "__main__":
    office = Office()
    # Test download
    file_path = office.media.download(url="https://www.youtube.com/watch?v=ZYRfUoR9Q4Y&ab_channel=RobinFrancis")
    # Test play (assuming download worked)
    office.media.play(file_path)
    # Simulate doing other things while playback runs
    print("Playback started. Waiting 60 seconds before stopping...")
    sleep(5*1)
    office.media.stop_playback()
    print("Script continues after stopping playback.")
    # Test screenshot
    office.media.screenshot()
    # Transcribe the audio
    result = office.llm.transcribe(audio_file=file_path)
    print(f"Lyrics: {result['text']}")
    # Translate the text to Vietnamese
    vi_text = office.llm.translate(result['text'], target_language="vi")
    print(f"Translated Lyrics: {vi_text}")