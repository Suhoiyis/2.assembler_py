## 电子科技大学信息与软件工程学院2025-2026学年第一学期（大三上）数字信息处理 综设III
### 一个32位RISC-V单周期CPU硬件及其SoC系统的设计与构建
本人目前负责的部分与上学期类似，仍然是读取输入的指令、将其转化为32位机器码并输出

_（上学期内容[assembler_py](https://github.com/Suhoiyis/assembler_py/tree/v2.0.0)）_

***
与上学期的不同之处于：
1.现在使用32位机器码
2.拓展了指令集的丰富度
3.使用`RISC-V GCC应用开发工具链`
***
代码内容仍旧在`src`文件夹里
使用说明参见`manual.md`
开发日志参见`Development_Log.md`
输入输出数据在`data`文件夹里
输入数据为`input.txt`，输出数据为`output.txt`
素材在`material`文件夹里
RISC-V GCC应用开发工具链相关内容在`src/C`
***

```
<2.assembler_py>/
 ├── 📁 src/
 |   ├── 📁 C/
 |   |    ├── start.S         # 汇编启动代码
 |   |    ├── os.ld           # 链接器脚本
 |   |    └── ***.c(s)        # ppt要求的三个.c文件
 |   |
 |   ├── 🐍 windows.py        # 汇编器的可视化窗口界面
 │   └── 🐍 assembler.py      # Python 汇编器脚本
 │
 ├── 📁 data/
 │   ├── 📁 uart/             # UART 输入输出相关
 │   ├── 📄 input.txt         # 汇编指令输入文件
 │   └── 📄 output.txt        # 汇编生成的 32 位机器码
 │
 ├── 📁 material/
 │   ├── 📁 pngs/             # 图片素材
 │   ├── 📝 registers.md      # 寄存器说明文档
 │   ├── 📝 codes.md          # 指令说明文档
 │   ├── 📊 一个32位....ppt    # 项目总ppt
 │   └── 📊 指令.ppt          # 指令演示文稿
 │
 ├── 📘 manual.md             # .py汇编器使用说明
 ├── 📘 RISCV-GCC_Manual.md   # RISC-V GCC应用开发工具链使用说明
 ├── 📝 Development_Log.md    # 开发日志
 └── 📖 README.md             # 项目说明文件（本文件）
```

***
##### 保持`main`分支，与最新发行版`Releases`一致，准确无误
##### `dev`应是最新进展的开发记录
##### ~~`assembler`是之前错误开发`反汇编器`时的分支，现已废弃~~
##### `cpp`是在[dev(2686e5c)](https://github.com/Suhoiyis/2.assembler_py/tree/2686e5c4eb4f8f03a88e56fafeddcf4640026d0f)分支的基础上，根据Gemini的建议，进一步开发了一个C++写的模拟器,但是与综设的核心要求内容无关，属于个人兴趣开发
