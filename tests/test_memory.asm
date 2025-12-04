# Test 3: memory sw/lw
# Expected: x3 = 42
lui x1, 0
addi x1, x1, 42
sw x1, 0(x0)
lw x3, 0(x0)
