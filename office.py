import lib
from time import sleep, time

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
    start_time = time()
    office.llm.verbose = False
    result = office.llm.transcribe(audio_file=file_path, language="en")
    run_time = time() - start_time
    print(f"Transcription completed in {run_time:.2f} seconds!")
    # Translate the text to Vietnamese
    vi_text = office.llm.translate(result['text'], target_language="vi")
    print(f"Translated Lyrics: {vi_text}")

    """ For select the best transcription models and parameters
    for method in ["whisper", "fast_whisper", "whisperx"]:
        for model in ["tiny", "base"]:
            for compute_type in ["float32", "int8"]:
                start_time = time()
                print(f"Transcribing audio using {method} model {model} with {compute_type} compute type... ", end="")
                result = office.llm.transcribe(audio_file=file_path, method=method, compute_type=compute_type)
                print(f"Lyrics: {result['text']}")
                run_time = time() - start_time
                print(f"Completed in {run_time:.2f} seconds!")

    # Translate the text to Vietnamese
    #vi_text = office.llm.translate(result['text'], target_language="vi")
    #print(f"Translated Lyrics: {vi_text}")
    """