#include "iss.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>

RiscvISS32::RiscvISS32() {
    reset();
}

void RiscvISS32::reset() {
    memset(regs, 0, sizeof(regs));
    pc = 0;
    halted = false;
    last_error.clear();
    memset(memory, 0, sizeof(memory));
    
    // 重置性能计数
    stats.instruction_count = 0;
    stats.cycle_count = 0;
    stats.branch_count = 0;
    stats.branch_taken_count = 0;
    stats.load_count = 0;
    stats.store_count = 0;
    stats.mul_count = 0;
    stats.div_count = 0;
}

// -------------------- 小端内存读写 --------------------
uint32_t RiscvISS32::read_word(uint32_t addr) {
    if (addr + 4 > sizeof(memory)) {
        last_error = "Memory read out of bounds";
        halted = true;
        return 0;
    }
    return (uint32_t)memory[addr]
         | (uint32_t)memory[addr + 1] << 8
         | (uint32_t)memory[addr + 2] << 16
         | (uint32_t)memory[addr + 3] << 24;
}

void RiscvISS32::write_word(uint32_t addr, uint32_t val) {
    if (addr + 4 > sizeof(memory)) {
        last_error = "Memory write out of bounds";
        halted = true;
        return;
    }
    memory[addr]     = (uint8_t)(val & 0xFF);
    memory[addr + 1] = (uint8_t)((val >> 8) & 0xFF);
    memory[addr + 2] = (uint8_t)((val >> 16) & 0xFF);
    memory[addr + 3] = (uint8_t)((val >> 24) & 0xFF);
}

uint16_t RiscvISS32::read_half(uint32_t addr) {
    if (addr + 2 > sizeof(memory)) {
        last_error = "Memory read out of bounds";
        halted = true;
        return 0;
    }
    return (uint16_t)memory[addr] | (uint16_t)memory[addr + 1] << 8;
}

void RiscvISS32::write_half(uint32_t addr, uint16_t val) {
    if (addr + 2 > sizeof(memory)) {
        last_error = "Memory write out of bounds";
        halted = true;
        return;
    }
    memory[addr]     = (uint8_t)(val & 0xFF);
    memory[addr + 1] = (uint8_t)((val >> 8) & 0xFF);
}

uint8_t RiscvISS32::read_byte(uint32_t addr) {
    if (addr >= sizeof(memory)) {
        last_error = "Memory read out of bounds";
        halted = true;
        return 0;
    }
    return memory[addr];
}

void RiscvISS32::write_byte(uint32_t addr, uint8_t val) {
    if (addr >= sizeof(memory)) {
        last_error = "Memory write out of bounds";
        halted = true;
        return;
    }
    memory[addr] = val;
}

// -------------------- 寄存器访问 --------------------
void RiscvISS32::set_reg(int idx, uint32_t val) {
    if (idx <= 0 || idx >= 32) return;
    regs[idx] = val;
}

uint32_t RiscvISS32::get_reg(int idx) const {
    if (idx < 0 || idx >= 32) return 0;
    if (idx == 0) return 0;
    return regs[idx];
}

// -------------------- 立即数相关 --------------------
int32_t RiscvISS32::sign_extend_imm(uint32_t imm, int bits) const {
    uint32_t mask = 1u << (bits - 1);
    if (imm & mask) {
        // 负数
        uint32_t all = ~((1u << bits) - 1);
        return (int32_t)(imm | all);
    }
    return (int32_t)imm;
}

int32_t RiscvISS32::decode_i_imm(uint32_t inst) const {
    uint32_t imm = (inst >> 20) & 0xFFF;
    return sign_extend_imm(imm, 12);
}

int32_t RiscvISS32::decode_s_imm(uint32_t inst) const {
    uint32_t imm11_5 = (inst >> 25) & 0x7F;
    uint32_t imm4_0  = (inst >> 7) & 0x1F;
    uint32_t imm = (imm11_5 << 5) | imm4_0;
    return sign_extend_imm(imm, 12);
}

int32_t RiscvISS32::decode_b_imm(uint32_t inst) const {
    uint32_t imm12   = (inst >> 31) & 0x1;
    uint32_t imm11   = (inst >> 7)  & 0x1;
    uint32_t imm10_5 = (inst >> 25) & 0x3F;
    uint32_t imm4_1  = (inst >> 8)  & 0xF;
    uint32_t imm = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1);
    return sign_extend_imm(imm, 13);
}

int32_t RiscvISS32::decode_u_imm(uint32_t inst) const {
    return (int32_t)(inst & 0xFFFFF000);
}

