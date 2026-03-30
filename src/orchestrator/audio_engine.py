import threading
import time
from typing import Any

import numpy as np
import sounddevice as sd

from src.orchestrator.system_logger import log_event


def gcc_phat(sig, refsig, fs=48000, max_tau=None, interp=1):
    '''
    Generalized Cross Correlation with Phase Transform
    '''
    # ensure reasonable size
    n = sig.shape[0] + refsig.shape[0]

    # Generalized Cross Correlation Phase Transform
    SIG = np.fft.rfft(sig, n=n)
    REFSIG = np.fft.rfft(refsig, n=n)
    R = SIG * np.conj(REFSIG)

    cc = np.fft.irfft(R / np.abs(R), n=(interp * n))

    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)

    cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))

    # find max cross correlation index
    shift = np.argmax(np.abs(cc)) - max_shift

    tau = shift / float(interp * fs)
    return tau, cc

class AudioEngine:
    def __init__(self):
        self.streams = {}
        self.active = False
        self.devices = self._scan_devices()
        self.telemetry = {"angle": 0, "vad": False, "rms": [], "status": "IDLE"}
        self.lock = threading.RLock() # Reentrant lock for safety
        self.active = False
        self.sensitivity = 0.5 # Default 50%
        self.last_angle = 0.0

        # Spatial Configuration for PS Eye
        self.MIC_DISTANCE_4CH = 0.06
        self.SOUND_SPEED = 343.0
        self.noise_floor = 0.005 # Baseline

    def verify_device_health(self, index: int, duration: float = 0.3) -> dict[str, Any]:
        """Performs a transient capture to verify real-time data flow."""
        try:
            device = next((d for d in self.devices if d["index"] == index), None)
            if not device:
                return {"status": "MISSING", "rms": 0}

            # Simple non-blocking capture test
            test_data = sd.rec(int(device['rate'] * duration),
                              samplerate=device['rate'],
                              channels=device['channels'],
                              device=index,
                              blocking=True)

            rms = np.sqrt(np.mean(test_data**2))
            return {
                "status": "HEALTHY" if rms > 1e-5 else "SILENT",
                "rms": float(rms),
                "channels": device['channels']
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "rms": 0}

    def refresh_devices(self):
        """Force re-scan of audio devices."""
        self.devices = self._scan_devices()
        # Update devices in telemetry immediately
        with self.lock:
            # Preserve stream status, just update devices
            pass
        return self.devices

    def _scan_devices(self):
        """Scans for Audio Devices using SoundDevice."""
        print("[AudioEngine] Scanning devices via PortAudio/WASAPI...")
        devs = []
        try:
            raw = sd.query_devices()
        except Exception:
            return []

        for i, d in enumerate(raw):
            name = d.get('name')
            channels = d.get('max_input_channels')

            if channels <= 0:
                continue

            is_ps_eye = False
            if channels == 4 or "camera" in name.lower() or "microphone (usb camera" in name.lower():
                is_ps_eye = True

            devs.append({
                "index": i,
                "name": name,
                "channels": channels,
                "rate": int(d.get('default_samplerate')),
                "is_eye": is_ps_eye
            })

            if is_ps_eye:
                print(f"  [FOUND] PS Eye Candidate: {name} ({channels} ch) [Index {i}]")

        return devs

    def _process_loop(self):
        """Background loop for Spatial Analysis."""
        while self.active:
            try:
                if hasattr(self, 'latest_chunk') and self.latest_chunk is not None:
                    data = self.latest_chunk

                    # 1. Adaptive VAD
                    rms = np.sqrt(np.mean(data**2))

                    # Slowly adapt noise floor (lowest energy seen)
                    self.noise_floor = min(self.noise_floor * 1.05, max(rms, 0.001))

                    # Speech detection: must be 2.5x above floor
                    is_speech = rms > (self.noise_floor * 2.5)

                    # 2. DoA
                    angle = 0
                    if is_speech and self.current_channels == 4:
                        try:
                            sig1 = data[:, 0]
                            sig2 = data[:, 3]
                            tau, _ = gcc_phat(sig1, sig2, fs=self.current_rate)
                            max_tau = self.MIC_DISTANCE_4CH / self.SOUND_SPEED
                            tau = max(min(tau, max_tau), -max_tau)
                            theta = np.arcsin(tau * self.SOUND_SPEED / self.MIC_DISTANCE_4CH)
                            angle = np.degrees(theta)
                        except Exception:
                             angle = 0

                    try:
                        # Smoothing (Exponential Moving Average)
                        # Sensitivity 0.0 = Heavy Smoothing (Slow)
                        # Sensitivity 1.0 = No Smoothing (Fast)
                        alpha = 0.1 + (self.sensitivity * 0.9)
                        self.last_angle = (alpha * angle) + ((1 - alpha) * self.last_angle)

                        with self.lock:
                            self.telemetry = {
                                "vad": bool(is_speech),
                                "rms": [float(np.sqrt(np.mean(data[:, c]**2))) for c in range(data.shape[1])],
                                "angle": float(self.last_angle), # Use smoothed angle
                                "raw_angle": float(angle),
                                "status": "LISTENING" if is_speech else "MONITORING",
                                "system_active": True
                            }
                    except Exception as e:
                         print(f"[AudioEngine] Telemetry Error: {e}")

            except Exception as e:
                print(f"[AudioEngine] Loop Error: {e}")
                time.sleep(0.1)

            time.sleep(0.05)

    def start_stream(self, device_index: int):
        try:
            device = next((d for d in self.devices if d["index"] == device_index), None)
            if not device:
                return False

            self.current_rate = device['rate']
            self.current_channels = device['channels']
            self.latest_chunk = None

            print(f"[AudioEngine] Opening {device['channels']}ch stream on {device['name']}...")

            def callback(indata, frames, time, status):
                self.latest_chunk = indata.copy()

            self.stream = sd.InputStream(
                device=device_index,
                channels=device['channels'],
                samplerate=device['rate'],
                callback=callback,
                blocksize=2048
            )
            self.stream.start()
            # Set active state BEFORE thread start to ensure polling catches it
            self.active = True
            log_event("AUDIO", f"Stream ACTIVE on device {device_index} ({device['channels']}ch)")

            # Start Processor
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()

            return True
        except Exception as e:
            print(f"[AudioEngine] Start Error: {e}")
            self.active = False
            return False

    def stop_stream(self):
        self.active = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

    def get_telemetry(self):
        """Returns current state for API."""
        with self.lock:
            # Inject system active state into stream telemetry
            telemetry_copy = self.telemetry.copy()
            telemetry_copy["system_active"] = self.active

            return {
                "devices": self.devices,
                "stream": telemetry_copy
            }

    def close(self):
        self.stop_stream()

