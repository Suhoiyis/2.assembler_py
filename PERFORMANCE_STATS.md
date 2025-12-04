# RISC-V ISS 性能统计功能

## 概述

ISS 内置性能计数器，可以在程序执行后自动输出详细的性能分析数据。这个功能对于：
- 理解程序的指令执行模式
- 优化关键路径中的循环和分支
- 评估乘除法等昂贵操作的使用频率
- 验证预期的指令分布

## 性能指标说明

### 基础指标

| 指标 | 说明 |
|------|------|
| **Total Instructions** | 执行的总指令数（不含停机指令） |
| **Total Cycles** | 执行消耗的总周期数（当前模型：1 指令 = 1 周期） |
| **CPI** | 每条指令平均周期数（Cycles Per Instruction）<br/>计算：Total Cycles / Total Instructions |

### 指令分类统计

| 指令类别 | 包含指令 | 用途 |
|---------|---------|------|
| **Branch Instructions** | BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL, JALR | 控制流指令<br/>taken: 分支条件成立数<br/>not taken: 分支条件不成立数 |
| **Load Instructions** | LB, LH, LW, LBU, LHU | 从内存读取数据 |
| **Store Instructions** | SB, SH, SW | 将数据写入内存 |
| **Multiply Instructions** | MUL, MULH, MULHSU, MULHU | RV32M 乘法运算 |
| **Divide Instructions** | DIV, DIVU, REM, REMU | RV32M 除法和取余运算 |
| **Other Instructions** | ADD, SUB, AND, OR, XOR, 等 | 其他所有指令 |

## 性能统计示例

### 示例 1：简单计数循环（test_loop.asm）

```
Total Instructions:     22
Total Cycles:           22
CPI (Cycles/Instr):     1.00

Branch Instructions:    5 (taken: 4, not taken: 1)
Load Instructions:      0
Store Instructions:     0
Multiply Instructions:  0
Divide Instructions:    0
Other Instructions:     17
```

**分析**：
- 程序执行 22 条指令
- 分支密度：5/22 ≈ 23%
- 分支命中率（taken）：4/5 = 80%（说明循环大部分时间分支被执行）
- 无内存操作，无乘除法

### 示例 2：乘法测试（test_mul.asm）

```
Total Instructions:     6
Total Cycles:           6
CPI (Cycles/Instr):     1.00

Branch Instructions:    0 (taken: 0, not taken: 0)
Load Instructions:      0
Store Instructions:     0
Multiply Instructions:  1
Divide Instructions:    0
Other Instructions:     5
```

**分析**：
- 非常短的程序（6 条指令）
- 包含 1 个 MUL 运算
- 其他 5 条指令用于设置操作数和加载结果

### 示例 3：内存操作测试（test_memory.asm）

```
Total Instructions:     5
Total Cycles:           5
CPI (Cycles/Instr):     1.00

Branch Instructions:    0 (taken: 0, not taken: 0)
Load Instructions:      1
Store Instructions:     1
Multiply Instructions:  0
Divide Instructions:    0
Other Instructions:     3
```

**分析**：
- 程序包含 1 个 STORE + 1 个 LOAD
- 其他指令用于设置地址和操作数
- 在实际硬件中，这个程序会因为内存延迟而需要 5+ 周期

## CPI 解释

**CPI (Cycles Per Instruction)** 是衡量 CPU 效率的关键指标。

### 当前 ISS 模型

当前 ISS 采用的是**理想 1-周期 CPI 模型**：
- 每条指令恰好消耗 1 个周期
- CPI 始终为 1.00
- 这反映了一个完全流水化、无冲突的理想 CPU

### 实际硬件中的 CPI

真实处理器的 CPI 通常 > 1，原因包括：

| 原因 | 周期增加 |
|------|---------|
| 分支预测失误 | +1 到 +5 周期 |
| 内存访问延迟 | +10 到 +100+ 周期 |
| 乘法操作 | +3 到 +10 周期 |
| 除法操作 | +10 到 +40 周期 |
| 流水线冲突 | 变化 |

### 将来的扩展

可以通过为不同指令类型设置不同的"延迟权重"来模拟实际 CPI：

```cpp
// 伪代码示例
case MUL:
    stats.cycle_count += 3;  // MUL 消耗 3 周期
    break;
case LW:
    stats.cycle_count += 5;  // 内存访问消耗 5 周期
    break;
```

## 使用场景

### 1. 验证循环优化

编写两个版本的循环：
```asm
# 版本 1：简单循环
loop:
    addi x1, x1, 1
    bne x1, x2, loop

# 版本 2：循环展开（Unrolling）
loop:
    addi x1, x1, 1
    addi x1, x1, 1
    addi x1, x1, 1
    bne x1, x2, loop
```

对比的性能统计数据，观察分支密度变化。

### 2. 评估乘法操作的成本

编写一个包含大量乘法的程序，统计 Multiply Instructions 的比例。

### 3. 内存占比分析

