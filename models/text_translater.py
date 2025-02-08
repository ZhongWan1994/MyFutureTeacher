from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import MarianTokenizer, MarianMTModel


class Translator:
    def __init__(self, en_zh_model_path, zh_en_model_path):
        self.en_zh_tokenizer = MarianTokenizer.from_pretrained(en_zh_model_path)
        self.en_zh_model = MarianMTModel.from_pretrained(en_zh_model_path)
        self.zh_en_tokenizer = AutoTokenizer.from_pretrained(zh_en_model_path)
        self.zh_en_model = AutoModelForSeq2SeqLM.from_pretrained(zh_en_model_path)

    def translate_en_to_zh(self, input_text):
        input_ids = self.en_zh_tokenizer(input_text, return_tensors="pt").input_ids
        outputs = self.en_zh_model.generate(input_ids)
        translated_text = self.en_zh_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

    def translate_zh_to_en(self, chinese_text):
        input_ids = self.zh_en_tokenizer(chinese_text, return_tensors="pt").input_ids
        outputs = self.zh_en_model.generate(input_ids)
        translated_text = self.zh_en_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

