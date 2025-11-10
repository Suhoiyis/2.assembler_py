# windows_32bit.py
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, font
import re
import time

# 汇编器逻辑 (从 assembler.py 复制并修改)

# 寄存器名称到编号的映射表
REGISTER_MAP = {
    'x0': 0, 'zero': 0, 'r0': 0,
    'x1': 1, 'ra': 1, 'r1': 1,
    'x2': 2, 'sp': 2,
    'x3': 3, 'gp': 3,
    'x4': 4, 'tp': 4,
    'x5': 5, 't0': 5,
    'x6': 6, 't1': 6,
    'x7': 7, 't2': 7,
    'x8': 8, 's0': 8, 'fp': 8,
    'x9': 9, 's1': 9,
    'x10': 10, 'a0': 10,
    'x11': 11, 'a1': 11,
    'x12': 12, 'a2': 12,
    'x13': 13, 'a3': 13,
    'x14': 14, 'a4': 14,
    'x15': 15, 'a5': 15,
    'x16': 16, 'a6': 16,
    'x17': 17, 'a7': 17,
    'x18': 18, 's2': 18,
    'x19': 19, 's3': 19,
    'x20': 20, 's4': 20,
    'x21': 21, 's5': 21,
    'x22': 22, 's6': 22,
    'x23': 23, 's7': 23,
    'x24': 24, 's8': 24,
    'x25': 25, 's9': 25,
    'x26': 26, 's10': 26,
    'x27': 27, 's11': 27,
    'x28': 28, 't3': 28,
    'x29': 29, 't4': 29,
    'x30': 30, 't5': 30,
    'x31': 31, 't6': 31,
}

# 反向映射，用于GUI显示
REG_NUM_TO_NAME = {
    0: 'x0(zero)',
    1: 'x1(ra)',
    2: 'x2(sp)',
    3: 'x3(gp)',
    4: 'x4(tp)',
    5: 'x5(t0)',
    6: 'x6(t1)',
    7: 'x7(t2)',
    8: 'x8(s0/fp)',
    9: 'x9(s1)',
    10: 'x10(a0)',
    11: 'x11(a1)',
    12: 'x12(a2)',
    13: 'x13(a3)',
    14: 'x14(a4)',
    15: 'x15(a5)',
    16: 'x16(a6)',
    17: 'x17(a7)',
    18: 'x18(s2)',
    19: 'x19(s3)',
    20: 'x20(s4)',
    21: 'x21(s5)',
    22: 'x22(s6)',
    23: 'x23(s7)',
    24: 'x24(s8)',
    25: 'x25(s9)',
    26: 'x26(s10)',
    27: 'x27(s11)',
    28: 'x28(t3)',
    29: 'x29(t4)',
    30: 'x30(t5)',
    31: 'x31(t6)',
}


