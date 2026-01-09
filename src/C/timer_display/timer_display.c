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




// // 假设 Timer 频率是 CLK 频率，这里我们需要一个简单的计数法
// // 如果没有除法，我们只能通过减法来实现计数

// void timer_main() {
//     // 这种变量放在 data 段，不占栈空间
//     static unsigned int counter = 0;
//     static unsigned char sec_unit = 0;
//     static unsigned char sec_tens = 0;
//     static unsigned char min_unit = 0;
//     static unsigned char min_tens = 0;

//     // 初始化显示 00-00-00
//     SMG_BASE[0] = 0; SMG_BASE[1] = 0;
//     SMG_BASE[2] = 0; SMG_BASE[3] = 0;
//     SMG_BASE[4] = 0; SMG_BASE[5] = 0;

//     unsigned int last_timer = TIMER_COUNTER;

//     while (1) {
//         unsigned int current_timer = TIMER_COUNTER;

//         // 假设 CPU 频率 1MHz (需根据实际情况调整)
//         // 也就是说 1000000 个 tick 代表 1秒
//         // 用减法代替除法
//         if (current_timer - last_timer >= 1000000) {
//             last_timer = current_timer; // 更新基准

//             // 手动进位逻辑，避免使用 % 和 /
//             sec_unit++;
//             if (sec_unit >= 10) {
//                 sec_unit = 0;
//                 sec_tens++;
//                 if (sec_tens >= 6) {
//                     sec_tens = 0;
//                     min_unit++;
//                     if (min_unit >= 10) {
//                         min_unit = 0;
//                         min_tens++;
//                         // ... 继续进位
//                     }
//                 }
//             }

//             // 更新显示
//             SMG_BASE[5] = sec_unit;
//             SMG_BASE[4] = sec_tens;
//             SMG_BASE[3] = min_unit;
//             SMG_BASE[2] = min_tens;

//             // 闪烁 LED
//             if (sec_unit & 1) LED_REG = 0xF0;
//             else LED_REG = 0x0F;
//         }
//     }
// }


// void start_kernel() {
//     // 保留安全 SP
//     asm volatile("li sp, 0x100000ff");
//     timer_main();
// }