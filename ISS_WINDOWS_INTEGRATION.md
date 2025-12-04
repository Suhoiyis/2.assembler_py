# ISS 与 Windows.py 集成指南

## 概述

本指南说明如何将 RISC-V ISS 集成到 `windows.py` GUI 中，使用户可以在不需要 FPGA 硬件的情况下执行和调试汇编代码。

## 集成目标

**当前状态**：
- windows.py：汇编代码编辑器 + 汇编器（生成机器码）
- ISS：独立的命令行工具

**目标状态**：
- windows.py：汇编代码编辑器 + 一键执行 + 结果显示
- 用户可选择：在 ISS 上运行（快速调试）或在 FPGA 上运行（实际验证）

## 实现方案

### 方案 A：快速集成（推荐，2 小时）

在 windows.py 的按钮面板中添加一个"Run on Simulator"按钮。

#### 1. 添加必要的导入

在 `windows.py` 顶部添加：

```python
import subprocess
import re
import os
```

#### 2. 在主窗口类中添加方法

```python
class RISCV_GUI:
    def __init__(self, ...):
        # ... 现有初始化代码 ...
        
        # 在按钮创建部分添加
        self.sim_button = tk.Button(
            self.button_frame, 
            text="Run on Simulator",
            command=self.run_on_simulator,
            bg="#4CAF50",  # 绿色
            fg="white",
            font=("Arial", 10)
        )
        self.sim_button.pack(side=tk.LEFT, padx=5)
    
    def run_on_simulator(self):
        """Execute the assembled code on ISS instead of FPGA"""
        try:
            # 第1步：保证有编译好的 ISS
            if not self.ensure_iss_compiled():
                self.status_text.insert(tk.END, 
                    "Error: ISS not compiled. Please compile first.\n")
                return
            
            # 第2步：汇编代码
            asm_file = "temp_test.asm"
            bin_file = "temp_test.bin"
            
            # 保存汇编代码到临时文件
            asm_code = self.text.get("1.0", tk.END)
            with open(asm_file, 'w') as f:
                f.write(asm_code)
            
            # 调用汇编器
            sys.path.insert(0, './src')
            from assembler import assemble
            assemble(asm_file, bin_file)
            
            # 第3步：运行 ISS
            result = subprocess.run(
                ["./build/iss", bin_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # 第4步：解析输出并显示结果
            self.display_simulator_results(result.stdout)
            
        except subprocess.TimeoutExpired:
            self.status_text.insert(tk.END, 
                "Error: Simulator timeout (infinite loop?)\n")
        except Exception as e:
            self.status_text.insert(tk.END, 
                f"Error running simulator: {str(e)}\n")
    
    def ensure_iss_compiled(self):
        """Check if ISS is compiled, compile if needed"""
        if not os.path.exists("./build/iss"):
            self.status_text.insert(tk.END, 
                "Compiling ISS...\n")
            try:
                result = subprocess.run(
                    ["g++", "-std=c++17", "-O2",
                     "-I./src/cpp",
                     "-o", "build/iss",
                     "src/cpp/iss.cpp", "src/cpp/main.cpp"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    self.status_text.insert(tk.END, 
                        f"Compilation error:\n{result.stderr}\n")
                    return False
                self.status_text.insert(tk.END, 
                    "✓ ISS compiled successfully\n")
            except Exception as e:
                self.status_text.insert(tk.END, 
                    f"Compilation error: {str(e)}\n")
                return False
        return True
    
    def display_simulator_results(self, output):
        """Parse ISS output and display results in GUI"""
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, "=== SIMULATOR RESULTS ===\n\n")
        
        # 提取寄存器值
        lines = output.split('\n')
        reg_values = {}
        
        in_reg_section = False
        for line in lines:
            if line.startswith("x"):
                # 格式: x1=0000000a
                match = re.match(r'x(\d+)=([0-9a-f]+)', line)
                if match:
                    reg_num = int(match.group(1))
                    reg_val = int(match.group(2), 16)
                    reg_values[reg_num] = reg_val
            elif "Performance Statistics" in line:
                # 找到性能统计部分
                in_perf = True
        
        # 显示关键寄存器
        self.status_text.insert(tk.END, "--- Register Values ---\n")
        for i in [1, 2, 3, 4, 5, 10, 11]:  # 常用寄存器
            if i in reg_values:
                self.status_text.insert(tk.END, 
                    f"x{i:2d} = {reg_values[i]:10d} (0x{reg_values[i]:08x})\n")
        
        # 显示性能统计
        if "Performance Statistics" in output:
            self.status_text.insert(tk.END, "\n--- Performance Statistics ---\n")
            in_stats = False
            for line in lines:
                if "Performance Statistics" in line:
                    in_stats = True
                elif in_stats:
                    if "===========" in line:
                        break
                    if line.strip():
                        self.status_text.insert(tk.END, line + "\n")
        
        # 显示原始输出供参考
        self.status_text.insert(tk.END, "\n--- Full Output ---\n")
        self.status_text.insert(tk.END, output)
```

