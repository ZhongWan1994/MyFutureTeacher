MyFutureTeacher

这是一个自动化的外语口语练习脚本，你需要有4G以上的显存才能在本机正常运行大模型生成语音

1、安装依赖库
2、huggingface的镜像库hf-mirror：https://hf-mirror.com/ 中下载相关大模型到model_weights，若效果不满意，可以自己换一个更大的模型
    2Noise/ChatTTS
    2121-8/japanese-parler-tts-mini-bate
    Helsinki-NLP/opus-mt-en-zh
    Helsinki-NLP/opus-mt-zh-en
    openai/whisper-small 
    
3、elements下的txt为全量的英语单词表，remain文件夹下初始化全量英语单词表，单词抽样后，被抽样的单词转移到history文件夹中
4、运行前，先配置好ini文件

    
    
