import time
import wave

import librosa
import numpy as np
from pynput import keyboard

from my_audio.recorder import Recorder, AudioData


class AudioMaker:
    def __init__(self):
        self.rec = Recorder()
        self.is_recording = False

    def on_press(self, key):
        start_time = time.time()
        try:
            if key == keyboard.Key.space:
                if not self.is_recording:
                    print("开始录音...")
                    self.rec.start()
                    self.is_recording = True
                else:
                    print("停止录音...")
                    self.rec.stop()
                    end_time = time.time()
                    print('录音时间为%ds' % (end_time - start_time))
                    self.is_recording = False
                    return False

        except AttributeError:
            pass

    def listen(self, origin_sentence=None, origin_sentence_translated=None):
        if origin_sentence:
            print("原文：", origin_sentence)
        if origin_sentence_translated:
            print("译文：", origin_sentence_translated)
        print('按空格键开始录音，再按一次空格键停止录音')
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
        return self.rec.get_audio_data()

    @staticmethod
    def resample_and_normalize(audio_data):
        # 将字节流转换为 numpy 数组
        audio_array = np.frombuffer(audio_data.audio_bytes, dtype=np.int16)
        # 采样率转换
        resampled_audio = librosa.resample(y=audio_array.astype(np.float32), orig_sr=audio_data.sample_rate,
                                           target_sr=16000)
        # 归一化处理
        max_val = np.max(np.abs(resampled_audio)) + 1e-8  # 添加极小值防止除零
        resampled_audio = resampled_audio / max_val
        # 计算 resampled_audio 的时长
        duration = len(resampled_audio) / 16000

        return resampled_audio, duration

    @staticmethod
    def save(audio_data, filename):
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(audio_data.channels)
        wf.setsampwidth(audio_data.sample_width)
        wf.setframerate(audio_data.sample_rate)
        wf.writeframes(audio_data.audio_bytes)
        wf.close()
        print("已保存录音")

    @staticmethod
    def read_wav_to_audio_data(file_path):
        with wave.open(file_path, 'rb') as wf:
            # 获取 WAV 文件的元信息
            sample_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            channels = wf.getnchannels()

            # 读取音频数据
            audio_bytes = wf.readframes(wf.getnframes())

        # 创建 AudioData 对象
        audio_data = AudioData(audio_bytes, sample_rate, sample_width, channels)
        return audio_data
