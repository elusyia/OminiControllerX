---
title: Omini_ControllerX
category: SOF
author: Elusyia
tags: OMINI
---
## Omini_ControllerX

使用手柄控制VRCLens

src文件结构:
- driver
  - gamepad 手柄的参数读取部分
- plugins
  - omini_controller omini控制器的osc参数
  - vrclens vrclens的osc参数
- drone.py 继承了gamepad的类, 将手柄抽象为无人机, 也负责空间计算
- main.py 主程序逻辑, 在这里配置键位