if __name__ == "__main__":
    print("--- ImpressionCore Spatial Audio v1.0 ---")
    engine = AudioEngine()

    # Select 4-channel device
    eye = next((d for d in engine.devices if d["channels"] == 4), None)
    # Fallback to stereo eye if needed (though spatial wont work well)
    if not eye:
        eye = next((d for d in engine.devices if d["is_eye"]), None)

    if eye:
        print(f"Target: {eye['name']} ({eye['channels']} ch)")
        engine.latest_chunk = None
        if engine.start_stream(eye['index']):
            try:
                print("Listening for spatial cues (CTRL+C to stop)...")
                while True:
                    if hasattr(engine, 'latest_chunk') and engine.latest_chunk is not None:
                        data = engine.latest_chunk

                        # 1. Voice Activity Detection (Energy)
                        rms = np.sqrt(np.mean(data**2))
                        if rms > 0.01: # Threshold
                            # 2. Direction of Arrival (if 4ch)
                            angle_str = ""
                            if eye['channels'] == 4:
                                # Use Mic 0 (Left) and Mic 3 (Right) - Max Baseline 60mm
                                sig1 = data[:, 0]
                                sig2 = data[:, 3]

                                # GCC-PHAT
                                tau, _ = gcc_phat(sig1, sig2, fs=engine.current_rate)

                                # Delta calculation
                                # tau = d * sin(theta) / c
                                # theta = arcsin(tau * c / d)
                                max_tau = engine.MIC_DISTANCE_4CH / engine.SOUND_SPEED

                                # Clamp tau to physical limits
                                tau = max(min(tau, max_tau), -max_tau)

                                try:
                                    theta = np.arcsin(tau * engine.SOUND_SPEED / engine.MIC_DISTANCE_4CH)
                                    degrees = np.degrees(theta)

                                    # Visual format:  [  <--  0  -->  ]
                                    pos = int((degrees + 90) / 10) # 0..18
                                    compass = ["-"] * 19
                                    compass[pos] = "O"
                                    angle_str = f"[{''.join(compass)}] {degrees:.0f}°"
                                except Exception:
                                    angle_str = "[Calc Err]"

                            bars = "|" * int(rms * 100)
                            print(f"{angle_str} Lvl:{bars}")
                        else:
                            # Silence
                            pass

                    time.sleep(0.05)
            except KeyboardInterrupt:
                pass
            engine.close()
    else:
        print("No PS Eye found.")
