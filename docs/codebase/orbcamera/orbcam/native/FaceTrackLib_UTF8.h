//------------------------------------------------------------------------------
// <copyright file="FaceTrackLib.h" company="Microsoft">
//     Copyright (c) Microsoft Corporation.  All rights reserved.
// </copyright>
//------------------------------------------------------------------------------

#pragma once

#ifdef _WINDOWS
#include <objbase.h>
#include <windows.h>
#endif

#define FTAPI STDMETHODCALLTYPE

// Interfaces
//#if defined( _WIN32 ) && !defined( _NO_COM)
DEFINE_GUID(IID_IFTFaceTracker, 0x1a00a7ba, 0xc217, 0x11e0, 0xac, 0x90, 0x00, 0x24, 0x81, 0x14, 0x41, 0xfd);
DEFINE_GUID(IID_IFTResult, 0x1a00a7bb, 0xc217, 0x11e0, 0xac, 0x90, 0x00, 0x24, 0x81, 0x14, 0x41, 0xfd);
DEFINE_GUID(IID_IFTImage, 0x1a00a7bc, 0xc217, 0x11e0, 0xac, 0x90, 0x00, 0x24, 0x81, 0x14, 0x41, 0xfd);
DEFINE_GUID(IID_IFTModel, 0x1a00a7bd, 0xc217, 0x11e0, 0xac, 0x90, 0x00, 0x24, 0x81, 0x14, 0x41, 0xfd);
//#endif

#ifdef __cplusplus

#ifndef DECLSPEC_UUID
#if _MSC_VER >= 1100
#define DECLSPEC_UUID(x)    __declspec(uuid(x))
#else
#define DECLSPEC_UUID(x)
#endif
#endif

interface DECLSPEC_UUID("1A00A7BA-C217-11E0-AC90-0024811441FD") IFTFaceTracker;
interface DECLSPEC_UUID("1A00A7BB-C217-11E0-AC90-0024811441FD") IFTResult;
interface DECLSPEC_UUID("1A00A7BC-C217-11E0-AC90-0024811441FD") IFTImage;
interface DECLSPEC_UUID("1A00A7BD-C217-11E0-AC90-0024811441FD") IFTModel;

#if defined(_COM_SMARTPTR_TYPEDEF)
_COM_SMARTPTR_TYPEDEF(IFTFaceTracker, __uuidof(IFTFaceTracker));
_COM_SMARTPTR_TYPEDEF(IFTResult, __uuidof(IFTResult));
_COM_SMARTPTR_TYPEDEF(IFTImage, __uuidof(IFTImage));
_COM_SMARTPTR_TYPEDEF(IFTModel, __uuidof(IFTModel));
#endif

#endif

// Data structures
struct FT_SENSOR_DATA;
struct FT_CAMERA_CONFIG;
struct FT_VECTOR2D;
struct FT_VECTOR3D;
struct FT_TRIANGLE;
struct FT_WEIGHTED_RECT;

// Face Tracking Error Codes
#define FT_FACILITY                             0xFAC   // FT facility error code               // Face Tracking facility error code
#define FT_ERROR_INVALID_MODELS                 MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 1)    // Returned when the face tracking models loaded by the tracking engine have incorrect format
#define FT_ERROR_INVALID_INPUT_IMAGE            MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 2)    // Returned when passed input image is invalid
#define FT_ERROR_FACE_DETECTOR_FAILED           MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 3)    // Returned when face tracking fails due to face detection errors
#define FT_ERROR_AAM_FAILED                     MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 4)    // Returned when face tracking fails due to errors in tracking individual face parts
#define FT_ERROR_NN_FAILED                      MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 5)    // Returned when face tracking fails due to inability of the Neural Network to find nose, mouth corners and eyes
#define FT_ERROR_UNINITIALIZED                  MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 6)    // Returned when uninitialized face tracker is used
#define FT_ERROR_INVALID_MODEL_PATH             MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 7)    // Returned when a file path to the face model files is invalid or when the model files could not be located
#define FT_ERROR_EVAL_FAILED                    MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 8)    // Returned when face tracking worked but later evaluation found that the quality of the results was poor
#define FT_ERROR_INVALID_CAMERA_CONFIG          MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 9)    // Returned when the passed camera configuration is invalid
#define FT_ERROR_INVALID_3DHINT                 MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 10)   // Returned when the passed 3D hint vectors contain invalid values (for example out of range)
#define FT_ERROR_HEAD_SEARCH_FAILED             MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 11)   // Returned when the system cannot find the head area in the passed data based on passed 3D hint vectors or region of interest rectangle
#define FT_ERROR_USER_LOST                      MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 12)   // Returned when the user ID of the subject being tracked is switched or lost so we should call StartTracking on next call for tracking face
#define FT_ERROR_KINECT_DLL_FAILED              MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 13)   // Returned when Kinect DLL failed to load
#define FT_ERROR_KINECT_NOT_CONNECTED           MAKE_HRESULT(SEVERITY_ERROR, FT_FACILITY, 14)   // Returned when Kinect sensor was not detected in the system 

