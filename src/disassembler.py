import os

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
    'x31': 31, 't6': 31
}
INSTRUCTION_MAP = {
    'add': {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0000000'},
    'sub': {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0100000'},
    'sll': {'type': 'R', 'opcode': '0110011', 'funct3': '001', 'funct7': '0000000'},
    'slt': {'type': 'R', 'opcode': '0110011', 'funct3': '010', 'funct7': '0000000'},
    'sltu': {'type': 'R', 'opcode': '0110011', 'funct3': '011', 'funct7': '0000000'},
    'xor': {'type': 'R', 'opcode': '0110011', 'funct3': '100', 'funct7': '0000000'},
    'srl': {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0000000'},
    'sra': {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0100000'},
    'or': {'type': 'R', 'opcode': '0110011', 'funct3': '110', 'funct7': '0000000'},
    'and': {'type': 'R', 'opcode': '0110011', 'funct3': '111', 'funct7': '0000000'},
    'mul': {'type': 'R', 'opcode': '0110011', 'funct3': '000', 'funct7': '0000001'},
    'mulh': {'type': 'R', 'opcode': '0110011', 'funct3': '001', 'funct7': '0000001'},
    'mulhsu': {'type': 'R', 'opcode': '0110011', 'funct3': '010', 'funct7': '0000001'},
    'mulhu': {'type': 'R', 'opcode': '0110011', 'funct3': '011', 'funct7': '0000001'},
    'div': {'type': 'R', 'opcode': '0110011', 'funct3': '100', 'funct7': '0000001'},
    'divu': {'type': 'R', 'opcode': '0110011', 'funct3': '101', 'funct7': '0000001'},
    'rem': {'type': 'R', 'opcode': '0110011', 'funct3': '110', 'funct7': '0000001'},
    'remu': {'type': 'R', 'opcode': '0110011', 'funct3': '111', 'funct7': '0000001'},
    'addi': {'type': 'I', 'opcode': '0010011', 'funct3': '000'},
    'slti': {'type': 'I', 'opcode': '0010011', 'funct3': '010'},
    'sltiu': {'type': 'I', 'opcode': '0010011', 'funct3': '011'},
    'xori': {'type': 'I', 'opcode': '0010011', 'funct3': '100'},
    'ori': {'type': 'I', 'opcode': '0010011', 'funct3': '110'},
    'andi': {'type': 'I', 'opcode': '0010011', 'funct3': '111'},
    'slli': {'type': 'I-shift', 'opcode': '0010011', 'funct3': '001'},
    'srli': {'type': 'I-shift', 'opcode': '0010011', 'funct3': '101', 'funct7': '0000000'},
    'srai': {'type': 'I-shift', 'opcode': '0010011', 'funct3': '101', 'funct7': '0100000'},
    'lb': {'type': 'I-load', 'opcode': '0000011', 'funct3': '000'},
    'lh': {'type': 'I-load', 'opcode': '0000011', 'funct3': '001'},
    'lw': {'type': 'I-load', 'opcode': '0000011', 'funct3': '010'},
    'lbu': {'type': 'I-load', 'opcode': '0000011', 'funct3': '100'},
    'lhu': {'type': 'I-load', 'opcode': '0000011', 'funct3': '101'},
    'jalr': {'type': 'I-jalr', 'opcode': '1100111', 'funct3': '000'},
    'sb': {'type': 'S', 'opcode': '0100011', 'funct3': '000'},
    'sh': {'type': 'S', 'opcode': '0100011', 'funct3': '001'},
    'sw': {'type': 'S', 'opcode': '0100011', 'funct3': '010'},
    'beq': {'type': 'B', 'opcode': '1100011', 'funct3': '000'},
    'bne': {'type': 'B', 'opcode': '1100011', 'funct3': '001'},
    'blt': {'type': 'B', 'opcode': '1100011', 'funct3': '100'},
    'bge': {'type': 'B', 'opcode': '1100011', 'funct3': '101'},
    'bltu': {'type': 'B', 'opcode': '1100011', 'funct3': '110'},
    'bgeu': {'type': 'B', 'opcode': '1100011', 'funct3': '111'},
    'lui': {'type': 'U', 'opcode': '0110111'},
    'auipc': {'type': 'U', 'opcode': '0010111'},
    'jal': {'type': 'J', 'opcode': '1101111'},
}


REVERSE_MAP = {}
for name, details in INSTRUCTION_MAP.items():
    key = (
        details['opcode'],
        details.get('funct3'), # Use .get() for safe access
        details.get('funct7')
    )
    REVERSE_MAP[key] = {'mnemonic': name, 'type': details['type']}

ABI_MAP = {v: k for k, v in REGISTER_MAP.items() if 'x' not in k and 'r' not in k and k not in ('zero', 'fp')}
ABI_MAP[0] = 'zero'


def from_twos_complement(bin_str):
    val = int(bin_str, 2)
    bits = len(bin_str)
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def disassemble_r_type(code, details):
    rs2_bin, rs1_bin, rd_bin = code[7:12], code[12:17], code[20:25]
    rd = ABI_MAP.get(int(rd_bin, 2), f'x{int(rd_bin, 2)}')
    rs1 = ABI_MAP.get(int(rs1_bin, 2), f'x{int(rs1_bin, 2)}')
    rs2 = ABI_MAP.get(int(rs2_bin, 2), f'x{int(rs2_bin, 2)}')
    return f"{details['mnemonic']} {rd}, {rs1}, {rs2}"

def disassemble_i_type(code, details):
    imm_bin, rs1_bin, rd_bin = code[0:12], code[12:17], code[20:25]
    rd = ABI_MAP.get(int(rd_bin, 2), f'x{int(rd_bin, 2)}')
    rs1 = ABI_MAP.get(int(rs1_bin, 2), f'x{int(rs1_bin, 2)}')
    imm = from_twos_complement(imm_bin)
    instr_type = details['type']
    if instr_type == 'I-load' or instr_type == 'I-jalr':
        return f"{details['mnemonic']} {rd}, {imm}({rs1})"
    elif instr_type == 'I-shift':
        shamt = int(imm_bin[-5:], 2)
        return f"{details['mnemonic']} {rd}, {rs1}, {shamt}"
    else:
        return f"{details['mnemonic']} {rd}, {rs1}, {imm}"

def disassemble_s_type(code, details):
    imm11_5, rs2_bin, rs1_bin, imm4_0 = code[0:7], code[7:12], code[12:17], code[20:25]
    rs1 = ABI_MAP.get(int(rs1_bin, 2), f'x{int(rs1_bin, 2)}')
    rs2 = ABI_MAP.get(int(rs2_bin, 2), f'x{int(rs2_bin, 2)}')
    imm = from_twos_complement(imm11_5 + imm4_0)
    return f"{details['mnemonic']} {rs2}, {imm}({rs1})"

def disassemble_b_type(code, details):
    imm12, imm10_5, rs2_bin, rs1_bin, imm4_1, imm11 = code[0], code[1:7], code[7:12], code[12:17], code[20:24], code[24]
    rs1 = ABI_MAP.get(int(rs1_bin, 2), f'x{int(rs1_bin, 2)}')
    rs2 = ABI_MAP.get(int(rs2_bin, 2), f'x{int(rs2_bin, 2)}')
    imm_bin = imm12 + imm11 + imm10_5 + imm4_1 + '0'
    imm = from_twos_complement(imm_bin)
    return f"{details['mnemonic']} {rs1}, {rs2}, {imm}"

def disassemble_u_type(code, details):
    imm_bin, rd_bin = code[0:20], code[20:25]
    rd = ABI_MAP.get(int(rd_bin, 2), f'x{int(rd_bin, 2)}')
    # For LUI, the immediate is often displayed as the value for the upper bits
    imm = int(imm_bin, 2)
    return f"{details['mnemonic']} {rd}, {imm}"

def disassemble_j_type(code, details):
    imm20, imm10_1, imm11, imm19_12, rd_bin = code[0], code[1:11], code[11], code[12:20], code[20:25]
    rd = ABI_MAP.get(int(rd_bin, 2), f'x{int(rd_bin, 2)}')
    imm_bin = imm20 + imm19_12 + imm11 + imm10_1 + '0'
    imm = from_twos_complement(imm_bin)
    return f"{details['mnemonic']} {rd}, {imm}"


# 主流程

def disassemble_instruction(code):
    if len(code) != 32 or not all(c in '01' for c in code):
        return f"错误: 无效的输入 '{code}'"

    opcode = code[25:32]
    funct3 = code[17:20]
    funct7 = code[0:7]

    # 尝试用最精确的 key (opcode, funct3, funct7) 查找
    details = REVERSE_MAP.get((opcode, funct3, funct7))
    # 如果找不到，尝试忽略 funct7
    if not details:
        details = REVERSE_MAP.get((opcode, funct3, None))
    # 如果还找不到，尝试忽略 funct3 和 funct7 (适用于 U/J 型)
    if not details:
        details = REVERSE_MAP.get((opcode, None, None))

    if not details:
        return f"未知指令 (opcode:{opcode}, funct3:{funct3}, funct7:{funct7})"

    handler_map = {
        'R': disassemble_r_type,
        'I': disassemble_i_type,
        'I-shift': disassemble_i_type,
        'I-load': disassemble_i_type,
        'I-jalr': disassemble_i_type,
        'S': disassemble_s_type,
        'B': disassemble_b_type,
        'U': disassemble_u_type,
        'J': disassemble_j_type,
    }

    return handler_map[details['type']](code, details)

def disassemble_file(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            for line_num, line in enumerate(infile, 1):
                code = line.strip()
                if not code: continue
                assembly = disassemble_instruction(code)
                outfile.write(f"{assembly}\n")
        print(f"反汇编成功！结果已保存至 '{output_path}'。")
    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_path}' 未找到。")
    except Exception as e:
        print(f"发生错误: {e}")


input_filename = "dis_input.txt"
output_filename = "dis_output.txt"

disassemble_file(input_filename, output_filename)
