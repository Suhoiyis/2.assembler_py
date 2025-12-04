# Test REM: 42 % 5 = 2 (signed remainder)
lui x1, 0
addi x1, x1, 42
lui x2, 0
addi x2, x2, 5
rem x3, x1, x2
