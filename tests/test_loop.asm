# Test 2: loop with counter
# Expected: x1 = 5 (addi x1, x1, 1 executed 5 times)
lui x1, 0
addi x1, x1, 0
lui x10, 0
addi x10, x10, 0
lui x5, 0
addi x5, x5, 5
loop:
  addi x1, x1, 1
  addi x10, x10, 1
  bne x10, x5, loop
