import threading
import time

import pyaudio


class AudioData:
    def __init__(self, audio_bytes, sample_rate, sample_width, channels):
        """
        初始化 AudioData 类
        :param audio_bytes: 音频数据的字节流
        :param sample_rate: 采样率
        :param sample_width: 采样宽度（以字节为单位）
        :param channels: 声道数
        """
        self.audio_bytes = audio_bytes
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.channels = channels

    def get_duration(self):
        """
        计算音频的时长（以秒为单位）
        :return: 音频时长
        """
        num_frames = len(self.audio_bytes) // (self.sample_width * self.channels)
        return num_frames / self.sample_rate

    def __repr__(self):
        """
        返回对象的字符串表示形式
        :return: 字符串表示
        """
        return f"AudioData(sample_rate={self.sample_rate}, sample_width={self.sample_width}, channels={self.channels}, duration={self.get_duration():.2f}s)"


class Recorder:
    def __init__(self, chunk=1024, channels=1, rate=64000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = False
        self._frames = []

    def start(self):
        self._running = True
        threading._start_new_thread(self._recording, ())
        threading._start_new_thread(self._tick, ())

    def _tick(self):
        t = 0
        while self._running:
            time.sleep(1)
            t += 1
            print(f"\r录音 {t} s", end='', flush=True)
            if t > 30:
                print("超过最大录音时长，停止...")
                self._running = False
                break

    def _recording(self):
        self._frames = []
        audio = pyaudio.PyAudio()

        stream = audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

    def stop(self):
        self._running = False

    def get_audio_data(self):
        audio = pyaudio.PyAudio()
        audio_bytes = b''.join(self._frames)
        sample_width = audio.get_sample_size(self.FORMAT)
        audio.terminate()
        return AudioData(audio_bytes, self.RATE, sample_width, self.CHANNELS)
