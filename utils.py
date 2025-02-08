import os
import random
import select
import sys
from config import *
from playsound import playsound


class Utils:

    @staticmethod
    def pop_topic(file_path, random_choice=False):
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                topics = file.readlines()
                topics = [topic.strip() for topic in topics if topic.strip()]  # 去除空白行和首尾空格

            if not topics:
                return None

            if random_choice:
                # 随机选择一个话题
                index = random.randint(0, len(topics) - 1)
            else:
                # 按顺序选择第一个话题
                index = 0

            # 获取选中的话题
            selected_topic = topics.pop(index)

            # 将剩余的话题写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                for topic in topics:
                    file.write(topic + '\n')

            return selected_topic
        except FileNotFoundError:
            print("未找到 topic.txt 文件。")
            return None

    @staticmethod
    def select():
        if not REVIEW:
            file_path = SELECT_PATH.replace("@", VOB_LIB)
        else:
            file_path = SELECT_HISTORY_PATH.replace("@", VOB_LIB)
        try:
            # 打开文件
            with open(file_path, 'r', encoding='utf-8') as file:
                # 读取文件内容
                content = file.read()
                # 将内容按空白字符分割成单词列表
                all_words = content.split()
                # 过滤掉长度小于等于 1 的单词
                valid_words = [word for word in all_words if len(word) > 1]
                # 检查有效单词数量是否足够采样
                if len(valid_words) < SAMPLE_VOCAB_NUM:
                    print("文件中的有效单词数量少于采样数量，将返回所有有效单词。")
                    remaining_words = []
                    sampled_words = valid_words
                else:
                    # 进行随机采样
                    sampled_words = random.sample(valid_words, SAMPLE_VOCAB_NUM)
                    # 获取剩余的单词
                    remaining_words = [word for word in valid_words if word not in sampled_words]
            if not REVIEW:
                # 将剩余的单词重新写回文件
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("\n".join(remaining_words))
                Utils.record2history(sampled_words, SELECT_HISTORY_PATH.replace("@", VOB_LIB))
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return []
        except Exception as e:
            print(f"发生错误: {e}")
            return []
        return sampled_words

    @staticmethod
    def record2history(word_list, filepath):
        with open(filepath, 'a', encoding='utf-8') as file:
            for word in word_list:
                file.write(word + '\n')

    @staticmethod
    def get_lang(lang):
        lang_str = "英文"
        if lang == "en":
            lang_str = "英文"
        elif lang == "jap":
            lang_str = "日文"
        return lang_str

    def pack_prompt_by_list(self, gen_list):
        lang = self.get_lang(LANGUAGE)
        s = "请根据列表，为我创建A/B两人的%s对话，A一句B一句，并在每句后面用()附上中文翻译，用上列表内所有的单词，只需返回对话结果，其他的提示不要，以下是我提供的列表：%s (生僻、违禁词、不适当、违背公序良俗的词汇或者你实在无法用上的单词自动忽略！)"
        return s % (lang, str(gen_list))

    def pack_prompt_by_topic(self, topic, episode_len=20, lang=LANGUAGE):
        lang = self.get_lang(lang)
        return "创建关于<%s>的A/B两人%d回合左右的%s对话，A一句B一句，并在每句后面用()附上中文翻译" % (
        topic, episode_len, lang)

    @staticmethod
    def pack_prmpt_by_cosplay(role_name, episode_len=20, lang=LANGUAGE):
        return "请你扮演<%s>作为角色A,我作为角色B,产生%d回合的%s对话，A一句B一句，并在每句后面用()附上中文翻译" % (
        role_name, episode_len, lang)

    @staticmethod
    def get_sentences(role="A"):
        sentences = []
        try:
            with open(DIALOGUE_BOARD_PATH, 'r', encoding='utf-8') as file:
                for line in file:
                    if "A" not in line and "B" not in line:
                        continue
                    if line.startswith(f"{role}"):
                        # 去除行首的角色标识和引号
                        try:
                            line = line.replace(f"{role}", "").replace(":", "")
                        except:
                            pass
                        try:
                            line = line.replace(f"{role}", "").replace("：", "")
                        except:
                            pass
                        line = line.strip()
                        # 先查找中文括号的起始位置
                        translation_start_zh = line.find("（")
                        # 再查找英文括号的起始位置
                        translation_start_en = line.find("(")
                        # 取最先找到的括号位置作为翻译起始位置（如果都没找到则为 -1）
                        translation_start = min(translation_start_zh, translation_start_en) if (
                                translation_start_zh != -1 and translation_start_en != -1) else max(
                            translation_start_zh, translation_start_en)
                        if translation_start != -1:
                            # 截取翻译之前的部分
                            line = line[:translation_start]
                        # 去除行末的引号和换行符
                        line = line.rstrip("\"\n")
                        sentences.append(line)
        except FileNotFoundError:
            print(f"文件 {DIALOGUE_BOARD_PATH} 未找到。")
        except Exception as e:
            print(f"发生错误: {e}")
        return sentences

    @staticmethod
    def get_sentences_translated(role="A"):
        translated_sentences = []
        try:
            with open(DIALOGUE_BOARD_PATH, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.startswith(f"{role}: "):
                        # 尝试查找中文括号
                        start_index = line.find("（")
                        end_index = line.find("）")
                        # 如果没找到中文括号，尝试查找英文括号
                        if start_index == -1 or end_index == -1:
                            start_index = line.find("(")
                            end_index = line.find(")")
                        if start_index != -1 and end_index != -1:
                            # 提取中文翻译
                            translation = line[start_index + 1:end_index]
                            translated_sentences.append(translation)
        except FileNotFoundError:
            print(f"文件 {DIALOGUE_BOARD_PATH} 未找到。")
        except Exception as e:
            print(f"发生错误: {e}")
        return translated_sentences

    @staticmethod
    def get_wav_files(folder_path, prefix='a_sentence_'):
        wav_files = []
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix) and filename.endswith('.wav'):
                try:
                    parts = filename.split('_')
                    number_str = parts[2].split('.')[0]
                    number = int(number_str)
                    file_path = os.path.join(folder_path, filename)
                    wav_files.append((number, file_path))
                except (IndexError, ValueError):
                    continue

        wav_files.sort(key=lambda x: x[0])
        return [path for _, path in wav_files]

    @staticmethod
    def play_wav_file(file_path):
        try:
            playsound(file_path)
        except Exception as e:
            print(f"播放音频文件时出错: {e}")

    @staticmethod
    def clear_input_buffer():
        while True:
            # 使用 select 检查标准输入是否有数据可读
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                # 如果有数据可读，读取一个字符并丢弃
                sys.stdin.read(1)
            else:
                # 没有数据可读，退出循环
                break

    @staticmethod
    def replace_question_mark(sentences):
        return [sentence.replace("?", ".").replace("'", "").replace("!", ".").replace("？", ".").replace("！", ".") for sentence in sentences]

    @staticmethod
    def add_tail_break_mark(sentences):
        if LANGUAGE == "jap":
            return sentences
        return [sentence + "[uv_break]" for sentence in sentences]

