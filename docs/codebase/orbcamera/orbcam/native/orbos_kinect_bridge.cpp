#line 1 "d:\\Projects\\orbcamera\\orbcam\\native\\orbos_kinect_bridge.cpp"
#include <windows.h>
// Include NuiApi first
#include <NuiApi.h>
// Then FaceTrackLib (Converted to UTF-8)
#include <FaceTrackLib_UTF8.h>
#include <stdint.h>
#include <stdio.h>

#define EXPORT extern "C" __declspec(dllexport)

IFTFaceTracker* g_pFaceTracker = NULL;
IFTResult* g_pFTResult = NULL;
IFTImage* g_pVideoFrame = NULL;
IFTImage* g_pDepthFrame = NULL;

EXPORT int InitFaceTracking(int width, int height, const wchar_t* pszModelPath) {
    if (g_pFaceTracker) return 1;

    g_pFaceTracker = FTCreateFaceTracker();
    if (!g_pFaceTracker) return -1;

    FT_CAMERA_CONFIG videoConfig = { (UINT)width, (UINT)height, 0 };
    FT_CAMERA_CONFIG depthConfig = { 320, 240, 0 }; // Standard depth res for FT
    
    printf("DEBUG: Init with Width=%d, Height=%d, Model='%ls'\n", width, height, pszModelPath);

    HRESULT hr = g_pFaceTracker->Initialize(&videoConfig, &depthConfig, NULL, pszModelPath);
    if (FAILED(hr)) {
        g_pFaceTracker->Release();
        g_pFaceTracker = NULL;
        return (int)hr;
    }

    hr = g_pFaceTracker->CreateFTResult(&g_pFTResult);
    if (FAILED(hr)) return (int)hr;

    g_pVideoFrame = FTCreateImage();
    g_pDepthFrame = FTCreateImage();

    return 0;
}

EXPORT void ShutdownFaceTracking() {
    if (g_pFTResult) g_pFTResult->Release();
    if (g_pFaceTracker) g_pFaceTracker->Release();
    if (g_pVideoFrame) g_pVideoFrame->Release();
    if (g_pDepthFrame) g_pDepthFrame->Release();
    g_pFTResult = NULL;
    g_pFaceTracker = NULL;
    g_pVideoFrame = NULL;
    g_pDepthFrame = NULL;
}

EXPORT int ProcessFace(void* colorBuffer, void* depthBuffer, float* outPose) {
    if (!g_pFaceTracker || !g_pFTResult) return -1;
    
    // Setup video frame
    g_pVideoFrame->Attach(640, 480, colorBuffer, FTIMAGEFORMAT_UINT8_B8G8R8X8, 640*4);
    
    // In SDK 1.8, depth is often optional for basic tracking but better with it
    HRESULT hr = g_pFaceTracker->Initialize(NULL, NULL, NULL, NULL); // dummy re-init check? No.
    // Revert to correct call in case we fixed it upstream
    
    FT_SENSOR_DATA sensorData(g_pVideoFrame, NULL, 1.0f, NULL);
    
    // Note: StartTracking is expensive, usually you'd use ContinueTracking
    // But for a simple bridge test, we'll start.
    hr = g_pFaceTracker->StartTracking(&sensorData, NULL, NULL, g_pFTResult);
    
    if (SUCCEEDED(hr)) {
        hr = g_pFTResult->GetStatus();
        if (SUCCEEDED(hr)) {
            float scale;
            float rotation[3];
            float translation[3];
            g_pFTResult->Get3DPose(&scale, rotation, translation);
            outPose[0] = scale;
            outPose[1] = rotation[0]; outPose[2] = rotation[1]; outPose[3] = rotation[2];
            outPose[4] = translation[0]; outPose[5] = translation[1]; outPose[6] = translation[2];
            return 0;
        }
    }
    
    return (int)hr;
}

// Simple struct to hold key joint data
struct SimpleSkeleton {
    float Head[3];
    float Neck[3];
    float HandLeft[3];
    float HandRight[3];
    int IsTracked;
};

EXPORT int GetSkeleton(void* pSensorPtr, SimpleSkeleton* outSkeleton, int timeoutMs) {
    if (!pSensorPtr || !outSkeleton) return -1;
    
    INuiSensor* pSensor = static_cast<INuiSensor*>(pSensorPtr);
    
    NUI_SKELETON_FRAME skeletonFrame = {0};
    HRESULT hr = pSensor->NuiSkeletonGetNextFrame(timeoutMs, &skeletonFrame);
    
    if (FAILED(hr)) return (int)hr;
    
    // Find the first tracked skeleton
    for (int i = 0; i < NUI_SKELETON_COUNT; ++i) {
        if (skeletonFrame.SkeletonData[i].eTrackingState == NUI_SKELETON_TRACKED) {
            const NUI_SKELETON_DATA& data = skeletonFrame.SkeletonData[i];
            
            // Helper lambda/macro to copy vector
            auto CopyVec = [&](const Vector4& src, float* dst) {
                dst[0] = src.x; dst[1] = src.y; dst[2] = src.z;
            };
            
            CopyVec(data.SkeletonPositions[NUI_SKELETON_POSITION_HEAD], outSkeleton->Head);
            CopyVec(data.SkeletonPositions[NUI_SKELETON_POSITION_SHOULDER_CENTER], outSkeleton->Neck);
            CopyVec(data.SkeletonPositions[NUI_SKELETON_POSITION_HAND_LEFT], outSkeleton->HandLeft);
            CopyVec(data.SkeletonPositions[NUI_SKELETON_POSITION_HAND_RIGHT], outSkeleton->HandRight);
            
            outSkeleton->IsTracked = 1;
            return 0; // Success, found a skeleton
        }
    }
    
    outSkeleton->IsTracked = 0; // No skeleton found this frame
    return 0;
}


// Accelerometer
EXPORT int GetAccelerometer(void* pSensorPtr, float* x, float* y, float* z) {
    if (!pSensorPtr) return -1;
    INuiSensor* pSensor = static_cast<INuiSensor*>(pSensorPtr);
    Vector4 reading;
    HRESULT hr = pSensor->NuiAccelerometerGetCurrentReading(&reading);
    if (SUCCEEDED(hr)) {
        *x = reading.x; *y = reading.y; *z = reading.z;
        return 0;
    }
    return (int)hr;
}

// Color Settings (Brightness/Contrast)
EXPORT int GetColorSettings(void* pSensorPtr, double* brightness, double* contrast) {
    if (!pSensorPtr) return -1;
    INuiSensor* pSensor = static_cast<INuiSensor*>(pSensorPtr);
    INuiColorCameraSettings* pSettings = NULL;
    HRESULT hr = pSensor->NuiGetColorCameraSettings(&pSettings);
    if (SUCCEEDED(hr) && pSettings) {
       pSettings->NuiGetBrightness(brightness);
       pSettings->NuiGetContrast(contrast);
       pSettings->Release();
       return 0;
    }
    return (int)hr;
}

EXPORT int SetColorSettings(void* pSensorPtr, double brightness, double contrast) {
    if (!pSensorPtr) return -1;
    INuiSensor* pSensor = static_cast<INuiSensor*>(pSensorPtr);
    INuiColorCameraSettings* pSettings = NULL;
    HRESULT hr = pSensor->NuiGetColorCameraSettings(&pSettings);
    if (SUCCEEDED(hr) && pSettings) {
       if (brightness >= 0) pSettings->NuiSetBrightness(brightness);
       if (contrast >= 0) pSettings->NuiSetContrast(contrast);
       pSettings->Release();
       return 0;
    }
    return (int)hr;
}
