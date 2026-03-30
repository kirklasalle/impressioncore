@echo off
REM Build script for Kinect Enhanced Bridge DLL (K2VR-style Face Tracking)
REM Requires: Visual Studio 2022 Build Tools, Kinect SDK 1.8, Kinect Developer Toolkit 1.8

cd /d d:\Projects\impressioncore\tools
echo [BUILD] Setting up Visual Studio 2022 x64 environment...
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

set KINECT_SDK=C:\Program Files\Microsoft SDKs\Kinect\v1.8
set KINECT_TOOLKIT=C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0
set SRC_FILE=kinect_bridge_enhanced.cpp
set OUT_FILE=kinect_bridge_enhanced.dll
set OUT_DIR=d:\Projects\impressioncore\bin

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo [BUILD] Compiling %SRC_FILE% with FaceTrackLib (K2VR-style)...
echo [BUILD] Kinect SDK: %KINECT_SDK%
echo [BUILD] Developer Toolkit: %KINECT_TOOLKIT%

cl /LD /EHsc /O2 /MD "%SRC_FILE%" ^
    /I"%KINECT_SDK%\inc" ^
    /I"%KINECT_TOOLKIT%\inc" ^
    /Fe"%OUT_DIR%\%OUT_FILE%" ^
    /link /LIBPATH:"%KINECT_SDK%\lib\amd64" ^
          /LIBPATH:"%KINECT_TOOLKIT%\Lib\amd64" ^
    Kinect10.lib FaceTrackLib.lib ole32.lib oleaut32.lib

if %ERRORLEVEL% EQU 0 (
    echo [BUILD] SUCCESS! DLL created at: %OUT_DIR%\%OUT_FILE%
    echo [BUILD] Face Tracking enabled via native FaceTrackLib (K2VR methodology)

) else (
    echo [BUILD] FAILED with error code: %ERRORLEVEL%
)

pause
