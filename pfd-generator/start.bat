@echo off
cd /d "%~dp0"
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
echo Starting PFD Generator...
echo http://localhost:5180
start http://localhost:5180
npx vite --port 5180
