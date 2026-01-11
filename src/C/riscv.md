riscv-none-embed-gcc -nostdlib -fno-builtin -march=rv32im -T os.ld  -o main.elf start.S main.c

riscv-none-embed-objcopy -O binary main.elf main.bin

用于反汇编：

riscv-none-embed-gcc -g -O0 -nostdlib -fno-builtin -march=rv32im -T os.ld -o main.elf start.S main.c

riscv-none-embed-objdump -D -S -l -M numeric -C --disassembler-options=no-aliases main.elf

riscv-none-embed-objdump -D -S -l -M numeric main.elf > main.txt 2>&1