#ifdef __cplusplus
extern "C" {
#endif


#if defined(_XBOX)
    #define DllExport
#elif !defined(DllExport)
    #define DllExport __declspec(dllimport)
#endif

/// <summary>
/// Creates a face tracker instance and returns its IFTFaceTracker interface. Returned interface's refcount is incremented; 
/// after use it must be released by calling Release(). 
/// <param name="reserved">Reserved value, should always be NULL</param>
/// </summary>
/// <returns>Interface pointer in case of success, or NULL if it cannot create this instance.</returns>
DllExport IFTFaceTracker* FTAPI FTCreateFaceTracker( PVOID reserved = NULL );

/// <summary>
/// Creates an image object instance and returns its IFTImage interface. The returned interface's refcount is incremented; 
/// after use it needs to be released by calling Release(). 
/// </summary>
/// <returns>Interface pointer in case of success, or NULL if it cannot create this instance.</returns>
DllExport IFTImage* FTAPI FTCreateImage();

/// <summary>
/// A declaration of the pointer to the function used for mapping Kinect's depth frame coordinates to video frame coordinates.
/// By default the face tracking engine uses Kinect's depth to color frame mapping function when users do not pass a pointer to their custom version.
/// </summary>
/// <param name="depthFrameWidth">depth frame width</param>
/// <param name="depthFrameHeight">depth frame height</param>
/// <param name="colorFrameWidth">color frame width</param>
/// <param name="colorFrameHeight">color frame height</param>
/// <param name="zoomFactor">video frame zoom factor</param>
/// <param name="viewOffset">video frame view offset in the native video camera frame defined by its left-top corner X,Y coordinates</param>
/// <param name="depthX">X coordinate of the depth point to convert</param>
/// <param name="depthY">Y coordinate of the depth point to convert</param>
/// <param name="depthZ">distance in millimeters to the depth frame point defined by (depthX, depthY)</param>
/// <param name="pColorX">returned video frame X coordinate</param>
/// <param name="pColorY">returned video frame Y coordinate</param>
/// <returns>S_OK if the method succeeds. E_INVALIDARG, E_POINTER if the method fails.</returns>
typedef HRESULT (FTAPI *FTRegisterDepthToColor)(UINT depthFrameWidth, UINT depthFrameHeight, UINT colorFrameWidth, UINT colorFrameHeight, 
                                          FLOAT zoomFactor, POINT viewOffset, LONG depthX, LONG depthY, USHORT depthZ, LONG* pColorX, LONG* pColorY);

/*
    Face Tracking Lib interfaces
*/

#undef INTERFACE
#define INTERFACE IFTFaceTracker

/// <summary>
/// IFTFaceTracker is the main interface used for face tracking. An IFTFaceTracking object is created by using the FTCreateFaceTracker Function.
/// </summary>
DECLARE_INTERFACE_(IFTFaceTracker, IUnknown)
{
    /*** IUnknown methods ***/
    STDMETHOD(QueryInterface)(THIS_ REFIID riid, void** ppvObj) PURE;
    STDMETHOD_(ULONG, AddRef)(THIS) PURE;
    STDMETHOD_(ULONG, Release)(THIS) PURE;

    /*** IFTFaceTracker methods ***/
    
    /// <summary>Initializes an IFTFaceTracker instance.</summary>
    /// <param name="pVideoCameraConfig">Video camera configuration.</param>
    /// <param name="pDepthCameraConfig">Optional. Depth camera configuration. Not used if NULL is passed.</param>
    /// <param name="depthToColorMappingFunc">A pointer to the depth-to-color coordinates mapping function.</param>
    /// <param name="pszModelPath">Path to a directory that contains face model. This is optional parameter and if it's not set, default model will be used (this is default use case).</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER, FT_ERROR_INVALID_MODEL_PATH, FT_ERROR_INVALID_MODELS, E_OUTOFMEMORY</returns>
    STDMETHOD(Initialize)(THIS_ const FT_CAMERA_CONFIG* pVideoCameraConfig, const FT_CAMERA_CONFIG* pDepthCameraConfig, 
        FTRegisterDepthToColor depthToColorMappingFunc, PCWSTR pszModelPath) PURE;
     
    /// <summary>
    /// Resets the IFTFaceTracker instance to a clean state (the same state that exists after calling the Initialize() method).
    /// </summary>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED.</returns>
    STDMETHOD(Reset)(THIS) PURE;

    /// <summary>
    /// Creates a result object instance and returns its IFTResult interface. The returned interface refcount is incremented, 
    /// so after you use it, you must release it by calling Release(). 
    /// </summary>
    /// <param name="ppFTResult">A returned interface pointer if successful; otherwise, NULL if it cannot create this instance.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_POINTER.</returns>
    STDMETHOD(CreateFTResult)(THIS_ IFTResult** ppFTResult) PURE;

    /// <summary>
    /// Sets shape units (SUs) that the face tracker uses for passed values. 
    /// </summary>
    /// <param name="headScale">Scale of the head. It is a positive value defined as HeadSize/AverageHeadSize, where size is either head width or height. Average head width is set to be 15.6cm</param>
    /// <param name="pSUCoefs">Float array of SU coefficients.</param>
    /// <param name="suCount">Number of elements in the pSUCoefs array.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_INVALIDARG, E_POINTER.</returns>
    STDMETHOD(SetShapeUnits)(THIS_ FLOAT headScale, const FLOAT* pSUCoefs, UINT suCount) PURE;

    /// <summary>
    /// Returns shape units (SUs) that the face tracker is using. If the passed ppSUCoefs parameter is NULL, it returns number of SUs used in the loaded face model.
    /// </summary>
    /// <param name="pHeadScale">A pointer to the head scale. It is a positive value defined as HeadSize/AverageHeadSize, where size is either head width or height. Average head width is set to be 15.6cm</param>
    /// <param name="ppSUCoefs">A pointer to a float array of shape unit coefficients. The array must be large enough to contain all of the SUs for the loaded face model.</param>
    /// <param name="pSUCount">Number of returned shape unit coefficients. This parameter is IN/OUT and must be initialized to the size of the *ppSUCoefs array when passed in.</param>
    /// <param name="pHaveConverged">true if shape unit coefficients converged to realistic values; otherwise, false (the SU coefficients are still converging).</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_INVALIDARG, E_POINTER.</returns>
    STDMETHOD(GetShapeUnits)(THIS_ FLOAT* pHeadScale, FLOAT** ppSUCoefs, UINT* pSUCount, BOOL* pHaveConverged) PURE;

    /// <summary>
    /// Sets the shape unit (SU) computational state. This method allows you to enable or disable 3D-shape computation in the face tracker. If enabled, the face tracker will continue to refine SUs. 
    /// </summary>
    /// <param name="isEnabled">true to enable SU computation, false to disable SU computation.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED.</returns>
    STDMETHOD(SetShapeComputationState)(THIS_ BOOL isEnabled) PURE;

    /// <summary>
    /// Returns whether the shape unit (SU) computational state is enabled or disabled. If enabled, the face tracker continues refining the SUs. 
    /// </summary>
    /// <param name="pIsEnabled">A pointer to a variable that receives the returned value.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_POINTER.</returns>
    STDMETHOD(GetShapeComputationState)(THIS_ BOOL* pIsEnabled) PURE;

    /// <summary>
    /// Returns an IFTModel Interface interface to the loaded face model. The returned interface refcount is incremented, so after you use it, 
    /// you must release it by calling Release(). 
    /// </summary>
    /// <param name="ppModel">A returned interface pointer if successful; otherwise, NULL if it cannot create this instance.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_POINTER.</returns>
    STDMETHOD(GetFaceModel)(THIS_ IFTModel** ppModel) PURE;

    /// <summary>
    /// Starts face tracking. StartTracking() detects a face based on the passed parameters, then identifies characteristic points and begins tracking. 
    /// This process is more expensive than simply tracking (done by calling ContinueTracking()), but more robust. Therefore, if running at a high frame rate 
    /// you should only use StartTracking() to initiate the tracking process, and then you should use ContinueTracking() to continue tracking. 
    /// If the frame rate is low and the face tracker cannot keep up with fast face and head movement (or if there is too much motion blur), 
    /// you can use StartTracking() solely (instead of the usual sequence of StartTracking(), ContinueTracking(), ContinueTracking(), and so on). 
    /// </summary>
    /// <param name="pSensorData">Input from the video and depth cameras (depth is optional).</param>
    /// <param name="pRoi">Optional, NULL if not provided. Region of interest in the passed video frame where the face tracker should search for a face to initiate tracking.</param>
    /// <param name="headPoints[2]">
    /// Optional, NULL if not provided. Array that contains two 3D points in camera space if known (for example, from a Kinect skeleton). 
    /// The first element is the neck position and the second element is the head center position. 
    /// The camera space is defined as: right handed, the origin at the camera optical center; Y points up; units are in meters. 
    /// </param>
    /// <param name="pFTResult">IFTResult Interface pointer that receives computed face tracking results.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails due to programmatic errors, the return value can be FT_ERROR_UNINITIALIZED, E_INVALIDARG, E_POINTER.
    /// To check if the face tracking was successful, you should call IFTResult::GetStatus() method.
    /// </returns>
    STDMETHOD(StartTracking)(THIS_ const FT_SENSOR_DATA* pSensorData, const RECT* pRoi, const FT_VECTOR3D headPoints[2], IFTResult* pFTResult) PURE;

    /// <summary>
    /// Continues the face tracking process that was initiated by StartTracking(). This method is faster than StartTracking() and is used only for tracking. 
    /// If the face being tracked moves too far from the previous location (for example, when the input frame rate is low), this method fails. 
    /// </summary>
    /// <param name="pSensorData">Input from the video and depth cameras (depth is optional).</param>
    /// <param name="headPoints[2]">
    /// Optional, NULL if not provided. Array that contains two 3D points in camera space if known (for example, from a Kinect skeleton). 
    /// The first element is the neck position and the second element is the head center position. 
    /// The camera space is defined as: right handed, the origin at the camera optical center; Y points up; units are in meters. 
    /// </param>
    /// <param name="pFTResult">IFTResult Interface pointer that receives computed face tracking results.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails due to programmatic errors, the return value can be FT_ERROR_UNINITIALIZED, E_INVALIDARG, E_POINTER.
    /// To check if the face tracking was successful, you should call IFTResult::GetStatus() method.
    /// </returns>
    STDMETHOD(ContinueTracking)(THIS_ const FT_SENSOR_DATA* pSensorData, const FT_VECTOR3D headPoints[2], IFTResult* pFTResult) PURE;

    /// <summary>
    /// Detects faces in the provided video frame. It returns an array of faces and the detection confidence level for each face. 
    /// The confidence level is a value between 0 and 1 (where 0 is the lowest and 1 is highest). 
    /// </summary>
    /// <param name="pSensorData">Input from the video and depth cameras (currently, depth input is ignored).</param>
    /// <param name="pRoi">
    /// Optional, NULL if not provided. Region of interest in the video frame where the detector must look for faces. 
    /// If NULL, the detector uses the full frame.
    /// </param>
    /// <param name="pFaces">Returned array of weighted face rectangles (where weight is a detection confidence level).</param>
    /// <param name="pFaceCount">On input, it must have a size of the pFaces array. On output, it contains the number of faces detected and returned in pFaces.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be FT_ERROR_UNINITIALIZED, E_INVALIDARG, E_POINTER, or FT_ERROR_FACE_DETECTOR_FAILED.</returns>
    STDMETHOD(DetectFaces)(THIS_ const FT_SENSOR_DATA* pSensorData, const RECT* pRoi, FT_WEIGHTED_RECT* pFaces, UINT* pFaceCount) PURE;
};

/// <summary>Specifies image formats supported by the face tracking engine</summary>
typedef enum _FTIMAGEFORMAT
{
    FTIMAGEFORMAT_INVALID = 0,          // Invalid format
    FTIMAGEFORMAT_UINT8_GR8,            // Grayscale image where each pixel is 1 byte (or 8 bits). 
    FTIMAGEFORMAT_UINT8_R8G8B8,         // RGB image (same as ARGB but without an alpha channel).
    FTIMAGEFORMAT_UINT8_X8R8G8B8,       // Same as ARGB (the alpha channel byte is present but not used). 
    FTIMAGEFORMAT_UINT8_A8R8G8B8,       // ARGB format (the first byte is the alpha transparency channel; remaining bytes are 8-bit red, green, and blue channels). 
    FTIMAGEFORMAT_UINT8_B8G8R8X8,       // Same as BGRA (the alpha channel byte is present but not used). 
    FTIMAGEFORMAT_UINT8_B8G8R8A8,       // BGRA format (the last byte is the alpha transparency channel; remaining bytes are 8-bit red, green, and blue channels). 
    FTIMAGEFORMAT_UINT16_D16,           // 16-bit per pixel depth data that represents the distance to a pixel in millimeters. 
    FTIMAGEFORMAT_UINT16_D13P3          // 16-bit per pixel depth data that represents the distance to a pixel in millimeters. The last three bits represent the user ID (Kinect's depth data format).
} FTIMAGEFORMAT;

#undef INTERFACE
#define INTERFACE IFTImage

/// <summary>
/// IFTImage is a helper interface that can wrap various image buffers
/// </summary>
DECLARE_INTERFACE_(IFTImage, IUnknown)
{
    /*** IUnknown methods ***/
    STDMETHOD(QueryInterface)(THIS_ REFIID riid, void** ppvObj) PURE;
    STDMETHOD_(ULONG, AddRef)(THIS) PURE;
    STDMETHOD_(ULONG, Release)(THIS) PURE;

    /*** IFTImage methods ***/    

    /// <summary>
    /// Allocates memory for the image of passed width, height and format. The memory is owned by this interface and is released when the interface is released or 
    /// when another Allocate() call happens. Allocate() deallocates currently allocated memory if its internal buffers are not big enough to fit new image data. 
    /// If its internal buffers are big enough, no new allocation occurs. 
    /// </summary>
    /// <param name="width">Image width in pixels.</param>
    /// <param name="height">Image height in pixels.</param>
    /// <param name="format">Image format.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_OUTOFMEMORY.</returns>
    STDMETHOD(Allocate)(THIS_ UINT width, UINT height, FTIMAGEFORMAT format) PURE;

    /// <summary>
    /// Attaches this interface to external memory pointed to by pData, which is assumed to be sufficiently large to contain an image of the given size and format. 
    /// The memory referenced by pData is not deallocated when this interface is released. The caller owns the image buffer in this case and is responsible for its lifetime management. 
    /// </summary>
    /// <param name="width">Image width in pixels.</param>
    /// <param name="height">Image height in pixels.</param>
    /// <param name="pData">External image buffer.</param>
    /// <param name="format">Image format.</param>
    /// <param name="stride">Number of bytes between the beginning of two image rows (the image buffer could be aligned, so stride could be more than width*pixelSizeInBytes).</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER, E_OUTOFMEMORY.</returns>
    STDMETHOD(Attach)(THIS_ UINT width, UINT height, void* pData, FTIMAGEFORMAT format, UINT stride) PURE;

    /// <summary>
    /// Frees internal memory and sets this image to the empty state (0 size)
    /// </summary>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_UNEXPECTED, E_POINTER, E_OUTOFMEMORY.</returns>
    STDMETHOD(Reset)(THIS) PURE;

    /// <summary>Accessor to width of the image.</summary>
    /// <returns>Width of the image in pixel.</returns>
    STDMETHOD_(UINT, GetWidth)(THIS) PURE;

    /// <summary>Accessor to height of the image.</summary>
    /// <returns>Height of the image in pixel.</returns>
    STDMETHOD_(UINT, GetHeight)(THIS) PURE;

    /// <summary>Accessor to stride of the image.</summary>
    /// <returns>Stride of the image.</returns>
    STDMETHOD_(UINT, GetStride)(THIS) PURE;

    /// <summary>Accessor to bytes per pixel of the image.</summary>
    /// <returns>Bytes per pixel of the image.</returns>
    STDMETHOD_(UINT, GetBytesPerPixel)(THIS) PURE;

    /// <summary>Accessor to buffer size of the image.</summary>
    /// <returns>Size in bytes of the internal image buffer</returns>
    STDMETHOD_(UINT, GetBufferSize)(THIS) PURE;

    /// <summary>Accessor to format of the image.</summary>
    /// <returns>Format of the image.</returns>
    STDMETHOD_(FTIMAGEFORMAT, GetFormat)(THIS) PURE;

    /// <summary>Accessor to format of the image.</summary>
    /// <returns>BYTE pointer to buffer.</returns>
    STDMETHOD_(BYTE*, GetBuffer)(THIS) PURE;

    /// <summary>Accessor to the image buffer ownership state.</summary>
    /// <returns>True if this interface is attached to the external buffer, false - otherwise.</returns>
    STDMETHOD_(BOOL, IsAttached)(THIS) PURE;

    /// <summary>
    /// Non-allocating copy method. It copies this image data to pDestImage. It fails, if pDestImage doesn't have the right size or format. 
    /// If pDestImage has a different format, then this method attempts to convert pixels to pDestImage image format (if possible and supported).
    /// </summary>
    /// <param name="pDestImage">Destination image to copy data to.</param>
    /// <param name="pSrcRect">Source rectangle to copy data from in the source image (to support cut and paste operation). If NULL, the whole image gets copied.</param>
    /// <param name="destRow">Destination location (row) of the image data (to support cut and paste operation).</param>
    /// <param name="destColumn">Destination location (column) of the image data (to support cut and paste operation).</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER, E_OUTOFMEMORY.</returns>
    STDMETHOD(CopyTo)(THIS_ IFTImage* pDestImage, const RECT* pSrcRect, UINT destRow, UINT destColumn) PURE;

    /// <summary>
    /// Draws a line on the image.
    /// </summary>
    /// <param name="startPoint">Start point in image coordinates.</param>
    /// <param name="endPoint">End  point in image coordinates.</param>
    /// <param name="color">Line color in ARGB format (first byte is not used, second byte is red channel, third is green, fourth is blue)</param>
    /// <param name="lineWidthPx">Line width in pixels.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG.</returns>
    STDMETHOD(DrawLine)(THIS_ POINT startPoint, POINT endPoint, UINT32 color, UINT lineWidthPx) PURE;
};

#undef INTERFACE
#define INTERFACE IFTResult

/// <summary>
/// IFTResult interface represents the result of a face tracking operation.
/// </summary>
DECLARE_INTERFACE_(IFTResult, IUnknown)
{
    /*** IUnknown methods ***/
    STDMETHOD(QueryInterface)(THIS_ REFIID riid, void** ppvObj) PURE;
    STDMETHOD_(ULONG, AddRef)(THIS) PURE;
    STDMETHOD_(ULONG, Release)(THIS) PURE;

    /*** IFTImage methods ***/
    
    /// <summary>
    /// Resets this instance to a clean state.
    /// </summary>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_UNEXPECTED, E_OUTOFMEMORY.</returns>
    STDMETHOD(Reset)(THIS) PURE;

    /// <summary>
    /// Copies all data from this instance to another instance of IFTResult.
    /// </summary>
    /// <param name="pFTResultDst">IFTResult instance to copy data to.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER, E_OUTOFMEMORY.</returns>
    STDMETHOD(CopyTo)(THIS_ IFTResult* pFTResultDst) PURE;

    /// <summary>
    /// Returns the result of the face tracking operation.
    /// </summary>
    /// <returns>S_OK if a face is tracked successfully. If tracking fails, the return value can be FT_ERROR_FACE_DETECTOR_FAILED, FT_ERROR_AAM_FAILED, FT_ERROR_NN_FAILED, FT_ERROR_EVAL_FAILED.</returns>
    STDMETHOD(GetStatus)(THIS) PURE;

    /// <summary>
    /// Returns a face rectangle in video frame coordinates.
    /// </summary>
    /// <param name="pRect">A pointer to RECT structure to receive the returned face rectangle.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_POINTER.</returns>
    STDMETHOD(GetFaceRect)(THIS_ RECT* pRect) PURE;

    /// <summary>
    /// Returns 2D (X,Y) coordinates of the key points on the aligned face in video frame coordinates.
    /// </summary>
    /// <param name="ppPoints">Array of 2D points (as FT_VECTOR2D).</param>
    /// <param name="pPointCount">Number of elements in ppPoints.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_POINTER.</returns>
    STDMETHOD(Get2DShapePoints)(THIS_ FT_VECTOR2D** ppPoints, UINT* pPointCount) PURE;

    /// <summary>
    /// Returns 3D pose information.
    /// </summary>
    /// <param name="pScale">Face scale where 1.0 scale means that it is equal in size to the loaded 3D model (in the model space).</param>
    /// <param name="rotationXYZ">Three-element array of Euler rotation angles in degrees in the following sequence: first element, rotation around X; second element, rotation around Y; third element, rotation around Z.</param>
    /// <param name="translationXYZ">Three-element array of 3D translations in meters in the following sequence: first element, translation in X; second element, translation in Y; third element, translation in Z.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_POINTER.</returns>
    STDMETHOD(Get3DPose)(THIS_ FLOAT* pScale, FLOAT rotationXYZ[3], FLOAT translationXYZ[3]) PURE;

    /// <summary>
    /// Returns Animation Unit (AU) coefficients. These coefficients represent deformations of the 3D mask caused by the moving parts of the face (mouth, eyebrows, and so on). 
    /// </summary>
    /// <param name="ppCoefficients">Returned array of AUs</param>
    /// <param name="pAUCount">Number of elements in ppCoefficients.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_POINTER.</returns>
    STDMETHOD(GetAUCoefficients)(THIS_ FLOAT** ppCoefficients, UINT* pAUCount) PURE;
};

#undef INTERFACE
#define INTERFACE IFTModel

/// <summary>
/// IFTModel represents a 3D face model used in face tracking
/// </summary>
DECLARE_INTERFACE_(IFTModel, IUnknown)
{
    /*** IUnknown methods ***/
    STDMETHOD(QueryInterface)(THIS_ REFIID riid, void** ppvObj) PURE;
    STDMETHOD_(ULONG, AddRef)(THIS) PURE;
    STDMETHOD_(ULONG, Release)(THIS) PURE;

    /*** IFTModel methods ***/
    
    /// <summary>
    /// Gets the number of Shape Units (SUs) used in the 3D face model.
    /// </summary>
    /// <returns>Number of Shape Units (SUs).</returns>
    STDMETHOD_(UINT, GetSUCount)(THIS) PURE;
    
    /// <summary>
    /// Gets the number of Animation Units (AUs) used in the 3D face model.
    /// </summary>
    /// <returns>Number of Animation Units (AUs).</returns>
    STDMETHOD_(UINT, GetAUCount)(THIS) PURE;

    /// <summary>
    /// Gets the mesh triangles of the 3D face model.
    /// </summary>
    /// <param name="ppTriangles">Pointer to the array of returned mesh triangles. Each triangle structure (FT_TRIANGLE) contains 3 zero based indexes of the corresponding mesh vertices in clockwise fashion</param>
    /// <param name="pTriangleCount">Number of returned triangles in ppTriangles.</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_POINTER.</returns>
    STDMETHOD(GetTriangles)(THIS_ FT_TRIANGLE** ppTriangles, UINT* pTriangleCount) PURE;

    /// <summary>
    /// Gets the number of vertices in the 3D face model.
    /// </summary>
    /// <returns>Number of vertices in the 3D face model.</returns>
    STDMETHOD_(UINT, GetVertexCount)(THIS) PURE;

    /// <summary>
    /// Returns the 3D face model vertices transformed by the passed Shape Units, Animation Units, scale stretch, rotation and translation
    /// </summary>
    /// <param name="pSUCoefs">Shape unit coefficients.</param>
    /// <param name="suCount">Shape unit count.</param>
    /// <param name="pAUCoefs">Animation unit coefficients.</param>
    /// <param name="auCount">Animation unit count.</param>
    /// <param name="scale">Scale.</param>
    /// <param name="roationXYZ">Three-element array of Euler rotation angles in degrees in the following sequence: first element, rotation around X; second element, rotation around Y; third element, rotation around Z.</param>
    /// <param name="translationXYZ">Three-element array of 3D translations in meters in the following sequence: first element, translation in X; second element, translation in Y; third element, translation in Z.</param>
    /// <param name="pVertices">An array of returned 3D vertices</param>
    /// <param name="vertexCount">Number of returned vertices in pVertices array</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER.</returns>
    STDMETHOD(Get3DShape)(THIS_ const FLOAT* pSUCoefs, UINT suCount, const FLOAT* pAUCoefs, UINT auCount, FLOAT scale, const FLOAT roationXYZ[3], const FLOAT translationXYZ[3], 
        FT_VECTOR3D* pVertices, UINT vertexCount) PURE;

    /// <summary>
    /// Returns the 3D face model vertices transformed by the passed Shape Units, Animation Units, scale stretch, rotation and translation and
    /// projected to the video frame
    /// </summary>
    /// <param name="pCameraConfig">
    /// Video camera configuration to use to project a 3D shape from the camera space to a camera’s image plane. 
    /// Specifically, the Face Tracking SDK needs the focal length value for correct perspective projection.
    /// </param>
    /// <param name="zoomFactor">Specifies the camera’s zoom factor for the image plane on which to project a 3D shape.</param>
    /// <param name="viewOffset">
    /// Specifies the left, top coordinates of the view area read from a camera in the camera’s native frame (which may have a higher resolution than what is returned to a PC). 
    /// The view area is not necessarily the same as the camera’s native resolution, which may be higher (for example, as with a Kinect camera). 
    /// In this case, the program reads only the portion of the camera’s native frame. The left, top coordinates of this portion in the native camera frame is the view offset.
    /// </param>
    /// <param name="pSUCoefs">Shape unit coefficients.</param>
    /// <param name="suCount">Shape unit count.</param>
    /// <param name="pAUCoefs">Animation unit coefficients.</param>
    /// <param name="auCount">Animation unit count.</param>
    /// <param name="scale">Scale.</param>
    /// <param name="roationXYZ">Three-element array of Euler rotation angles in degrees in the following sequence: first element, rotation around X; second element, rotation around Y; third element, rotation around Z.</param>
    /// <param name="translationXYZ">Three-element array of 3D translations in meters in the following sequence: first element, translation in X; second element, translation in Y; third element, translation in Z.</param>
    /// <param name="pVertices">An array of returned 3D vertices</param>
    /// <param name="vertexCount">Number of returned vertices in pVertices array</param>
    /// <returns>If the method succeeds, the return value is S_OK. If the method fails, the return value can be E_INVALIDARG, E_POINTER.</returns>
    STDMETHOD(GetProjectedShape)(THIS_ const FT_CAMERA_CONFIG* pCameraConfig, FLOAT zoomFactor, POINT viewOffset, const FLOAT* pSUCoefs, UINT suCount, const FLOAT* pAUCoefs, UINT auCount, FLOAT scale, const FLOAT rotationXYZ[3], const FLOAT translationXYZ[3], 
        FT_VECTOR2D* pVertices, UINT vertexCount) PURE;
};


/*
 * Face Tracking Lib data structures
 */

/// <summary>
/// Contains the video or depth camera configuration parameters.
/// </summary>
struct FT_CAMERA_CONFIG
{   
    // Note that camera pixels should be square
    UINT  Width;            // frame width in pixels, allowed range - 1-UINT_MAX
    UINT  Height;           // frame height in pixels, allowed range - 1-UINT_MAX
    FLOAT FocalLength;      // camera’s focal length in pixels, allowed range - 0-FLOAT_MAX, where 0 value means - use an estimated focal length (average for most cameras, the tracking precision may degrade)
};

/// <summary>
/// Contains input data for a face tracking operation.
/// </summary>
struct FT_SENSOR_DATA
{
#ifdef __cplusplus
    FT_SENSOR_DATA(IFTImage* pVideoFrameParam = NULL, IFTImage* pDepthFrameParam = NULL, FLOAT zoomFactorParam = 1.0f, const POINT* pViewOffsetParam = NULL)
        : pVideoFrame(pVideoFrameParam), pDepthFrame(pDepthFrameParam), ZoomFactor(zoomFactorParam)
    {
        ViewOffset.x = pViewOffsetParam ? pViewOffsetParam->x : 0;
        ViewOffset.y = pViewOffsetParam ? pViewOffsetParam->y : 0;
    }
#endif

    IFTImage* pVideoFrame;  // a pointer to a video frame. Must be synchronized with the depth frame passed in the same structure.
    IFTImage* pDepthFrame;  // a pointer to a depth frame. Must be synchronized with the video frame passed in the same structure.
    FLOAT     ZoomFactor;   // camera’s zoom factor for the video frame (value 1.0f means - no zoom is used)
    POINT     ViewOffset;   // the left, top coordinates of the video frame view area read from the camera’s native frame (which may have a higher resolution than what is returned to a PC). 
};

/// <summary>
/// Represents a 2D vector with x,y elements
/// </summary>
struct FT_VECTOR2D
{
#ifdef __cplusplus
    FT_VECTOR2D(FLOAT xParam = 0, FLOAT yParam = 0) : x(xParam), y(yParam) {}
#endif
    FLOAT x;
    FLOAT y;
};

/// <summary>
/// Represents a 3D vector with x,y,z elements
/// </summary>
struct FT_VECTOR3D
{
#ifdef __cplusplus
    FT_VECTOR3D(FLOAT xParam = 0, FLOAT yParam = 0, FLOAT zParam = 0) : x(xParam), y(yParam), z(zParam) {}
#endif
    FLOAT x;
    FLOAT y;
    FLOAT z;
};

/// <summary>
/// Represents a mesh triangle with i,j,k vertex indexes
/// </summary>
struct FT_TRIANGLE
{
    INT i;  // index of first vertex
    INT j;  // index of second vertex
    INT k;  // index of third vertex
};

/// <summary>
/// Represents a weighted rectangle
/// </summary>
struct FT_WEIGHTED_RECT
{
    FLOAT Weight;   // some weight 
    RECT  Rect;     // rectangle coordinates as RECT structure
};


#ifdef __cplusplus
};
#endif
