import re

# 寄存器名称到编号的映射表
REGISTER_MAP = {
    'x0': 0, 'zero': 0,
    'x1': 1, 'ra': 1,
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
    # R-type (RV32M Extension)，等待验证
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
        # format(value, '0_width_b')
        return format(num, f'0{bits}b')
    else:
        # Two's complement for negative numbers
        return format((1 << bits) + num, f'0{bits}b')


# 各类型指令处理器
def get_reg_num(reg_name):
    # 通过名称查找寄存器编号
    return REGISTER_MAP.get(reg_name.lower())

def handle_r_type(instr, operands):
    rd_num, rs1_num, rs2_num = get_reg_num(operands[0]), get_reg_num(operands[1]), get_reg_num(operands[2])
    if any(r is None for r in [rd_num, rs1_num, rs2_num]): return None
    rd, rs1, rs2 = format(rd_num, '05b'), format(rs1_num, '05b'), format(rs2_num, '05b')
    return instr['funct7'] + rs2 + rs1 + instr['funct3'] + rd + instr['opcode']

def handle_i_type(instr, operands):
    rd_num, rs1_num = get_reg_num(operands[0]), get_reg_num(operands[1])
    if any(r is None for r in [rd_num, rs1_num]): return None
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    imm = to_signed_binary(int(operands[2]), 12)
    return imm + rs1 + instr['funct3'] + rd + instr['opcode']

def handle_i_shift_type(instr, operands):
    rd_num, rs1_num = get_reg_num(operands[0]), get_reg_num(operands[1])
    if any(r is None for r in [rd_num, rs1_num]): return None
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    shamt = format(int(operands[2]), '05b')
    return instr['funct7'] + shamt + rs1 + instr['funct3'] + rd + instr['opcode']

def handle_i_load_type(instr, operands):
    rd_num, rs1_num = get_reg_num(operands[0]), get_reg_num(operands[2])
    if any(r is None for r in [rd_num, rs1_num]): return None
    rd, rs1 = format(rd_num, '05b'), format(rs1_num, '05b')
    imm = to_signed_binary(int(operands[1]), 12)
    return imm + rs1 + instr['funct3'] + rd + instr['opcode']

def handle_s_type(instr, operands):
    rs2_num, rs1_num = get_reg_num(operands[0]), get_reg_num(operands[2])
    if any(r is None for r in [rs2_num, rs1_num]): return None
    rs2, rs1 = format(rs2_num, '05b'), format(rs1_num, '05b')
    imm = to_signed_binary(int(operands[1]), 12)
    imm11_5, imm4_0 = imm[0:7], imm[7:12]
    return imm11_5 + rs2 + rs1 + instr['funct3'] + imm4_0 + instr['opcode']

def handle_b_type(instr, operands):
    rs1_num, rs2_num = get_reg_num(operands[0]), get_reg_num(operands[1])
    if any(r is None for r in [rs1_num, rs2_num]): return None
    rs1, rs2 = format(rs1_num, '05b'), format(rs2_num, '05b')

    imm_val = int(operands[2])

    # Extract immediate bits using reliable bitwise shifts and masks
    imm12 = (imm_val >> 12) & 1
    imm11 = (imm_val >> 11) & 1
    imm10_5 = (imm_val >> 5) & 0b111111  # 6 bits
    imm4_1 = (imm_val >> 1) & 0b1111    # 4 bits

    # Convert extracted parts to binary strings
    imm12_bin = format(imm12, '01b')
    imm11_bin = format(imm11, '01b')
    imm10_5_bin = format(imm10_5, '06b')
    imm4_1_bin = format(imm4_1, '04b')

    # Assemble the final instruction string
    # Format: imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode
    return imm12_bin + imm10_5_bin + rs2 + rs1 + instr['funct3'] + imm4_1_bin + imm11_bin + instr['opcode']

def handle_u_type(instr, operands):
    rd_num = get_reg_num(operands[0])
    if rd_num is None: return None
    rd = format(rd_num, '05b')
    imm = to_signed_binary(int(operands[1]), 20)
    return imm + rd + instr['opcode']

def handle_j_type(instr, operands):
    rd_num = get_reg_num(operands[0])
    if rd_num is None: return None
    rd = format(rd_num, '05b')
    imm = to_signed_binary(int(operands[1]), 21)
    imm20, imm10_1, imm11, imm19_12 = imm[0], imm[10:20], imm[9], imm[1:9]
    return imm20 + imm10_1 + imm11 + imm19_12 + rd + instr['opcode']

# 指令解析与分发 (已更新正则表达式)
def parse_and_convert(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None

    # 更通用的正则表达式，用于捕获物理寄存器(x_num)或ABI名称
    reg = r'([a-zA-Z0-9]+)'
    imm = r'(-?\d+)'

    patterns = [
        (rf'(\w+)\s+{reg},\s*{reg},\s*{reg}', ('R')),
        (rf'(\w+)\s+{reg},\s*{reg},\s*{imm}', ('I', 'I-shift', 'B')),
        (rf'(\w+)\s+{reg},\s*{imm}\({reg}\)', ('S', 'I-load')),
        (rf'(\w+)\s+{reg},\s*{imm}', ('U', 'J')),
    ]

    original_line = line
    line = line.lower() # 转为小写以匹配map

    for pattern, types in patterns:
        match = re.match(pattern, line)
        if match:
            mnemonic = match.group(1)
            if mnemonic in INSTRUCTION_MAP and INSTRUCTION_MAP[mnemonic]['type'] in types:
                instr_info = INSTRUCTION_MAP[mnemonic]
                instr_type = instr_info['type']
                operands = match.groups()[1:]

                handler_map = {
                    'R': handle_r_type, 'I': handle_i_type, 'I-shift': handle_i_shift_type,
                    'I-load': handle_i_load_type, 'S': handle_s_type, 'B': handle_b_type,
                    'U': handle_u_type, 'J': handle_j_type,
                }

                machine_code = handler_map[instr_type](instr_info, operands)

                if machine_code:
                    return machine_code, None
                else:
                    return None, f"警告: 指令 '{original_line}' 中包含无效的寄存器名称。"

    return None, f"警告: 无法解析或不支持的指令 '{original_line}'，已跳过。"

# 主转换函数
def convert_instructions_to_machine_code(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            for line_num, line in enumerate(infile, 1):
                machine_code, error_msg = parse_and_convert(line)
                if machine_code:
                    outfile.write(machine_code + '\n')
                elif error_msg:
                    print(f"第 {line_num} 行: {error_msg}")
        print(f"转换完成！机器码已保存至 '{output_file_path}'。")
    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_file_path}' 未找到。")
    except Exception as e:
        print(f"发生未知错误: {e}")


input_filename = "data/input.txt"
output_filename = "data/output.txt"

# 执行
convert_instructions_to_machine_code(input_filename, output_filename)