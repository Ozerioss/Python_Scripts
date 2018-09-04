@echo off
setlocal
:: Size is in bytes
set "min.size=100000"

for /f  "usebackq delims=;" %%A in (`dir /b /A:-D *.*`) do If %%~zA LSS %min.size% del "%%A"