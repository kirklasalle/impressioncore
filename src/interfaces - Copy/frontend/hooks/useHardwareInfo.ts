import { useState, useEffect } from 'react';

interface HardwareInfo {
  vramGB: number;
  deviceName: string;
  isLowVram: boolean;
  cudaVersion?: string;
  recommendedSettings: {
    batchSize: number;
    maxHiddenSize: number;
    maxLayers: number;
    shouldUseCheckpointing: boolean;
    shouldUseFp16: boolean;
    maxSequenceLength: number;
  };
}

export function useHardwareInfo() {
  const [hardwareInfo, setHardwareInfo] = useState<HardwareInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHardwareInfo() {
      try {
        const response = await fetch('/api/v1/hardware/info');
        if (!response.ok) {
          throw new Error('Failed to fetch hardware information');
        }

        const data = await response.json();
        
        // Extract relevant hardware information
        const { system_info, optimization_settings } = data;
        const gpuInfo = system_info.devices?.[0] || {};
        
        // Calculate recommended settings based on hardware
        const vramGB = gpuInfo.total_memory_gb || 0;
        const isLowVram = vramGB <= 4.0;
        
        // Conservative settings for 4GB VRAM cards like 1050 Ti
        const recommendedSettings = {
          batchSize: isLowVram ? 1 : Math.floor(vramGB / 4),
          maxHiddenSize: isLowVram ? 768 : 1024,
          maxLayers: isLowVram ? 12 : 24,
          shouldUseCheckpointing: isLowVram,
          shouldUseFp16: isLowVram,
          maxSequenceLength: isLowVram ? 1024 : 2048,
        };

        setHardwareInfo({
          vramGB,
          deviceName: gpuInfo.name || 'Unknown GPU',
          isLowVram,
          cudaVersion: system_info.cuda_version,
          recommendedSettings,
        });
      } catch (err) {
        setError(err.message);
        // Fallback to conservative settings if hardware detection fails
        setHardwareInfo({
          vramGB: 4,
          deviceName: 'Unknown GPU',
          isLowVram: true,
          recommendedSettings: {
            batchSize: 1,
            maxHiddenSize: 768,
            maxLayers: 12,
            shouldUseCheckpointing: true,
            shouldUseFp16: true,
            maxSequenceLength: 1024,
          },
        });
      } finally {
        setIsLoading(false);
      }
    }

    fetchHardwareInfo();
  }, []);

  // Polling for hardware status updates (memory usage, etc.)
  useEffect(() => {
    if (!hardwareInfo) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/v1/status');
        if (!response.ok) return;

        const data = await response.json();
        const memStats = data.system_resources?.memory;
        
        if (memStats) {
          setHardwareInfo(prev => ({
            ...prev!,
            currentVramUsage: memStats.cuda_allocated_gb || 0,
            availableVram: prev!.vramGB - (memStats.cuda_reserved_gb || 0),
          }));
        }
      } catch (err) {
        // Silent fail for polling - don't update if error
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [hardwareInfo]);

  return { hardwareInfo, isLoading, error };
}