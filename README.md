# reSpeake

一个为 **ReSpeaker USB Mic Array** 制作的 360° 声音方向雷达。它先在电脑上完成
声源方向、VAD 和可视化验证，未来可以无缝迁移到机器狗的 ROS 2 感知系统。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/License-MIT-green)

## 当前功能

- 浏览器中的 360° 声源雷达
- 实时显示 DOA 方向与 VAD 状态
- 最近声源方向轨迹
- 自动发现 `2886:0018` ReSpeaker，读取真实 DOA/VAD
- LED 环自动进入 VAD/DOA 跟随模式
- 六通道 ALSA 采集并提取 DSP 处理后的 Channel 0
- 真实 RMS / dBFS 音量显示
- VAD 自动分段并在本地保存单声道 WAV
- 网页语音时间线
- 无硬件也能运行的模拟模式
- 为 ReSpeaker 硬件接入预留统一接口
- 零 Web 框架依赖，Python 标准库即可启动

## 快速开始

```bash
python -m respeake.app
```

打开 <http://127.0.0.1:8765>。程序会自动连接 ReSpeaker；未发现设备时回退到模拟数据。

指定监听地址或端口：

```bash
python -m respeake.app --host 0.0.0.0 --port 9000
```

安装硬件依赖并强制使用真实设备：

```bash
python -m pip install -e '.[hardware]'
python -m respeake.app --source hardware
```

自动录音保存在本地 `recordings/`，该目录已加入 `.gitignore`，不会上传到公开仓库。
可使用 `--no-audio` 禁用音频采集，或通过 `--recordings-dir` 修改保存目录。

Linux 用户如果遇到 `Access denied`，安装仓库提供的 udev 规则：

```bash
sudo install -m 0644 config/60-respeaker.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb --attr-match=idVendor=2886
```

重新插拔设备后再运行。不要长期用 root 运行网页服务。

硬件资料：<https://wiki.seeedstudio.com/ReSpeaker-USB-Mic-Array/>

> 该型号已经 EOL；本项目主要服务已有设备和原型开发。

## 路线图

- [x] ReSpeaker DOA/VAD USB 驱动
- [x] 12 颗 RGB LED 与雷达方向同步
- [x] 音量与语音活动时间线
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

