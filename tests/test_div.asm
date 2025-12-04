# Test DIV: 42 / 5 = 8 (signed division)
lui x1, 0
addi x1, x1, 42
lui x2, 0
addi x2, x2, 5
div x3, x1, x2
