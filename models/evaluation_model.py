import numpy as np


class EvaluationModel:
    def __init__(self):
        pass

    @staticmethod
    def _word_matching_similarity(text1, text2):
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common_words = words1.intersection(words2)
        all_words = words1.union(words2)
        return len(common_words) / len(all_words)

    @staticmethod
    def _sigmoid_duration_score(duration1, duration2, k=1.0):
        """
        计算基于 Sigmoid 函数的发音时长得分。

        :param duration1: 你的发音时长
        :param duration2: 标准发音时长
        :param k: Sigmoid 函数的斜率参数，用于控制得分变化的速率
        :return: 得分，范围在 [-1, 1] 之间
        """
        diff = duration1 - duration2
        score = 2 / (1 + np.exp(-k * diff)) - 1
        return - score

    def eval(self, sentence1, sentence2, duration1, duration2):
        v1 = self._word_matching_similarity(sentence1, sentence2)
        v2 = self._sigmoid_duration_score(duration1, duration2)
        return 0.5 * (v1 + v2)
