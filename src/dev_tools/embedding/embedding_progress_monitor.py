#!/usr/bin/env python3
"""
ImpressionCore Embedding Progress Monitor
Real-time monitoring of the ultimate universal embedder
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime

def monitor_embedding_progress():
    """Monitor the embedding progress in real-time"""
    
    embeddings_dir = Path("src/embeddings")
    
    print("🔍 ImpressionCore Embedding Progress Monitor")
    print("=" * 50)
    print(f"📅 Started monitoring at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    last_file_count = 0
    start_time = time.time()
    
    while True:
        try:
            # Count embedding files
            embedding_files = list(embeddings_dir.glob("*_embeddings.npy"))
            metadata_files = list(embeddings_dir.glob("*_metadata.json"))
            
            # Get total files from metadata
            total_embedded = 0
            modalities_found = []
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    total_embedded += len(metadata)
                    modality = metadata_file.stem.replace('_metadata', '')
                    modalities_found.append(modality)
                except:
                    continue
            
            # Check for summary files
            summary_files = list(embeddings_dir.glob("*_summary_*.json"))
            latest_summary = None
            if summary_files:
                latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
            
            # Display current status
            current_time = datetime.now().strftime('%H:%M:%S')
            elapsed = time.time() - start_time
            
            print(f"\\r🕐 {current_time} | 📊 Files embedded: {total_embedded:,} | 🎯 Modalities: {len(modalities_found)} | ⏱️ {elapsed/60:.1f}min", end="", flush=True)
            
            # Check if process completed
            if latest_summary:
                try:
                    with open(latest_summary, 'r') as f:
                        summary = json.load(f)
                    if summary.get('embedding_complete', False):
                        print("\\n\\n🎉 EMBEDDING COMPLETED!")
                        print(f"✅ Total files processed: {summary['files_processed']:,}")
                        print(f"🎯 Modalities: {summary['total_modalities']}")
                        print(f"⏱️ Total time: {summary['processing_time_formatted']}")
                        print(f"📋 Summary: {latest_summary}")
                        break
                except:
                    pass
            
            # Check for significant progress
            if total_embedded > last_file_count + 10000:
                print(f"\\n📈 Progress milestone: {total_embedded:,} files embedded!")
                last_file_count = total_embedded
            
            time.sleep(30)  # Check every 30 seconds
        
        except KeyboardInterrupt:
            print(f"\\n\\n⏹️ Monitoring stopped by user")
            print(f"📊 Last seen: {total_embedded:,} files embedded across {len(modalities_found)} modalities")
            break
        except Exception as e:
            print(f"\\n❌ Monitor error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_embedding_progress()
