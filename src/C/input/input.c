/*
 * Input 终极修复版
 *
 * 修复原理:
 * 使用 start_kernel 作为跳板 (Wrapper) 进行栈指针 (SP) 修复，
 * 然后跳转到 main_logic。
 * * 这样 main_logic 的帧指针 (FP/S0) 就会基于正确的 RAM 地址建立，
 * 确保局部变量 dividend/divisor 能被正确读写。
 */

// === 硬件地址 ===
#define UART_BASE 0x30000000
#define UART_CTRL   (*(volatile unsigned int*)(UART_BASE + 0x00))
#define UART_STATUS (*(volatile unsigned int*)(UART_BASE + 0x04))
#define UART_TXDATA (*(volatile unsigned int*)(UART_BASE + 0x0c))
#define UART_RXDATA (*(volatile unsigned int*)(UART_BASE + 0x10))

#define GPIO_BASE   0x40000000
// 数码管 (偏移 0x1 - 0x6)
#define SMG_PTR     ((volatile unsigned char *)(GPIO_BASE + 0x01))

#define TX_BUSY_BIT (1 << 0)
#define RX_DONE_BIT (1 << 1)

// === RAM 辅助 (用于观察调试) ===
#define RAM_PTR     ((volatile unsigned int *)0x10000000)

unsigned int uart_rx() {
    while (!(UART_STATUS & RX_DONE_BIT));
    unsigned int data = UART_RXDATA;
    UART_STATUS = 0;
    return data;
}

void uart_tx(unsigned int data) {
    while (UART_STATUS & TX_BUSY_BIT);
    UART_TXDATA = data;
    UART_STATUS |= TX_BUSY_BIT;
}

// 实际的主逻辑函数
// 这个函数被调用时，SP 已经是正确的 RAM 地址了
void main_logic() {

    // 初始化
    UART_CTRL = 3;

    while (1) {
        // 1. 接收被除数
        unsigned int dividend = uart_rx();

        // 显示被除数 (适配硬件译码，直接写数值)
        SMG_PTR[2] = dividend % 10;
        SMG_PTR[1] = (dividend / 10) % 10;
        SMG_PTR[0] = (dividend / 100) % 10;

        // 2. 接收除数
        unsigned int divisor = uart_rx();

        // 显示除数
        SMG_PTR[5] = divisor % 10;
        SMG_PTR[4] = (divisor / 10) % 10;
        SMG_PTR[3] = (divisor / 100) % 10;

        // 3. 计算
        unsigned int quotient = 0;
        unsigned int remainder = 0;

        // 此时 divisor 是从 RAM 栈上正确读出的，数据稳定
        if (divisor != 0) {
            quotient = dividend / divisor;
            remainder = dividend % divisor;
        }

        // 4. 发送结果
        uart_tx(quotient);
        uart_tx(remainder);

        // 调试：存入 RAM 0x10000000 以便仿真器观察
        RAM_PTR[0] = dividend;
        RAM_PTR[1] = divisor;
        RAM_PTR[2] = quotient;
        RAM_PTR[3] = remainder;
    }
}

// 入口函数 (裸机启动点)
// 它的唯一任务就是修好栈，然后把控制权交给 main_logic
void start_kernel() {
    // 1. 强制修复栈指针到 RAM (0x10010000)
    // 必须在调用任何子函数之前执行
    asm volatile("li sp, 0x10010000");

    // 2. 调用主逻辑
    // 这会导致一次函数跳转，新的函数会建立正确的栈帧(Stack Frame)
    main_logic();
}