#### 3. 修改按钮布局

在创建 FPGA 相关按钮的地方（假设原代码中有"Compile"和"Load"按钮），按如下方式调整：

```python
# 创建一个新的框架来放置模拟器和 FPGA 按钮
sim_fpga_frame = tk.Frame(self.button_frame, bg=self.bg_color)
sim_fpga_frame.pack(side=tk.LEFT, padx=10)

# ISS 模拟器按钮（绿色）
self.sim_button = tk.Button(
    sim_fpga_frame,
    text="▶ Run on Simulator",
    command=self.run_on_simulator,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20
)
self.sim_button.pack(pady=5)

# FPGA 按钮（蓝色）
self.fpga_button = tk.Button(
    sim_fpga_frame,
    text="▶ Run on FPGA",
    command=self.run_on_fpga,  # 现有方法
    bg="#2196F3",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20
)
self.fpga_button.pack(pady=5)
```

### 方案 B：高级集成（完整，4 小时）

实现功能更丰富的集成，包括：

#### 1. 双窗格显示（ISS vs FPGA）

```python
class DualExecutionWindow:
    def __init__(self, parent):
        # 左侧：ISS 执行结果
        self.left_frame = tk.LabelFrame(
            parent, text="Simulator (ISS)", 
            bg="#e8f5e9"
        )
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.sim_output = tk.Text(self.left_frame, height=20, width=40)
        self.sim_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧：FPGA 执行结果
        self.right_frame = tk.LabelFrame(
            parent, text="Hardware (FPGA)",
            bg="#e3f2fd"
        )
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fpga_output = tk.Text(self.right_frame, height=20, width=40)
        self.fpga_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
```

#### 2. 结果对比

```python
def compare_results(self, sim_regs, fpga_regs):
    """Compare simulator and FPGA results"""
    differences = []
    for i in range(32):
        if sim_regs.get(i) != fpga_regs.get(i):
            differences.append({
                'register': f'x{i}',
                'sim_value': sim_regs.get(i),
                'fpga_value': fpga_regs.get(i)
            })
    
    if differences:
        return f"⚠ {len(differences)} differences found:\n" + \
               "\n".join([
                   f"{d['register']}: SIM=0x{d['sim_value']:08x}, " +
                   f"FPGA=0x{d['fpga_value']:08x}"
                   for d in differences
               ])
    else:
        return "✓ ISS and FPGA results match perfectly!"
```

#### 3. 时间统计

```python
def run_on_simulator_with_timing(self):
    """Run on simulator and measure execution time"""
    import time
    
    start_time = time.time()
    # ... ISS 执行代码 ...
    elapsed = time.time() - start_time
    
    self.status_text.insert(tk.END, 
        f"\nExecution time: {elapsed*1000:.2f} ms\n")
```

## 集成检查清单

- [ ] 添加 `import subprocess, re, os`
- [ ] 创建 `run_on_simulator()` 方法
- [ ] 创建 `ensure_iss_compiled()` 方法
- [ ] 创建 `display_simulator_results()` 方法
- [ ] 在按钮面板中添加"Run on Simulator"按钮
- [ ] 测试基本功能（运行 test_loop.asm）
- [ ] 测试性能统计显示
- [ ] 验证错误处理（无效汇编代码、无限循环等）

