
#include "iss.h"
#include <cstdio>
#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
	RiscvISS32 sim;

	if (argc < 2) {
		std::printf("Usage: %s <program_file>\n", argv[0]);
		std::printf("Supported formats: assembler.py 32-bit binary text, hex text, or raw .bin\n");
		return 1;
	}

	const char* filename = argv[1];
	if (!sim.load_program(filename)) {
		std::fprintf(stderr, "Failed to load '%s' : %s\n", filename, sim.get_error());
		return 2;
	}

	std::printf("Program loaded. Running...\n");

	// 运行直到遇到全 0 指令 或 错误
	int steps = 0;
	while (!sim.is_halted() && steps < 1000000) {
		if (!sim.step()) break;
		steps++;
	}

    std::printf("Execution finished after %d steps. halted=%d\n", steps, (int)sim.is_halted());
    sim.dump_regs();
    sim.print_stats();  // 输出性能统计
    std::printf("--- memory dump (0x0 - 0x40) ---\n");
    sim.dump_memory(0, 64);
    return 0;
}