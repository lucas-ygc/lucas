---
title: pcm音频格式详解
type: categories
categories: 音视频协议
description: pcm音频格式详解
swiper_index: 1
abbrlink: d3ea8c5e
typora-root-url: ./..\..\..
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
---

# 1、pcm是什么？
pcm是脉冲编码调制，是数字音频的存储格式。

# 2、pcm的组成
pcm音频文件由两部分组成：
1. 头部信息
2. 音频数据

## 2-1、头部信息
头部信息中包含了音频文件的采样率、声道数等信息，用于描述音频文件的属性。

## 2-2、音频数据
音频数据是实际的波形数据，以二进制形式存储在文件中。


# 3、pcm的采样率
采样率是指每秒从录音设备或声音文件里采样的次数，它描述了音频文件的长度。

采样率越高，音频文件的长度就越长。
采样率越低，音频文件的长度就越短。

常见的采样率有：
1. 8kHz：电话
2. 16kHz：CD
3. 22.05kHz：低音炮
4. 44.1kHz：CD
5. 48kHz：DVD

采样率越高，音质就越好。
采样率越低，音质就越差。

采样率越高，文件大小就越大。
采样率越低，文件大小就越小。

用高于采样率的播放器播放高于采样率的音频文件，会降低音质。声音比较尖锐。
用低于采样率的播放器播放低于采样率的音频文件，会降低音质。声音比较模糊、低沉。


# 4、pcm的采样位数

采样位数是指每个采样点占用的二进制位数。
常见的采样位数有：
1. 8位：表示每个采样点占用的二进制位数为8位
2. 16位：表示每个采样点占用的二进制位数为16位
3. 24位：表示每个采样点占用的二进制位数为24位
4. 32位：表示每个采样点占用的二进制位数为32位
采样位数越高，音质越好。
采样位数越低，音质就越差。
采样位数越高，文件大小就越大。
采样位数越低，文件大小就越小。


# 5、pcm的声道数
声道数是描述音频文件中的声音来源和数量的术语。

1. 单声道：只有一个声音源
2. 双声道：有两个声音源

# 6、文件大小
文件大小 = 采样率 * 时长 * 声道数 * 采样位数 / 8

当送数据播放时，如果送的太快，就会造成声音的撕裂。
采样8000Hz，16位，双声道，时长5s的文件大小 = 8000 * 16 * 2 * 5 / 8 = 320kb
可以将16000，转换成8000，只需要将每两个字节删掉一个就可以实现。

双声道有存储顺序问题，需要具体分析。
# 7、pcm的编码格式
pcm音频文件一般不直接播放，需要先进行编码，常见的编码格式有：
1. WAV：微软公司开发的音频文件格式
2. AAC：高级音频编码
3. MP3：高压缩比音频编码
4. OGG：开源音频编码
5. FLAC：无损音频编码
6. AMR：音频码率压缩格式

扩展：
g711：G.711是ITU-T语音编码的推荐标准之一。
g711采样率：8kHz
g711采样位数：8位
g711声道数：单声道
g711编码格式：PCM

调试音频用0db音频文件调试
相关软件Cool Edit Pro。


```c

int convert_sample_rate_8k_to_16k_linear(const int16_t* input_data, int input_size,
                                         int16_t** output_data, int* output_size) {
    // 计算输入样本数
    int input_samples = input_size / sizeof(int16_t);
    
    // 计算输出样本数 (输入的2倍)
    int output_samples = input_samples * 2;
    
    // 分配输出缓冲区
    *output_data = (int16_t*)malloc(output_samples * sizeof(int16_t));
    if (!(*output_data)) {
        printf("无法分配输出缓冲区内存\n");
        return -1;
    }
    
    // 执行线性插值重采样
    for (int i = 0; i < input_samples; i++) {
        // 直接复制原始样本
        (*output_data)[2 * i] = input_data[i];
        
        // 如果不是最后一个样本，进行插值
        if (i < input_samples - 1) {
            // 线性插值: (当前样本 + 下一个样本) / 2
            (*output_data)[2 * i + 1] = (input_data[i] + input_data[i + 1]) / 2;
        } else {
            // 最后一个样本，复制原始值
            (*output_data)[2 * i + 1] = input_data[i];
        }
    }
    
    // 设置输出大小
    *output_size = output_samples * sizeof(int16_t);
    
    printf("重采样完成: 输入%d个样本，输出%d个样本\n", input_samples, output_samples);
    return 0;
}

```