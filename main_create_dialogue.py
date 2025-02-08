from utils import Utils
from config import *

if __name__ == '__main__':

    utils = Utils()
    key = input("1.根据话题创建对话？2.根据随机选词聊创建对话（仅限英文模型下）？ 1 or 2")
    if key.strip() == "1":
        topic = Utils.pop_topic(TOPIC_PATH,False)
        Utils.record2history([topic], TOPIC_HISTORY_PATH)
        print(utils.pack_prompt_by_topic(topic, EPISODE_LEN, LANGUAGE))
        print("复制以上内容，打开豆包生成对话，再粘贴到dialogue_board.txt")
    elif key.strip() == "2":
        assert LANGUAGE == "en"
        vocab_list = utils.select()
        res = utils.pack_prompt_by_list(vocab_list)
        print(res)
        print("复制以上内容，打开豆包生成对话，再粘贴到dialogue_board.txt")
    else:
        print("按1 or 2，请重试")
