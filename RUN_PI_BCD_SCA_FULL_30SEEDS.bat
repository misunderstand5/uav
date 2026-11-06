@echo off
setlocal
cd /d "%~dp0"
if /I not "%CONDA_DEFAULT_ENV%"=="uav_old" (
  echo [ERROR] Please run: conda activate uav_old
  pause
  exit /b 2
)
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set PYTHONUNBUFFERED=1
python -u scripts\run_pi_bcd_sca_full_eval.py --seeds 9000-9029 --max-steps 400 --out-dir results\02_PI_BCD_SCA\full_common30
if errorlevel 1 pause
pause
