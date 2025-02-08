from dataclasses import dataclass
from typing import Optional

import ChatTTS
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from rubyinserter import add_ruby
from transformers import AutoTokenizer
from config import *



@dataclass(repr=False, eq=False)
class RefineTextParams:
    prompt: str = ""
    top_P: float = 0.7
    top_K: int = 20
    temperature: float = 0.7
    repetition_penalty: float = 1.0
    max_new_token: int = 384
    min_new_token: int = 0
    show_tqdm: bool = True
    ensure_non_empty: bool = True
    manual_seed: Optional[int] = None


@dataclass(repr=False, eq=False)
class InferCodeParams(RefineTextParams):
    prompt: str = "[speed_5]"
    spk_emb: Optional[str] = None
    spk_smp: Optional[str] = None
    txt_smp: Optional[str] = None
    temperature: float = 0.3
    repetition_penalty: float = 1.05
    max_new_token: int = 2048
    stream_batch: int = 24
    stream_speed: int = 12000
    pass_first_n_batches: int = 2


class Text2AudioModel:
    def __init__(self):
        torch._dynamo.config.cache_size_limit = 64
        torch._dynamo.config.suppress_errors = True
        torch.set_float32_matmul_precision('high')
        if LANGUAGE == "jap":
            # 初始化日语模型
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.japanese_model = ParlerTTSForConditionalGeneration.from_pretrained(JAP_TEXT2AUDIO_PATH).to(self.device)
            self.japanese_tokenizer = AutoTokenizer.from_pretrained(JAP_TEXT2AUDIO_PATH)
        elif LANGUAGE == "en":
            # 初始化英语模型
            self.english_chat = ChatTTS.Chat()
            self.english_chat.load(custom_path=EN_TEXT2AUDIO_PATH)

    @staticmethod
    def _is_japanese(text):
        # 简单判断文本是否包含日语字符
        for char in text:
            if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
                return True
        return False

    def text_to_audio(self, text, output_path, speed=SPEED, description=None):
        if self._is_japanese(text):
            # 日语文本处理
            text = add_ruby(text)
            if description is None:
                description = "A female speaker with a slightly high-pitched voice delivers her words at a moderate speed with a quite monotone tone in a confined environment, resulting in a quite clear audio recording."
            max_length = 512
            description_inputs = self.japanese_tokenizer(description, return_tensors="pt", padding=True,
                                                         truncation=True, max_length=max_length)
            input_ids = description_inputs["input_ids"].to(self.device)
            text_inputs = self.japanese_tokenizer(text, return_tensors="pt", padding=True, truncation=True,
                                                  max_length=max_length)
            prompt_input_ids = text_inputs["input_ids"].to(self.device)
            generation = self.japanese_model.generate(
                input_ids=input_ids,
                prompt_input_ids=prompt_input_ids,
            )
            audio_arr = generation.cpu().numpy().squeeze()
            sf.write(output_path, audio_arr, self.japanese_model.config.sampling_rate)
            print(f"音频已成功保存到 {output_path}")
        else:
            # 英语文本处理
            texts = [text]
            params_refine_text = RefineTextParams(
                prompt="",
                top_P=0.7,
                top_K=20,
                temperature=0.7,
                repetition_penalty=1.0,
                max_new_token=384,
                min_new_token=0,
                show_tqdm=True,
                ensure_non_empty=True,
                manual_seed=None,
            )
            params_infer_code = InferCodeParams(
                prompt=speed,
                spk_emb=None,
                spk_smp=None,
                txt_smp=None,
                temperature=0.3,
                repetition_penalty=1.05,
                max_new_token=2048,
                stream_batch=32,
                stream_speed=12000,
                pass_first_n_batches=2
            )

            ws = self.english_chat.infer(texts,
                                         do_text_normalization=True,
                                         params_refine_text=params_refine_text,
                                         params_infer_code=params_infer_code)
            sample_rate = 24000
            sf.write(output_path, ws[0], sample_rate)
            print(f"音频已成功保存到 {output_path}")
