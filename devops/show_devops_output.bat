@echo off
setlocal enabledelayedexpansion
title DevOps Output Demonstration - College Event Management System
color 0B
chcp 65001 >nul

:: Navigate to script directory
cd /d "%~dp0"
if exist "CollegeEventManagement" (
    cd "CollegeEventManagement"
)

:MENU
cls
echo ===============================================================================
echo      COLLEGE EVENT MANAGEMENT SYSTEM - DEVOPS PIPELINE OUTPUT DEMO
echo ===============================================================================
echo.
echo   [1] Show GIT Status and Information
echo   [2] Show DOCKER Status, Images and Containers
echo   [3] Show JENKINS Pipeline Details and Jenkinsfile
echo   [4] Show FRONTEND / Application Status and Launch in Browser
echo   [5] Show ALL Outputs in Sequence (Full Viva / Demo Presentation)
echo   [6] Exit
echo.
echo ===============================================================================
set /p choice="Enter your choice [1-6]: "

if "%choice%"=="1" goto SHOW_GIT
if "%choice%"=="2" goto SHOW_DOCKER
if "%choice%"=="3" goto SHOW_JENKINS
if "%choice%"=="4" goto SHOW_FRONTEND
if "%choice%"=="5" goto SHOW_ALL
if "%choice%"=="6" goto EXIT_PROMPT
echo Invalid choice. Try again.
timeout /t 2 >nul
goto MENU

:: ============================================================================
:: 1. GIT SECTION
:: ============================================================================
:SHOW_GIT
cls
echo ===============================================================================
echo                           [1/4] GIT OUTPUT & REPOSITORY
echo ===============================================================================
echo.
echo [1.1] Checking Git Installation:
git --version
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [!] Notice: This folder is not initialized as a Git repository yet.
    echo.
    echo Sample simulated Git commands for demonstration:
    echo   ^> git status
    echo   ^> git log -n 3 --oneline
    echo.
    echo Would you like to initialize a local Git repository and create an initial commit?
    set /p initgit="Initialize Git repo now? (Y/N): "
    if /i "!initgit!"=="Y" (
        git init
        git add .
        git commit -m "feat: College Event Management System DevOps Project with Docker and Jenkins"
        echo.
        echo [OK] Initialized Git repository and created initial commit!
        echo.
    )
)

git rev-parse --is-inside-work-tree >nul 2>&1
if not errorlevel 1 (
    echo -------------------------------------------------------------------------------
    echo [1.2] Current Git Branch:
    git branch --show-current 2>nul || git branch
    echo.
    echo -------------------------------------------------------------------------------
    echo [1.3] Git Status:
    git status -s
    echo.
    echo -------------------------------------------------------------------------------
    echo [1.4] Recent Git Commit History:
    git log --oneline -n 5 2>nul
    echo.
    echo -------------------------------------------------------------------------------
    echo [1.5] Remote Repositories:
    git remote -v
)
echo.
echo ===============================================================================
echo [Git Output Finished]
echo ===============================================================================
if "%batch_mode%"=="1" goto :eof
pause
goto MENU

:: ============================================================================
:: 2. DOCKER SECTION
:: ============================================================================
:SHOW_DOCKER
cls
echo ===============================================================================
echo                         [2/4] DOCKER OUTPUT & STATUS
echo ===============================================================================
echo.
echo [2.1] Docker Version:
docker --version 2>nul || echo Docker command not found in PATH!
echo.
echo [2.2] Checking Docker Daemon:
docker info >nul 2>&1
if errorlevel 1 (
    echo [!] WARNING: Docker Desktop daemon is not currently running.
    echo     Please start Docker Desktop if you wish to run/build containers.
    echo.
    echo Showing Dockerfile configuration for this project instead:
    echo -------------------------------------------------------------------------------
    type Dockerfile | more /E
) else (
    echo [OK] Docker daemon is running!
    echo.
    echo -------------------------------------------------------------------------------
    echo [2.3] Active & Existing Docker Containers:
    docker ps -a --filter "name=college-event" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo.
    echo -------------------------------------------------------------------------------
    echo [2.4] Docker Images:
    docker images college-event*
    echo.
    echo -------------------------------------------------------------------------------
    echo [2.5] Persistent Volumes:
    docker volume ls --filter "name=college_event"
)
echo.
echo ===============================================================================
echo [Docker Output Finished]
echo ===============================================================================
if "%batch_mode%"=="1" goto :eof
pause
goto MENU

