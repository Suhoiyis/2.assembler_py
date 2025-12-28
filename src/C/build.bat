@echo off
SETLOCAL

:: --- Configuration ---
:: Make sure these files are in the same folder as build.bat
SET LINKER_SCRIPT=os.ld
SET STARTUP_FILE=start.S
:: ---------------------

:: 1. Check if C file is provided
IF "%~1"=="" (
    echo [ERROR] No C file provided.
    echo.
    echo Usage: %~n0 your_program.c
    goto :Bail
)

SET C_FILE=%1
SET BASE_NAME=%~n1

:: 2. Check if required files exist
IF NOT EXIST "%C_FILE%" (
    echo [ERROR] C file not found: %C_FILE%
    goto :Bail
)
IF NOT EXIST "%LINKER_SCRIPT%" (
    echo [ERROR] Linker script not found: %LINKER_SCRIPT%
    goto :Bail
)
IF NOT EXIST "%STARTUP_FILE%" (
    echo [ERROR] Startup file not found: %STARTUP_FILE%
    goto :Bail
)

echo [--- Starting RISC-V Build for: %BASE_NAME% ---]

:: 3. Step 1: Compile and Link (.c + .S -> .elf)
echo [1/2] Compiling and Linking...
riscv-none-embed-gcc -nostdlib -fno-builtin -march=rv32im -mabi=ilp32 -T %LINKER_SCRIPT% -o %BASE_NAME%.elf %C_FILE% %STARTUP_FILE%

:: 4. CRITICAL: Check if GCC failed
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] GCC compilation failed! Build stopped.
    goto :Bail
)

:: 5. Step 2: Convert .elf to .bin
echo [2/2] Converting .elf to .bin ...
riscv-none-embed-objcopy -O binary %BASE_NAME%.elf %BASE_NAME%.bin

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Objcopy conversion failed!
    goto :Bail
)

echo.
echo [--- Build Succeeded! ---]
echo   Output ELF: %BASE_NAME%.elf
echo   Output BIN: %BASE_NAME%.bin
echo [--------------------------]

ENDLOCAL
goto :EOF

:Bail
echo.
echo [--- Build FAILED ---]
ENDLOCAL