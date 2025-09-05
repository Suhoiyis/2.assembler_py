## 电子科技大学信息与软件工程学院2025-2026学年第一学期（大三上）数字信息处理 综设III
### 一个32位RISC-V单周期CPU硬件及其SoC系统的设计与构建
本人目前负责的部分与上学期类似，仍然是读取输入的指令、将其转化为32位机器码并输出

_（上学期内容[assembler_py](https://github.com/Suhoiyis/assembler_py/tree/v2.0.0)）_

***
与上学期的不同之处于：  
1.现在使用32位机器码  
2.拓展了指令集的丰富度
***
代码内容仍旧在`src`文件夹里  
使用说明参见`manual.md`  
开发日志参见`Development_Log.md`  
输入输出数据在`data`文件夹里  
输入数据为`input.txt`，输出数据为`output.txt`  
素材在`material`文件夹里
***
<2.assembler_py>/  
|-- src/  
|--|-- assembler.py   (Python汇编器脚本)  
|  
|-- data/  
|--|-- input.txt      (存放汇编指令)  
|--|-- output.txt     (保存生成的32位机器码)  
|  
|-- material/  
|--|-- pngs/ (图片素材)  
|--|-- registers.md    (寄存器说明)  
|--|-- codes.md (指令说明)  
|--|-- 指令.ppt  
|  
|-- manual.md (使用说明)  
|-- Development_Log.md (开发日志)  
|-- README.md (本文件)  
***
##### 保持`main`分支，与最新发行版`Releases`一致，准确无误  
##### `dev`应是最新进展的开发记录