:: ============================================================================
:: 3. JENKINS SECTION
:: ============================================================================
:SHOW_JENKINS
cls
echo ===============================================================================
echo                        [3/4] JENKINS PIPELINE OUTPUT
echo ===============================================================================
echo.
echo [3.1] Checking Jenkins Service on localhost:8080 ...
curl.exe -I -m 2 http://localhost:8080 >nul 2>&1
if errorlevel 1 (
    echo [*] Jenkins server is not reachable on http://localhost:8080 (Offline or running on another port).
) else (
    echo [OK] Jenkins service is ACTIVE and reachable at http://localhost:8080!
)
echo.
echo -------------------------------------------------------------------------------
echo [3.2] Jenkinsfile Pipeline Configuration (Build, Test, Deploy):
echo -------------------------------------------------------------------------------
type Jenkinsfile
echo.
echo -------------------------------------------------------------------------------
echo [3.3] Running Automated Test Suite (Stage 2: Test in Jenkins):
echo -------------------------------------------------------------------------------
python -m pytest test_app.py -v --tb=short
echo.
echo ===============================================================================
echo [Jenkins Output Finished]
echo ===============================================================================
if "%batch_mode%"=="1" goto :eof
pause
goto MENU

:: ============================================================================
:: 4. FRONTEND SECTION
:: ============================================================================
:SHOW_FRONTEND
cls
echo ===============================================================================
echo                   [4/4] FRONTEND / APPLICATION OUTPUT
echo ===============================================================================
echo.
echo [4.1] Checking local frontend server (Port 5000 / 5002)...
set APP_URL=
curl.exe -s -m 2 http://127.0.0.1:5000/ >nul 2>&1
if not errorlevel 1 (
    set APP_URL=http://localhost:5000
    echo [OK] Local Flask Application is LIVE at http://localhost:5000
) else (
    curl.exe -s -m 2 http://127.0.0.1:5002/ >nul 2>&1
    if not errorlevel 1 (
        set APP_URL=http://localhost:5002
        echo [OK] Containerized Application is LIVE at http://localhost:5002
    ) else (
        echo [!] Frontend is not currently listening on port 5000 or 5002.
    )
)

echo.
echo -------------------------------------------------------------------------------
echo [4.2] Application Endpoints:
echo   - Student Portal / Home:   http://localhost:5000/  (or 5002)
echo   - Events Directory:        http://localhost:5000/events
echo   - Track Registration:      http://localhost:5000/track
echo   - Admin Dashboard:         http://localhost:5000/admin
echo   - Admin Login:             http://localhost:5000/admin/login  (Password: admin123)
echo -------------------------------------------------------------------------------
echo.

if not "!APP_URL!"=="" (
    set /p openbr="Open Frontend in your browser right now? (Y/N): "
    if /i "!openbr!"=="Y" (
        start "" "!APP_URL!"
        start "" "!APP_URL!/admin"
        echo Opened Student Portal and Admin Dashboard in browser.
    )
) else (
    echo To start the frontend manually, run:
    echo   python app.py
)
echo.
echo ===============================================================================
echo [Frontend Output Finished]
echo ===============================================================================
if "%batch_mode%"=="1" goto :eof
pause
goto MENU

:: ============================================================================
:: 5. SHOW ALL (VIVA / PRESENTATION MODE)
:: ============================================================================
:SHOW_ALL
set batch_mode=1
call :SHOW_GIT
echo.
pause
call :SHOW_DOCKER
echo.
pause
call :SHOW_JENKINS
echo.
pause
call :SHOW_FRONTEND
echo.
set batch_mode=0
echo ===============================================================================
echo                   ALL 4 DEVOPS OUTPUTS DEMONSTRATED!
echo ===============================================================================
pause
goto MENU

:EXIT_PROMPT
echo Exiting DevOps Output Demo. Good luck with your presentation!
timeout /t 2 >nul
exit /b 0
