/*
 * Timer "汇编风格" C语言版
 *
 * 策略:
 * 1. 模仿汇编代码的寄存器使用方式。
 * 2. 尽量减少中间变量，直接计算直接写入。
 * 3. 使用裸函数启动。
 */

#define TIMER_BASE      0x20000000
#define TIMER_COUNTER   (*(volatile unsigned int *)(TIMER_BASE + 0x00))

#define GPIO_BASE       0x40000000
#define SMG_BASE        ((volatile unsigned char *)(GPIO_BASE + 0x01))
#define LED_REG         (*(volatile unsigned char *)(GPIO_BASE + 0x00))

// 模仿汇编，不定义多余变量
void timer_main() {
    LED_REG = 0xFF; // 点亮 LED

    while (1) {
        // 1. 读取并计算总秒数
        // 寄存器 t0, t1 级别
        unsigned int ticks = TIMER_COUNTER;

        unsigned int total_seconds = ticks / 1000;

        // SMG_BASE[4] = total_seconds % 60 / 10;
        // SMG_BASE[5] = total_seconds % 60 % 10;

        // SMG_BASE[2] = (total_seconds / 60) % 60 / 10;
        // SMG_BASE[3] = (total_seconds / 60) % 60 % 10;

        // SMG_BASE[0] = (total_seconds / 3600) % 100 / 10;
        // SMG_BASE[1] = (total_seconds / 3600) % 100 % 10;

        unsigned int seconds = total_seconds % 60;
        unsigned int minutes = (total_seconds / 60) % 60;
        unsigned int hours   = (total_seconds / 3600) % 100;


        SMG_BASE[5] = seconds ;
        SMG_BASE[3] = minutes ;
        SMG_BASE[1] = hours   ;






        // --- LED ---
        if ((total_seconds) & 1) { // 奇数秒
            LED_REG = 0xF0;
        } else {
            LED_REG = 0x0F;
        }
    }
}

// 启动入口
void start_kernel() {
    // 既然汇编版不需要栈，C版我们也给它一个极小的栈意思一下
    // 0x10000040 (64 Bytes)
    asm volatile("li sp, 0x10000100");

    // 跳转
    timer_main();
}