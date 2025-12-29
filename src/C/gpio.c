/*
 * Timer 原始值测试
 *
 * 目的:
 * 1. 直接显示 TIMER_COUNTER 的原始值 (低 6 位十六进制)
 * 2. 如果数码管显示 000000 且不动，说明 Timer 地址错或没启动。
 * 3. 如果数码管狂闪，说明 Timer 是好的，之前的除法/逻辑有问题。
 */

#define TIMER_BASE      0x20000000
#define TIMER_COUNTER   (*(volatile unsigned int *)(TIMER_BASE + 0x00))

#define GPIO_BASE       0x40000000
#define SMG_PTR         ((volatile unsigned char *)(GPIO_BASE + 0x01))
#define LED_REG         (*(volatile unsigned char *)(GPIO_BASE + 0x00))

// 真正的主逻辑
void timer_main() {
    LED_REG = 0xFF;

    while (1) {
        // 直接读取原始值
        unsigned int ticks = TIMER_COUNTER;

        // 显示 ticks 的低 6 位 (十六进制风格，0-F)
        // 注意：你的数码管是硬件译码，只能显示 0-9
        // 所以我们把 ticks 拆成 6 个十进制位显示

        SMG_PTR[0] = (ticks / 100000) % 10;
        SMG_PTR[1] = (ticks / 10000) % 10;
        SMG_PTR[2] = (ticks / 1000) % 10;
        SMG_PTR[3] = (ticks / 100) % 10;
        SMG_PTR[4] = (ticks / 10) % 10;
        SMG_PTR[5] = ticks % 10;

        // 心跳
        if ((ticks % 1024) < 512) {
            LED_REG = 0x0F;
        } else {
            LED_REG = 0xF0;
        }
    }
}

void start_kernel() {
    // 保留安全 SP
    asm volatile("li sp, 0x10010000");
    timer_main();
}