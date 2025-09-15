import threading
import time
import math
import tgfx

# Check for required packages
try:
    import simpleaudio as sa
    from pydub import AudioSegment
    AUDIO_ENABLED = True
except ImportError:
    AUDIO_ENABLED = False

if AUDIO_ENABLED:
    class AudioPlayer:
        def __init__(self, filename):
            self.filename = filename
            self.audio = AudioSegment.from_file(filename).set_channels(2).set_frame_rate(44100)
            self.sample_rate = self.audio.frame_rate
            self.num_channels = self.audio.channels
            self.bytes_per_sample = self.audio.sample_width

            self.play_obj = None
            self.start_time = 0
            self.elapsed_before_pause = 0
            self.is_playing = False
            self.is_paused = False
            self.lock = threading.Lock()
            self.duration = len(self.audio) / 1000.0  # seconds

        def _make_wave(self, segment):
            return sa.WaveObject(segment.raw_data,
                                 self.num_channels,
                                 self.bytes_per_sample,
                                 self.sample_rate)

        def play(self):
            with self.lock:
                if not self.is_playing:
                    seg = self.audio[self.elapsed_before_pause * 1000:]
                    wave_obj = self._make_wave(seg)
                    self.play_obj = wave_obj.play()
                    self.start_time = time.time()
                    self.is_playing = True
                    self.is_paused = False

        def pause(self):
            with self.lock:
                if self.is_playing and not self.is_paused:
                    if self.play_obj:
                        self.play_obj.stop()
                    self.elapsed_before_pause += time.time() - self.start_time
                    self.is_paused = True
                    self.is_playing = False

        def stop(self):
            with self.lock:
                if self.play_obj:
                    self.play_obj.stop()
                self.play_obj = None
                self.is_playing = False
                self.is_paused = False
                self.elapsed_before_pause = 0

        def is_active(self):
            return self.play_obj and self.play_obj.is_playing()

        def current_time(self):
            if self.is_playing:
                return min(self.elapsed_before_pause + (time.time() - self.start_time), self.duration)
            return min(self.elapsed_before_pause, self.duration)

    def play(filename, canvas):
        try:
            player = AudioPlayer(filename)
            running = True

            def centered_put(position, text, color=(255, 255, 255)):
                x = position[0] + math.floor(canvas.size[0] / 2) - math.floor(len(text) / 2)
                canvas.put((x, position[1]), text, color=color)

            while running:
                try:
                    key = tgfx.getkey()
                except Exception:
                    key = None

                if key == "p":
                    player.play()
                elif key == " ":
                    player.pause()
                elif key == "s":
                    player.stop()
                elif key == "q":
                    player.stop()
                    break

                canvas.clear()
                centered_put((0, 0), f"Now Playing: {filename}", color=(0, 200, 255))
                centered_put((0, 2), "[P]lay [SPACE] Pause [S]top [Q]uit Player", color=(127, 127, 255))

                if player.is_playing:
                    status, color = "▶ Playing", (0, 255, 0)
                elif player.is_paused:
                    status, color = "⏸ Paused", (255, 255, 0)
                else:
                    status, color = "■ Stopped", (255, 0, 0)
                centered_put((0, 4), status, color=color)

                elapsed = player.current_time()
                progress = elapsed / player.duration if player.duration > 0 else 0
                bar_width = 40
                filled = int(progress * bar_width)
                bar = "█" * filled + "-" * (bar_width - filled)
                time_str = f"{int(elapsed)}/{int(player.duration)} sec"

                centered_put((0, 6), f"[{bar}] {int(progress*100)}%", color=(0, 200, 0))
                centered_put((0, 7), time_str, color=(200, 200, 200))

                canvas.print()
                time.sleep(0.1)

        except Exception as e:
            print("AudioPlayer error:", e)
            try:
                player.stop()
            except Exception:
                pass

else:
    print("Error: simpleaudio and/or pydub not installed. AudioPlayer cannot run uwu")
