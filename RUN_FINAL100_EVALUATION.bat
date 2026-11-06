@echo off
setlocal
cd /d "%~dp0"
if /I not "%CONDA_DEFAULT_ENV%"=="uav_old" (
  echo [ERROR] Please run: conda activate uav_old
  pause
  exit /b 2
)
echo ============================================================
echo WARNING: FINAL TEST ONLY
echo Run this only after algorithms, parameters, code and metrics are frozen.
echo Seeds 10000-10099 must not be used for model selection.
echo ============================================================
set CUBLAS_WORKSPACE_CONFIG=:4096:8
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set NUMEXPR_NUM_THREADS=1
set PYTHONUNBUFFERED=1
python -u scripts\evaluate_common30_matrix.py --seeds 10000-10099 --device cuda --workers 1 --out-dir results\08_FINAL_TEST100
if errorlevel 1 (
  echo [FAILED] Final test evaluation failed.
  pause
  exit /b 1
)
echo [SUCCESS] Final 100-seed test completed.
pause
