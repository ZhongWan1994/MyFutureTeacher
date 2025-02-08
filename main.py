import os
import warnings
from time import sleep
from config import *
from tqdm import tqdm

from models.audio2text import Audio2TextModel
from models.evaluation_model import EvaluationModel
from models.text2audio import Text2AudioModel
from my_audio.audio_maker import AudioMaker
from utils import Utils

# 屏蔽所有警告
warnings.filterwarnings("ignore")

if __name__ == '__main__':
    print("~~~欢迎来到外语学习频道~~~")

    print("加载%s模型，请稍候..." % Utils.get_lang(LANGUAGE))
    audio2text_model = Audio2TextModel()
    text2audio_model = Text2AudioModel()
    audio_maker = AudioMaker()
    eval_model = EvaluationModel()
    print("加载模型完毕")

    a_sentences = Utils.get_sentences("A")
    b_sentences = Utils.get_sentences("B")
    a_sentences_translated = Utils.get_sentences_translated("A")
    b_sentences_translated = Utils.get_sentences_translated("B")
    a_sentences_origin, b_sentences_origin, a_sentences_translated_origin, b_sentences_translated_origin = a_sentences.copy(), b_sentences.copy(), a_sentences_translated.copy(), b_sentences_translated.copy()
    pipeline = [Utils.replace_question_mark, Utils.add_tail_break_mark]

    for step in pipeline:
        a_sentences = step(a_sentences)
        b_sentences = step(b_sentences)

    gen_key = input("需要生成角色的音频文件吗(先检查dialogue_board.txt内容是否正确) ：y/n")
    if gen_key == 'y':
        print("生成角色A音频: ")
        for i, a_sentence_p in tqdm(enumerate(a_sentences), total=len(a_sentences), desc="生成音频进度", position=0,
                                    leave=True):
            text2audio_model.text_to_audio(a_sentence_p, os.path.join(AUDIO_OUTPUT_PATH, "a_sentence_%d.wav" % i))

        print("生成角色B音频: ")
        for i, b_sentence_p in tqdm(enumerate(b_sentences), total=len(b_sentences), desc="生成音频进度", position=0,
                                    leave=True):
            text2audio_model.text_to_audio(b_sentence_p, os.path.join(AUDIO_OUTPUT_PATH, "b_sentence_%d.wav" % i))

    a_wav_file_paths = Utils.get_wav_files(AUDIO_OUTPUT_PATH, "a_sentence_")
    b_wav_file_paths = Utils.get_wav_files(AUDIO_OUTPUT_PATH, "b_sentence_")
    sleep(1)

    for i, (a_sentence, a_wav_file_path) in enumerate(zip(a_sentences_origin, a_wav_file_paths)):
        print("原文 A: %s" % a_sentence)
        print("译文 A: %s" % a_sentences_translated_origin[i])
        Utils.play_wav_file(a_wav_file_path)
        print("原文 B: %s" % b_sentences_origin[i])
        print("译文 B: %s" % b_sentences_translated_origin[i])
        b_wav_file_path = b_wav_file_paths[i]

        while True:
            choice = input("请输入操作指令[a: 再听一遍原文A, b: 听原文B, c: 朗读原文B, n: 下一个句子] : ")
            if choice.strip() == 'a':
                Utils.play_wav_file(a_wav_file_path)
            elif choice.strip() == 'b':
                Utils.play_wav_file(b_wav_file_path)
            elif choice.strip() == 'c':
                audio_data = audio_maker.listen(origin_sentence=b_sentences_origin[i],
                                                origin_sentence_translated=b_sentences_translated_origin[i])
                audio_maker.save(audio_data, os.path.join(AUDIO_OUTPUT_PATH, "user_b_sentence_%d.wav" % i))
                rn_audio_data, duration1 = audio_maker.resample_and_normalize(audio_data)
                text = audio2text_model.audio2text(rn_audio_data)

                std_audio_data = audio_maker.read_wav_to_audio_data(b_wav_file_paths[i])
                std_audio_data, duration2 = audio_maker.resample_and_normalize(std_audio_data)
                print("my Text: ", text)
                print("normal Text: ", b_sentences_origin[i])
                print("您的得分为：", eval_model.eval(text, b_sentences_origin[i], duration1, duration2))
            elif choice.strip() == 'n':
                break
            else:
                print(choice)
                print("无效的指令，请重新输入。")

    print("今天就到此为止吧，明天继续~")
