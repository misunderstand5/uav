@echo off
setlocal
cd /d "%~dp0"
if /I not "%CONDA_DEFAULT_ENV%"=="uav_old" (
 echo [ERROR] Please activate uav_old first.
 exit /b 2
)
python -u scripts\audit_matrix_progress.py
if errorlevel 1 exit /b 1
python -u scripts\plot_convergence.py --window 20
if errorlevel 1 exit /b 1
python -u scripts\package_results_for_analysis.py
if errorlevel 1 exit /b 1
echo [SUCCESS] HQC_SAC_PAPER_EXPERIMENT_DATA_FOR_ANALYSIS.zip ready.
