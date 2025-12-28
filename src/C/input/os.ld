/*
 * https://sourceware.org/binutils/docs/ld/Miscellaneous-Commands.html
 * OUTPUT_ARCH command specifies a particular output machine architecture.
 * "riscv" is the name of the architecture for both 64-bit and 32-bit
 * RISC-V target. We will further refine this by using -march=rv32im
 * and -mabi=ilp32 when calling gcc.
 */
OUTPUT_ARCH( "riscv" )

/*
 * https://sourceware.org/binutils/docs/ld/Entry-Point.html
 * ENTRY command is used to set the "entry point", which is the first instruction
 * to execute in a program.
 * The argument of ENTRY command is a symbol name, here is "_start" which is
 * defined in start.S.
 */
ENTRY( _start )

/*
 * https://sourceware.org/binutils/docs/ld/MEMORY.html
 * The MEMORY command describes the location and size of blocks of memory in
 * the target.
 * The syntax for MEMORY is:
 * MEMORY
 * {
 *     name [(attr)] : ORIGIN = origin, LENGTH = len
 *     ......
 * }
 * Each line defines a memory region.
 * Each memory region must have a distinct name within the MEMORY command. Here
 * we define two region named as "rom" and "ram".
 * The "attr" string is an optional list of attributes that specify whether to
 * use a particular memory region for an input section which is not explicitly
 * mapped in the linker script. Here we assign 'w' (writeable), 'x' (executable),
 * and 'a' (allocatable). We use '!' to invert 'r' (read-only) and
 * 'i' (initialized).
 * The "ORIGIN" is used to set the start address of the memory region. Here we
 * place it right at the beginning of 0x0000_0000 because this is where the
 * riscv cpu will start executing.
 * Finally LENGTH = 4K tells the linker that we have 4K megabyte of RAM.
 * The linker will double check this to make sure everything can fit.
 */
MEMORY
{
	flash  (wxa!ri) : ORIGIN = 0x00000000, LENGTH = 16K
	ram   (wxa!ri) : ORIGIN = 0x10000000, LENGTH = 8K
}

SECTIONS
{
	/*
         * We are going to layout all text sections in .text output section,
         * starting with .text. The asterisk("*") in front of the
         * parentheses means to match the .text section of ANY object file.
         */
        .text : {
                PROVIDE(_text_start = .);
                *(.text .text.*)
                PROVIDE(_text_end = .);
		. = ALIGN(4);
        } >flash AT>flash

	.lalign : {
    		. = ALIGN(4);
    		PROVIDE( _data_lma = . );
  		} >flash AT>flash 

  	.dalign : {
    		. = ALIGN(4);
    		PROVIDE( _data_start = . );
  		} >ram AT>flash 
	
	.rodata : {
                PROVIDE(_rodata_start = .);
                *(.rodata .rodata.*)
                PROVIDE(_rodata_end = .);
                . = ALIGN(4);
        } >flash AT>flash

	.data : {
		/*
                 * . = ALIGN(4) tells the linker to align the current memory
                 * location to 4 bytes. This will insert padding bytes until
                 * current location becomes aligned on 4-byte boundary.
                 */
		. = ALIGN(4);
		/*
                 * sdata and data are essentially the same thing. We do not need
                 * to distinguish sdata from data.
                 */
                *(.sdata .sdata.*)
                *(.data .data.*)
		. = ALIGN(4);
	} >ram AT>flash 

	PROVIDE(_data_end = .);

	PROVIDE(_bss_start = .);
	.bss :{
                /*
                 * https://sourceware.org/binutils/docs/ld/Input-Section-Common.html
                 * In most cases, common symbols in input files will be placed
                 * in the ‘.bss’ section in the output file.
                 */
                *(.sbss .sbss.*)
                *(.bss .bss.*)
                *(COMMON)
		. = ALIGN(4);
        } >ram AT>flash 
	PROVIDE(_bss_end = .);

	PROVIDE(_memory_start = ORIGIN(ram));
        PROVIDE(_memory_end = ORIGIN(ram) + LENGTH(ram));
	
	/* stack */
	PROVIDE(_stack_start = _bss_end);
        PROVIDE(_stack_end = _stack_start + 512);

	/* heap */
	PROVIDE(_heap_start = _stack_end);
        PROVIDE(_heap_size = _memory_end - _heap_start);
}
