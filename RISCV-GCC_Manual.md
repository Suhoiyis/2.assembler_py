# RISC-V GCC应用开发工具链 说明

## 使用[RISC-V GCC应用开发工具链](https://github.com/ilg-archived/riscv-none-gcc/releases)  

<u>交叉编译是指在一个平台上生成另一个平台的可执行代码的过程</u>  

使用预编译工具链。_gnu-mcu-eclipse-riscv32-none-gcc-8.2.0-2.2-20190521-0004-win64_ 是一个由 _GNU MCU Eclipse_ 项目提供的、适用于 Windows 64 位系统的 RISC-V 32 位交叉编译工具链。这个工具链主要用于裸机嵌入式开发（bare-metal embedded development），适用于开发基于 RISC-V 架构的微控制器  

|           工具            |              说明                 |
|:------------------------:|:---------------------------------:|
|riscv-none-embed-gcc      |GCC 编译器，用于编译 RISC-V 裸机程序   |
|riscv-none-embed-g++      |C++ 编译器                          |
|riscv-none-embed-objcopy  |将 ELF 文件转换为二进制文件（如 .bin）  |
|riscv-none-embed-size     |查看程序的内存占用情况                 |
|riscv-none-embed-objdump  |反汇编 ELF 文件                      |
|riscv-none-embed-gdb      |GDB 调试器，用于调试嵌入式程序         |

RISC-V ELF（Executable and Linkable Format）文件是一种用于可执行文件、目标代码、共享库和核心转储的标准文件格式。ELF 文件格式是跨平台的，支持多种架构，包括 RISC-V。对于 RISC-V 架构而言，ELF 文件不仅包含了程序代码，还包括了数据、符号表、重定位信息等，这些对链接器和加载器来说至关重要。  

***

### 使用流程：  
安装好工具链后（ ___目标.c文件,start.S,os.ld在同一文件夹下___）

1.生成目标程序`.elf`  
`riscv-none-embed-gcc -nostdlib -fno-builtin -march=rv32im -T os.ld  -o main.elf main.c start.S`

2.生成二进制文件`.bin`  
`riscv-none-embed-objcopy -O binary main.elf main.bin`  

上板

.c文件是ppt里要求三个的：`流水LED灯` `时钟显示` `UART数据接收/显示`  

***

### `start.S` (汇编启动代码)
这是程序的真正入口点。当 RISC-V 芯片上电或复位时，它会从一个固定的地址（在 os.ld 中定义为 0x00000000）开始执行 。这个文件就在那个地址。  
它的主要工作是为 C 语言代码准备好运行环境，因为 C 语言需要一些基本的内存设置才能正常工作。

这个文件主要做了四件事：

1. 复制 `.data` 段：  
    - `la a0, _data_lma`：加载 `.data` 段在 Flash (LMA, Load Memory Address) 中的 存储 地址 。  
    - `la a1, _data_start`：加载 `.data` 段在 RAM (VMA, Virtual Memory Address) 中的 运行 地址 。  
    - `lw/sw` 循环：将已初始化的全局变量从 Flash（只读）复制到 RAM（可读写）中。  

2. 清零 `.bss` 段：  
    - `la a0, _bss_start`：获取 `.bss` 段的起始地址 。  
    - `sw zero, (a0)` 循环：将所有未初始化的全局变量的内存区域全部设置为 0。  

3. 设置栈指针 (Stack Pointer)：  
`la sp, _stack_end`：设置栈指针 sp 。C 语言函数调用和局部变量都需要栈。  


4. 跳转到 C 代码：  
`j start_kernel`：当 C 语言环境准备好后，跳转到 `main.c` 文件中（使用的.c文件）`start_kernel` 函数，开始执行 C 代码。


***
### `os.ld` (链接器脚本)  
这是一个蓝图，它告诉链接器（`ld`，`gcc` 会自动调用它）如何组织所有的代码和数据，并将它们放入您定义的内存区域中。

它的主要作用是：

1. 定义入口点：  
    - `ENTRY(_start)`：告诉链接器，程序的入口是 `start.S` 文件中定义的 `_start` 标签 。

2. 定义内存布局 (MEMORY)：  
    - `flash (ORIGIN = 0x00000000, LENGTH = 16K)`：定义了一个名为 `flash` 的 16K 大小的只读内存区域（ROM），CPU 从这里启动 。  
    - `ram (ORIGIN = 0x10000000, LENGTH = 8K)`：定义了一个名为 `ram` 的 8K 大小的可读写内存区域（RAM） 。  

