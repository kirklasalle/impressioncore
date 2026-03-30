@echo off
REM Install Essential ImpressionCore Development Extensions
REM Priority: High-Impact ML/AI Development Tools

echo 🚀 Installing Essential Extensions for ImpressionCore Development...
echo.

echo === Phase 1: Critical ML/AI Development Tools ===
echo Installing TensorBoard support...
code-insiders --install-extension ms-toolsai.tensorboard

echo Installing Python Image Preview (multimodal debugging)...
code-insiders --install-extension 076923.python-image-preview

echo Installing Scalene Profiler (AI-powered memory profiling)...
code-insiders --install-extension emeryberger.scalene

echo Installing NVIDIA Nsight (CUDA profiling)...
code-insiders --install-extension nvidia.nsight-vscode-edition

echo.
echo === Phase 2: Data Science & Analysis ===
echo Installing Data Wrangler (dataset exploration)...
code-insiders --install-extension ms-toolsai.datawrangler

echo Installing Python Resource Monitor...
code-insiders --install-extension kaih2o.python-resource-monitor

echo Installing SandDance (advanced visualization)...
code-insiders --install-extension msrvida.vscode-sanddance

echo.
echo === Phase 3: Scientific Computing ===
echo Installing LaTeX Previewer (research documentation)...
code-insiders --install-extension mjpvs.latex-previewer

echo Installing DVC (experiment tracking)...
code-insiders --install-extension iterative.dvc

echo.
echo === Phase 4: Enhanced Development ===
echo Installing AI/ML Debugger suite...
code-insiders --install-extension yashh130021.vscode-ai-debugger

echo Installing Plotly snippets (scientific visualization)...
code-insiders --install-extension analytic-signal.snippets-plotly

echo.
echo 🎉 Essential ImpressionCore extensions installed!
echo.
echo New capabilities added:
echo ✅ TensorBoard integration for training monitoring
echo ✅ Multimodal data visualization and debugging  
echo ✅ AI-powered memory profiling for consumer hardware
echo ✅ CUDA performance optimization tools
echo ✅ Advanced dataset exploration and analysis
echo ✅ Scientific documentation and research tools
echo ✅ Comprehensive ML debugging suite
echo.
echo Next: Restart VS Code to activate all extensions
pause
