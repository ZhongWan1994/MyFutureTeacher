from transformers import WhisperProcessor, WhisperForConditionalGeneration

from config import *


class Audio2TextModel:
    def __init__(self, language=LANGUAGE):

        self.processor = WhisperProcessor.from_pretrained(AUDIO2TEXT_PATH)
        self.model = WhisperForConditionalGeneration.from_pretrained(AUDIO2TEXT_PATH)
        self.language = self.get_lang(language)
        self.model.config.forced_decoder_ids = None

    @staticmethod
    def get_lang(lang):
        lang_str = "en"
        if lang == "en":
            lang_str = "english"
        elif lang == "jap":
            lang_str = "japanese"
        return lang_str

    def audio2text(self, audio_data, sampling_rate=16000):
        processed = self.processor(
            audio_data,
            sampling_rate=sampling_rate,
            return_tensors="pt",
            return_attention_mask=True
        )
        generate_kwargs = {
            "input_features": processed.input_features,
            "attention_mask": processed.attention_mask,
            "language": self.language,
            "task": "transcribe",
            "forced_decoder_ids": None
        }
        predicted_ids = self.model.generate(**generate_kwargs)
        transcription = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True
        )
        return transcription[0]


