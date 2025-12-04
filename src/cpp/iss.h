#ifndef ISS_H
#define ISS_H

#include <cstdint>
#include <string>

class RiscvISS32 {
public:
    RiscvISS32();
    ~RiscvISS32() = default;

    // 初始化 / 重置
    void reset();

    // 程序加载（支持 assembler.py 生成的 32-bit 二进制文本、hex 文本、以及原始 bin）
    bool load_program(const char* filename);

    // 执行控制
    bool step();                 // 单步执行一条指令
    void run_until_halt();

    // 调试接口
    void dump_regs() const;
    void dump_memory(uint32_t addr, uint32_t len) const;
    void print_stats() const;  // 性能计数输出
    uint32_t get_reg(int idx) const;
    uint32_t get_pc() const { return pc; }
    bool is_halted() const { return halted; }
    const char* get_error() const { return last_error.c_str(); }

private:
    // 硬件模型
    uint32_t regs[32];
    uint32_t pc;
    uint8_t memory[64 * 1024]; // 64KB

    bool halted;
    std::string last_error;

    // 性能计数统计
    struct Stats {
        uint64_t instruction_count;    // 总指令数
        uint64_t cycle_count;          // CPU 周期数
        uint64_t branch_count;         // 分支指令数（含分支未取）
        uint64_t branch_taken_count;   // 分支已取数
        uint64_t load_count;           // 加载指令数
        uint64_t store_count;          // 存储指令数
        uint64_t mul_count;            // 乘法指令数
        uint64_t div_count;            // 除法指令数
    } stats;

    // 内存访问（小端）
    uint32_t read_word(uint32_t addr);
    void write_word(uint32_t addr, uint32_t val);
    uint16_t read_half(uint32_t addr);
    void write_half(uint32_t addr, uint16_t val);
    uint8_t read_byte(uint32_t addr);
    void write_byte(uint32_t addr, uint8_t val);

    // 寄存器写入（保证 x0 恒为 0）
    void set_reg(int idx, uint32_t val);

    // 译码执行主流程
    bool fetch_and_decode_execute();

    // 立即数生成
    int32_t sign_extend_imm(uint32_t imm, int bits) const;
    int32_t decode_i_imm(uint32_t inst) const;
    int32_t decode_s_imm(uint32_t inst) const;
    int32_t decode_b_imm(uint32_t inst) const;
    int32_t decode_u_imm(uint32_t inst) const;
    int32_t decode_j_imm(uint32_t inst) const;
};

#endif // ISS_H
