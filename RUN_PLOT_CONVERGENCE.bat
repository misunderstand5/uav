@echo off
setlocal
cd /d "%~dp0"
if /I not "%CONDA_DEFAULT_ENV%"=="uav_old" (
  echo [ERROR] Please run: conda activate uav_old
  pause
  exit /b 2
)
set CUBLAS_WORKSPACE_CONFIG=:4096:8
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set PYTHONUNBUFFERED=1
python -u scripts\plot_convergence.py --window 20
if errorlevel 1 (
  echo [FAILED] See logs under results\00_AUDIT_PROGRESS and the relevant run folder.
  pause
  exit /b 1
)
echo [SUCCESS]
pause
