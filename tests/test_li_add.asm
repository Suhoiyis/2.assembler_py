# Test 1: lui+addi + add
# Expected: x2 = 20 (10+10)
lui x1, 0
addi x1, x1, 10
add x2, x1, x1
