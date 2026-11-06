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
python -u scripts\audit_matrix_progress.py && python -u scripts\plot_convergence.py --window 20 && python -u scripts\aggregate_relay_distribution.py --input results\08_FINAL_TEST100 --extra-input results\02_PI_BCD_SCA\final100 --output results\06_RELAY_DISTRIBUTION && python -u scripts\package_results_for_analysis.py
if errorlevel 1 (
  echo [FAILED] See logs under results\00_AUDIT_PROGRESS and the relevant run folder.
  pause
  exit /b 1
)
echo [SUCCESS]
pause
