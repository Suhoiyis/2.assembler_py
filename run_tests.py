#!/usr/bin/env python3
"""
自动化测试脚本：从汇编代码生成机器码 -> 运行 ISS -> 验证寄存器值
"""

import subprocess
import sys
import os
import re

def run_assembler(asm_file, bin_file):
    """使用 assembler.py 生成机器码"""
    script = f"""
import sys
sys.path.insert(0, 'src')
from assembler import assemble
assemble('{asm_file}', '{bin_file}')
"""
    result = subprocess.run(
        ['python3', '-c', script],
        cwd='/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py',
        capture_output=True,
        text=True
    )
    return 'SUCCESS' in result.stdout or result.returncode == 0

def run_iss(bin_file):
    """运行 ISS 并返回寄存器值"""
    result = subprocess.run(
        ['/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/build/iss', bin_file],
        capture_output=True,
        text=True
    )
    
    # 解析输出：提取 x0=xxx, x1=xxx 等
    regs = {}
    for line in result.stdout.split('\n'):
        match = re.match(r'x(\d+)=([0-9a-f]+)', line.strip())
        if match:
            reg_idx = int(match.group(1))
            hex_val = match.group(2)
            regs[f'x{reg_idx}'] = int(hex_val, 16)
    return regs

def test_li_add():
    """测试 1: lui+addi+add"""
    print("\n[Test 1] lui+addi+add")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_li_add.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_li_add.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x2', 0) == 20 and regs.get('x1', 0) == 10
    
    print(f"  x1={regs.get('x1', 0)} (expect 10)")
    print(f"  x2={regs.get('x2', 0)} (expect 20)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_loop():
    """测试 2: 循环计数"""
    print("\n[Test 2] loop with counter")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_loop.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_loop.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x1', 0) == 5 and regs.get('x10', 0) == 5
    
    print(f"  x1={regs.get('x1', 0)} (expect 5)")
    print(f"  x10={regs.get('x10', 0)} (expect 5)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_memory():
    """测试 3: 内存读写"""
    print("\n[Test 3] memory sw/lw")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_memory.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_memory.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x1', 0) == 42 and regs.get('x3', 0) == 42
    
    print(f"  x1={regs.get('x1', 0)} (expect 42)")
    print(f"  x3={regs.get('x3', 0)} (expect 42)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_mul():
    """测试 4: MUL (3 * 7 = 21)"""
    print("\n[Test 4] MUL (RV32M)")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_mul.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_mul.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x3', 0) == 21 and regs.get('x1', 0) == 3 and regs.get('x2', 0) == 7
    
    print(f"  x1={regs.get('x1', 0)} (expect 3)")
    print(f"  x2={regs.get('x2', 0)} (expect 7)")
    print(f"  x3={regs.get('x3', 0)} (expect 21)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_div():
    """测试 5: DIV (42 / 5 = 8)"""
    print("\n[Test 5] DIV (RV32M)")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_div.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_div.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x3', 0) == 8 and regs.get('x1', 0) == 42 and regs.get('x2', 0) == 5
    
    print(f"  x1={regs.get('x1', 0)} (expect 42)")
    print(f"  x2={regs.get('x2', 0)} (expect 5)")
    print(f"  x3={regs.get('x3', 0)} (expect 8)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_rem():
    """测试 6: REM (42 % 5 = 2)"""
    print("\n[Test 6] REM (RV32M)")
    asm = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_rem.asm'
    bin_file = '/home/yu/桌面/UESTC/3.1/zongshe/2.assembler_py/tests/test_rem.bin'
    
    if not run_assembler(asm, bin_file):
        print("  ✗ Assembler failed")
        return False
    
    regs = run_iss(bin_file)
    passed = regs.get('x3', 0) == 2 and regs.get('x1', 0) == 42 and regs.get('x2', 0) == 5
    
    print(f"  x1={regs.get('x1', 0)} (expect 42)")
    print(f"  x2={regs.get('x2', 0)} (expect 5)")
    print(f"  x3={regs.get('x3', 0)} (expect 2)")
    print(f"  {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

if __name__ == '__main__':
    print("=" * 50)
    print("RISC-V ISS Automated Test Suite")
    print("=" * 50)
    
    results = []
    results.append(test_li_add())
    results.append(test_loop())
    results.append(test_memory())
    results.append(test_mul())
    results.append(test_div())
    results.append(test_rem())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Summary: {passed}/{total} tests passed")
    print("=" * 50)
    
    sys.exit(0 if all(results) else 1)
