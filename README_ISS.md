# RISC-V 32-bit 软件 ISS（指令集模拟器）

一个用 C++ 实现的 RISC-V 32 位硬件指令集模拟器（ISS），支持 **RV32I + RV32M** 指令集。可加载由 `assembler.py` 生成的机器码，执行并验证汇编代码的正确性。

## 项目结构

```
2.assembler_py/
├── src/
│   ├── assembler.py          # Python 汇编器（生成机器码）
│   └── cpp/
│       ├── iss.h             # ISS 类声明
│       ├── iss.cpp           # ISS 核心实现（存储、译码、执行、调试）
│       └── main.cpp          # 主程序入口
├── tests/
│   ├── test_li_add.asm       # 测试 1: 加法运算 (expecting x2=20)
│   ├── test_loop.asm         # 测试 2: 循环计数 (expecting x1=5)
│   ├── test_memory.asm       # 测试 3: 内存读写 (expecting x3=42)
│   ├── test_mul.asm          # 测试 4: MUL 乘法 (expecting x3=21) [RV32M]
│   ├── test_div.asm          # 测试 5: DIV 除法 (expecting x3=8) [RV32M]
│   ├── test_rem.asm          # 测试 6: REM 取余 (expecting x3=2) [RV32M]
│   └── *.bin                 # 生成的机器码文件
├── build/
│   └── iss                   # 编译出的 ISS 可执行文件
├── run_tests.py              # 自动化测试脚本
├── data/
│   └── output.txt            # assembler.py 输出的机器码
└── README.md                 # 本文件
```

## 快速开始

### 1. 编译 ISS

```bash
mkdir -p build
g++ -std=c++17 -O2 \
    -I./src/cpp \
    -o build/iss \
    src/cpp/iss.cpp src/cpp/main.cpp
```

### 2. 运行示例程序

以下两种方式均可：

#### 方式 A：运行原有的大程序
```bash
./build/iss data/output.txt
```

### 3. 查看性能统计

ISS 每次执行程序后自动输出性能统计：

```bash
./build/iss tests/test_loop.bin
```

输出示例：
```
========== Performance Statistics ==========
Total Instructions:     22
Total Cycles:           22
CPI (Cycles/Instr):     1.00

--- Instruction Breakdown ---
Branch Instructions:    5 (taken: 4, not taken: 1)
Load Instructions:      0
Store Instructions:     0
Multiply Instructions:  0
Divide Instructions:    0
Other Instructions:     17
===========================================
```

**性能指标说明：**
- **Total Instructions**：执行的总指令数
- **Total Cycles**：执行消耗的总周期数
- **CPI**：每条指令平均周期数（Cycles Per Instruction）
- **Instruction Breakdown**：各类型指令的统计
  - 分支指令：条件分支（B-type）和无条件跳转（JAL）
  - 取值指令：所有 LOAD 操作
  - 存储指令：所有 STORE 操作
  - 乘法指令：MUL、MULH、MULHSU、MULHU
  - 除法指令：DIV、DIVU、REM、REMU
  - 其他指令：算术、逻辑、立即数等

#### 方式 B：运行单个小测试
```bash
./build/iss tests/test_li_add.bin      # 测试加法：x2 should = 20
./build/iss tests/test_loop.bin        # 测试循环：x1 should = 5
./build/iss tests/test_memory.bin      # 测试内存：x3 should = 42
./build/iss tests/test_mul.bin         # 测试乘法(RV32M)：x3 should = 21
./build/iss tests/test_div.bin         # 测试除法(RV32M)：x3 should = 8
./build/iss tests/test_rem.bin         # 测试取余(RV32M)：x3 should = 2
```

### 3. 运行完整自动化测试

```bash
python3 run_tests.py
```

输出示例：
```
==================================================
RISC-V ISS Automated Test Suite
==================================================

[Test 1] lui+addi+add
  x1=10 (expect 10)
  x2=20 (expect 20)
  ✓ PASS

[Test 2] loop with counter
  x1=5 (expect 5)
  x10=5 (expect 5)
  ✓ PASS

[Test 3] memory sw/lw
  x1=42 (expect 42)
  x3=42 (expect 42)
  ✓ PASS

[Test 4] MUL (RV32M)
  x1=3 (expect 3)
  x2=7 (expect 7)
  x3=21 (expect 21)
  ✓ PASS

[Test 5] DIV (RV32M)
  x1=42 (expect 42)
  x2=5 (expect 5)
  x3=8 (expect 8)
  ✓ PASS

[Test 6] REM (RV32M)
  x1=42 (expect 42)
  x2=5 (expect 5)
  x3=2 (expect 2)
  ✓ PASS

==================================================
Summary: 6/6 tests passed
==================================================
```

## 核心模块说明

### 1. 存储模型（Memory & Register Model）

- **寄存器堆**：32 个 32-bit 通用寄存器 (x0-x31)，x0 恒为 0
- **内存**：64 KB 线性寻址空间，采用小端字节序
- **程序计数器（PC）**：32-bit，初始为 0

