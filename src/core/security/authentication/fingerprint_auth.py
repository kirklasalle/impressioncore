"""
Fingerprint Authentication Provider for ImpressionCore Security Infrastructure
Phase 8A: Security Infrastructure Foundation

This module provides fingerprint recognition authentication optimized for GTX 1050 Ti hardware.
Uses lightweight algorithms and memory-efficient processing for real-time fingerprint verification.

Author: ImpressionCore Development Team
Created: 2025-05-31
Hardware Target: GTX 1050 Ti (4GB VRAM)
Memory Target: <32MB for fingerprint authentication operations
"""

import asyncio
import numpy as np
import logging
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass

from .auth_base import (
    BiometricAuthenticationBase,
    AuthenticationResult,
    AuthenticationStatus,
    AuthenticationType,
    AuthenticationError
)

# Image processing imports (lightweight alternatives for GTX 1050 Ti)
try:
    import cv2
    from skimage import morphology, filters, measure
    from scipy import ndimage
    from scipy.spatial.distance import euclidean
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logging.warning("Image processing libraries not available. Fingerprint authentication will use simulated mode.")

@dataclass
class Minutiae:
    """Fingerprint minutiae point representation"""
    x: int
    y: int
    angle: float
    type: str  # 'ending' or 'bifurcation'
    quality: float