## 测试步骤

### 1. 单元测试：ISS 独立运行

```bash
cd /home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py
./build/iss tests/test_loop.bin
# 应该看到寄存器输出和性能统计
```

### 2. 集成测试：从 windows.py 运行

- 打开 windows.py
- 点击"Run on Simulator"按钮
- 验证输出包含：
  - 寄存器值
  - 性能统计（CPI、指令计数等）

### 3. 对比测试：ISS vs FPGA

在方案 B 中：
- 同时在 ISS 和 FPGA 上运行
- 比较寄存器值
- 记录执行时间差异

## 可能的问题与解决

### 问题 1：ISS 编译失败

**症状**：`g++: command not found`

**解决**：
```bash
sudo apt-get install build-essential
# 或在 macOS:
brew install gcc
```

### 问题 2：无限循环导致 GUI 卡死

**症状**：点击按钮后 GUI 无响应

**解决**：添加超时和后台线程

```python
def run_on_simulator_threaded(self):
    """Run simulator in background thread to prevent GUI freeze"""
    import threading
    
    thread = threading.Thread(target=self.run_on_simulator)
    thread.daemon = True
    thread.start()
```

### 问题 3：路径问题

**症状**：`./build/iss: No such file or directory`

**解决**：使用绝对路径

```python
iss_path = os.path.join(os.getcwd(), "build", "iss")
result = subprocess.run([iss_path, bin_file], ...)
```

## 性能考虑

| 操作 | 耗时 | 优化方案 |
|------|------|---------|
| 首次 ISS 编译 | ~2-3 秒 | 在后台或缓存 |
| 后续 ISS 运行 | ~100 ms | 足够快 |
| FPGA 配置 | ~5 秒 | 保持不变 |
| FPGA 执行 | ~1 秒 | 取决于程序 |

**优化建议**：
- 首次编译时显示进度条
- 编译成功后禁用编译按钮
- 使用线程处理长时间操作

## 扩展建议

### 高级功能 1：逐步执行（Step Debug）

```python
def step_instruction(self):
    """Execute one instruction at a time"""
    # 需要修改 ISS：添加 step() 接口
    # 或通过 IPC/socket 通信
```

### 高级功能 2：设置断点

```python
def set_breakpoint(self, address):
    """Set breakpoint at PC address"""
    # 在汇编代码特定行号设置断点
    # 修改 ISS：支持断点
```

### 高级功能 3：内存查看器

```python
def view_memory(self, start_addr, length):
    """Display memory contents"""
    # 解析 ISS 的内存转储输出
    # 在 GUI 中显示为表格
```

## 部署建议

### 文件组织

```
2.assembler_py/
├── windows.py               # 修改版本（集成 ISS）
├── src/
│   ├── assembler.py
│   └── cpp/
│       ├── iss.h
│       ├── iss.cpp
│       └── main.cpp
├── build/
│   └── iss                  # 编译后的可执行文件
├── tests/
│   └── *.bin                # 测试用例
└── ISS_Integration_Guide.md # 本文件
```

### 打包和分发

```bash
# 生成可执行包
pyinstaller --onefile windows.py

# 包含 ISS 可执行文件
cp build/iss dist/

# 最终包含：
# dist/windows.exe (or windows)
# dist/iss
# dist/src/assembler.py
```

## 总结

通过添加 ISS 集成，用户可以：

✅ 快速测试汇编代码（无需 FPGA）  
✅ 查看详细的性能统计  
✅ 对比模拟器和硬件结果  
✅ 离线调试和优化代码  

**预期工作量**：方案 A（2 小时）或方案 B（4-6 小时）  
**复杂度**：低（主要是 subprocess + 字符串解析）  
**收益**：大（用户体验显著改善）

---

建议从方案 A 开始，成功后再考虑方案 B 的高级功能。
