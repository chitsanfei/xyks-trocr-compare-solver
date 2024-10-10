<div align="center">
    <img src="./.assets/icon.png" height="200" alt="xyks-dl-solver"> 
    <h1>xyks-dl-solver</h1>
    <b>小猿口算答题的一个 Deep Learning based OCR 实现</b>
</div>

</br>

<p align="center">
    <a href="https://github.com/chitsanfei/xyks-dl-solver/issues"><img src="https://img.shields.io/github/issues/chitsanfei/xyks-dl-solver"></a>
    <a href="https://github.com/chitsanfei/xyks-dl-solver/forks"><img src="https://img.shields.io/github/forks/chitsanfei/xyks-dl-solver"></a>
    <a href="https://github.com/chitsanfei/xyks-dl-solver"><img src="https://img.shields.io/github/stars/chitsanfei/xyks-dl-solver"></a>
    <a href="https://github.com/chitsanfei/xyks-dl-solver/blob/main/LICENSE"><img src="https://img.shields.io/github/license/chitsanfei/xyks-dl-solver"></a>
    <a href="https://github.com/chitsanfei/xyks-dl-solver"><img src="https://img.shields.io/github/commit-activity/t/chitsanfei/xyks-dl-solver"></a>
</p>

# 前言

很幽默，只是因为群友发了个小猿口算，然后我想着为什么不做一个 DL-based 的 OCR 方案呢，遂写了。

经过实践，机器队打不过人工队，所以各位小朋友放心使用。

# 特点

- 基于微软的 trocr 开源模型，最新最热 transformer 架构模型，天哪，那是接近的！
```
self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-stage1')
self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-stage1')
```
- 引入了输入的随机扰动，放心！
```
x_offset = random.randint(-max_offset, max_offset)
y_offset = random.randint(-max_offset, max_offset)
```
- 推理可以运行在 cuda 上。
- 自动下载 ADB！
- 项目 Maintainer 基本不负责更新喵！

# 快速开始
1. 下载：
```git
git clone https://github.com/chitsanfei/xyks-dl-solver
```
2. 安装依赖：
```bash
cd xyks-dl-solver && pip install -r requirements.txt
```
3. （可选）建议你使用 conda 管理依赖，或使用 pyenv，自行查询方案。（小朋友要学会用咕噜咕噜！）

4. 润：
```
python main.py
```
> 特别的，第一次运行可能会生成配置，如果失败了请再次运行一次。

**如果没有显卡，建议小朋友在经济允许的情况下去买一个显卡哦！这样就可以开始你的深度学习之旅了（）**

# 潜在问题

- 只测试过 Windows（尤其是 ADB 自动下载），其它平台的问题，即使有问题，那也就是有问题。
- 模型从抱抱脸下过来，建议使用量子虫洞，抱抱脸下载模型默认路径不在本 repo，建议百度找一找在哪。
- **由于截图需要从 ADB 传输，还要经过推理，本项目荣获小猿口算算法 Speedrun 竞赛倒数**。经十轮测试，青铜段位在有机器人的情况下，约一半持平，3/10 干不过人工队。

# 声明

## 模型使用
- [TrOCR](https://huggingface.co/docs/transformers/en/model_doc/trocr)

## 开源许可

本项目使用 GPL3 开源。
```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```
