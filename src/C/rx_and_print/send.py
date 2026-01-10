#!/usr/bin/env python3
"""
用法:
    ./send.py 123 45
"""

import sys
import struct
import serial

# ====== 固定配置（根据你的硬件修改这里）======
SERIAL_PORT = "/dev/ttyUSB0"   # ← 改成你的串口
BAUD_RATE  = 9600         # ← 改成你的波特率
# =========================================

def send_numbers(num1, num2):
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            data = struct.pack('<II', num1, num2)  # 两个小端序 uint32
            ser.write(data)
            print(f"已发送: {num1} 和 {num2} 到 {SERIAL_PORT}")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("用法: send_numbers.py <被除数> <除数>")
        print(f"示例: send_numbers.py 123 45")
        sys.exit(1)

    try:
        dividend = int(sys.argv[1])
        divisor  = int(sys.argv[2])

        # 可选：检查是否在 32 位无符号范围内
        if not (0 <= dividend <= 0xFFFFFFFF and 0 <= divisor <= 0xFFFFFFFF):
            print("警告: 数值超出 32 位范围，但仍将发送（高位会被截断）")
    except ValueError:
        print("请输入有效的整数！", file=sys.stderr)
        sys.exit(1)

    send_numbers(dividend, divisor)

if __name__ == "__main__":
    main()