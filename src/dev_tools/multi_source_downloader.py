#!/usr/bin/env python3
"""
Multi-Source Dataset Downloader with Fallbacks for ImpressionCore-B1
===================================================================
Downloads missing modalities from multiple sources with fallback options
"""

import os
import requests
import zipfile
import json
from pathlib import Path
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiSourceDownloader:
    def __init__(self, data_dir="src/data/real_datasets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Define multiple sources for each modality with fallbacks
        self.sources = {
            'documents': [
                {
                    'name': 'ArXiv Papers Sample',
                    'url': 'https://www.kaggle.com/datasets/Cornell-University/arxiv',
                    'type': 'manual',
                    'description': 'Scientific papers from arXiv (requires manual download from Kaggle)',
                    'format': 'json + metadata'
                },
                {
                    'name': 'SEC EDGAR Filings',
                    'url': 'https://www.sec.gov/data.json',
                    'type': 'api',
                    'description': 'Government financial documents',
                    'format': 'json + html'
                },
                {
                    'name': 'Project Gutenberg Sample',
                    'url': 'https://www.gutenberg.org/files/74/74-0.txt',
                    'type': 'direct',
                    'description': 'Free text documents',
                    'format': 'txt'
                }
            ],
            
            'point_clouds': [
                {
                    'name': 'Stanford 3D Scanning Repository',
                    'url': 'http://graphics.stanford.edu/data/3Dscanrep/',
                    'type': 'manual',
                    'description': 'Original Stanford PLY files (requires manual download)',
                    'format': 'ply'
                },
                {
                    'name': 'Point Cloud Library Samples',
                    'url': 'https://sourceforge.net/projects/pointclouds/files/PCD%20datasets/',
                    'type': 'manual',
                    'description': 'PCL sample datasets',
                    'format': 'pcd'
                },
                {
                    'name': 'Sample Point Cloud Generation',
                    'url': 'synthetic',
                    'type': 'generate',
                    'description': 'Generate sample point clouds',
                    'format': 'ply'
                }
            ],
            
            '3d_models': [
                {
                    'name': 'Creazilla 3D Models',
                    'url': 'https://creazilla.com/sections/3d-model',
                    'type': 'manual',
                    'description': '36,000+ free 3D models (requires manual download)',
                    'format': 'obj, fbx, gltf'
                },
                {
                    'name': 'Sketchfab Free Models',
                    'url': 'https://sketchfab.com/3d-models?features=downloadable&sort_by=-likeCount',
                    'type': 'manual',
                    'description': 'Free downloadable 3D models',
                    'format': 'gltf, obj, fbx'
                },
                {
                    'name': 'Open3dModel',
                    'url': 'https://open3dmodel.com/',
                    'type': 'manual',
                    'description': '162,000+ free 3D models',
                    'format': 'multiple'
                }
            ],
            
            'geospatial': [
                {
                    'name': 'Natural Earth Data',
                    'url': 'https://www.naturalearthdata.com/downloads/',
                    'type': 'manual',
                    'description': 'Free vector and raster map data',
                    'format': 'shp, geojson'
                },
                {
                    'name': 'World Boundaries GeoJSON',
                    'url': 'https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson',
                    'type': 'direct',
                    'description': 'World countries boundaries',
                    'format': 'geojson'
                },
                {
                    'name': 'OpenStreetMap Data',
                    'url': 'https://download.geofabrik.de/',
                    'type': 'manual',
                    'description': 'OSM extracts worldwide',
                    'format': 'osm, shp'
                }
            ],
            
            'medical_imaging': [
                {
                    'name': 'NIH Cancer Imaging Archive',
                    'url': 'https://www.cancerimagingarchive.net/',
                    'type': 'manual',
                    'description': 'Thousands of medical images (requires registration)',
                    'format': 'dicom'
                },
                {
                    'name': 'MedPix Database',
                    'url': 'https://medpix.nlm.nih.gov/home',
                    'type': 'manual',
                    'description': '59,000+ medical images (requires registration)',
                    'format': 'dicom, jpg'
                },
                {
                    'name': '3DICOM Sample Library',
                    'url': 'https://3dicomviewer.com/dicom-library/',
                    'type': 'manual',
                    'description': 'Sample DICOM files',
                    'format': 'dicom, nii'
                }
            ],
            
            'audio_transcripts': [
                {
                    'name': 'Common Voice with Transcripts',
                    'url': 'https://commonvoice.mozilla.org/en/datasets',
                    'type': 'manual',
                    'description': 'Audio with validated transcripts',
                    'format': 'mp3 + tsv'
                },
                {
                    'name': 'LibriSpeech',
                    'url': 'https://www.openslr.org/12/',
                    'type': 'manual',
                    'description': 'Read English speech with transcripts',
                    'format': 'flac + txt'
                }
            ],
            
            'captioned_videos': [
                {
                    'name': 'YouTube-8M',
                    'url': 'https://research.google.com/youtube8m/',
                    'type': 'manual',
                    'description': 'Video understanding dataset with labels',
                    'format': 'video + json'
                },
                {
                    'name': 'MSR-VTT',
                    'url': 'https://www.microsoft.com/en-us/research/publication/msr-vtt-a-large-video-description-dataset-for-bridging-video-and-language/',
                    'type': 'manual',
                    'description': 'Video to text dataset',
                    'format': 'video + json'
                }
            ]
        }

    def download_direct_files(self):
        """Download files that can be downloaded directly"""
        logger.info("🌐 Downloading directly accessible files...")
        
        downloads = []
        
        # World boundaries GeoJSON
        try:
            geo_dir = self.data_dir / "geospatial"
            geo_dir.mkdir(exist_ok=True)
            
            url = "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = geo_dir / "world_boundaries.geojson"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            downloads.append(str(file_path))
            logger.info(f"✅ Downloaded: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download world boundaries: {e}")
        
        # Project Gutenberg sample
        try:
            docs_dir = self.data_dir / "documents"
            docs_dir.mkdir(exist_ok=True)
            
            url = "https://www.gutenberg.org/files/74/74-0.txt"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = docs_dir / "gutenberg_sample.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            downloads.append(str(file_path))
            logger.info(f"✅ Downloaded: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download Gutenberg sample: {e}")
        
        # US States GeoJSON
        try:
            url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = geo_dir / "us_states.geojson"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            downloads.append(str(file_path))
            logger.info(f"✅ Downloaded: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to download US states: {e}")
        
        return downloads

    def generate_synthetic_point_clouds(self):
        """Generate sample point cloud files"""
        logger.info("🎯 Generating synthetic point clouds...")
        
        pc_dir = self.data_dir / "point_clouds"
        pc_dir.mkdir(exist_ok=True)
        
        try:
            import numpy as np
            
            # Generate different types of point clouds
            point_clouds = [
                ("sphere", self._generate_sphere_points(1000)),
                ("cube", self._generate_cube_points(1000)),
                ("plane", self._generate_plane_points(1000)),
                ("random", np.random.randn(1000, 3))
            ]
            
            generated_files = []
            for name, points in point_clouds:
                file_path = pc_dir / f"synthetic_{name}.ply"
                self._save_ply_file(points, file_path)
                generated_files.append(str(file_path))
                logger.info(f"✅ Generated: {file_path}")
            
            return generated_files
            
        except ImportError:
            logger.error("❌ NumPy required for point cloud generation")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to generate point clouds: {e}")
            return []

    def _generate_sphere_points(self, n_points):
        """Generate points on a sphere surface"""
        import numpy as np
        
        phi = np.random.uniform(0, 2*np.pi, n_points)
        costheta = np.random.uniform(-1, 1, n_points)
        u = np.random.uniform(0, 1, n_points)
        
        theta = np.arccos(costheta)
        r = u**(1/3)
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        
        return np.column_stack([x, y, z])

    def _generate_cube_points(self, n_points):
        """Generate points in a cube"""
        import numpy as np
        return np.random.uniform(-1, 1, (n_points, 3))

    def _generate_plane_points(self, n_points):
        """Generate points on a plane with some noise"""
        import numpy as np
        
        x = np.random.uniform(-1, 1, n_points)
        y = np.random.uniform(-1, 1, n_points)
        z = 0.1 * np.random.randn(n_points)  # Small noise in z
        
        return np.column_stack([x, y, z])

    def _save_ply_file(self, points, file_path):
        """Save points as PLY file"""
        with open(file_path, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("end_header\n")
            
            for point in points:
                f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f}\n")

    def generate_sample_3d_models(self):
        """Generate sample 3D model files"""
        logger.info("🎯 Generating sample 3D models...")
        
        models_dir = self.data_dir / "3d_models"
        models_dir.mkdir(exist_ok=True)
        
        try:
            # Generate simple OBJ files
            obj_content = """# Simple cube
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
v  1.0  1.0 -1.0
v -1.0  1.0 -1.0
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0  1.0

f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 5 1 4 8
"""
            
            cube_file = models_dir / "sample_cube.obj"
            with open(cube_file, 'w') as f:
                f.write(obj_content)
            
            # Generate simple glTF
            gltf_content = {
                "asset": {"version": "2.0"},
                "scene": 0,
                "scenes": [{"nodes": [0]}],
                "nodes": [{"mesh": 0}],
                "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
                "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3"}],
                "bufferViews": [{"buffer": 0, "byteLength": 36}],
                "buffers": [{"byteLength": 36}]
            }
            
            gltf_file = models_dir / "sample_triangle.gltf"
            with open(gltf_file, 'w') as f:
                json.dump(gltf_content, f, indent=2)
            
            generated_files = [str(cube_file), str(gltf_file)]
            
            for file_path in generated_files:
                logger.info(f"✅ Generated: {file_path}")
            
            return generated_files
            
        except Exception as e:
            logger.error(f"❌ Failed to generate 3D models: {e}")
            return []

    def create_instruction_files(self):
        """Create instruction files for manual downloads"""
        logger.info("📋 Creating instruction files for manual downloads...")
        
        instructions = {}
        
        for modality, sources in self.sources.items():
            modality_dir = self.data_dir / modality
            modality_dir.mkdir(exist_ok=True)
            
            readme_content = f"# {modality.replace('_', ' ').title()} Dataset Sources\n\n"
            readme_content += f"This directory contains {modality} data for ImpressionCore training.\n\n"
            readme_content += "## Available Sources (with fallbacks):\n\n"
            
            for i, source in enumerate(sources, 1):
                readme_content += f"### {i}. {source['name']} ({'Primary' if i == 1 else 'Fallback'})\n"
                readme_content += f"- **URL**: {source['url']}\n"
                readme_content += f"- **Type**: {source['type']}\n"
                readme_content += f"- **Format**: {source['format']}\n"
                readme_content += f"- **Description**: {source['description']}\n\n"
                
                if source['type'] == 'manual':
                    readme_content += f"  **Instructions**: Visit the URL and manually download relevant files to this directory.\n\n"
                elif source['type'] == 'api':
                    readme_content += f"  **Instructions**: Use API or programmatic access to download data.\n\n"
            
            readme_content += "## Usage Notes:\n"
            readme_content += "- Try sources in order (primary first, then fallbacks)\n"
            readme_content += "- Ensure downloaded files match the expected formats\n"
            readme_content += "- Check file integrity after download\n"
            
            readme_file = modality_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            instructions[modality] = str(readme_file)
            logger.info(f"📝 Created instructions: {readme_file}")
        
        return instructions

    def run_comprehensive_download(self):
        """Run the complete download process with fallbacks"""
        logger.info("🚀 Starting comprehensive multi-source download...")
        
        results = {
            'direct_downloads': [],
            'generated_files': [],
            'instruction_files': [],
            'summary': {}
        }
        
        # Download directly accessible files
        results['direct_downloads'] = self.download_direct_files()
        
        # Generate synthetic data where possible
        results['generated_files'].extend(self.generate_synthetic_point_clouds())
        results['generated_files'].extend(self.generate_sample_3d_models())
        
        # Create instruction files for manual downloads
        results['instruction_files'] = list(self.create_instruction_files().values())
        
        # Generate summary
        total_files = len(results['direct_downloads']) + len(results['generated_files'])
        results['summary'] = {
            'total_downloaded': len(results['direct_downloads']),
            'total_generated': len(results['generated_files']),
            'total_instruction_files': len(results['instruction_files']),
            'total_files_created': total_files,
            'modalities_covered': len(self.sources)
        }
        
        logger.info("📊 Download Summary:")
        logger.info(f"  📥 Direct downloads: {results['summary']['total_downloaded']}")
        logger.info(f"  🎯 Generated files: {results['summary']['total_generated']}")
        logger.info(f"  📋 Instruction files: {results['summary']['total_instruction_files']}")
        logger.info(f"  🎯 Total files created: {results['summary']['total_files_created']}")
        logger.info(f"  🔧 Modalities covered: {results['summary']['modalities_covered']}")
        
        return results

def main():
    """Main execution function"""
    print("🌟 Multi-Source Dataset Downloader for ImpressionCore-B1")
    print("=" * 60)
    
    downloader = MultiSourceDownloader()
    results = downloader.run_comprehensive_download()
    
    print("\n✅ Download process completed!")
    print(f"📁 Files created in: {downloader.data_dir}")
    print(f"🎯 Ready to embed {results['summary']['total_files_created']} new files")

if __name__ == "__main__":
    main()
