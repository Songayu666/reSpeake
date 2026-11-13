# reSpeake

一个为 **ReSpeaker USB Mic Array** 制作的 360° 声音方向雷达。它先在电脑上完成
声源方向、VAD 和可视化验证，未来可以无缝迁移到机器狗的 ROS 2 感知系统。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/License-MIT-green)

## 当前功能

- 浏览器中的 360° 声源雷达
- 实时显示 DOA 方向与 VAD 状态
- 最近声源方向轨迹
- 无硬件也能运行的模拟模式
- 为 ReSpeaker 硬件接入预留统一接口
- 零 Web 框架依赖，Python 标准库即可启动

## 快速开始

```bash
python -m respeake.app
```

打开 <http://127.0.0.1:8765>。默认使用模拟数据，移动页面上的角度滑块即可测试。

指定监听地址或端口：

```bash
python -m respeake.app --host 0.0.0.0 --port 9000
```

## 接入真实 ReSpeaker

当前版本先把 UI、事件模型和设备抽象跑通。下一步将接入 Seeed 的
`usb_4_mic_array` Python 3 驱动，读取 `DOAANGLE` 与 VAD，并同步控制 LED 环。

硬件资料：<https://wiki.seeedstudio.com/ReSpeaker-USB-Mic-Array/>

> 该型号已经 EOL；本项目主要服务已有设备和原型开发。

## 路线图

- [ ] ReSpeaker DOA/VAD USB 驱动
- [ ] 12 颗 RGB LED 与雷达方向同步
- [ ] 音量与语音活动时间线
- [ ] 本地唤醒词
- [ ] Whisper 转写
- [ ] 摄像头人物与声源方向匹配
- [ ] ROS 2 消息输出

## 目录

```text
respeake/
├── app.py       # HTTP API 与静态页面服务
├── model.py     # 线程安全的雷达状态
├── sources.py   # 模拟/硬件数据源
└── web/         # 浏览器界面
```

## License

MIT

