riscv-none-embed-gcc -nostdlib -fno-builtin -march=rv32im -T os.ld  -o a.elf start.S main.c

riscv-none-embed-objcopy -O binary main.elf main.bin