int32_t RiscvISS32::decode_j_imm(uint32_t inst) const {
    uint32_t imm20    = (inst >> 31) & 0x1;
    uint32_t imm19_12  = (inst >> 12) & 0xFF;
    uint32_t imm11     = (inst >> 20) & 0x1;
    uint32_t imm10_1   = (inst >> 21) & 0x3FF;
    uint32_t imm = (imm20 << 20) | (imm19_12 << 12) | (imm11 << 11) | (imm10_1 << 1);
    return sign_extend_imm(imm, 21);
}

// -------------------- 程序加载 --------------------
static inline void trim_right(std::string &s) {
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r' || s.back() == ' ' || s.back() == '\t')) s.pop_back();
}

bool RiscvISS32::load_program(const char* filename) {
    // 读取所有文本行，判断格式；若都不符合则尝试二进制加载
    std::ifstream ifs(filename);
    if (!ifs) {
        // 尝试作为二进制
        FILE* f = fopen(filename, "rb");
        if (!f) return false;
        reset();
        size_t n = fread(memory, 1, sizeof(memory), f);
        fclose(f);
        pc = 0;
        return n > 0;
    }

    std::vector<std::string> lines;
    std::string line;
    while (std::getline(ifs, line)) {
        trim_right(line);
        // skip empty / comment-only
        bool only_ws = true;
        for (char c: line) if (!isspace((unsigned char)c)) { only_ws = false; break; }
        if (only_ws) continue;
        lines.push_back(line);
    }

    if (lines.empty()) {
        // nothing usable, fail
        return false;
    }

    // 判断是否为 32-bit 二进制字符串（只含 0/1，长度至少32）
    bool all_binary_lines = true;
    bool all_hex_lines = true;
    for (auto &ln : lines) {
        bool saw01 = false;
        bool sawHex = false;
        for (char c: ln) {
            if (c == '0' || c == '1') saw01 = true;
            if (isxdigit((unsigned char)c)) sawHex = true;
            if (c == '#' || c == ';') break; // comment start
        }
        // check binary-like: contains at least one 0/1 and no other non-space chars
        bool binary_like = true;
        int count01 = 0;
        for (char c: ln) {
            if (c == '0' || c == '1') count01++;
            else if (isspace((unsigned char)c)) continue;
            else if (c == '#' || c == ';') break;
            else binary_like = false;
        }
        if (!(binary_like && count01 >= 32)) all_binary_lines = false;

        // check hex-like: sscanf %x should succeed on trimmed start
        unsigned int tmp;
        const char* cstr = ln.c_str();
        if (sscanf(cstr, "%x", &tmp) != 1) all_hex_lines = false;
    }

    reset();
    uint32_t addr = 0;
    if (all_binary_lines) {
        for (auto &ln : lines) {
            uint32_t instr = 0;
            int bits = 0;
            for (char c: ln) {
                if (c == '0' || c == '1') {
                    instr = (instr << 1) | (uint32_t)(c - '0');
                    bits++; if (bits == 32) break;
                } else if (isspace((unsigned char)c)) continue;
                else if (c == '#' || c == ';') break;
            }
            if (bits != 32) {
                last_error = "Bad binary line (not 32 bits)";
                return false;
            }
            write_word(addr, instr);
            addr += 4;
            if (addr >= sizeof(memory)) break;
        }
        pc = 0;
        return true;
    }

    if (all_hex_lines) {
        for (auto &ln : lines) {
            unsigned int instr = 0;
            if (sscanf(ln.c_str(), "%x", &instr) == 1) {
                write_word(addr, instr);
                addr += 4;
                if (addr >= sizeof(memory)) break;
            } else {
                last_error = "Bad hex line";
                return false;
            }
        }
        pc = 0;
        return true;
    }

    // else, fallback false
    last_error = "Unknown text program format";
    return false;
}

