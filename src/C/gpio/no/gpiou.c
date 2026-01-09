#define TIMER_BASE      0x20000000
#define TIMER_COUNTER   (*(volatile unsigned int *)(TIMER_BASE + 0x00))

#define GPIO_BASE       0x40000000
#define SMG_PTR         ((volatile unsigned char *)(GPIO_BASE + 0x01))
#define LED_REG         (*(volatile unsigned char *)(GPIO_BASE + 0x00))


unsigned int seconds;

// 真正的主逻辑
void timer_main() {
    LED_REG = 0xFF;

    while (1) {
        // 直接读取原始值
        unsigned int ticks = TIMER_COUNTER;

        seconds = ticks /10;

        SMG_PTR[0] = (seconds / 100000) % 10;
        SMG_PTR[1] = (seconds / 10000) % 10;
        SMG_PTR[2] = (seconds / 1000) % 10;
        SMG_PTR[3] = (seconds / 100) % 10;
        SMG_PTR[4] = (seconds / 10) % 10;
        SMG_PTR[5] = seconds % 10;

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