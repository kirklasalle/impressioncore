@echo off
echo Installing Driver Certificate...
rem Create a cert
makecert -r -pe -ss PrivateCertStore -n "CN=Antigravity Driver" Antigravity.cer
certmgr.exe /add Antigravity.cer /s /r localMachine root

echo Installing Driver with PnPUtil...
pnputil /add-driver OrbMP\OrbMP.inf /install

echo Scanning for hardware changes...
pnputil /scan-devices

echo Done.
pause