// -------------------- 译码 + 执行 --------------------
bool RiscvISS32::fetch_and_decode_execute() {
    if (halted) return false;
    if (pc + 4 > sizeof(memory)) {
        last_error = "PC out of bounds";
        halted = true;
        return false;
    }

    uint32_t inst = read_word(pc);
    if (halted) return false;

    uint32_t opcode = inst & 0x7F;
    uint32_t rd     = (inst >> 7) & 0x1F;
    uint32_t funct3 = (inst >> 12) & 0x7;
    uint32_t rs1    = (inst >> 15) & 0x1F;
    uint32_t rs2    = (inst >> 20) & 0x1F;
    uint32_t funct7 = (inst >> 25) & 0x7F;

    uint32_t next_pc = pc + 4;
    
    // 性能计数：总指令数和周期数
    stats.instruction_count++;
    stats.cycle_count += 1;  // 基础周期

    switch (opcode) {
        case 0x33: { // R-type
            uint32_t a = get_reg(rs1);
            uint32_t b = get_reg(rs2);
            uint32_t res = 0;
            if (funct7 == 0x00) {
                switch (funct3) {
                    case 0x0: res = a + b; break; // ADD
                    case 0x1: res = a << (b & 0x1F); break; // SLL
                    case 0x2: res = ((int32_t)a < (int32_t)b) ? 1 : 0; break; // SLT
                    case 0x3: res = (a < b) ? 1 : 0; break; // SLTU
                    case 0x4: res = a ^ b; break; // XOR
                    case 0x5: res = a >> (b & 0x1F); break; // SRL
                    case 0x6: res = a | b; break; // OR
                    case 0x7: res = a & b; break; // AND
                }
            } else if (funct7 == 0x20) {
                switch (funct3) {
                    case 0x0: res = a - b; break; // SUB
                    case 0x5: res = (int32_t)a >> (b & 0x1F); break; // SRA
                }
            } else if (funct7 == 0x01) { // RV32M Extension
                int64_t aa = (int32_t)a;
                int64_t bb = (int32_t)b;
                uint64_t aau = a;
                uint64_t bbu = b;
                switch (funct3) {
                    case 0x0: { // MUL
                        int64_t prod = aa * bb;
                        res = (uint32_t)(prod & 0xFFFFFFFFLL);
                        stats.mul_count++;
                        break;
                    }
                    case 0x1: { // MULH (signed * signed, return high 32 bits)
                        int64_t prod = aa * bb;
                        res = (uint32_t)((prod >> 32) & 0xFFFFFFFFLL);
                        stats.mul_count++;
                        break;
                    }
                    case 0x2: { // MULHSU (signed * unsigned, return high 32 bits)
                        int64_t prod = aa * (int64_t)bbu;
                        res = (uint32_t)((prod >> 32) & 0xFFFFFFFFLL);
                        stats.mul_count++;
                        break;
                    }
                    case 0x3: { // MULHU (unsigned * unsigned, return high 32 bits)
                        uint64_t prod = aau * bbu;
                        res = (uint32_t)((prod >> 32) & 0xFFFFFFFFULL);
                        stats.mul_count++;
                        break;
                    }
                    case 0x4: { // DIV (signed division)
                        if (bb == 0) {
                            res = 0xFFFFFFFFU; // RISC-V: divide by zero returns -1
                        } else {
                            res = (uint32_t)(aa / bb);
                        }
                        stats.div_count++;
                        break;
                    }
                    case 0x5: { // DIVU (unsigned division)
                        if (bbu == 0) {
                            res = 0xFFFFFFFFU; // divide by zero returns -1
                        } else {
                            res = (uint32_t)(aau / bbu);
                        }
                        stats.div_count++;
                        break;
                    }
                    case 0x6: { // REM (signed remainder)
                        if (bb == 0) {
                            res = a; // RISC-V: remainder by zero returns dividend
                        } else {
                            res = (uint32_t)(aa % bb);
                        }
                        stats.div_count++;
                        break;
                    }
                    case 0x7: { // REMU (unsigned remainder)
                        if (bbu == 0) {
                            res = a; // remainder by zero returns dividend
                        } else {
                            res = (uint32_t)(aau % bbu);
                        }
                        break;
                    }
                }
            }
            set_reg(rd, res);
            break;
        }

        case 0x13: { // I-type ALU
            uint32_t a = get_reg(rs1);
            int32_t imm = decode_i_imm(inst);
            uint32_t res = 0;
            switch (funct3) {
                case 0x0: res = a + imm; break; // ADDI
                case 0x2: res = ((int32_t)a < imm) ? 1 : 0; break; // SLTI
                case 0x3: res = (a < (uint32_t)imm) ? 1 : 0; break; // SLTIU
                case 0x4: res = a ^ (uint32_t)imm; break; // XORI
                case 0x6: res = a | (uint32_t)imm; break; // ORI
                case 0x7: res = a & (uint32_t)imm; break; // ANDI
                case 0x1: res = a << (imm & 0x1F); break; // SLLI
                case 0x5:
                    if ((inst >> 25) == 0x00) res = a >> (imm & 0x1F); // SRLI
                    else res = (int32_t)a >> (imm & 0x1F); // SRAI
                    break;
            }
            set_reg(rd, res);
            break;
        }

        case 0x03: { // Loads
            uint32_t base = get_reg(rs1);
            int32_t imm = decode_i_imm(inst);
            uint32_t addr = base + imm;
            uint32_t val = 0;
            stats.load_count++;  // 计数加载指令
            switch (funct3) {
                case 0x0: { // LB
                    val = (int32_t)(int8_t)read_byte(addr);
                    break;
                }
                case 0x1: { // LH
                    val = (int32_t)(int16_t)read_half(addr);
                    break;
                }
                case 0x2: { // LW
                    val = read_word(addr);
                    break;
                }
                case 0x4: { // LBU
                    val = read_byte(addr);
                    break;
                }
                case 0x5: { // LHU
                    val = read_half(addr);
                    break;
                }
            }
            set_reg(rd, val);
            break;
        }

        case 0x23: { // Stores
            uint32_t base = get_reg(rs1);
            uint32_t val = get_reg(rs2);
            int32_t imm = decode_s_imm(inst);
            uint32_t addr = base + imm;
            stats.store_count++;  // 计数存储指令
            switch (funct3) {
                case 0x0: write_byte(addr, (uint8_t)(val & 0xFF)); break; // SB
                case 0x1: write_half(addr, (uint16_t)(val & 0xFFFF)); break; // SH
                case 0x2: write_word(addr, val); break; // SW
            }
            break;
        }

        case 0x63: { // Branch
            uint32_t a = get_reg(rs1);
            uint32_t b = get_reg(rs2);
            int32_t imm = decode_b_imm(inst);
            bool take = false;
            stats.branch_count++;  // 计数分支指令
            switch (funct3) {
                case 0x0: take = (a == b); break; // BEQ
                case 0x1: take = (a != b); break; // BNE
                case 0x4: take = ((int32_t)a < (int32_t)b); break; // BLT
                case 0x5: take = ((int32_t)a >= (int32_t)b); break; // BGE
                case 0x6: take = (a < b); break; // BLTU
                case 0x7: take = (a >= b); break; // BGEU
            }
            if (take) {
                next_pc = pc + imm;
                stats.branch_taken_count++;  // 计数分支已取
            }
            break;
        }

        case 0x6F: { // JAL
            int32_t imm = decode_j_imm(inst);
            set_reg(rd, pc + 4);
            next_pc = pc + imm;
            stats.branch_count++;       // 无条件跳转也算分支
            stats.branch_taken_count++;
            break;
        }

        case 0x67: { // JALR
            int32_t imm = decode_i_imm(inst);
            uint32_t base = get_reg(rs1);
            set_reg(rd, pc + 4);
            next_pc = (base + imm) & ~1u;
            break;
        }

        case 0x37: { // LUI
            int32_t imm = decode_u_imm(inst);
            set_reg(rd, (uint32_t)imm);
            break;
        }

        case 0x17: { // AUIPC
            int32_t imm = decode_u_imm(inst);
            set_reg(rd, pc + imm);
            break;
        }

        case 0x00: // treating 0 as halt if entire instruction is 0
            if (inst == 0) { halted = true; return true; }
            break;

        default:
            last_error = "Unknown opcode";
            halted = true;
            return false;
    }

    pc = next_pc;
    return true;
}

