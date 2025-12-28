/*
 * Timer 终极修复版 (256MB RAM + 毫秒计数)
 */

// === 硬件地址 ===
#define TIMER_BASE      0x20000000
#define TIMER_COUNTER   (*(volatile unsigned int *)(TIMER_BASE + 0x00))

#define GPIO_BASE       0x40000000
#define SMG_PTR         ((volatile unsigned char *)(GPIO_BASE + 0x01))
#define LED_REG         (*(volatile unsigned char *)(GPIO_BASE + 0x00))

// 主逻辑函数
void timer_main() {
    LED_REG = 0xFF; // 点亮 LED

    while (1) {
        // 1. 读取毫秒数
        // 硬件计数器直接返回毫秒
        unsigned int current_ms = TIMER_COUNTER;

        // 2. 转换为总秒数
        unsigned int total_seconds = current_ms / 1000;

        // 3. 计算 HH:MM:SS
        unsigned int seconds = total_seconds % 60;
        unsigned int minutes = (total_seconds / 60) % 60;
        unsigned int hours   = (total_seconds / 3600) % 100;

        // 4. 显示 (从左到右: HH MM SS)
        // 假设 SEG1(PTR[0]) 是最左边

        // 小时
        SMG_PTR[0] = hours / 10;
        SMG_PTR[1] = hours % 10;
        // 分钟
        SMG_PTR[2] = minutes / 10;
        SMG_PTR[3] = minutes % 10;
        // 秒
        SMG_PTR[4] = seconds / 10;
        SMG_PTR[5] = seconds % 10;

        // 5. LED 心跳
        if ((current_ms % 1000) < 500) {
            LED_REG = 0x0F;
        } else {
            LED_REG = 0xF0;
        }

        // 6. 软件延时 (防止数码管刷新过快)
        // 现代 CPU 很快，如果不加延时，数码管可能会有重影
        for (volatile int i = 0; i < 5000; i++);
    }
}

// 启动入口
void start_kernel() {
    // RAM Start (0x10000000) + 256MB (0x10000000) = 0x20000000
    // 这里的 0x20000000 是 "栈底" (Stack Bottom)，向下生长
    asm volatile("li sp, 0x20000000");

    // 跳转主逻辑
    timer_main();
}