编写矩阵乘法程序，统计 Load/Store 指令的比例。

## 性能计数器的实现

### 数据结构

```cpp
struct Stats {
    uint64_t instruction_count;      // 执行的总指令数
    uint64_t cycle_count;             // 执行的总周期数
    uint64_t branch_count;            // 分支指令总数
    uint64_t branch_taken_count;      // 分支条件成立的次数
    uint64_t load_count;              // 加载指令数
    uint64_t store_count;             // 存储指令数
    uint64_t mul_count;               // 乘法指令数
    uint64_t div_count;               // 除法/取余指令数
};
```

### 计数位置

每条指令执行时，相应的计数器在 `fetch_and_decode_execute()` 函数中自动更新：

```cpp
void RiscvISS32::fetch_and_decode_execute() {
    // 每条指令开始时
    stats.instruction_count++;
    stats.cycle_count++;
    
    // 根据指令类型进一步计数
    switch(opcode) {
        case 0x33:  // R-type
            if (funct3 == 0 && funct7 == 1) {  // MUL
                stats.mul_count++;
            }
            break;
        case 0x63:  // B-type
            stats.branch_count++;
            if (branch_taken) {
                stats.branch_taken_count++;
            }
            break;
        // ... 其他指令类型
    }
}
```

## 性能统计输出格式

每次执行程序完成后，ISS 自动打印格式化输出：

```
========== Performance Statistics ==========
Total Instructions:     <数值>
Total Cycles:           <数值>
CPI (Cycles/Instr):     <计算值>

--- Instruction Breakdown ---
Branch Instructions:    <总数> (taken: <数值>, not taken: <数值>)
Load Instructions:      <数值>
Store Instructions:     <数值>
Multiply Instructions:  <数值>
Divide Instructions:    <数值>
Other Instructions:     <数值>
===========================================
```

## 编程建议

### 如何解读性能统计

1. **理解分支行为**
   ```
   Branch Instructions: 10 (taken: 9, not taken: 1)
   // 说明：非常高的分支命中率（90%）
   // 可能表示紧密循环，预测友好
   ```

2. **识别内存瓶颈**
   ```
   Load Instructions: 50
   Store Instructions: 40
   Total Instructions: 100
   // 90/100 = 90% 的指令是内存操作
   // 这是内存密集型程序，可能需要缓存优化
   ```

3. **评估计算复杂度**
   ```
   Multiply Instructions: 30
   Divide Instructions: 5
   Total Instructions: 200
   // (30 + 5) / 200 = 17.5% 的指令是乘除法
   // 可能需要考虑乘法器性能
   ```

## 常见问题

### Q: 为什么我的程序 CPI 总是 1.00？

A: 当前 ISS 使用理想 1-周期模型。在将来的版本中，可以通过为不同指令类型分配不同权重来模拟真实 CPI。

### Q: 分支命中率如何计算？

A: `分支命中率 = branch_taken / branch_count`

例如：4 taken / 5 total = 80% 命中率

### Q: 如何关闭性能统计输出？

A: 可以注释掉 `main.cpp` 中的 `sim.print_stats();` 调用。

### Q: 为什么 Load Instructions 计数有时为 0？

A: 因为程序中没有使用 LB, LH, LW, LBU, LHU 这些指令。可以通过编写测试程序验证。

## 扩展思路

### 1. 添加更多性能指标

```cpp
struct Stats {
    // ... 现有字段 ...
    
    // 可添加的新字段
    uint64_t cache_hits;         // 缓存命中数（模拟）
    uint64_t cache_misses;       // 缓存未命中数
    uint64_t stall_cycles;       // 停滞周期数
    uint64_t forward_count;      // 寄存器转发次数
};
```

### 2. 分支预测模拟

```cpp
// 简单的分支历史表（BHT）模拟
class BranchPredictor {
    std::map<uint32_t, bool> history;  // PC -> 上次是否 taken
public:
    bool predict(uint32_t pc);
    void update(uint32_t pc, bool was_taken);
};
```

### 3. 内存层次模型

```cpp
// 模拟 L1/L2 缓存的内存访问延迟
class MemoryHierarchy {
    const int L1_HIT_LATENCY = 1;
    const int L2_HIT_LATENCY = 10;
    const int DRAM_HIT_LATENCY = 100;
public:
    int get_latency(uint32_t addr);
};
```

### 4. 能耗估计

```cpp
// 根据指令类型和内存访问估计能耗
struct PowerModel {
    static const int ALU_POWER = 1;       // mW
    static const int MUL_POWER = 10;      // mW
    static const int DRAM_POWER = 100;    // mW
public:
    int estimate_power(const Instruction& inst);
};
```

## 总结

性能统计功能提供了：
✓ 对程序执行特性的定量分析
✓ 识别性能瓶颈的基础数据
✓ 验证优化效果的量化指标
✓ 教学中理解 ISA 执行特性的工具

通过分析这些统计数据，可以更深入地理解 RISC-V 指令集和处理器微架构的相互关系。
