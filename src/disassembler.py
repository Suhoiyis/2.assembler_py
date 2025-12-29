import os
import sys

# --- 1. 核心映射表 (保留原脚本逻辑) ---
REGISTER_MAP = {
    'x0': 0, 'zero': 0, 'r0': 0, 'x1': 1, 'ra': 1, 'r1': 1, 'x2': 2, 'sp': 2,
    'x3': 3, 'gp': 3, 'x4': 4, 'tp': 4, 'x5': 5, 't0': 5, 'x6': 6, 't1': 6,
    'x7': 7, 't2': 7, 'x8': 8, 's0': 8, 'fp': 8, 'x9': 9, 's1': 9, 'x10': 10, 'a0': 10,
    'x11': 11, 'a1': 11, 'x12': 12, 'a2': 12, 'x13': 13, 'a3': 13, 'x14': 14, 'a4': 14,
    'x15': 15, 'a5': 15, 'x16': 16, 'a6': 16, 'x17': 17, 'a7': 17, 'x18': 18, 's2': 18,
    'x19': 19, 's3': 19, 'x20': 20, 's4': 20, 'x21': 21, 's5': 21, 'x22': 22, 's6': 22,
    'x23': 23, 's7': 23, 'x24': 24, 's8': 24, 'x25': 25, 's9': 25, 'x26': 26, 's10': 26,
    'x27': 27, 's11': 27, 'x28': 28, 't3': 28, 'x29': 29, 't4': 29, 'x30': 30, 't5': 30,
    'x31': 31, 't6': 31
}

# 增加了 csrrw 等指令的支持，以防万一
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
    key = (details['opcode'], details.get('funct3'), details.get('funct7'))
    REVERSE_MAP[key] = {'mnemonic': name, 'type': details['type']}

ABI_MAP = {v: k for k, v in REGISTER_MAP.items() if 'x' not in k and 'r' not in k and k not in ('zero', 'fp')}
ABI_MAP[0] = 'zero'

# --- 2. 辅助函数 ---

def from_twos_complement(bin_str):
    val = int(bin_str, 2)
    bits = len(bin_str)
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# 反汇编实现 (I/R/S/B/U/J)
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
    imm = int(imm_bin, 2)
    return f"{details['mnemonic']} {rd}, 0x{imm:x}"

def disassemble_j_type(code, details):
    imm20, imm10_1, imm11, imm19_12, rd_bin = code[0], code[1:11], code[11], code[12:20], code[20:25]
    rd = ABI_MAP.get(int(rd_bin, 2), f'x{int(rd_bin, 2)}')
    imm_bin = imm20 + imm19_12 + imm11 + imm10_1 + '0'
    imm = from_twos_complement(imm_bin)
    return f"{details['mnemonic']} {rd}, {imm}"

def disassemble_instruction(code_bin_str):
    if len(code_bin_str) != 32:
        return f"Error: Invalid Length {len(code_bin_str)}"

    opcode = code_bin_str[25:32]
    funct3 = code_bin_str[17:20]
    funct7 = code_bin_str[0:7]

    details = REVERSE_MAP.get((opcode, funct3, funct7))
    if not details: details = REVERSE_MAP.get((opcode, funct3, None))
    if not details: details = REVERSE_MAP.get((opcode, None, None))

    if not details:
        # 即使无法解码，也显示出 opcode 方便调试
        return f"UNKNOWN_INSTRUCTION (Op: {opcode}, F3: {funct3}, F7: {funct7})"

    handler_map = {
        'R': disassemble_r_type, 'I': disassemble_i_type, 'I-shift': disassemble_i_type,
        'I-load': disassemble_i_type, 'I-jalr': disassemble_i_type, 'S': disassemble_s_type,
        'B': disassemble_b_type, 'U': disassemble_u_type, 'J': disassemble_j_type,
    }
    return handler_map[details['type']](code_bin_str, details)

# --- 3. Hex 转换逻辑 ---

def process_hex_input(hex_string):
    """
    处理 Hex 字符串 (e.g., "1301 01fe")
    假设输入是 Little-Endian (低字节在前)，每4字节为一条指令
    """
    # 1. 清理空格和换行
    clean_hex = hex_string.replace(" ", "").replace("\n", "").replace("\r", "")

    if len(clean_hex) % 8 != 0:
        print(f"警告: Hex 长度 ({len(clean_hex)}) 不是 8 的倍数，末尾可能被截断。")

    instructions = []
    print(f"{'Address':<8} | {'Hex Code':<10} | {'Assembly'}")
    print("-" * 50)

    for i in range(0, len(clean_hex), 8):
        chunk = clean_hex[i:i+8]
        if len(chunk) < 8: break

        # 2. 处理 Little Endian
        # 输入: "130101fe" -> 字节: 13, 01, 01, fe
        # 实际指令 (Big Endian int): 0xfe010113
        # 转换: fe010113

        byte0 = chunk[0:2]
        byte1 = chunk[2:4]
        byte2 = chunk[4:6]
        byte3 = chunk[6:8]

        # 重新组合成大端序用于解码
        reordered_hex = byte3 + byte2 + byte1 + byte0

        # 转成 32位 二进制字符串
        try:
            val = int(reordered_hex, 16)
            bin_str = format(val, '032b')

            # 反汇编
            asm = disassemble_instruction(bin_str)
            print(f"{i//2:04x}     | {reordered_hex}   | {asm}")
        except ValueError:
            print(f"{i//2:04x}     | {chunk}   | Error parsing hex")

# --- 4. 主函数 ---
if __name__ == "__main__":
    # 这里填入刚才的 Hex 数据
    user_hex_data = """
1301 01fd 2326 8102 1304 0103 b707 0040
1307 f0ff 2380 e700 b707 0020 83a7 0700
2326 f4fe 0327 c4fe 9307 803e b357 f702
2324 f4fe b707 0010 83a7 0700 0327 84fe
e30c f7fc b707 0010 0327 84fe 23a0 e700
0327 84fe 9307 c003 b377 f702 2322 f4fe
0327 84fe 9307 c003 3357 f702 9307 c003
b377 f702 2320 f4fe 0327 84fe b717 0000
9387 07e1 3357 f702 9307 4006 b377 f702
232e f4fc 0327 c4fd 9307 a000 3357 f702
b707 0040 9387 1700 1377 f70f 2380 e700
0327 c4fd 9307 a000 3377 f702 b707 0040
9387 2700 1377 f70f 2380 e700 0327 04fe
9307 a000 3357 f702 b707 0040 9387 3700
1377 f70f 2380 e700 0327 04fe 9307 a000
3377 f702 b707 0040 9387 4700 1377 f70f
2380 e700 0327 44fe 9307 a000 3357 f702
b707 0040 9387 5700 1377 f70f 2380 e700
0327 44fe 9307 a000 3377 f702 b707 0040
9387 6700 1377 f70f 2380 e700 8327 44fe
93f7 1700 638a 0700 b707 0040 1307 f000
2380 e700 6ff0 5fec b707 0040 1307 00ff
2380 e700 6ff0 5feb 3711 0010 1301 0180
eff0 1fe9 1300 0000 ffff ffff


    """

    print("开始反汇编提供的 Hex 数据...")
    process_hex_input(user_hex_data)