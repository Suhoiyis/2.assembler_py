# windows_32bit.py
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, font
import re
import time

# ==============================================================================
# 汇编器逻辑 (从 assembler.py 复制并修改)
# ==============================================================================

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
    0: 'x0(zero)', 1: 'x1(ra)', 2: 'x2(sp)', 3: 'x3(gp)',
    4: 'x4(tp)', 5: 'x5(t0)', 6: 'x6(t1)', 7: 'x7(t2)',
    8: 'x8(s0/fp)', 9: 'x9(s1)', 10: 'x10(a0)', 11: 'x11(a1)',
    12: 'x12(a2)', 13: 'x13(a3)', 14: 'x14(a4)', 15: 'x15(a5)',
    16: 'x16(a6)', 17: 'x17(a7)', 18: 'x18(s2)', 19: 'x19(s3)',
    20: 'x20(s4)', 21: 'x21(s5)', 22: 'x22(s6)', 23: 'x23(s7)',
    24: 'x24(s8)', 25: 'x25(s9)', 26: 'x26(s10)', 27: 'x27(s11)',
    28: 'x28(t3)', 29: 'x29(t4)', 30: 'x30(t5)', 31: 'x31(t6)',
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
    source_line_map = [] # [新] 存储(机器码索引, 原始行号)
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
                    source_line_map.append((len(machine_codes) - 1, line_num)) # [新] 记录行号
                matched = True
                break

        if not matched and not any(f"第 {line_num} 行" in e for e in errors):
            errors.append(f"第 {line_num} 行: 无法解析的操作数格式 '{line_to_parse}'")

        address += 4
    return machine_codes, errors, source_line_map # [新] 返回行号


