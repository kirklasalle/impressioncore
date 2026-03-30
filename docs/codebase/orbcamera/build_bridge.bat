@echo off
set "LLVM_BIN=C:\Program Files\LLVM\bin"
set "KINECT_INC=C:\Program Files\Microsoft SDKs\Kinect\v1.8\inc"
set "TOOLKIT_INC=C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0\inc"
set "TOOLKIT_LIB=C:\Program Files\Microsoft SDKs\Kinect\Developer Toolkit v1.8.0\Lib\amd64\FaceTrackLib.lib"

echo [1/2] Compiling C++ Bridge...
"%LLVM_BIN%\clang.exe" -v -c orbcam/native/orbos_kinect_bridge.cpp -o orbcam/native/orbos_kinect_bridge.o -I"%KINECT_INC%" -I"%TOOLKIT_INC%" -Iorbcam/native
if %ERRORLEVEL% NEQ 0 (
    echo Compilation Failed!
    exit /b %ERRORLEVEL%
)

echo [2/2] Linking DLL...
"%LLVM_BIN%\clang.exe" -shared orbcam/native/orbos_kinect_bridge.o -o orbcam/native/orbos_kinect_bridge.dll "%TOOLKIT_LIB%" "C:\Program Files\Microsoft SDKs\Kinect\v1.8\lib\amd64\Kinect10.lib" -fuse-ld=lld
if %ERRORLEVEL% NEQ 0 (
    echo Linking Failed!
    exit /b %ERRORLEVEL%
)

echo Build SUCCESS!
dir orbcam\native\orbos_kinect_bridge.dll
