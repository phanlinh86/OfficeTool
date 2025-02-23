"""
    This module is used for media files like images, videos, etc.
    Some functionalities are:
    1. Download media files from websites
    2. Play media files
    3. Record audio
    4. Record video
    5. Take screenshots
"""
import yt_dlp
import os
from time import time, sleep
import vlc
import pyaudio
import wave
import cv2
import pyautogui
import threading

class Media(object):
    def __init__(self):
        self.player = None  # Store the VLC player instance
        self.instance = None  # Store the VLC instance
        self.playback_thread = None  # Store the playback thread
        self.stop_event = threading.Event()  # Event to signal stop
        self.out_path = "../output"
        self.verbose = False

    def download(self, url=None):
        """
        Downloads media from a URL using yt-dlp.

        Parameters:
            url (str, optional): The URL of the media to download. Defaults to None.

        Returns:
            str or None: The file path if successful, None if an error occurs.
        """
        if not url or not isinstance(url, str):
            print("A valid URL string is required to download media.")
            return None
        output_path =  self.out_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'verbose': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.verbose:
                    start_time = time()
                    print("Downloading media...", end=" ")
                info = ydl.extract_info(url, download=False)
                file_path = ydl.prepare_filename(info)
                ydl.download(url)
                if self.verbose:
                    download_time = time() - start_time
                    print(f"\rDownload Completed in {download_time:.2f} seconds! File saved as: {file_path}")
                return file_path
        except yt_dlp.DownloadError as e:
            print(f"Download Error: {e}")
            return None
        except yt_dlp.ExtractorError as e:
            print(f"Extractor Error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def play(self, filename):
        """
        Plays a media file using VLC in a non-blocking thread.

        Parameters:
            filename (str): The path to the media file to play.

        Returns:
            bool: True if playback starts successfully, False otherwise.
        """
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return False

        if self.playback_thread and self.playback_thread.is_alive():
            print("Another playback is already in progress. Stop it first with stop_playback().")
            return False

        if self.verbose:
            print(f"Attempting to play: {os.path.abspath(filename)}")

        self.stop_event.clear()  # Ensure stop event is reset
        self.playback_thread = threading.Thread(target=self._play_in_thread, args=(filename,))
        self.playback_thread.start()
        return True

    def _play_in_thread(self, filename, audio_only=False):
        """Helper method to run playback in a separate thread."""
        try:
            # Configure VLC instance
            vlc_args = ['--verbose=-1', '--vout=direct3d11', '--no-spu']
            if audio_only:
                vlc_args.append('--no-video')
            if self.verbose:
                print(f"Creating VLC instance with args: {vlc_args}")
            self.instance = vlc.Instance(*vlc_args)
            self.player = self.instance.media_player_new()
            media = self.instance.media_new(filename)
            self.player.set_media(media)
            if self.verbose:
                print(f"Starting playback in thread: {filename}")

            if self.player.play() == -1:
                print("VLC failed to start playback.")
                return

            # Keep playing until stopped or finished
            while not self.stop_event.is_set():
                state = self.player.get_state()
                if state in [vlc.State.Ended, vlc.State.Error]:
                    break
                sleep(1)
            if self.verbose:
                if self.player.get_state() == vlc.State.Ended:
                    print("Playback completed.")
                elif self.stop_event.is_set():
                    print("Playback interrupted by user.")
                else:
                    print(f"Playback stopped with state: {self.player.get_state()}")

        except Exception as e:
            print(f"Playback error in thread: {e}")
        finally:
            if self.player:
                self.player.stop()
                self.player.release()
            if self.instance:
                self.instance.release()
            self.player = None
            self.instance = None
            self.stop_event.clear()  # Reset stop event

    def stop_playback(self):
        """
        Stops the currently playing media.

        Returns:
            bool: True if stopped successfully, False if no playback was active.
        """
        if not self.playback_thread or not self.playback_thread.is_alive():
            print("No playback is currently active.")
            return False

        self.stop_event.set()  # Signal the thread to stop
        self.playback_thread.join()  # Wait for the thread to finish
        if self.verbose:
            print("Playback stopped.")
        return True

    def record_audio(self, filename, duration):
        """
        Records audio from the microphone for a specified duration.

        Parameters:
            filename (str): The path where the audio file (WAV) will be saved.
            duration (int): Recording duration in seconds.

        Returns:
            bool: True if recording is successful, False otherwise.
        """
        if not isinstance(duration, (int, float)) or duration <= 0:
            print("Duration must be a positive number.")
            return False

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            print(f"Recording audio for {duration} seconds...")
            frames = []

            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()
            file_path = self.out_path + "/" + filename
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            print(f"Audio saved as: {file_path}")
            return True
        except Exception as e:
            print(f"Audio recording error: {e}")
            return False

    def record_video(self, filename, duration):
        """
        Records video from the webcam for a specified duration.

        Parameters:
            filename (str): The path where the video file (AVI) will be saved.
            duration (int): Recording duration in seconds.

        Returns:
            bool: True if recording is successful, False otherwise.
        """
        if not isinstance(duration, (int, float)) or duration <= 0:
            print("Duration must be a positive number.")
            return False

        try:
            cap = cv2.VideoCapture(0)  # Open default webcam
            if not cap.isOpened():
                print("Cannot access webcam.")
                return False

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            file_path = self.out_path + "/" + filename
            out = cv2.VideoWriter(file_path, fourcc, 20.0, (640, 480))

            print(f"Recording video for {duration} seconds...")
            start_time = time()
            while time() - start_time < duration:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()
            print(f"Video saved as: {file_path}")
            return True
        except Exception as e:
            print(f"Video recording error: {e}")
            return False

    def screenshot(self, filename="screenshot.png"):
        """
        Takes a screenshot and saves it as an image file.

        Parameters:
            filename (str): The path where the screenshot (PNG) will be saved.

        Returns:
            bool: True if screenshot is successful, False otherwise.
        """
        try:
            file_path = self.out_path + "/" + filename
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
            if self.verbose:
                print(f"Screenshot saved as: {file_path}")
            return True
        except Exception as e:
            print(f"Screenshot error: {e}")
            return False


if __name__ == "__main__":
    media = Media()
    # Test download
    downloaded_file = media.download(url="https://www.youtube.com/watch?v=ZYRfUoR9Q4Y&ab_channel=RobinFrancis")
    # Test play (assuming download worked)
    media.play(downloaded_file)
    # Simulate doing other things while playback runs
    print("Playback started. Waiting 5 seconds before stopping...")
    sleep(5)
    media.stop_playback()
    print("Script continues after stopping playback.")
    # Test screenshot
    media.screenshot()