# ==============================================================================
# 32位RISC-V模拟器
# ==============================================================================
class Simulator32Bit:
    def __init__(self):
        self.registers = [0] * 32  # 32个 32位寄存器
        self.memory = bytearray(65536) # 64KB 的字节内存
        self.pc = 0
        self.previous_pc = 0
        self.halted = False
        self.pc_to_source_line_map = {} # PC (地址) -> 源代码行号

    def reset(self):
        self.registers = [0] * 32
        self.memory = bytearray(len(self.memory))
        self.pc = 0
        self.previous_pc = 0
        self.halted = False
        self.pc_to_source_line_map = {}
        self.set_reg_value(2, len(self.memory))
        print("Simulator Reset.")

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
        address = 0
        for code_str in binary_codes:
            if len(code_str) != 32:
                print(f"Warning: Invalid machine code string: {code_str}")
                continue

            # 将32位二进制字符串转为整数，再转为4字节（小端）
            code_int = int(code_str, 2)
            try:
                self.memory[address : address + 4] = code_int.to_bytes(4, 'little')
            except OverflowError:
                print(f"Error: Machine code 0x{code_int:X} too large?")
                pass
            address += 4

        # 构建 PC (地址) -> 行号的映射
        self.pc_to_source_line_map = {}
        for (instr_index, line_num) in source_line_map_list:
            pc_address = instr_index * 4 # 每条指令4字节
            self.pc_to_source_line_map[pc_address] = line_num

        self.pc = 0
        self.halted = False
        print(f"Loaded {len(binary_codes)} instructions.")

    def fetch(self):
        if not (0 <= self.pc < len(self.memory) - 3):
            print(f"PC out of bounds: {self.pc}")
            self.halted = True
            return None

        # 从内存读取4字节（小端）并组装成32位指令
        instr_bytes = self.memory[self.pc : self.pc + 4]
        instruction_word = int.from_bytes(instr_bytes, 'little')
        return instruction_word

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
                    # [新] 为无符号操作准备操作数
                    rs1_unsigned = rs1_val & 0xFFFFFFFF
                    rs2_unsigned = rs2_val & 0xFFFFFFFF

                    if funct3 == 0b000: # mul
                        result = rs1_val * rs2_val
                    elif funct3 == 0b001: # mulh [cite: 190]
                        result = (rs1_val * rs2_val) >> 32
                    elif funct3 == 0b010: # mulhsu [cite: 192]
                        result = (rs1_val * rs2_unsigned) >> 32
                    elif funct3 == 0b011: # mulhu [cite: 194]
                        result = (rs1_unsigned * rs2_unsigned) >> 32
                    elif funct3 == 0b100: # div [cite: 196]
                        if rs2_val == 0:
                            result = -1 # 除以0，结果全为1
                        elif rs1_val == -2147483648 and rs2_val == -1:
                            result = -2147483648 # 溢出
                        else:
                            result = int(float(rs1_val) / rs2_val) # C-style 截断
                    elif funct3 == 0b101: # divu [cite: 198]
                        if rs2_unsigned == 0:
                            result = 0xFFFFFFFF # 除以0，结果全为1
                        else:
                            result = rs1_unsigned // rs2_unsigned
                    elif funct3 == 0b110: # rem [cite: 200]
                        if rs2_val == 0:
                            result = rs1_val # 除以0，结果为被除数
                        elif rs1_val == -2147483648 and rs2_val == -1:
                            result = 0 # 溢出
                        else:
                            # 使用C-style截断除法来计算余数
                            div_val = int(float(rs1_val) / rs2_val)
                            result = rs1_val - (div_val * rs2_val)
                    elif funct3 == 0b111: # remu [cite: 202]
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
                if funct3 == 0b000: result = rs1_val + imm # addi
                elif funct3 == 0b010: result = 1 if rs1_val < imm else 0 # slti
                elif funct3 == 0b011: result = 1 if (rs1_val & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0 # sltiu
                elif funct3 == 0b100: result = rs1_val ^ imm # xori
                elif funct3 == 0b110: result = rs1_val | imm # ori
                elif funct3 == 0b111: result = rs1_val & imm # andi
                elif funct3 == 0b001: # slli
                    shamt = (instr_word >> 20) & 0x1F
                    result = rs1_val << shamt
                elif funct3 == 0b101:
                    shamt = (instr_word >> 20) & 0x1F
                    if funct7 == 0b0000000: result = (rs1_val & 0xFFFFFFFF) >> shamt # srli
                    elif funct7 == 0b0100000: result = rs1_val >> shamt # srai
                self.set_reg_value(rd, result)

            # I-type (Load)
            elif opcode == 0b0000011:
                base_addr = self.get_reg_value(rs1)
                offset = self.sign_extend(instr_word >> 20, 12)
                mem_addr = (base_addr + offset) & 0xFFFFFFFF

                if not (0 <= mem_addr < len(self.memory)):
                    raise MemoryError(f"Load address 0x{mem_addr:X} out of bounds")

                if funct3 == 0b000: # lb
                    val = int.from_bytes(self.memory[mem_addr:mem_addr+1], 'little', signed=True)
                elif funct3 == 0b001: # lh
                    val = int.from_bytes(self.memory[mem_addr:mem_addr+2], 'little', signed=True)
                elif funct3 == 0b010: # lw
                    val = int.from_bytes(self.memory[mem_addr:mem_addr+4], 'little', signed=True)
                elif funct3 == 0b100: # lbu
                    val = int.from_bytes(self.memory[mem_addr:mem_addr+1], 'little', signed=False)
                elif funct3 == 0b101: # lhu
                    val = int.from_bytes(self.memory[mem_addr:mem_addr+2], 'little', signed=False)
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

                if not (0 <= mem_addr < len(self.memory)):
                    raise MemoryError(f"Store address 0x{mem_addr:X} out of bounds")

                if funct3 == 0b000: # sb
                    self.memory[mem_addr:mem_addr+1] = rs2_val.to_bytes(1, 'little', signed=True)
                elif funct3 == 0b001: # sh
                    self.memory[mem_addr:mem_addr+2] = rs2_val.to_bytes(2, 'little', signed=True)
                elif funct3 == 0b010: # sw
                    self.memory[mem_addr:mem_addr+4] = rs2_val.to_bytes(4, 'little', signed=True)
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
                if funct3 == 0b000 and rs1_val == rs2_val: branch_taken = True # beq
                elif funct3 == 0b001 and rs1_val != rs2_val: branch_taken = True # bne
                elif funct3 == 0b100 and rs1_val < rs2_val: branch_taken = True # blt
                elif funct3 == 0b101 and rs1_val >= rs2_val: branch_taken = True # bge
                elif funct3 == 0b110 and (rs1_val & 0xFFFFFFFF) < (rs2_val & 0xFFFFFFFF): branch_taken = True # bltu
                elif funct3 == 0b111 and (rs1_val & 0xFFFFFFFF) >= (rs2_val & 0xFFFFFFFF): branch_taken = True # bgeu

                if branch_taken:
                    next_pc = (self.pc + imm) & 0xFFFFFFFF

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
            print(f"执行错误: PC=0x{self.pc:08X}, Instr=0x{instr_word:08X}, Error={e}")
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


# ==============================================================================
# GUI 应用程序 (基于 windows.py 修改)
# ==============================================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("32位RISC-V单周期CPU模拟器")

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

        ttk.Label(code_area_frame, text="汇编代码 (RV32I):").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0,5))

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
        main_frame.columnconfigure(1, weight=2) # 给右侧面板更大权重
        right_pane.columnconfigure(0, weight=1) # 寄存器
        right_pane.columnconfigure(1, weight=1) # 内存
        right_pane.rowconfigure(1, weight=1)

        # --- 寄存器视图 (32个) ---
        ttk.Label(right_pane, text="寄存器:").grid(row=0, column=0,sticky=tk.NW, padx=(0,5), pady=(0,2))
        self.reg_frame = ttk.Frame(right_pane)
        self.reg_frame.grid(row=1, column=0, sticky='nsew', padx=(0,5))
        self.reg_labels = {}
        for i in range(32):
            reg_name = self.reg_num_to_name.get(i, f'x{i}')
            # 分两列显示
            row_idx = i % 16
            col_idx = (i // 16) * 2

            ttk.Label(self.reg_frame, text=f"{reg_name:<10}").grid(row=row_idx, column=col_idx, sticky=tk.W, padx=2, pady=1)
            self.reg_labels[i] = ttk.Label(self.reg_frame, text="0 (0x00000000)", width=20, relief=tk.GROOVE, anchor=tk.W)
            self.reg_labels[i].grid(row=row_idx, column=col_idx + 1, sticky=tk.W, padx=2, pady=1)

        # PC 单独显示
        self.pc_label_title = ttk.Label(self.reg_frame, text="PC:")
        self.pc_label_title.grid(row=16, column=0, sticky=tk.W, padx=2, pady=(5,1))
        self.pc_label_val = ttk.Label(self.reg_frame, text="0 (0x00000000)", width=20, relief=tk.GROOVE, anchor=tk.W)
        self.pc_label_val.grid(row=16, column=1, sticky=tk.W, padx=2, pady=(5,1))


        # --- 内存视图 (32位) ---
        ttk.Label(right_pane, text="内存视图 (32位字):").grid(row=0, column=1, sticky=tk.NW, padx=(5,0), pady=(0,2))
        self.mem_frame = ttk.Frame(right_pane)
        self.mem_frame.grid(row=1, column=1, sticky='nsew', padx=(5,0))
        self.mem_frame.rowconfigure(2, weight=1)
        self.mem_frame.columnconfigure(0, weight=1)

        mem_nav_frame = ttk.Frame(self.mem_frame)
        mem_nav_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5))
        ttk.Label(mem_nav_frame, text="地址(Hex):").pack(side=tk.LEFT, padx=(0,2))
        self.mem_addr_entry = ttk.Entry(mem_nav_frame, width=10)
        self.mem_addr_entry.pack(side=tk.LEFT, padx=2)
        self.mem_addr_entry.insert(0, "0") # 默认显示地址 0
        ttk.Button(mem_nav_frame, text="跳转", command=self.go_to_memory_address).pack(side=tk.LEFT, padx=2)

        self.memory_display_text = tk.Text(self.mem_frame, wrap='none', undo=False, font=self.actual_code_font, width=30)
        self.memory_display_text.grid(row=1, column=0, sticky='nsew')
        mem_v_scrollbar = ttk.Scrollbar(self.mem_frame, orient="vertical", command=self.memory_display_text.yview)
        mem_v_scrollbar.grid(row=1, column=1, sticky='ns')
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
            can_run_or_step = not self.simulator.halted and self.simulator.pc < len(self.simulator.memory)
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

            # [新] 接收 source_line_map
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
            if not (0 <= start_addr < len(self.simulator.memory)):
                self.status_label.config(text=f"错误: 地址 0x{start_addr:X} 超出内存范围")
                return

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
        # 更新内存视图，显示32位字
        if not hasattr(self, 'memory_display_text') or not self.memory_display_text.winfo_exists():
            return

        self.memory_display_text.config(state='normal')
        self.memory_display_text.delete('1.0', 'end')

        start_addr = self.memory_view_start_addr
        num_words_to_show = 64
        end_addr = min(start_addr + num_words_to_show * 4, len(self.simulator.memory))
        addr_width = 8 # 32位地址

        for current_addr in range(start_addr, end_addr, 4):
            word_bytes = self.simulator.memory[current_addr : current_addr + 4]
            word_val = int.from_bytes(word_bytes, 'little')

            # 格式化显示
            hex_val = f"{word_val:08X}"
            line = f"0x{current_addr:0{addr_width}X}: {hex_val}\n"
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
        if not self.is_running_continuously or self.simulator.halted:
            self.is_running_continuously = False
            if self._continuous_run_job:
                self.root.after_cancel(self._continuous_run_job)
                self._continuous_run_job = None

            current_status = self.status_label.cget("text")
            if "暂停" not in current_status and "停止" not in current_status:
                final_status = "程序执行完毕." if self.simulator.halted else "模拟器已停止."
                self.status_label.config(text=final_status)

            self._update_button_states()
            self.update_ui_state()
            return

        # 断点检查
        current_pc = self.simulator.pc
        if current_pc in self.simulator.pc_to_source_line_map:
            source_line_num = self.simulator.pc_to_source_line_map[current_pc]
            if source_line_num in self.breakpoints:
                self.is_running_continuously = False
                self.status_label.config(text=f"在断点处暂停: 第 {source_line_num} 行 (PC=0x{current_pc:08X})")
                self._update_button_states()
                self.update_ui_state()
                return

        if not self.simulator.step():
            self.is_running_continuously = False
            self.status_label.config(text="模拟器执行时遇到错误或结束。")
            self._update_button_states()
            self.update_ui_state()
            return

        self.update_ui_state(is_continuous_run=True)

        if self.is_running_continuously and not self.simulator.halted:
            delay_ms = 1 # 32位很快，延迟调低
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