bool RiscvISS32::step() {
    if (halted) return false;
    return fetch_and_decode_execute();
}

void RiscvISS32::run_until_halt() {
    while (!halted) {
        if (!step()) break;
    }
}

// -------------------- 调试输出 --------------------
void RiscvISS32::dump_regs() const {
    // 输出格式: x0=00000000 (小写 hex, 无 0x 前缀)，每行一个寄存器
    for (int i = 0; i < 32; ++i) {
        uint32_t v = (i == 0) ? 0u : regs[i];
        printf("x%d=%08x\n", i, v);
    }
    printf("PC=%08x\n", pc);
}

void RiscvISS32::dump_memory(uint32_t addr, uint32_t len) const {
    if (addr + len > sizeof(memory)) len = sizeof(memory) - addr;
    for (uint32_t i = 0; i < len; i += 16) {
        printf("%08x: ", addr + i);
        for (uint32_t j = 0; j < 16 && i + j < len; ++j) {
            printf("%02x ", memory[addr + i + j]);
        }
        printf("\n");
    }
}

void RiscvISS32::print_stats() const {
    printf("\n========== Performance Statistics ==========\n");
    printf("Total Instructions:     %lu\n", (unsigned long)stats.instruction_count);
    printf("Total Cycles:           %lu\n", (unsigned long)stats.cycle_count);
    printf("CPI (Cycles/Instr):     %.2f\n", 
           stats.instruction_count > 0 ? (double)stats.cycle_count / stats.instruction_count : 0.0);
    printf("\n--- Instruction Breakdown ---\n");
    printf("Branch Instructions:    %lu (taken: %lu, not taken: %lu)\n",
           (unsigned long)stats.branch_count,
           (unsigned long)stats.branch_taken_count,
           (unsigned long)(stats.branch_count - stats.branch_taken_count));
    printf("Load Instructions:      %lu\n", (unsigned long)stats.load_count);
    printf("Store Instructions:     %lu\n", (unsigned long)stats.store_count);
    printf("Multiply Instructions:  %lu\n", (unsigned long)stats.mul_count);
    printf("Divide Instructions:    %lu\n", (unsigned long)stats.div_count);
    printf("Other Instructions:     %lu\n",
           (unsigned long)(stats.instruction_count - stats.branch_count - stats.load_count - 
           stats.store_count - stats.mul_count - stats.div_count));
    printf("===========================================\n\n");
}

