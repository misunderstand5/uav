@echo off
setlocal
cd /d "%~dp0"
if /I not "%CONDA_DEFAULT_ENV%"=="uav_old" (
  echo [ERROR] Please run: conda activate uav_old
  pause
  exit /b 2
)
echo ============================================================
echo WARNING: FINAL SEALED TEST
echo Run only after PI-BCD-SCA has passed the solver/runtime gate and all algorithms are frozen.
echo Seeds 10000-10099 are reserved for final testing.
echo ============================================================
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set PYTHONUNBUFFERED=1
python -u scripts\run_pi_bcd_sca_full_eval.py --seeds 10000-10099 --max-steps 400 --out-dir results\02_PI_BCD_SCA\final100
if errorlevel 1 (
  echo [FAILED] PI-BCD-SCA final-100 evaluation failed.
  pause
  exit /b 1
)
echo [SUCCESS] PI-BCD-SCA final-100 test completed.
pause
