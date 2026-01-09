
       	.global _start

	.text
_start:
	/* 把 data section 从 flash 搬运到 ram 中 */
    	la a0, _data_lma
    	la a1, _data_start
    	la a2, _data_end
    	bgeu a1, a2, 2f
1:
    	lw t0, (a0)     /* 从 flash 中取出一个 word 的数据 */
    	sw t0, (a1)     /* 将取出的数据存入 ram 中对应位置 */
    	addi a0, a0, 4
    	addi a1, a1, 4
    	bltu a1, a2, 1b
2:
	# Set all bytes in the BSS section to zero.
        la      a0, _bss_start
        la      a1, _bss_end
        bgeu    a0, a1, 2f
1:
        sw      zero, (a0)
        addi    a0, a0, 4
        bltu    a0, a1, 1b
2:
    	la      sp, _stack_end    # set the initial stack pointer

				 
    	j   	start_kernel      # jump to kernel

