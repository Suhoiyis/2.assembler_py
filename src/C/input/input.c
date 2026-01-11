/*
 * Input 硬件协议适配版
 *
 * 协议依据:
 * 发送: 等待0 -> 写数据 -> 手动置1 (触发硬件)
 * 接收: 等待1 -> 读数据 -> 手动置0 (清除标志)
 *
 * 同时包含:
 * 1. 栈指针修复 (防止变量丢失)
 * 2. 数码管直写 (适配硬件译码)
 */

// === 硬件地址 ===
#define UART_BASE 0x30000000
#define UART_CTRL   (*(volatile unsigned int*)(UART_BASE + 0x00))
#define UART_STATUS (*(volatile unsigned int*)(UART_BASE + 0x04))
#define UART_TXDATA (*(volatile unsigned int*)(UART_BASE + 0x0c))
#define UART_RXDATA (*(volatile unsigned int*)(UART_BASE + 0x10))

#define GPIO_BASE   0x40000000
#define SMG_PTR     ((volatile unsigned char *)(GPIO_BASE + 0x01))

// 状态位掩码
#define TX_BUSY_BIT (1 << 0) // Bit 0: 发送忙
#define RX_DONE_BIT (1 << 1) // Bit 1: 接收完成

// 接收函数 (严格遵循文档)
unsigned int uart_rx() {
    // 1. 循环等待接收状态位为 1
    while (!(UART_STATUS & RX_DONE_BIT));

    // 2. 从接收数据寄存器读入数据
    unsigned int data = UART_RXDATA;

    // 3. 将接收状态位设为 0 (清接收标志)
    // 这里使用 &= ~RX_DONE_BIT 只清除接收位，不影响发送位
    UART_STATUS &= ~RX_DONE_BIT;

    return data;
}

// 发送函数 (严格遵循文档)
void uart_tx(unsigned int data) {
    // 1. 等待发送状态位为 0
    while (UART_STATUS & TX_BUSY_BIT);

    // 2. 将数据写入发送数据寄存器
    UART_TXDATA = data;

    // 3. 将发送状态位设为 1 (触发硬件发送)
    UART_STATUS |= TX_BUSY_BIT;
}

// 主逻辑 (保留栈修复后的逻辑)
void main_logic() {
    // 初始化 UART 控制寄存器
    // 第0位发送使能，第1位接收使能 -> 0x03
    UART_CTRL = 3;

    while (1) {
        // --- 接收被除数 ---
        unsigned int dividend = uart_rx();

        // 显示 (直接写数值)
        SMG_PTR[2] = dividend % 10;
        SMG_PTR[1] = (dividend / 10) % 10;
        SMG_PTR[0] = (dividend / 100) % 10;

        // --- 接收除数 ---
        unsigned int divisor = uart_rx();

        // 显示
        SMG_PTR[5] = divisor % 10;
        SMG_PTR[4] = (divisor / 10) % 10;
        SMG_PTR[3] = (divisor / 100) % 10;

        // --- 计算 ---
        unsigned int quotient = 0;
        unsigned int remainder = 0;

        // 此时 divisor 在 RAM 中，读取是安全的
        if (divisor != 0) {
            quotient = dividend / divisor;
            remainder = dividend % divisor;
        }

        // --- 发送结果 ---
        uart_tx(quotient);

        // 简单延时防止粘包
        for(volatile int i=0; i<1000; i++);

        uart_tx(remainder);
    }
}

// 启动入口
void start_kernel() {
    // 1. 强制修复栈指针 (RAM 64KB处，安全值)
    asm volatile("li sp, 0x10010000");

    // 2. 跳转主逻辑
    main_logic();
}