**关键函数**：
- `read_word(addr)` / `write_word(addr, val)` - 小端 4 字节读写
- `read_half(addr)` / `write_half(addr, val)` - 小端 2 字节读写
- `read_byte(addr)` / `write_byte(addr, val)` - 字节读写
- `set_reg(idx, val)` - 寄存器写入（自动保证 x0=0）

### 2. 指令加载器（Loader）

支持三种格式：
1. **32-bit 二进制文本**：assembler.py 的默认输出（每行 32 个 0/1）
2. **16 进制文本**：每行一个 32-bit 16 进制数
3. **原始二进制**：.bin 文件直接读入

**关键函数**：
- `load_program(filename)` - 自动检测格式并加载

### 3. 译码单元（Decoder）

支持完整的 RV32I 指令集：

**R-Type** (Register-Register Operations)
- ADD, SUB, AND, OR, XOR, SLL, SRL, SRA
- SLT, SLTU

**I-Type** (Register-Immediate Operations)
- ADDI, ANDI, ORI, XORI, SLTI, SLTIU
- SLLI, SRLI, SRAI

**I-Type Load**
- LB, LH, LW (字节/半字/字读)
- LBU, LHU (无符号字节/半字读)

**S-Type Store**
- SB, SH, SW (字节/半字/字写)

**B-Type Branch**
- BEQ, BNE, BLT, BGE, BLTU, BGEU

**J-Type Jump**
- JAL, JALR

**U-Type & Pseudo**
- LUI, AUIPC

**RV32M 乘除法扩展**
- MUL, MULH, MULHSU, MULHU (乘法及高位结果)
- DIV, DIVU (有符号/无符号除法)
- REM, REMU (有符号/无符号取余)
- 支持除零检查：除以零返回 -1，取余零返回被除数

**Halt**
- 全 0 指令（0x00000000）表示停机

**关键函数**：
- `decode_i_imm(inst)` - I-Type 立即数提取与符号扩展
- `decode_s_imm(inst)` - S-Type 立即数
- `decode_b_imm(inst)` - B-Type 立即数
- `decode_j_imm(inst)` - J-Type 立即数

### 4. 执行单元（Execution Engine）

- `fetch_and_decode_execute()` - 单个指令的完整周期
- `step()` - 执行一条指令
- `run_until_halt()` - 运行至停机

所有指令均以大 switch-case 结构实现，支持有符号/无符号比较、算术右移等细节。

### 5. 调试接口（Debug Interface）

**寄存器输出**：
```
dump_regs()  // 输出所有 32 寄存器 + PC，格式：
// x0=00000000
// x1=0000000a
// ...
// PC=00000070
```

**内存输出**：
```
dump_memory(addr, len)  // 16 字节/行的 Hex Dump
```

## 验证与测试

完整的自动化测试脚本 `run_tests.py` 包含：
1. **汇编编译** → assembler.py 调用
2. **ISS 执行** → 运行机器码
3. **结果验证** → 检查寄存器值

当前已通过的测试：
- ✓ 算术运算（加法）
- ✓ 循环与分支
- ✓ 内存读写
- ✓ 乘法运算（RV32M）
- ✓ 除法运算（RV32M）
- ✓ 取余运算（RV32M）

**总计：6/6 自动化测试通过**

## 设计亮点

1. **完整 RV32I + RV32M 支持** - 40+ 条指令，包含乘除法
2. **小端内存模型** - 与 Linux/ARM 一致，符合 RISC-V 规范
3. **符号扩展处理** - 正确处理立即数的符号位、除以零检查
4. **无缝集成** - ISS 可直接接收 assembler.py 的输出，无需格式转换
5. **自动化测试** - 端到端验证汇编代码正确性

## 后续扩展计划

- [x] RV32M 乘除法扩展 (MUL, DIV, REM 等) ✓ **已完成**
- [ ] 浮点指令集 (RV32F)
- [ ] 中断与异常处理
- [ ] 与 windows.py 的串口集成（将 ISS 作为虚拟 FPGA）
- [ ] 性能计数（指令数、周期数）

## 使用示例

### 编写新汇编测试

1. 创建 `.asm` 文件 (例如 `test_shift.asm`)：
```asm
# Test: shift operations
lui x1, 0
addi x1, x1, 8
slli x2, x1, 2          # x2 = 8 << 2 = 32
```

2. 使用 assembler.py 生成机器码：
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from assembler import assemble
assemble('test_shift.asm', 'test_shift.bin')
"
```

3. 用 ISS 运行：
```bash
./build/iss test_shift.bin
```

4. 检查寄存器输出中 x2 是否为 32 (0x20)

## 编译与环境要求

- **编译器**：GCC 5.0+ 或 Clang 3.8+（支持 C++17）
- **Python**：3.6+ （用于 assembler.py）
- **OS**：Linux, macOS, Windows (MSYS2/MinGW)

## 简历素材

这个项目展示了：
✓ 低级别硬件模拟能力（寄存器、内存、小端字节序）
✓ 完整指令集解码与执行（32+ 条指令）
✓ 位运算与二进制处理能力
✓ C++ 工程实践（类设计、内存管理、错误处理）
✓ 自动化测试与验证（Python 脚本）
✓ 综合设计与系统集成（与 assembler.py、windows.py 配合）