# 指令信息库
INSTRUCTION_MAP = {
    # R-type
    'add':    {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0000000'},
    'sub':    {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0100000'},
    'sll':    {'type': 'R', 'opcode': '0110011', 'funct3': '001', 'funct7': '0000000'},
    'slt':    {'type': 'R', 'opcode': '0110011', 'funct3': '010', 'funct7': '0000000'},
    'sltu':   {'type': 'R', 'opcode': '0110011', 'funct3': '011', 'funct7': '0000000'},
    'xor':    {'type': 'R', 'opcode': '0110011', 'funct3': '100', 'funct7': '0000000'},
    'srl':    {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0000000'},
    'sra':    {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0100000'},
    'or':     {'type': 'R', 'opcode': '0110011', 'funct3': '110', 'funct7': '0000000'},
    'and':    {'type': 'R', 'opcode': '0110011', 'funct3': '111', 'funct7': '0000000'},
    # R-type (RV32M Extension)
    'mul':    {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0000001'},
    'mulh':   {'type': 'R', 'opcode': '0110011', 'funct3': '001', 'funct7': '0000001'},
    'mulhsu': {'type': 'R', 'opcode': '0110011', 'funct3': '010', 'funct7': '0000001'},
    'mulhu':  {'type': 'R', 'opcode': '0110011', 'funct3': '011', 'funct7': '0000001'},
    'div':    {'type': 'R', 'opcode': '0110011', 'funct3': '100', 'funct7': '0000001'},
    'divu':   {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0000001'},
    'rem':    {'type': 'R', 'opcode': '0110011', 'funct3': '110', 'funct7': '0000001'},
    'remu':   {'type': 'R', 'opcode': '0110011', 'funct3': '111', 'funct7': '0000001'},
    # I-type
    'addi':   {'type': 'I', 'opcode': '0010011', 'funct3': '000'},
    'slti':   {'type': 'I', 'opcode': '0010011', 'funct3': '010'},
    'sltiu':  {'type': 'I', 'opcode': '0010011', 'funct3': '011'},
    'xori':   {'type': 'I', 'opcode': '0010011', 'funct3': '100'},
    'ori':    {'type': 'I', 'opcode': '0010011', 'funct3': '110'},
    'andi':   {'type': 'I', 'opcode': '0010011', 'funct3': '111'},
    'slli':   {'type': 'I-shift', 'opcode': '0010011', 'funct3': '001', 'funct7': '0000000'},
    'srli':   {'type': 'I-shift', 'opcode': '0010011', 'funct3': '101', 'funct7': '0000000'},
    'srai':   {'type': 'I-shift', 'opcode': '0010011', 'funct3': '101', 'funct7': '0100000'},
    'lb':     {'type': 'I-load', 'opcode': '0000011', 'funct3': '000'},
    'lh':     {'type': 'I-load', 'opcode': '0000011', 'funct3': '001'},
    'lw':     {'type': 'I-load', 'opcode': '0000011', 'funct3': '010'},
    'lbu':    {'type': 'I-load', 'opcode': '0000011', 'funct3': '100'},
    'lhu':    {'type': 'I-load', 'opcode': '0000011', 'funct3': '101'},
    'jalr':   {'type': 'I', 'opcode': '1100111', 'funct3': '000'},
    # S-type
    'sb':     {'type': 'S', 'opcode': '0100011', 'funct3': '000'},
    'sh':     {'type': 'S', 'opcode': '0100011', 'funct3': '001'},
    'sw':     {'type': 'S', 'opcode': '0100011', 'funct3': '010'},
    # B-type
    'beq':    {'type': 'B', 'opcode': '1100011', 'funct3': '000'},
    'bne':    {'type': 'B', 'opcode': '1100011', 'funct3': '001'},
    'blt':    {'type': 'B', 'opcode': '1100011', 'funct3': '100'},
    'bge':    {'type': 'B', 'opcode': '1100011', 'funct3': '101'},
    'bltu':   {'type': 'B', 'opcode': '1100011', 'funct3': '110'},
    'bgeu':   {'type': 'B', 'opcode': '1100011', 'funct3': '111'},
    # U-type
    'lui':    {'type': 'U', 'opcode': '0110111'},
    'auipc':  {'type': 'U', 'opcode': '0010111'},
    # J-type
    'jal':    {'type': 'J', 'opcode': '1101111'},
}

# 将一个十进制数转换为指定位数的二进制补码字符串
def to_signed_binary(num, bits):
    if num >= 0:
        return format(num, f'0{bits}b')
    else:
        return format((1 << bits) + num, f'0{bits}b')

def get_reg_num(reg_name):
    return REGISTER_MAP.get(reg_name.lower())

def handle_r_type(instr, operands):
    rd_name, rs1_name, rs2_name = operands[0], operands[1], operands[2]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rs1_num = get_reg_num(rs1_name);
    if rs1_num is None: return None, f"无效的源寄存器 (rs1): '{rs1_name}'"
    rs2_num = get_reg_num(rs2_name);
    if rs2_num is None: return None, f"无效的源寄存器 (rs2): '{rs2_name}'"
    rd, rs1, rs2 = format(rd_num, '05b'), format(rs1_num, '05b'), format(rs2_num, '05b')
    return instr['funct7'] + rs2 + rs1 + instr['funct3'] + rd + instr['opcode'], None

def handle_i_type(instr, operands):
    rd_name, rs1_name = operands[0], operands[1]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rs1_num = get_reg_num(rs1_name);
    if rs1_num is None: return None, f"无效的源寄存器 (rs1): '{rs1_name}'"
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    imm = to_signed_binary(int(operands[2], 0), 12)
    return imm + rs1 + instr['funct3'] + rd + instr['opcode'], None

def handle_i_shift_type(instr, operands):
    rd_name, rs1_name = operands[0], operands[1]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rs1_num = get_reg_num(rs1_name);
    if rs1_num is None: return None, f"无效的源寄存器 (rs1): '{rs1_name}'"
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    shamt = format(int(operands[2], 0), '05b') # 移位量是5位
    return instr['funct7'] + shamt + rs1 + instr['funct3'] + rd + instr['opcode'], None

def handle_i_load_type(instr, operands):
    rd_name, rs1_name = operands[0], operands[2]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rs1_num = get_reg_num(rs1_name);
    if rs1_num is None: return None, f"无效的基址寄存器 (rs1): '{rs1_name}'"
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    imm = to_signed_binary(int(operands[1], 0), 12)
    return imm + rs1 + instr['funct3'] + rd + instr['opcode'], None

def handle_s_type(instr, operands):
    rs2_name, rs1_name = operands[0], operands[2]
    rs2_num = get_reg_num(rs2_name);
    if rs2_num is None: return None, f"无效的源寄存器 (rs2): '{rs2_name}'"
    rs1_num = get_reg_num(rs1_name);
    if rs1_num is None: return None, f"无效的基址寄存器 (rs1): '{rs1_name}'"
    rs2, rs1 = format(rs2_num, '05b'), format(rs1_num, '05b')
    imm_val = int(operands[1], 0)
    imm = to_signed_binary(imm_val, 12)
    imm11_5, imm4_0 = imm[0:7], imm[7:12]
    return imm11_5 + rs2 + rs1 + instr['funct3'] + imm4_0 + instr['opcode'], None

def handle_b_type(instr, operands):
    op1_name, op2_name = operands[0], operands[1]
    rs1_num = get_reg_num(op1_name);
    if rs1_num is None: return None, f"无效的源寄存器 (rs1): '{op1_name}'"
    rs2_num = get_reg_num(op2_name);
    if rs2_num is None: return None, f"无效的源寄存器 (rs2): '{op2_name}'"
    rs1, rs2 = format(rs1_num, '05b'), format(rs2_num, '05b')

    imm_val = int(operands[2], 0)
    if imm_val % 2 != 0:
        return None, f"B类型偏移量必须是2的倍数: {imm_val}"

    imm_bin = to_signed_binary(imm_val, 13) # B-type 立即数是13位
    imm12 = imm_bin[0]
    imm10_5 = imm_bin[2:8]
    imm4_1 = imm_bin[8:12]
    imm11 = imm_bin[1]
    return imm12 + imm10_5 + rs2 + rs1 + instr['funct3'] + imm4_1 + imm11 + instr['opcode'], None

def handle_u_type(instr, operands):
    rd_name = operands[0]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rd = format(rd_num, '05b')

    imm_val = int(operands[1], 0)
    imm = to_signed_binary(imm_val, 20) # U-type 立即数是20位
    return imm + rd + instr['opcode'], None

def handle_j_type(instr, operands):
    rd_name = operands[0]
    rd_num = get_reg_num(rd_name);
    if rd_num is None: return None, f"无效的目标寄存器 (rd): '{rd_name}'"
    rd = format(rd_num, '05b')

    imm_val = int(operands[1], 0)
    if imm_val % 2 != 0:
        return None, f"J类型偏移量必须是2的倍数: {imm_val}"

    imm_bin = to_signed_binary(imm_val, 21) # J-type 立即数是21位

    imm20 = imm_bin[0]
    imm10_1 = imm_bin[10:20]
    imm11 = imm_bin[9]
    imm19_12 = imm_bin[1:9]
    return imm20 + imm10_1 + imm11 + imm19_12 + rd + instr['opcode'], None

def clean_line(line):
    return line.split('#')[0].split('//')[0].strip()

def first_pass(lines):
    symbol_table = {}
    address = 0
    for line in lines:
        cleaned = clean_line(line)
        if not cleaned: continue
        label_match = re.match(r'^\s*([a-zA-Z_]\w*):\s*$', cleaned)
        label_with_instr_match = re.match(r'^\s*([a-zA-Z_]\w*):\s*(.*)', cleaned)
        if label_match:
            symbol_table[label_match.group(1).lower()] = address
        elif label_with_instr_match:
            label = label_with_instr_match.group(1).lower()
            instr = label_with_instr_match.group(2).strip()
            symbol_table[label] = address
            if instr: address += 4
        else: address += 4
    return symbol_table, None

def second_pass(lines, symbol_table):
    machine_codes = []
    source_line_map = [] # 存储(机器码索引, 原始行号)
    address = 0
    errors = []
    for line_num, line in enumerate(lines, 1):
        cleaned = clean_line(line)
        if ':' in cleaned:
            cleaned = re.sub(r'^\s*[a-zA-Z_]\w*:\s*', '', cleaned).strip()
        if not cleaned: continue
        try:
            mnemonic_lower = cleaned.split()[0].lower()
            if mnemonic_lower not in INSTRUCTION_MAP:
                errors.append(f"第 {line_num} 行: 未知指令 '{mnemonic_lower}'")
                address += 4
                continue
        except IndexError:
            # 可能是空行或只有标签的行，安全跳过
            continue

        instr_info = INSTRUCTION_MAP[mnemonic_lower]
        instr_type = instr_info['type']

        reg = r'([a-zA-Z0-9]+)'
        imm = r'(-?0x[0-9a-fA-F]+|-?\d+)'
        label = r'[a-zA-Z_]\w*'
        target = f'({imm}|{label})'

        patterns = [
            (rf'{reg},\s*{reg},\s*{reg}', ('R')),
            (rf'{reg},\s*{reg},\s*{target}', ('I', 'I-shift', 'B')),
            (rf'{reg},\s*{imm}\({reg}\)', ('S', 'I-load')),
            (rf'{reg},\s*{target}', ('U', 'J')),
        ]

        line_to_parse = ' '.join(cleaned.split()[1:])

        matched = False
        for pattern, types in patterns:
            if instr_type not in types: continue
            match = re.fullmatch(pattern, line_to_parse.lower())
            if match:
                operands = list(match.groups())
                operands = [op for op in operands if op is not None]

                if instr_type in ('B', 'J'):
                    op_target = operands[-1]
                    offset = 0
                    try:
                        offset = int(op_target, 0)
                    except ValueError:
                        target_lower = op_target.lower()
                        if target_lower not in symbol_table:
                            errors.append(f"第 {line_num} 行: 未定义的标签 '{op_target}'")
                            matched = True; break
                        target_address = symbol_table[target_lower]
                        offset = target_address - address
                    operands[-1] = str(offset)

                handler_map = {
                    'R': handle_r_type, 'I': handle_i_type, 'I-shift': handle_i_shift_type,
                    'I-load': handle_i_load_type, 'S': handle_s_type, 'B': handle_b_type,
                    'U': handle_u_type, 'J': handle_j_type,
                }

                code, err = handler_map[instr_type](instr_info, operands)
                if err:
                    errors.append(f"第 {line_num} 行 ({cleaned}): {err}")
                else:
                    machine_codes.append(code)
                    source_line_map.append((len(machine_codes) - 1, line_num)) # 记录行号
                matched = True
                break

        if not matched and not any(f"第 {line_num} 行" in e for e in errors):
            errors.append(f"第 {line_num} 行: 无法解析的操作数格式 '{line_to_parse}'")

        address += 4
    return machine_codes, errors, source_line_map # 返回行号


# 32位RISC-V模拟器
class Simulator32Bit:
    def __init__(self):
        # 1. 创建物理设备
        # ROM(flash)为32K, RAM为16K
        # 为留出余量，我们都使用 64KB (0x10000)
        self.rom = bytearray(64 * 1024)  # 64KB ROM
        self.ram = bytearray(64 * 1024)  # 64KB RAM

        # 2. 模拟外设寄存器 (根据PPT)
        self.timer_counter = 0

        self.uart_ctrl_reg = 0
        self.uart_status_reg = 0   # (0 = 空闲, 允许发送)
        self.uart_baud_reg = 0
        self.uart_txdata_reg = 0
        self.uart_rxdata_reg = 0

        self.gpio_leds = 0
        self.gpio_smgs = bytearray(8) # (偏移 0x1-0x7)

        # 3. 模拟器状态
        self.registers = [0] * 32  # 32个 32位寄存器
        self.pc = 0
        self.previous_pc = 0
        self.halted = False
        self.pc_to_source_line_map = {} # PC (地址) -> 源代码行号

        self.error_message = None # 添加错误信息变量

        # 4. 初始化状态
        self.reset()

    def reset(self):
        # 重置所有寄存器和PC
        self.registers = [0] * 32
        self.pc = 0
        self.previous_pc = 0
        self.halted = False
        self.error_message = None # 重置错误信息

        # 清空 RAM (ROM在加载时被写入，不需要重置)
        self.ram = bytearray(len(self.ram))

        # 清空外设寄存器
        self.timer_counter = 0
        self.uart_ctrl_reg = 0
        self.uart_status_reg = 0
        self.uart_baud_reg = 0
        self.uart_txdata_reg = 0
        self.uart_rxdata_reg = 0
        self.gpio_leds = 0
        self.gpio_smgs = bytearray(8)

        # 根据PPT的链接脚本和启动代码
        # 栈(sp)在RAM中，并且从上向下增长。
        # 将sp(x2)设置为RAM的VMA地址 (0x1000_0000)
        # 加上我们模拟的RAM的物理大小 (64KB)。
        RAM_VMA_START = 0x10000000
        RAM_PHYSICAL_SIZE = len(self.ram) # 65536
        self.set_reg_value(2, RAM_VMA_START + RAM_PHYSICAL_SIZE)

        # self.pc_to_source_line_map 在加载时会重建
        print("SoC Simulator Reset.")
    def _get_device_and_offset(self, address):
        """根据地址返回 (物理设备, 偏移量) 或 (None, None)"""

        # ROM 区
        if 0x0000_0000 <= address < (0x0000_0000 + len(self.rom)):
            return self.rom, address - 0x0000_0000
        # RAM 区
        elif 0x1000_0000 <= address < (0x1000_0000 + len(self.ram)):
            return self.ram, address - 0x1000_0000

        # Timer 区  4 字节的范围
        elif 0x2000_0000 <= address < 0x2000_0004:
            return "timer", address - 0x2000_0000

        # UART 区 (根据PPT，范围是 0x00 到 0x10)
        elif 0x3000_0000 <= address < 0x3000_0014: # (0x10 + 4 字节)
            return "uart", address - 0x3000_0000

        # GPIO 区  (根据PPT，范围是 0x00 到 0x07)
        elif 0x4000_0000 <= address < 0x4000_0008:
            return "gpio", address - 0x4000_0000

        else:
            return None, None # 未映射的地址

    def mem_read(self, address, num_bytes, signed=False):
        """
        从内存总线读取数据。
        num_bytes 必须是 1, 2, 或 4.
        """
        device, offset = self._get_device_and_offset(address)

        if device == "timer":
            # Timer的读取逻辑
            reg_val = 0
            if offset >= 0x00 and offset < 0x04:
                reg_val = self.timer_counter # Timer在偏移量0处

            # 根据请求的字节数和偏移量返回正确的字节
            byte_offset_in_word = address % 4
            val_bytes = reg_val.to_bytes(4, 'little', signed=False) # Timer是无符号的

            if num_bytes == 1:
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+1], 'little', signed=signed)
            elif num_bytes == 2:
                if byte_offset_in_word > 2: raise MemoryError(f"Unaligned 2-byte read at 0x{address:X}")
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+2], 'little', signed=signed)
            elif num_bytes == 4:
                if byte_offset_in_word != 0: raise MemoryError(f"Unaligned 4-byte read at 0x{address:X}")
                return int.from_bytes(val_bytes, 'little', signed=signed)

        elif device == "uart":
            # 模拟读取UART寄存器
            reg_val = 0
            if offset >= 0x00 and offset < 0x04: reg_val = self.uart_ctrl_reg
            elif offset >= 0x04 and offset < 0x08: reg_val = self.uart_status_reg
            elif offset >= 0x08 and offset < 0x0C: reg_val = self.uart_baud_reg
            elif offset >= 0x0C and offset < 0x10: reg_val = self.uart_txdata_reg
            elif offset >= 0x10 and offset < 0x14: reg_val = self.uart_rxdata_reg
            # else: reg_val = 0 (默認為0)

            # 根据请求的字节数和偏移量返回正确的字节
            byte_offset_in_word = address % 4
            val_bytes = reg_val.to_bytes(4, 'little')

            if num_bytes == 1:
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+1], 'little', signed=signed)
            elif num_bytes == 2:
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+2], 'little', signed=signed)
            elif num_bytes == 4:
                return int.from_bytes(val_bytes, 'little', signed=signed)

        elif device == "gpio":
            # [已修复] GPIO的读取逻辑
            # [cite_start]根据PPT，GPIO寄存器是按字节偏移的 [cite: 221, 222]
            reg_val_word = 0

            if offset >= 0x00 and offset < 0x04:
                # 访问第一个字 (0x40000000 - 0x40000003)
                # [cite_start]LSB (offset 0) = leds [cite: 221]
                # [cite_start]Offset 1 = smg[1] [cite: 222]
                # Offset 2 = smg[2]
                # MSB (offset 3) = smg[3]
                reg_val_word = (self.gpio_smgs[3] << 24) | \
                            (self.gpio_smgs[2] << 16) | \
                            (self.gpio_smgs[1] << 8)  | \
                                self.gpio_leds

            elif offset >= 0x04 and offset < 0x08:
                # 访问第二个字 (0x40000004 - 0x40000007)
                # LSB (offset 4) = smg[4]
                # Offset 5 = smg[5]
                # Offset 6 = smg[6]
                # [cite_start]MSB (offset 7) = smg[7] [cite: 222]
                reg_val_word = (self.gpio_smgs[7] << 24) | \
                            (self.gpio_smgs[6] << 16) | \
                            (self.gpio_smgs[5] << 8)  | \
                                self.gpio_smgs[4]
            # else: reg_val_word = 0 (默認為0)

            # 根据请求的字节数和偏移量返回正确的字节
            byte_offset_in_word = address % 4
            val_bytes = reg_val_word.to_bytes(4, 'little', signed=False) # GPIO是无符号的

            if num_bytes == 1:
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+1], 'little', signed=signed)
            elif num_bytes == 2:
                if byte_offset_in_word > 2: raise MemoryError(f"Unaligned 2-byte read at 0x{address:X}")
                return int.from_bytes(val_bytes[byte_offset_in_word:byte_offset_in_word+2], 'little', signed=signed)
            elif num_bytes == 4:
                if byte_offset_in_word != 0: raise MemoryError(f"Unaligned 4-byte read at 0x{address:X}")
                return int.from_bytes(val_bytes, 'little', signed=signed)

        elif device is not None:
            # 从 ROM 或 RAM 读取
            if offset + num_bytes > len(device):
                raise MemoryError(f"Read address 0x{address:X} (offset {offset}) out of physical bounds for device")
            data_bytes = device[offset : offset + num_bytes]
            return int.from_bytes(data_bytes, 'little', signed=signed)

        raise MemoryError(f"Read from unmapped or invalid address 0x{address:X}")

    def mem_write(self, address, value, num_bytes):
        """
        向内存总线写入数据。
        num_bytes 必须是 1, 2, 或 4.
        """
        device, offset = self._get_device_and_offset(address)

        if device == "uart":
            # 模拟写入UART寄存器
            if offset == 0x00: self.uart_ctrl_reg = value; return
            elif offset == 0x08: self.uart_baud_reg = value; return
            elif offset == 0x0C: # UART_TXDATA [cite: 226]
                self.uart_txdata_reg = value & 0xFF
                # [模拟] 立即打印到控制台
                print(f"UART_TX: {self.uart_txdata_reg}")
                return

        elif device == "gpio":
            # 模拟写入GPIO [cite: 217-219]
            value_byte = value & 0xFF
            if offset == 0x00:
                self.gpio_leds = value_byte;
                print(f"GPIO_LEDS: {self.gpio_leds:08b}")
                return
            elif 0x01 <= offset <= 0x07:
                self.gpio_smgs[offset] = value_byte
                print(f"GPIO_SMG[{offset}]: {value_byte:X}")
                return

        elif device == self.rom:
            # 理论上ROM不可写，但加载程序时需要写入
            if offset + num_bytes > len(device):
                raise MemoryError(f"Write address 0x{address:X} out of physical ROM bounds")
            data_bytes = value.to_bytes(num_bytes, 'little', signed=False)
            device[offset : offset + num_bytes] = data_bytes
            return

        elif device == self.ram:
            if offset + num_bytes > len(device):
                raise MemoryError(f"Write address 0x{address:X} out of physical RAM bounds")
            data_bytes = value.to_bytes(num_bytes, 'little', signed=False)
            device[offset : offset + num_bytes] = data_bytes
            return

        raise MemoryError(f"Write to unmapped or invalid address 0x{address:X}")
    def get_reg_value(self, reg_idx):
        if not (0 <= reg_idx <= 31):
            raise ValueError(f"Invalid register index: {reg_idx}")
        if reg_idx == 0:
            return 0 # x0 恒为 0
        val = self.registers[reg_idx]
        if val & 0x80000000: # 检查符号位
            # 如果符号位为1，计算其负数值
            return val - 0x100000000
        else:
            # 否则, 它是一个正数
            return val

    def set_reg_value(self, reg_idx, value):
        if not (0 <= reg_idx <= 31):
            raise ValueError(f"Invalid register index: {reg_idx}")
        if reg_idx != 0: # x0 恒为 0
            # 模拟32位
            self.registers[reg_idx] = value & 0xFFFFFFFF

    def sign_extend(self, value, bits):
        sign_bit = 1 << (bits - 1)
        return (value & ((1 << bits) - 1)) - (1 << bits if value & sign_bit else 0)

    def load_program_from_binary_strings(self, binary_codes, source_line_map_list):
            self.reset()
            address = 0 # 程序从 0x00000000 (ROM) 开始
            
            for code_str in binary_codes:
                if len(code_str) != 32:
                    print(f"Warning: Invalid machine code string: {code_str}")
                    continue
                
                code_int = int(code_str, 2)
                try:
                    # 使用新的总线函数写入ROM
                    self.mem_write(address, code_int, 4)
                except Exception as e:
                    print(f"Error loading program at 0x{address:X}: {e}")
                    self.halted = True
                    return
                address += 4

            # 构建 PC (地址) -> 行号的映射
            self.pc_to_source_line_map = {}
            for (instr_index, line_num) in source_line_map_list:
                pc_address = instr_index * 4
                self.pc_to_source_line_map[pc_address] = line_num
            
            self.pc = 0
            self.halted = False
            print(f"Loaded {len(binary_codes)} instructions into ROM.")

    def fetch(self):
            if self.halted:
                return None
            try:
                instruction_word = self.mem_read(self.pc, 4, signed=False)
                return instruction_word
            except MemoryError as e:
                print(f"PC out of bounds or unmapped: {e}")
                self.error_message = error_msg # 保存错误     保存错误信息
                self.halted = True
                return None

    def decode_and_execute(self, instr_word):
        if instr_word == 0: # 常见
            print(f"Encountered NOP (0x00000000) at PC={self.pc:08X}. Halting.")
            self.halted = True
            return

        opcode = instr_word & 0x7F
        rd = (instr_word >> 7) & 0x1F
        funct3 = (instr_word >> 12) & 0x7
        rs1 = (instr_word >> 15) & 0x1F
        rs2 = (instr_word >> 20) & 0x1F
        funct7 = (instr_word >> 25) & 0x7F

        next_pc = self.pc + 4 # 默认PC+4

        try:
            # R-type
            if opcode == 0b0110011:
                rs1_val = self.get_reg_value(rs1)
                rs2_val = self.get_reg_value(rs2)
                result = 0
                if funct7 == 0b0000000:
                    if funct3 == 0b000: result = rs1_val + rs2_val # add
                    elif funct3 == 0b001: result = rs1_val << (rs2_val & 0x1F) # sll
                    elif funct3 == 0b010: result = 1 if (rs1_val < rs2_val) else 0 # slt (signed)
                    elif funct3 == 0b011: result = 1 if (rs1_val & 0xFFFFFFFF) < (rs2_val & 0xFFFFFFFF) else 0 # sltu (unsigned)
                    elif funct3 == 0b100: result = rs1_val ^ rs2_val # xor
                    elif funct3 == 0b101: result = (rs1_val & 0xFFFFFFFF) >> (rs2_val & 0x1F) # srl
                    elif funct3 == 0b110: result = rs1_val | rs2_val # or
                    elif funct3 == 0b111: result = rs1_val & rs2_val # and
                elif funct7 == 0b0100000:
                    if funct3 == 0b000: result = rs1_val - rs2_val # sub
                    elif funct3 == 0b101: result = rs1_val >> (rs2_val & 0x1F) # sra (signed)
                elif funct7 == 0b0000001: # M-Extension [cite: 186]
                    #  为无符号操作准备操作数
                    rs1_unsigned = rs1_val & 0xFFFFFFFF
                    rs2_unsigned = rs2_val & 0xFFFFFFFF

                    if funct3 == 0b000: # mul
                        result = rs1_val * rs2_val
                    elif funct3 == 0b001: # mulh
                        result = (rs1_val * rs2_val) >> 32
                    elif funct3 == 0b010: # mulhsu
                        result = (rs1_val * rs2_unsigned) >> 32
                    elif funct3 == 0b011: # mulhu
                        result = (rs1_unsigned * rs2_unsigned) >> 32
                    elif funct3 == 0b100: # div
                        if rs2_val == 0:
                            result = -1 # 除以0，结果全为1
                        elif rs1_val == -2147483648 and rs2_val == -1:
                            result = -2147483648 # 溢出
                        else:
                            result = int(float(rs1_val) / rs2_val) # C-style 截断
                    elif funct3 == 0b101: # divu
                        if rs2_unsigned == 0:
                            result = 0xFFFFFFFF # 除以0，结果全为1
                        else:
                            result = rs1_unsigned // rs2_unsigned
                    elif funct3 == 0b110: # rem
                        if rs2_val == 0:
                            result = rs1_val # 除以0，结果为被除数
                        elif rs1_val == -2147483648 and rs2_val == -1:
                            result = 0 # 溢出
                        else:
                            # 使用C-style截断除法来计算余数
                            div_val = int(float(rs1_val) / rs2_val)
                            result = rs1_val - (div_val * rs2_val)
                    elif funct3 == 0b111: # remu
                        if rs2_unsigned == 0:
                            result = rs1_unsigned # 除以0，结果为被除数
                        else:
                            result = rs1_unsigned % rs2_unsigned
                    else:
                        raise ValueError(f"Unimplemented R-Type M-Ext funct3={funct3:b}")

                else:
                    raise ValueError(f"Unimplemented R-Type funct7={funct7:b}")
                self.set_reg_value(rd, result)
            # I-type (Arithmetic)
            elif opcode == 0b0010011:
                rs1_val = self.get_reg_value(rs1)
                imm = self.sign_extend(instr_word >> 20, 12)
                result = 0

                if funct3 == 0b000: # addi
                    result = rs1_val + imm
                elif funct3 == 0b010: # slti
                    result = 1 if rs1_val < imm else 0
                elif funct3 == 0b011: # sltiu
                    result = 1 if (rs1_val & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
                elif funct3 == 0b100: # xori
                    result = rs1_val ^ imm
                elif funct3 == 0b110: # ori
                    result = rs1_val | imm
                elif funct3 == 0b111: # andi
                    result = rs1_val & imm
                elif funct3 == 0b001: # slli
                    # 必須檢查 funct7
                    if funct7 == 0b0000000:
                        shamt = (instr_word >> 20) & 0x1F # shamt 只有 5 位
                        result = rs1_val << shamt
                    else:
                        raise ValueError(f"Invalid slli with funct7={funct7:b}")
                elif funct3 == 0b101: # srli/srai
                    shamt = (instr_word >> 20) & 0x1F # shamt 只有 5 位
                    if funct7 == 0b0000000: # srli
                        result = (rs1_val & 0xFFFFFFFF) >> shamt
                    elif funct7 == 0b0100000: # srai
                        result = rs1_val >> shamt
                    else:
                        raise ValueError(f"Invalid srli/srai with funct7={funct7:b}")
                else:
                    raise ValueError(f"Unimplemented I-Type funct3={funct3:b}")

                self.set_reg_value(rd, result)

# I-type (Load)
            elif opcode == 0b0000011:
                base_addr = self.get_reg_value(rs1)
                offset = self.sign_extend(instr_word >> 20, 12)
                mem_addr = (base_addr + offset) & 0xFFFFFFFF

                val = 0
                if funct3 == 0b000: # lb
                    val = self.mem_read(mem_addr, 1, signed=True)
                elif funct3 == 0b001: # lh
                    val = self.mem_read(mem_addr, 2, signed=True)
                elif funct3 == 0b010: # lw
                    val = self.mem_read(mem_addr, 4, signed=True)
                elif funct3 == 0b100: # lbu
                    val = self.mem_read(mem_addr, 1, signed=False)
                elif funct3 == 0b101: # lhu
                    val = self.mem_read(mem_addr, 2, signed=False)
                else: raise ValueError(f"Unimplemented Load funct3={funct3:b}")
                self.set_reg_value(rd, val)

# S-type (Store)
            elif opcode == 0b0100011:
                base_addr = self.get_reg_value(rs1)
                rs2_val = self.get_reg_value(rs2)
                imm_11_5 = (instr_word >> 25) & 0x7F
                imm_4_0 = (instr_word >> 7) & 0x1F
                imm = self.sign_extend((imm_11_5 << 5) | imm_4_0, 12)
                mem_addr = (base_addr + imm) & 0xFFFFFFFF

                if funct3 == 0b000: # sb
                    self.mem_write(mem_addr, rs2_val, 1)
                elif funct3 == 0b001: # sh
                    self.mem_write(mem_addr, rs2_val, 2)
                elif funct3 == 0b010: # sw
                    self.mem_write(mem_addr, rs2_val, 4)
                else: raise ValueError(f"Unimplemented Store funct3={funct3:b}")

            # B-type (Branch)
            elif opcode == 0b1100011:
                rs1_val = self.get_reg_value(rs1)
                rs2_val = self.get_reg_value(rs2)
                imm_12 = (instr_word >> 31) & 1
                imm_10_5 = (instr_word >> 25) & 0x3F
                imm_4_1 = (instr_word >> 8) & 0xF
                imm_11 = (instr_word >> 7) & 1
                imm = self.sign_extend((imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1), 13)

                branch_taken = False
                if funct3 == 0b000: # beq
                    branch_taken = (rs1_val == rs2_val)
                elif funct3 == 0b001: # bne
                    branch_taken = (rs1_val != rs2_val)
                elif funct3 == 0b100: # blt
                    branch_taken = (rs1_val < rs2_val)
                elif funct3 == 0b101: # bge
                    branch_taken = (rs1_val >= rs2_val)
                elif funct3 == 0b110: # bltu
                    branch_taken = ((rs1_val & 0xFFFFFFFF) < (rs2_val & 0xFFFFFFFF))
                elif funct3 == 0b111: # bgeu
                    branch_taken = ((rs1_val & 0xFFFFFFFF) >= (rs2_val & 0xFFFFFFFF))

                if branch_taken:
                    next_pc = (self.pc + imm) & 0xFFFFFFFF
            # [结束替换]

            # U-type (LUI, AUIPC)
            elif opcode == 0b0110111: # lui
                imm = (instr_word & 0xFFFFF000) # 立即数在高20位
                self.set_reg_value(rd, self.sign_extend(imm, 32)) # 符号扩展
            elif opcode == 0b0010111: # auipc
                imm = (instr_word & 0xFFFFF000)
                self.set_reg_value(rd, (self.pc + self.sign_extend(imm, 32)) & 0xFFFFFFFF)

            # J-type (JAL)
            elif opcode == 0b1101111:
                imm_20 = (instr_word >> 31) & 1
                imm_10_1 = (instr_word >> 21) & 0x3FF
                imm_11 = (instr_word >> 20) & 1
                imm_19_12 = (instr_word >> 12) & 0xFF
                imm = self.sign_extend((imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1), 21)

                self.set_reg_value(rd, self.pc + 4) # 存储返回地址
                next_pc = (self.pc + imm) & 0xFFFFFFFF

            # I-type (JALR)
            elif opcode == 0b1100111:
                rs1_val = self.get_reg_value(rs1)
                imm = self.sign_extend(instr_word >> 20, 12)

                t = self.pc + 4
                next_pc = (rs1_val + imm) & ~1 # 目标地址，最后一位清0
                self.set_reg_value(rd, t) # 存储返回地址

            else:
                raise ValueError(f"Unknown opcode {opcode:07b}")

            self.pc = next_pc

        except Exception as e:
            error_msg = f"执行错误: PC=0x{self.pc:08X}, Instr=0x{instr_word:08X}, Error={e}"
            print(error_msg)
            self.error_message = error_msg # 存储错误信息
            import traceback
            traceback.print_exc()
            self.halted = True

    def step(self):
        if self.halted:
            print("模拟器已停止。")
            return False

        self.previous_pc = self.pc

        instruction = self.fetch()
        if instruction is None or self.halted:
            self.halted = True
            print(f"模拟器在 PC=0x{self.pc:08X} 处停止 (PC越界或Fetch失败).")
            return False

        self.decode_and_execute(instruction)

        if self.halted:
            return False
        return True


# GUI 应用程序
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("32位RISC-V")

        # 字体定义
        self.base_font_family = "Courier New"
        self.base_font_size = 11
        self.actual_code_font = font.Font(family=self.base_font_family, size=self.base_font_size)
        self.ui_font = ("Arial", 11)

        self.simulator = Simulator32Bit()
        self.reg_num_to_name = REG_NUM_TO_NAME

        self.is_running_continuously = False
        self._continuous_run_job = None
        self.run_step_counter = 0

        # 语法高亮标签
        self.highlight_tags = ['comment_tag', 'instruction_tag', 'register_tag']
        self.breakpoints = set()

        main_frame = ttk.Frame(root, padding=(5, 2, 5, 5))
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # --- 代码编辑区 ---
        code_area_frame = ttk.Frame(main_frame)
        code_area_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=(0, 5))
        main_frame.columnconfigure(0, weight=3)
        main_frame.rowconfigure(0, weight=1)

        code_area_frame.rowconfigure(1, weight=1)
        code_area_frame.columnconfigure(1, weight=1)

        ttk.Label(code_area_frame, text="汇编代码:").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0,5))

        self.line_numbers_text = tk.Text(code_area_frame, width=4, padx=1, takefocus=0, borderwidth=0,background='lightgrey', state='disabled', wrap='none',font=self.actual_code_font,spacing1=0, spacing2=0, spacing3=0)
        self.line_numbers_text.grid(row=1, column=0, sticky='ns')
        self.line_numbers_text.bind("<Button-1>", self.on_line_number_click)
        self.line_numbers_text.tag_configure("breakpoint_set_marker", foreground="red", font=self.actual_code_font)

        self.code_text = tk.Text(code_area_frame, width=60, height=25, borderwidth=0, wrap='none', undo=True,font=self.actual_code_font,spacing1=0, spacing2=0, spacing3=0)
        self.code_text.grid(row=1, column=1, sticky='nsew')

        self.v_scrollbar = ttk.Scrollbar(code_area_frame, orient="vertical", command=self._on_scrollbar_yview)
        self.v_scrollbar.grid(row=1, column=2, sticky='ns')
        self.code_text.config(yscrollcommand=self._on_text_scroll)
        self.h_scrollbar = ttk.Scrollbar(code_area_frame, orient="horizontal", command=self.code_text.xview)
        self.h_scrollbar.grid(row=2, column=1, sticky='ew')
        self.code_text.config(xscrollcommand=self.h_scrollbar.set)

        self.code_text.tag_configure('comment_tag', foreground='green', font=self.actual_code_font)
        self.code_text.tag_configure('instruction_tag', foreground='blue', font=self.actual_code_font)
        self.code_text.tag_configure('register_tag', foreground='red', font=self.actual_code_font)

        self.code_text.bind('<KeyRelease>', self.on_text_change)
        self.code_text.bind("<<Modified>>", self.on_text_modified)
        self.code_text.bind('<MouseWheel>', self._on_unified_mousewheel_scroll)
        self.code_text.bind('<Button-4>', self._on_unified_mousewheel_scroll)
        self.code_text.bind('<Button-5>', self._on_unified_mousewheel_scroll)
        self.line_numbers_text.bind('<MouseWheel>', self._on_unified_mousewheel_scroll)
        self.line_numbers_text.bind('<Button-4>', self._on_unified_mousewheel_scroll)
        self.line_numbers_text.bind('<Button-5>', self._on_unified_mousewheel_scroll)

        # --- 控制按钮 ---
        controls_frame = ttk.Frame(code_area_frame)
        controls_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)
        self.load_btn = ttk.Button(controls_frame, text="导入文件", command=self.load_file)
        self.load_btn.pack(side=tk.LEFT, padx=2)
        self.assemble_btn = ttk.Button(controls_frame, text="汇编", command=self.assemble_code)
        self.assemble_btn.pack(side=tk.LEFT, padx=2)
        self.step_btn = ttk.Button(controls_frame, text="单步", command=self.step_code, state=tk.DISABLED)
        self.step_btn.pack(side=tk.LEFT, padx=2)
        self.run_btn = ttk.Button(controls_frame, text="执行", command=self.run_code, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT, padx=2)
        self.stop_btn = ttk.Button(controls_frame, text="停止", command=self.stop_continuous_run, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        self.reset_btn = ttk.Button(controls_frame, text="重置", command=self.reset_simulator, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(code_area_frame, text="已就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5,0))
        self.code_text.tag_configure('current_execution_line_tag', background='yellow')
        self.current_highlighted_tk_line = None

        self._line_number_update_job = None
        self._highlight_job = None

        # --- 右侧面板 ---
        right_pane = ttk.Frame(main_frame, padding=(5, 0, 5, 5))
        right_pane.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=(0, 5))
        main_frame.columnconfigure(1, weight=2) # 保持右侧面板的权重

        # [修改] right_pane 改为1列, 多行
        right_pane.columnconfigure(0, weight=1)
        right_pane.rowconfigure(1, weight=0) # 寄存器行，不拉伸
        right_pane.rowconfigure(4, weight=1) # 内存行，拉伸

        # --- 寄存器视图 (32个) ---
        ttk.Label(right_pane, text="寄存器:").grid(row=0, column=0, sticky=tk.NW, padx=(0,5), pady=(0,2))
        self.reg_frame = ttk.Frame(right_pane)
        self.reg_frame.grid(row=1, column=0, sticky='new', padx=(0,5)) # 放在第1行，第0列
        self.reg_labels = {}
        for i in range(32):
            reg_name = self.reg_num_to_name.get(i, f'x{i}')
            # 分两列显示
            row_idx = i % 16
            col_idx = (i // 16) * 2

            ttk.Label(self.reg_frame, text=f"{reg_name:<10}").grid(row=row_idx, column=col_idx, sticky=tk.W, padx=2, pady=1)
            self.reg_labels[i] = ttk.Label(self.reg_frame, text="0 (0x00000000)", width=25, relief=tk.GROOVE, anchor=tk.W)
            self.reg_labels[i].grid(row=row_idx, column=col_idx + 1, sticky=tk.W, padx=2, pady=1)

        # PC 单独显示
        self.pc_label_title = ttk.Label(self.reg_frame, text="PC:")
        self.pc_label_title.grid(row=16, column=0, sticky=tk.W, padx=2, pady=(5,1))
        self.pc_label_val = ttk.Label(self.reg_frame, text="0 (0x00000000)", width=25, relief=tk.GROOVE, anchor=tk.W)
        self.pc_label_val.grid(row=16, column=1, sticky=tk.W, padx=2, pady=(5,1))

        separator = ttk.Separator(right_pane, orient='horizontal')
        separator.grid(row=2, column=0, sticky='ew', padx=5, pady=10)

        # --- 内存视图 (8位字節) ---
        ttk.Label(right_pane, text="内存视图:").grid(row=3, column=0, sticky=tk.NW, padx=(5,0), pady=(10,2)) # 放在第2行, 增加上邊距

        self.mem_frame = ttk.Frame(right_pane)
        self.mem_frame.grid(row=4, column=0, sticky='nsew', padx=(5,0)) # 放在第3行
        self.mem_frame.rowconfigure(2, weight=1)
        self.mem_frame.columnconfigure(0, weight=1)

        mem_nav_frame = ttk.Frame(self.mem_frame)
        mem_nav_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5))

        # 添加內存視圖的列標題
        # (前面的空格用於和地址欄對齊)
        header_str = "                              0     1     2     3     4     5     6     7      8     9    A    B    C    D    E    F"
        mem_header_label = ttk.Label(self.mem_frame, text=header_str, font=('Times New Roman', 11, 'bold'))
        mem_header_label.grid(row=1, column=0, columnspan=2, sticky='ew', padx=(0, 15)) # 放在第 1 行

        ttk.Label(mem_nav_frame, text="地址(Hex):").pack(side=tk.LEFT, padx=(0,2))
        self.mem_addr_entry = ttk.Entry(mem_nav_frame, width=10)
        self.mem_addr_entry.pack(side=tk.LEFT, padx=2)
        self.mem_addr_entry.insert(0, "0") # 默认显示地址 0
        ttk.Button(mem_nav_frame, text="跳转", command=self.go_to_memory_address).pack(side=tk.LEFT, padx=2)

# 内存显示文本区 (tk.Text)
        self.memory_display_text = tk.Text(self.mem_frame, wrap='none', undo=False,
                                        font=self.actual_code_font,
                                        width=62) # 重新设置固定宽度以匹配 "地址 + 16字节"
        self.memory_display_text.grid(row=2, column=0, sticky='nsew')

        # 内存显示区的垂直滚动条
        mem_v_scrollbar = ttk.Scrollbar(self.mem_frame, orient="vertical", command=self.memory_display_text.yview)
        mem_v_scrollbar.grid(row=2, column=1, sticky='ns')
        
        # [已移除] 水平滚动条
        # mem_h_scrollbar = ttk.Scrollbar(self.mem_frame, orient="horizontal", command=self.memory_display_text.xview)
        # mem_h_scrollbar.grid(row=2, column=0, sticky='ew')

        # 只关联垂直滚动条
        self.memory_display_text.config(yscrollcommand=mem_v_scrollbar.set)

        # --- 初始化 ---
        self.memory_view_start_addr = 0

        # 语法高亮模式
        self.opcodes = list(INSTRUCTION_MAP.keys())
        instructions_pattern = r"\b(" + "|".join(self.opcodes) + r")\b"
        register_names = list(REGISTER_MAP.keys())
        sorted_reg_names = sorted(register_names, key=len, reverse=True)
        all_registers_pattern = r"\b(" + "|".join(sorted_reg_names) + r")\b"

        self.highlight_patterns = {
            'comment_tag': r"(#|//|///)[^\n]*",
            'instruction_tag': instructions_pattern,
            'register_tag': all_registers_pattern,
        }
        self.highlight_order = ['comment_tag', 'instruction_tag', 'register_tag']

        self._redraw_line_numbers()
        self.apply_syntax_highlighting()
        self.update_ui_state()
        self.go_to_memory_address()


    def on_line_number_click(self, event):
        try:
            line_start_index = self.line_numbers_text.index(f"@{event.x},{event.y} linestart")
            clicked_line_num = int(line_start_index.split('.')[0])
            code_lines = int(self.code_text.index('end-1c').split('.')[0]) if self.code_text.get("1.0", "end-1c").strip() else 0

            if 1 <= clicked_line_num <= code_lines:
                if clicked_line_num in self.breakpoints:
                    self.breakpoints.remove(clicked_line_num)
                    print(f"断点已移除: 第 {clicked_line_num} 行")
                else:
                    self.breakpoints.add(clicked_line_num)
                    print(f"断点已设置: 第 {clicked_line_num} 行")
                self._redraw_line_numbers()
            else:
                print(f"无效的断点行: {clicked_line_num} (总代码行数: {code_lines})")
        except Exception:
            pass
        return "break"

    def _redraw_line_numbers(self, event=None):
        self.line_numbers_text.config(state='normal')
        self.line_numbers_text.delete('1.0', 'end')

        lines_str = self.code_text.index('end-1c').split('.')[0]
        lines = int(lines_str) if lines_str else 1
        first_char_of_last_line = self.code_text.get(f"{lines}.0") if lines > 0 else ""
        if not self.code_text.get("1.0", "end-1c").strip() and lines == 1 and not first_char_of_last_line:
            lines = 0

        max_digits = len(str(lines)) if lines > 0 else 1
        display_width = max_digits + 1
        self.line_numbers_text.config(width=display_width)

        if lines > 0:
            for i in range(1, lines + 1):
                line_display_content = ""
                apply_breakpoint_tag = False
                if i in self.breakpoints:
                    line_display_content = "●".rjust(max_digits)
                    apply_breakpoint_tag = True
                else:
                    line_display_content = str(i).rjust(max_digits)

                full_line_in_gutter = f"{line_display_content}\n"
                current_line_tk_index_str = f"{i}.0"
                self.line_numbers_text.insert('end', full_line_in_gutter)
                if apply_breakpoint_tag:
                    tag_start = current_line_tk_index_str
                    tag_end = f"{current_line_tk_index_str} + {len(line_display_content)} chars"
                    self.line_numbers_text.tag_add("breakpoint_set_marker", tag_start, tag_end)

        self.line_numbers_text.config(state='disabled')
        self.line_numbers_text.update_idletasks()
        self._scroll_sync_y()

    def _schedule_highlighting(self):
        if self._highlight_job:
            self.root.after_cancel(self._highlight_job)
        self._highlight_job = self.root.after(200, self.apply_syntax_highlighting)

    def apply_syntax_highlighting(self):
        if not hasattr(self, 'code_text') or not self.code_text.winfo_exists():
            return
        for tag in self.highlight_tags:
            self.code_text.tag_remove(tag, "1.0", "end")
        content = self.code_text.get("1.0", "end-1c")
        for tag_name in self.highlight_order:
            pattern = self.highlight_patterns.get(tag_name)
            if not pattern: continue
            flags = re.IGNORECASE
            for match in re.finditer(pattern, content, flags):
                start_index = f"1.0 + {match.start()} chars"
                end_index = f"1.0 + {match.end()} chars"
                self.code_text.tag_add(tag_name, start_index, end_index)

    def on_text_modified(self, event=None):
        if self.code_text.edit_modified():
            if self._line_number_update_job:
                self.root.after_cancel(self._line_number_update_job)
            self._line_number_update_job = self.root.after(50, self._redraw_line_numbers)
            if hasattr(self, '_schedule_highlighting'):
                self._schedule_highlighting()
            self.code_text.edit_modified(False)

    def on_text_change(self, event=None):
        if self._line_number_update_job:
            self.root.after_cancel(self._line_number_update_job)
        self._line_number_update_job = self.root.after(100, self._redraw_line_numbers)
        if hasattr(self, '_schedule_highlighting'):
            self._schedule_highlighting()

    def load_file(self, filepath=None):
        chosen_filepath = filepath
        if chosen_filepath is None:
            chosen_filepath = filedialog.askopenfilename(
                title="打开汇编文件",
                filetypes=(("汇编文件", "*.asm *.s *.txt"), ("所有文件", "*.*"))
            )
        if chosen_filepath:
            try:
                with open(chosen_filepath, 'r', encoding='utf-8') as f:
                    self.code_text.delete('1.0', tk.END)
                    self.code_text.insert('1.0', f.read())
                self.code_text.edit_modified(False)
                self.status_label.config(text=f"已加载: {chosen_filepath}")
                self._redraw_line_numbers()
                if hasattr(self, 'apply_syntax_highlighting'):
                    self.apply_syntax_highlighting()
                self.assemble_code() # 自动汇编
            except Exception as e:
                self.status_label.config(text=f"加载文件错误: {e}")

    def _update_current_line_highlight(self):
        # 移除旧高亮
        if self.current_highlighted_tk_line is not None:
            try:
                line_start = f"{self.current_highlighted_tk_line}.0"
                line_end = f"{self.current_highlighted_tk_line}.end lineend"
                self.code_text.tag_remove('current_execution_line_tag', line_start, line_end)
            except tk.TclError:
                pass
        self.current_highlighted_tk_line = None

        # 应用新高亮
        if not self.simulator.halted and hasattr(self.simulator, 'pc_to_source_line_map'):
            # 使用 previous_pc 来高亮刚刚执行过的指令
            current_pc = self.simulator.previous_pc

            if current_pc in self.simulator.pc_to_source_line_map:
                source_line_num_1_based = self.simulator.pc_to_source_line_map[current_pc]
                if source_line_num_1_based > 0:
                    try:
                        line_start_index = f"{source_line_num_1_based}.0"
                        line_end_index = f"{source_line_num_1_based}.end lineend"
                        self.code_text.tag_add('current_execution_line_tag', line_start_index, line_end_index)
                        self.code_text.see(line_start_index) # 滚动到该行
                        self.current_highlighted_tk_line = source_line_num_1_based
                    except tk.TclError as e:
                        print(f"高亮错误: 无法高亮行 {source_line_num_1_based} (PC={current_pc}): {e}")

    def _update_button_states(self):
        if self.is_running_continuously:
            self.run_btn.config(state=tk.DISABLED)
            self.step_btn.config(state=tk.DISABLED)
            self.assemble_btn.config(state=tk.DISABLED)
            self.load_btn.config(state=tk.DISABLED)
            self.reset_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            can_run_or_step = not self.simulator.halted and self.simulator.pc < len(self.simulator.rom)
            self.run_btn.config(state=tk.NORMAL if can_run_or_step else tk.DISABLED)
            self.step_btn.config(state=tk.NORMAL if can_run_or_step else tk.DISABLED)
            self.assemble_btn.config(state=tk.NORMAL)
            self.load_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def assemble_code(self):
        self.status_label.config(text="正在汇编...")
        self.root.update_idletasks()
        self._redraw_line_numbers()
        self.apply_syntax_highlighting()

        asm_code = self.code_text.get('1.0', tk.END)
        asm_lines = asm_code.splitlines()

        try:
            # 使用我们在此文件中定义的汇编函数
            symbol_table, err = first_pass(asm_lines)
            if err:
                self.status_label.config(text=f"汇编错误 (Pass 1): {err}")
                return

            # 接收 source_line_map
            binary_codes, errors, source_line_map_list = second_pass(asm_lines, symbol_table)

            if errors:
                self.status_label.config(text=f"汇编错误 (Pass 2): {errors[0]}")
                return

            # 加载到新的32位模拟器
            self.simulator.load_program_from_binary_strings(binary_codes, source_line_map_list)

            self.status_label.config(text=f"汇编成功: {len(binary_codes)} 条指令已加载。")
            self.simulator.halted = False

        except Exception as e:
            self.status_label.config(text=f"汇编失败: {e}")
            import traceback; traceback.print_exc()
            self.simulator.halted = True

        self.update_ui_state()
        self.go_to_memory_address() # 刷新内存视图

    def go_to_memory_address(self):
        addr_str = self.mem_addr_entry.get().strip()
        try:
            start_addr = int(addr_str, 16)
            # if not (0 <= start_addr < len(self.simulator.memory)):
            #     self.status_label.config(text=f"错误: 地址 0x{start_addr:X} 超出内存范围")
            #     return

            # 确保地址是4字节对齐的
            start_addr = start_addr & ~0x3
            self.mem_addr_entry.delete(0, tk.END)
            self.mem_addr_entry.insert(0, f"{start_addr:X}")
            self.memory_view_start_addr = start_addr
            self._update_memory_view()
            self.status_label.config(text=f"内存视图已跳转到地址 0x{start_addr:X}")
        except ValueError:
            self.status_label.config(text=f"错误: 无效的十六进制地址 '{addr_str}'")

    def _on_text_scroll(self, *args):
        self.v_scrollbar.set(*args)
        self.line_numbers_text.yview_moveto(args[0])

    def _on_scrollbar_yview(self, *args):
        self.code_text.yview(*args)
        self.line_numbers_text.yview(*args)

    def _on_unified_mousewheel_scroll(self, event):
        delta_scroll = 0
        if event.num == 4: delta_scroll = -1
        elif event.num == 5: delta_scroll = 1
        elif hasattr(event, 'delta') and event.delta != 0:
            delta_scroll = -1 * (event.delta // 120)
        if delta_scroll != 0:
            self.code_text.yview_scroll(delta_scroll, "units")
        return "break"


    def _scroll_sync_y(self, event=None):
        # 确保行号区的垂直滚动与代码区一致
        # 当代码区通过键盘、API等方式滚动时，其yscrollcommand会触发 _on_text_scroll
        # _on_text_scroll 已经负责了大部分同步。此函数可用于在其他情况下强制同步。
        top_fraction, _ = self.code_text.yview()
        self.line_numbers_text.yview_moveto(top_fraction)
        # 滚动条的位置也应该被正确设置，这由 _on_text_scroll -> self.v_scrollbar.set() 完成


    def _update_memory_view(self):
        # 更新内存视图为 "Hex Dump" 格式 (無ASCII)
        if not hasattr(self, 'memory_display_text') or not self.memory_display_text.winfo_exists():
            return

        self.memory_display_text.config(state='normal')
        self.memory_display_text.delete('1.0', 'end')

        start_addr = self.memory_view_start_addr
        # 确保地址从16字节对齐处开始
        start_addr = start_addr & ~0xF

        num_rows = 32 # 一次显示32行
        addr_width = 8 # 32位地址

        for row in range(num_rows):
            current_base_addr = start_addr + (row * 16)

            # 1. 格式化地址列
            addr_str = f"0x{current_base_addr:0{addr_width}X}: "

            hex_bytes_str = ""
            bytes_for_this_row = []

            # 2. 读取本行的16个字节
            for i in range(16):
                byte_addr = current_base_addr + i
                try:
                    byte_val = self.simulator.mem_read(byte_addr, 1, signed=False)
                    bytes_for_this_row.append(byte_val)
                except MemoryError:
                    bytes_for_this_row.append(None) # 未映射地址
                except Exception:
                    bytes_for_this_row.append(-1)   # 读取错误

            # 3. 格式化十六进制列
            for i, byte_val in enumerate(bytes_for_this_row):
                if i == 8:
                    hex_bytes_str += " " # 在中间加一空格

                if byte_val is None:
                    hex_bytes_str += "-- "
                elif byte_val == -1:
                    hex_bytes_str += "ER "
                else:
                    hex_bytes_str += f"{byte_val:02X} "

            # 4. [已移除] ASCII列

            # 5. 合并并插入行
            line = f"{addr_str} {hex_bytes_str}\n"
            self.memory_display_text.insert('end', line)

        self.memory_display_text.config(state='disabled')
    def update_ui_state(self, is_continuous_run=False):
        # 更新寄存器
        for i in range(32):
            val = self.simulator.get_reg_value(i)
            self.reg_labels[i].config(text=f"{val} (0x{val:08X})")

        # 更新PC
        pc_val = self.simulator.pc
        self.pc_label_val.config(text=f"{pc_val} (0x{pc_val:08X})")

        # 更新内存
        if not is_continuous_run:
            self._update_memory_view()
        elif self.run_step_counter % 20 == 0: # 连续运行时节流
            self._update_memory_view()

        self._update_button_states()
        self._scroll_sync_y()
        self._update_current_line_highlight()

    def step_code(self):
        if self.simulator.step():
            self.status_label.config(text=f"已单步执行. PC = 0x{self.simulator.pc:08X}")
        else:
            self.status_label.config(text="模拟器已停止")
        self.update_ui_state()

    def run_code(self):
        if self.is_running_continuously: return
        if self.simulator.halted:
            self.status_label.config(text="模拟器已停止，无法连续执行。请重置。")
            return
        self.is_running_continuously = True
        self.status_label.config(text="正在连续执行...")
        self._update_button_states()
        self._execute_next_instruction_in_run_mode()

    def _execute_next_instruction_in_run_mode(self):
        # 1. 检查是否应该停止 (由用户点击停止、模拟器已停止)
        if not self.is_running_continuously or self.simulator.halted:
            self.is_running_continuously = False # 确保标志位正确

            if self._continuous_run_job:
                self.root.after_cancel(self._continuous_run_job)
                self._continuous_run_job = None

            # 检查状态，避免覆盖“断点暂停”或“手动停止”
            current_status = self.status_label.cget("text")
            if "暂停" not in current_status and "停止" not in current_status:

                # [新] 区分错误还是正常结束
                if self.simulator.error_message:
                    self.status_label.config(text=f"模拟器因错误而停止!")
                else:
                    self.status_label.config(text="程序执行完毕。")

            self._update_button_states() # 更新所有按钮
            self.update_ui_state()       # 更新UI显示（寄存器、PC、高亮等）
            return # 结束本次执行

        # 2. 断点检查 (在执行指令之前)
        current_pc = self.simulator.pc
        if current_pc in self.simulator.pc_to_source_line_map:
            source_line_num = self.simulator.pc_to_source_line_map[current_pc]
            if source_line_num in self.breakpoints:
                # 命中断点
                self.is_running_continuously = False # 停止连续运行
                self.status_label.config(text=f"在断点处暂停: 第 {source_line_num} 行 (PC=0x{current_pc:08X})")
                self._update_button_states() # 更新按钮状态（启用"单步"、"执行"等）
                self.update_ui_state()       # 刷新UI以高亮断点行
                # 暂停执行，不调用 step() 也不安排下一次 after()
                return

        # 3. 如果没有命中断点，则执行一步
        # simulator.step() 会执行指令并更新PC。如果执行后出错或结束，它会返回 False。
        if not self.simulator.step():
            self.is_running_continuously = False # 模拟器内部停止了

            # 区分错误还是正常结束
            if self.simulator.error_message:
                self.status_label.config(text=f"模拟器因错误而停止!")
            else:
                self.status_label.config(text="程序执行完毕。")

            self._update_button_states()
            self.update_ui_state()
            return

        # 4. 更新UI并安排下一次执行
        # (节流, is_continuous_run=True)
        self.update_ui_state(is_continuous_run=True)

        # 再次检查，以防 step() 操作改变了状态
        if self.is_running_continuously and not self.simulator.halted:
            delay_ms = 1  # 32位很快，延迟调低
            self._continuous_run_job = self.root.after(delay_ms, self._execute_next_instruction_in_run_mode)

    def stop_continuous_run(self):
        if self.is_running_continuously:
            self.status_label.config(text="已手动停止连续执行.")
        self.is_running_continuously = False
        if self._continuous_run_job:
            self.root.after_cancel(self._continuous_run_job)
            self._continuous_run_job = None
        self._update_button_states()

    def reset_simulator(self):
        self.is_running_continuously = False
        if self._continuous_run_job:
            self.root.after_cancel(self._continuous_run_job)
            self._continuous_run_job = None

        self.simulator.reset()
        self.status_label.config(text="已重置.")
        self.breakpoints.clear()

        if self.current_highlighted_tk_line is not None:
            try:
                line_start = f"{self.current_highlighted_tk_line}.0"
                line_end = f"{self.current_highlighted_tk_line}.end lineend"
                self.code_text.tag_remove('current_execution_line_tag', line_start, line_end)
            except tk.TclError: pass
        self.current_highlighted_tk_line = None

        self._update_button_states()
        self.update_ui_state()
        self._redraw_line_numbers()


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()