class FingerprintQualityAssessment:
    """Fingerprint image quality assessment"""
    
    def __init__(self):
        self.min_resolution = (200, 200)
        self.min_contrast = 50
        self.min_clarity = 0.3
        self.min_area_coverage = 0.6
    
    def assess_image_quality(
        self, 
        fingerprint_image: np.ndarray
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Assess quality of fingerprint image
        
        Args:
            fingerprint_image: Grayscale fingerprint image
            
        Returns:
            Tuple of (quality_score, quality_metadata)
        """
        try:
            quality_metrics = {}
            quality_score = 1.0
            
            # Resolution check
            height, width = fingerprint_image.shape[:2]
            quality_metrics["resolution"] = (width, height)
            
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                quality_score *= 0.4
                quality_metrics["resolution_issue"] = "too_low"
            
            # Contrast assessment
            contrast = np.std(fingerprint_image)
            quality_metrics["contrast"] = float(contrast)
            
            if contrast < self.min_contrast:
                quality_score *= max(0.3, contrast / self.min_contrast)
                quality_metrics["contrast_issue"] = "too_low"
            
            # Clarity assessment (gradient-based)
            if IMAGE_PROCESSING_AVAILABLE:
                grad_x = cv2.Sobel(fingerprint_image, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(fingerprint_image, cv2.CV_64F, 0, 1, ksize=3)
                clarity = np.mean(np.sqrt(grad_x**2 + grad_y**2))
            else:
                # Simplified clarity estimate
                clarity = np.std(np.diff(fingerprint_image, axis=0)) + np.std(np.diff(fingerprint_image, axis=1))
            
            quality_metrics["clarity"] = float(clarity)
            
            if clarity < self.min_clarity:
                quality_score *= max(0.3, clarity / self.min_clarity)
                quality_metrics["clarity_issue"] = "blurry"
            
            # Area coverage (non-background pixels)
            if IMAGE_PROCESSING_AVAILABLE:
                # Threshold to separate fingerprint from background
                _, binary = cv2.threshold(fingerprint_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                coverage = np.sum(binary == 0) / (width * height)  # Assuming dark fingerprint on light background
            else:
                # Simplified coverage estimate
                threshold = np.mean(fingerprint_image)
                coverage = np.sum(fingerprint_image < threshold) / (width * height)
            
            quality_metrics["area_coverage"] = float(coverage)
            
            if coverage < self.min_area_coverage:
                quality_score *= max(0.5, coverage / self.min_area_coverage)
                quality_metrics["coverage_issue"] = "insufficient"
            
            # Dynamic range check
            dynamic_range = np.max(fingerprint_image) - np.min(fingerprint_image)
            quality_metrics["dynamic_range"] = float(dynamic_range)
            
            if dynamic_range < 100:  # Assuming 8-bit image
                quality_score *= max(0.4, dynamic_range / 255)
                quality_metrics["dynamic_range_issue"] = "limited"
            
            quality_score = max(0.0, min(1.0, quality_score))
            
            return quality_score, quality_metrics
            
        except Exception as e:
            logging.error(f"Fingerprint quality assessment error: {str(e)}")
            return 0.0, {"error": str(e)}

class FingerprintPreprocessor:
    """
    Fingerprint image preprocessing optimized for GTX 1050 Ti
    
    Provides efficient preprocessing steps to enhance fingerprint image
    quality while maintaining low memory usage.
    """
    
    def __init__(self, memory_limit_mb: int = 16):
        """
        Initialize fingerprint preprocessor
        
        Args:
            memory_limit_mb: Memory limit for preprocessing operations
        """
        self.memory_limit_mb = memory_limit_mb
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def preprocess_fingerprint(
        self, 
        fingerprint_image: np.ndarray,
        target_size: Tuple[int, int] = (256, 256)
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Preprocess fingerprint image for feature extraction
        
        Args:
            fingerprint_image: Input fingerprint image
            target_size: Target size for resized image
            
        Returns:
            Tuple of (processed_image, preprocessing_metadata)
        """
        try:
            preprocessing_metadata = {
                "original_shape": fingerprint_image.shape,
                "target_size": target_size
            }
            
            # Convert to grayscale if needed
            if len(fingerprint_image.shape) == 3:
                if IMAGE_PROCESSING_AVAILABLE:
                    processed_image = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
                else:
                    # Simple grayscale conversion
                    processed_image = np.mean(fingerprint_image, axis=2).astype(np.uint8)
                preprocessing_metadata["converted_to_grayscale"] = True
            else:
                processed_image = fingerprint_image.copy()
            
            # Resize to target size for memory efficiency
            if processed_image.shape[:2] != target_size:
                if IMAGE_PROCESSING_AVAILABLE:
                    processed_image = cv2.resize(processed_image, target_size, interpolation=cv2.INTER_CUBIC)
                else:
                    # Simple resize using numpy (basic interpolation)
                    processed_image = self._simple_resize(processed_image, target_size)
                preprocessing_metadata["resized"] = True
            
            # Histogram equalization for contrast enhancement
            if IMAGE_PROCESSING_AVAILABLE:
                processed_image = cv2.equalizeHist(processed_image)
            else:
                # Simple contrast enhancement
                processed_image = self._enhance_contrast(processed_image)
            preprocessing_metadata["contrast_enhanced"] = True
            
            # Noise reduction
            if IMAGE_PROCESSING_AVAILABLE:
                processed_image = cv2.GaussianBlur(processed_image, (3, 3), 0)
            else:
                # Simple smoothing
                processed_image = self._simple_smooth(processed_image)
            preprocessing_metadata["noise_reduced"] = True
            
            # Normalize to [0, 255] range
            processed_image = np.clip(processed_image, 0, 255).astype(np.uint8)
            
            return processed_image, preprocessing_metadata
            
        except Exception as e:
            self.logger.error(f"Fingerprint preprocessing error: {str(e)}")
            # Return original image on error
            return fingerprint_image, {"error": str(e)}
    
    def _simple_resize(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Simple image resize using numpy"""
        try:
            height, width = image.shape
            target_width, target_height = target_size
            
            # Calculate scaling factors
            scale_x = width / target_width
            scale_y = height / target_height
            
            # Create coordinate arrays
            y_coords = np.arange(target_height) * scale_y
            x_coords = np.arange(target_width) * scale_x
            
            # Clip coordinates to image bounds
            y_coords = np.clip(y_coords, 0, height - 1).astype(int)
            x_coords = np.clip(x_coords, 0, width - 1).astype(int)
            
            # Sample the image
            resized = image[np.ix_(y_coords, x_coords)]
            
            return resized
            
        except Exception:
            # Fallback to original image
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Simple contrast enhancement"""
        try:
            # Stretch histogram
            min_val = np.min(image)
            max_val = np.max(image)
            
            if max_val > min_val:
                enhanced = ((image - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                enhanced = image
            
            return enhanced
            
        except Exception:
            return image
    
    def _simple_smooth(self, image: np.ndarray) -> np.ndarray:
        """Simple image smoothing"""
        try:
            # 3x3 averaging kernel
            kernel = np.ones((3, 3)) / 9
            
            # Simple convolution
            height, width = image.shape
            smoothed = np.zeros_like(image)
            
            for i in range(1, height - 1):
                for j in range(1, width - 1):
                    smoothed[i, j] = np.sum(image[i-1:i+2, j-1:j+2] * kernel)
            
            # Copy borders
            smoothed[0, :] = image[0, :]
            smoothed[-1, :] = image[-1, :]
            smoothed[:, 0] = image[:, 0]
            smoothed[:, -1] = image[:, -1]
            
            return smoothed.astype(np.uint8)
            
        except Exception:
            return image

class MinutiaeExtractor:
    """
    Lightweight minutiae extraction for fingerprint authentication
    
    Extracts ridge endings and bifurcations using memory-efficient algorithms
    suitable for GTX 1050 Ti constraints.
    """
    
    def __init__(self, memory_limit_mb: int = 16):
        """
        Initialize minutiae extractor
        
        Args:
            memory_limit_mb: Memory limit for minutiae extraction
        """
        self.memory_limit_mb = memory_limit_mb
        self.min_minutiae_count = 12
        self.max_minutiae_count = 100
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_minutiae(
        self, 
        fingerprint_image: np.ndarray
    ) -> Tuple[List[Minutiae], Dict[str, Any]]:
        """
        Extract minutiae points from fingerprint image
        
        Args:
            fingerprint_image: Preprocessed fingerprint image
            
        Returns:
            Tuple of (minutiae_list, extraction_metadata)
        """
        try:
            extraction_metadata = {
                "image_shape": fingerprint_image.shape,
                "extraction_method": "ridge_analysis"
            }
            
            # Binarize image
            binary_image = self._binarize_image(fingerprint_image)
            
            # Thin the ridges
            thinned_image = self._thin_ridges(binary_image)
            
            # Extract minutiae points
            minutiae_list = self._find_minutiae_points(thinned_image)
            
            # Filter and validate minutiae
            filtered_minutiae = self._filter_minutiae(minutiae_list, fingerprint_image.shape)
            
            extraction_metadata.update({
                "raw_minutiae_count": len(minutiae_list),
                "filtered_minutiae_count": len(filtered_minutiae),
                "min_required": self.min_minutiae_count
            })
            
            return filtered_minutiae, extraction_metadata
            
        except Exception as e:
            self.logger.error(f"Minutiae extraction error: {str(e)}")
            return [], {"error": str(e)}
    
    def _binarize_image(self, image: np.ndarray) -> np.ndarray:
        """Binarize fingerprint image"""
        try:
            if IMAGE_PROCESSING_AVAILABLE:
                # Otsu's thresholding
                _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return binary
            else:
                # Simple thresholding
                threshold = np.mean(image)
                binary = (image > threshold).astype(np.uint8) * 255
                return binary
                
        except Exception:
            # Fallback binary image
            return (image > 128).astype(np.uint8) * 255
    
    def _thin_ridges(self, binary_image: np.ndarray) -> np.ndarray:
        """Thin ridge lines to single pixel width"""
        try:
            if IMAGE_PROCESSING_AVAILABLE:
                # Morphological thinning
                thinned = morphology.skeletonize(binary_image // 255)
                return (thinned * 255).astype(np.uint8)
            else:
                # Simple thinning approximation
                return self._simple_thin(binary_image)
                
        except Exception:
            return binary_image
    
    def _simple_thin(self, binary_image: np.ndarray) -> np.ndarray:
        """Simple ridge thinning implementation"""
        try:
            # This is a simplified thinning - in production, use proper skeletonization
            kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
            
            # Edge detection approximation
            if IMAGE_PROCESSING_AVAILABLE:
                edges = cv2.Canny(binary_image, 50, 150)
                return edges
            else:
                # Very simple edge detection
                height, width = binary_image.shape
                edges = np.zeros_like(binary_image)
                
                for i in range(1, height - 1):
                    for j in range(1, width - 1):
                        if binary_image[i, j] > 0:
                            # Check if it's an edge pixel
                            neighbors = binary_image[i-1:i+2, j-1:j+2]
                            if np.sum(neighbors == 0) > 0:  # Has background neighbors
                                edges[i, j] = 255
                
                return edges
                
        except Exception:
            return binary_image
    
    def _find_minutiae_points(self, thinned_image: np.ndarray) -> List[Minutiae]:
        """Find minutiae points in thinned image"""
        try:
            minutiae_list = []
            height, width = thinned_image.shape
            
            # Iterate through image to find minutiae
            for i in range(2, height - 2):
                for j in range(2, width - 2):
                    if thinned_image[i, j] > 0:  # Ridge pixel
                        # Analyze 3x3 neighborhood
                        neighborhood = thinned_image[i-1:i+2, j-1:j+2]
                        ridge_count = np.sum(neighborhood > 0) - 1  # Exclude center pixel
                        
                        if ridge_count == 1:
                            # Ridge ending
                            angle = self._calculate_ridge_angle(thinned_image, i, j)
                            quality = self._assess_minutiae_quality(thinned_image, i, j)
                            
                            minutiae = Minutiae(
                                x=j, y=i, angle=angle, type='ending', quality=quality
                            )
                            minutiae_list.append(minutiae)
                            
                        elif ridge_count >= 3:
                            # Bifurcation
                            angle = self._calculate_ridge_angle(thinned_image, i, j)
                            quality = self._assess_minutiae_quality(thinned_image, i, j)
                            
                            minutiae = Minutiae(
                                x=j, y=i, angle=angle, type='bifurcation', quality=quality
                            )
                            minutiae_list.append(minutiae)
            
            return minutiae_list
            
        except Exception as e:
            self.logger.error(f"Minutiae point detection error: {str(e)}")
            return []
    
    def _calculate_ridge_angle(self, image: np.ndarray, y: int, x: int) -> float:
        """Calculate ridge direction at given point"""
        try:
            # Simple gradient-based angle estimation
            if IMAGE_PROCESSING_AVAILABLE:
                # Use Sobel operators
                grad_x = cv2.Sobel(image[y-2:y+3, x-2:x+3], cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(image[y-2:y+3, x-2:x+3], cv2.CV_64F, 0, 1, ksize=3)
                angle = np.arctan2(np.mean(grad_y), np.mean(grad_x))
            else:
                # Simple finite difference
                height, width = image.shape
                if x > 0 and x < width - 1 and y > 0 and y < height - 1:
                    dx = float(image[y, x+1]) - float(image[y, x-1])
                    dy = float(image[y+1, x]) - float(image[y-1, x])
                    angle = np.arctan2(dy, dx)
                else:
                    angle = 0.0
            
            return float(angle)
            
        except Exception:
            return 0.0
    
    def _assess_minutiae_quality(self, image: np.ndarray, y: int, x: int) -> float:
        """Assess quality of minutiae point"""
        try:
            # Quality based on local contrast and clarity
            height, width = image.shape
            
            if y < 5 or y >= height - 5 or x < 5 or x >= width - 5:
                return 0.3  # Low quality for edge minutiae
            
            # Analyze local region
            local_region = image[y-5:y+6, x-5:x+6]
            
            # Quality factors
            contrast = np.std(local_region)
            clarity = np.sum(local_region > 0) / local_region.size
            
            # Combine quality factors
            quality = min(1.0, (contrast / 64.0) * clarity)
            
            return max(0.0, quality)
            
        except Exception:
            return 0.5  # Default quality
    
    def _filter_minutiae(
        self, 
        minutiae_list: List[Minutiae], 
        image_shape: Tuple[int, int]
    ) -> List[Minutiae]:
        """Filter and validate minutiae points"""
        try:
            # Filter by quality
            quality_threshold = 0.3
            filtered = [m for m in minutiae_list if m.quality >= quality_threshold]
            
            # Remove minutiae too close to image borders
            border_margin = 10
            height, width = image_shape
            
            filtered = [
                m for m in filtered 
                if (border_margin <= m.x < width - border_margin and 
                    border_margin <= m.y < height - border_margin)
            ]
            
            # Remove duplicate minutiae (too close together)
            min_distance = 10
            unique_minutiae = []
            
            for minutiae in filtered:
                is_duplicate = False
                for existing in unique_minutiae:
                    distance = euclidean((minutiae.x, minutiae.y), (existing.x, existing.y))
                    if distance < min_distance:
                        # Keep the higher quality one
                        if minutiae.quality > existing.quality:
                            unique_minutiae.remove(existing)
                        else:
                            is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_minutiae.append(minutiae)
            
            # Sort by quality and limit count
            unique_minutiae.sort(key=lambda m: m.quality, reverse=True)
            
            return unique_minutiae[:self.max_minutiae_count]
            
        except Exception as e:
            self.logger.error(f"Minutiae filtering error: {str(e)}")
            return minutiae_list

class FingerprintAuthenticator(BiometricAuthenticationBase):
    """
    Fingerprint authentication provider optimized for GTX 1050 Ti hardware
    
    Provides fingerprint recognition authentication using lightweight algorithms
    and memory-efficient processing suitable for consumer GPU constraints.
    
    Features:
    - Minutiae-based matching
    - Quality assessment and filtering
    - Memory-optimized preprocessing
    - Real-time performance monitoring
    - Hardware-aware processing pipelines
    """
    
    def __init__(
        self,
        config: Dict[str, Any] = None,
        memory_limit_mb: int = 32,
        enable_quality_check: bool = True,
        enable_logging: bool = True
    ):
        """
        Initialize fingerprint authenticator
        
        Args:
            config: Fingerprint authentication configuration
            memory_limit_mb: Memory limit for fingerprint processing
            enable_quality_check: Enable fingerprint quality assessment
            enable_logging: Enable detailed logging
        """
        super().__init__(config, memory_limit_mb, enable_logging=enable_logging)
        
        self.enable_quality_check = enable_quality_check
        
        # Initialize components
        self.preprocessor = FingerprintPreprocessor(memory_limit_mb // 2)
        self.minutiae_extractor = MinutiaeExtractor(memory_limit_mb // 2)
        self.quality_assessor = FingerprintQualityAssessment()
        
        # Fingerprint templates storage
        self._fingerprint_templates: Dict[str, Dict[str, Any]] = {}
        
        # Authentication thresholds
        self.similarity_threshold = config.get('similarity_threshold', 0.90) if config else 0.90
        self.min_minutiae_match = config.get('min_minutiae_match', 8) if config else 8
        self.max_minutiae_distance = config.get('max_minutiae_distance', 20) if config else 20
        
        if self.enable_logging:
            self.logger.info(f"Initialized FingerprintAuthenticator with {memory_limit_mb}MB memory limit")
            self.logger.info(f"Similarity threshold: {self.similarity_threshold}")
            self.logger.info(f"Quality check enabled: {enable_quality_check}")
    
    @property
    def authentication_type(self) -> AuthenticationType:
        """Return fingerprint authentication type"""
        return AuthenticationType.FINGERPRINT
    
    async def assess_quality(self, fingerprint_data: Any) -> Tuple[float, Dict[str, Any]]:
        """
        Assess quality of fingerprint data
        
        Args:
            fingerprint_data: Raw fingerprint image data
            
        Returns:
            Tuple of (quality_score, quality_metadata)
        """
        try:
            # Convert to numpy array if needed
            if isinstance(fingerprint_data, str):
                # File path provided
                if IMAGE_PROCESSING_AVAILABLE:
                    fingerprint_image = cv2.imread(fingerprint_data, cv2.IMREAD_GRAYSCALE)
                else:
                    # Simulated fingerprint image
                    fingerprint_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
            elif isinstance(fingerprint_data, bytes):
                # Raw image bytes
                if IMAGE_PROCESSING_AVAILABLE:
                    nparr = np.frombuffer(fingerprint_data, np.uint8)
                    fingerprint_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                else:
                    # Simulated conversion
                    fingerprint_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
            else:
                # Already numpy array
                fingerprint_image = np.array(fingerprint_data, dtype=np.uint8)
            
            # Assess image quality
            quality_score, quality_metadata = self.quality_assessor.assess_image_quality(fingerprint_image)
            
            return quality_score, quality_metadata
            
        except Exception as e:
            self.logger.error(f"Fingerprint quality assessment error: {str(e)}")
            return 0.0, {"error": str(e)}
    
    async def process_biometric_data(
        self,
        biometric_data: Any,
        user_id: str = None
    ) -> Tuple[Any, float]:
        """
        Process raw fingerprint data into fingerprint template and confidence score
        
        Args:
            biometric_data: Raw fingerprint image data
            user_id: Optional user ID for context
            
        Returns:
            Tuple of (fingerprint_template, processing_confidence)
        """
        try:
            # Convert to numpy array if needed
            if isinstance(biometric_data, str):
                # File path provided
                if IMAGE_PROCESSING_AVAILABLE:
                    fingerprint_image = cv2.imread(biometric_data, cv2.IMREAD_GRAYSCALE)
                else:
                    # Simulated fingerprint image
                    fingerprint_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
            elif isinstance(biometric_data, bytes):
                # Raw image bytes
                if IMAGE_PROCESSING_AVAILABLE:
                    nparr = np.frombuffer(biometric_data, np.uint8)
                    fingerprint_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                else:
                    # Simulated conversion
                    fingerprint_image = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
            else:
                # Already numpy array
                fingerprint_image = np.array(biometric_data, dtype=np.uint8)
            
            # Assess quality if enabled
            quality_score = 1.0
            quality_metadata = {}
            
            if self.enable_quality_check:
                quality_score, quality_metadata = await self.assess_quality(fingerprint_image)
            
            # Preprocess fingerprint image
            processed_image, preprocessing_metadata = self.preprocessor.preprocess_fingerprint(fingerprint_image)
            
            # Extract minutiae
            minutiae_list, extraction_metadata = self.minutiae_extractor.extract_minutiae(processed_image)
            
            # Create fingerprint template
            fingerprint_template = {
                "minutiae": [
                    {
                        "x": m.x,
                        "y": m.y,
                        "angle": m.angle,
                        "type": m.type,
                        "quality": m.quality
                    }
                    for m in minutiae_list
                ],
                "image_shape": processed_image.shape,
                "preprocessing": preprocessing_metadata,
                "extraction": extraction_metadata,
                "quality": quality_metadata,
                "creation_timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "template_version": "1.0"
            }
            
            # Calculate processing confidence
            processing_confidence = quality_score
            
            # Bonus for successful minutiae extraction
            if len(minutiae_list) >= self.minutiae_extractor.min_minutiae_count:
                processing_confidence = min(1.0, processing_confidence + 0.1)
            else:
                processing_confidence *= 0.5  # Penalty for insufficient minutiae
            
            # Bonus for good preprocessing
            if "error" not in preprocessing_metadata:
                processing_confidence = min(1.0, processing_confidence + 0.05)
            
            return fingerprint_template, processing_confidence
            
        except Exception as e:
            self.logger.error(f"Fingerprint data processing error: {str(e)}")
            # Return fallback template
            fallback_template = {
                "error": str(e),
                "fallback": True,
                "creation_timestamp": datetime.utcnow().isoformat()
            }
            return fallback_template, 0.0
    
    async def compare_biometric_templates(
        self,
        template1: Any,
        template2: Any
    ) -> float:
        """
        Compare two fingerprint templates and return similarity score
        
        Args:
            template1: First fingerprint template
            template2: Second fingerprint template
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Extract minutiae from templates
            if isinstance(template1, dict) and isinstance(template2, dict):
                minutiae1 = template1.get("minutiae", [])
                minutiae2 = template2.get("minutiae", [])
                
                if "error" in template1 or "error" in template2:
                    return 0.0  # Cannot compare templates with errors
                
                if not minutiae1 or not minutiae2:
                    return 0.0  # No minutiae to compare
                
                # Perform minutiae matching
                similarity_score = self._match_minutiae(minutiae1, minutiae2)
                
                return max(0.0, min(1.0, similarity_score))
            else:
                return 0.0  # Invalid template format
                
        except Exception as e:
            self.logger.error(f"Fingerprint template comparison error: {str(e)}")
            return 0.0
    
    def _match_minutiae(
        self, 
        minutiae1: List[Dict[str, Any]], 
        minutiae2: List[Dict[str, Any]]
    ) -> float:
        """
        Match minutiae between two fingerprint templates
        
        Args:
            minutiae1: Minutiae from first template
            minutiae2: Minutiae from second template
            
        Returns:
            Matching score between 0.0 and 1.0
        """
        try:
            if not minutiae1 or not minutiae2:
                return 0.0
            
            matched_pairs = 0
            total_comparisons = 0
            
            # Compare each minutiae in template1 with minutiae in template2
            for m1 in minutiae1:
                best_match_score = 0.0
                
                for m2 in minutiae2:
                    # Calculate spatial distance
                    spatial_distance = euclidean((m1["x"], m1["y"]), (m2["x"], m2["y"]))
                    
                    if spatial_distance <= self.max_minutiae_distance:
                        # Calculate angle difference
                        angle_diff = abs(m1["angle"] - m2["angle"])
                        angle_diff = min(angle_diff, 2 * np.pi - angle_diff)  # Wrap around
                        
                        # Type match bonus
                        type_match = 1.0 if m1["type"] == m2["type"] else 0.5
                        
                        # Quality factor
                        quality_factor = (m1["quality"] + m2["quality"]) / 2.0
                        
                        # Calculate match score
                        spatial_score = max(0.0, 1.0 - spatial_distance / self.max_minutiae_distance)
                        angle_score = max(0.0, 1.0 - angle_diff / (np.pi / 4))  # Within 45 degrees
                        
                        match_score = spatial_score * angle_score * type_match * quality_factor
                        best_match_score = max(best_match_score, match_score)
                
                if best_match_score > 0.7:  # Threshold for considering a match
                    matched_pairs += 1
                
                total_comparisons += 1
            
            # Calculate overall similarity
            if total_comparisons == 0:
                return 0.0
            
            match_ratio = matched_pairs / total_comparisons
            
            # Require minimum number of matches
            if matched_pairs < self.min_minutiae_match:
                match_ratio *= 0.5  # Penalty for insufficient matches
            
            # Bonus for higher number of total minutiae
            minutiae_bonus = min(0.1, len(minutiae1) / 50.0 + len(minutiae2) / 50.0)
            
            similarity_score = min(1.0, match_ratio + minutiae_bonus)
            
            return similarity_score
            
        except Exception as e:
            self.logger.error(f"Minutiae matching error: {str(e)}")
            return 0.0
    
    async def authenticate(
        self,
        user_id: str,
        credentials: Dict[str, Any],
        **kwargs
    ) -> AuthenticationResult:
        """
        Perform fingerprint authentication
        
        Args:
            user_id: User identifier
            credentials: Dictionary containing fingerprint data
                        Format: {
                            "biometric_data": <fingerprint_image_data>,
                            "template_type": "fingerprint"
                        }
            **kwargs: Additional authentication parameters
            
        Returns:
            AuthenticationResult with fingerprint authentication status
        """
        return await self.authenticate_biometric(
            user_id,
            credentials.get("biometric_data"),
            credentials.get("template_type", "fingerprint")
        )
    
    async def validate_session(self, session_id: str) -> AuthenticationResult:
        """Validate fingerprint authentication session"""
        return await super().validate_session(session_id)
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate fingerprint authentication session"""
        return await super().invalidate_session(session_id)
    
    def store_fingerprint_template(self, user_id: str, fingerprint_template: Dict[str, Any]):
        """
        Store fingerprint template for user
        
        Args:
            user_id: User identifier
            fingerprint_template: Processed fingerprint template
        """
        self.store_biometric_template(user_id, fingerprint_template, "fingerprint")
        self._fingerprint_templates[user_id] = fingerprint_template
        
        if self.enable_logging:
            self.logger.info(f"Stored fingerprint template for user {user_id}")
    
    def get_fingerprint_template(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve fingerprint template for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Fingerprint template if found, None otherwise
        """
        return self._fingerprint_templates.get(user_id)
    
    def get_fingerprint_performance_metrics(self) -> Dict[str, Any]:
        """
        Get fingerprint authentication performance metrics
        
        Returns:
            Dictionary containing fingerprint-specific performance metrics
        """
        base_metrics = self.get_performance_metrics()
        
        fingerprint_metrics = {
            "fingerprint_authenticator": base_metrics,
            "fingerprint_templates_stored": len(self._fingerprint_templates),
            "quality_check_enabled": self.enable_quality_check,
            "similarity_threshold": self.similarity_threshold,
            "min_minutiae_match": self.min_minutiae_match,
            "max_minutiae_distance": self.max_minutiae_distance,
            "minutiae_extraction": {
                "min_minutiae_count": self.minutiae_extractor.min_minutiae_count,
                "max_minutiae_count": self.minutiae_extractor.max_minutiae_count
            },
            "hardware_optimization": {
                "memory_limit_mb": self.memory_limit_mb,
                "target_hardware": "GTX 1050 Ti",
                "image_processing_available": IMAGE_PROCESSING_AVAILABLE
            }
        }
        
        return fingerprint_metrics