1. 定义段 (SECTIONS)：  
    - `.text : { ... } >flash AT>flash`：告诉链接器把所有可执行代码（`.text` ）和只读数据（`.rodata` ）都放到 `flash` 区域。  
    - `.data : { ... } >ram AT>flash`：这是最关键的一行。  
        - `>ram`：告诉链接器，`.data` 段（已初始化的变量）在 运行时 应该位于 `ram` 中 。

        - `AT>flash`：告诉链接器，在 生成 `a.elf` 文件时，把 `.data` 段的初始值 存储 在 `flash` 区域的末尾（紧跟在 `_data_lma` 之后 ）。

        - 这就是为什么 `start.S` 必须执行复制操作的原因：链接器把数据存在 `Flash`，`start.S` 负责在启动时把它搬运到 `RAM`。

    - `.bss : { ... } >ram AT>flash`：告诉链接器 `.bss` 段（未初始化的变量）在 运行时 也位于 `ram` 中 。

***
## 编译命令：

### `riscv-none-embed-gcc -nostdlib -fno-builtin -march=rv32im -T os.ld -o a.elf main.c start.S`

`riscv-none-embed-gcc`：安装的 `RISC-V` 交叉编译器。

`-nostdlib / -fno-builtin`：告诉编译器不要链接 C 标准库（`printf`, `malloc` 等）。因为这是裸机环境，没有操作系统来支持这些标准库函数。


`-march=rv32im`：指定目标 CPU 架构是 32 位 RISC-V，包含整数 (I) 和乘除 (M) 扩展 。

`-T os.ld`：告诉编译器“不要使用默认的链接脚本，必须使用 `os.ld` 这个内存地图”。

`-o a.elf`：指定输出文件的名字叫 `a.elf`。

`main.c start.S`：指定输入的源文件。编译器会分别编译 `main.c` 和汇编 `start.S`，然后把它们链接在一起。

***
### `riscv-none-embed-objcopy -O binary main.elf main.bin` 

作用是将编译链接生成的 **ELF 格式**可执行文件转换为**纯二进制（Binary）格式**文件。

拆解为以下几个部分：

1.  **`riscv-none-embed-objcopy`**:
    * 这是 GNU Binutils 工具集中的一个程序，专门用于处理目标文件（Object Copy）。
    * 功能是将一种对象文件格式的内容复制到另一种格式中，或者提取/修改其中的数据。

2.  **`-O binary` (Output Binary)**:
    * 一个非常关键的参数，指定了**输出文件的格式**。
    * `binary` 表示生成一个没有任何元数据（Metadata）、头文件（Header）或调试信息的“纯粹”数据文件。
    * 在这个文件中，字节的排列顺序直接对应于将要写入到硬件内存（Flash/ROM）中的实际字节顺序。

3.  **`main.elf`**:
    * **输入文件**。
    * ELF (Executable and Linkable Format) 是 Linux 和嵌入式系统中标准的二进制文件格式。它包含了很多额外信息，比如：
        * 代码段 (`.text`)、数据段 (`.data`) 在内存中的地址。
        * 符号表（函数名、变量名）。
        * 调试信息（源代码行号）。
        * 程序头（Program Header），告诉操作系统如何加载程序。
    * **问题**：您的裸机 RISC-V CPU 并没有操作系统来解析这些复杂的头文件信息。它只知道“从地址 0x00000000 开始执行指令”。如果直接把 `.elf` 烧录进去，CPU 会把 ELF 的头文件数据当成指令执行，导致立刻崩溃。

4.  **`main.bin`**:
    * **输出文件**。
    * 只包含程序的实际机器码和数据，没有任何“包装”。
    * 例如，如果您的程序第一条指令是 `nop` (机器码 `0x00000013`)，那么 `main.bin` 文件的头 4 个字节就是 `13 00 00 00`。
    * 这就是您可以直接通过串口下载到 RAM 或烧录到 Flash 中的文件格式。

#### 小结

* **ELF 文件**：给调试器（GDB）和操作系统看的，包含“说明书”。
* **BIN 文件**：给裸机 CPU 看的，只有“干货”（指令和数据）。

这条指令就是把“带说明书的产品”拆包，只留下“产品本身”，以便直接塞进芯片里运行。


## 总结：它们如何协同工作
使用编译命令 (gcc) 来编译 main.c (C代码) 和 start.S (启动代码)。

gcc 调用链接器，链接器读取链接器脚本 (os.ld) 作为蓝图。

os.ld 指示链接器：

把 start.S 中的 _start 作为程序入口 。

把代码（.text）放在 Flash 。

把数据（.data）的初始值存放在 Flash，但告诉程序它运行时在 RAM 。


为 .bss 和栈（stack）在 RAM 中预留空间 。


最终生成 a.elf 文件。当运行它时：

CPU 首先执行 start.S 的 _start。

start.S 根据 os.ld 定义的地址，把数据从 Flash 复制到 RAM，并清空 .bss。

start.S 设置好栈指针。

start.S 跳转到 main.c 中的 start_kernel 函数，您的 C 代码开始正式运行。
