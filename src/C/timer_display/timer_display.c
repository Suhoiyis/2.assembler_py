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

        // unsigned int total_seconds = ticks / 1000;

        SMG_BASE[4] = ((ticks/1000) % 60) / 10;
        SMG_BASE[5] = ((ticks/1000) % 60) % 10;

        SMG_BASE[2] = (((ticks/1000) / 60) % 60) / 10;
        SMG_BASE[3] = (((ticks/1000) / 60) % 60) % 10;

        SMG_BASE[0] = (((ticks/1000) / 3600) % 100) / 10;
        SMG_BASE[1] = (((ticks/1000) / 3600) % 100) % 10;
        // unsigned int seconds = total_seconds % 60;
        // unsigned int minutes = (total_seconds / 60) % 60;
        // unsigned int hours   = (total_seconds / 3600) % 100;


        // SMG_BASE[5] = seconds ;
        // SMG_BASE[3] = minutes ;
        // SMG_BASE[1] = hours   ;

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
    asm volatile("li sp, 0x10000100");
    timer_main();
}