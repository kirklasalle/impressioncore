import threading
import time
import re
from typing import Any

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

from src.orchestrator.system_logger import log_event


def audio_device_identity(name: str) -> str:
    """Create a provider-independent, name-based identity for duplicate endpoints."""
    normalized = (name or "").strip().lower()
    # MME truncates device names at 31 characters, including the input wrapper.
    # Only collapse the known Kinect USB Audio spelling, not all Kinect devices.
    if re.fullmatch(
        r"(?:microphone(?: array)?\s*\()?kinect usb au(?:dio)?\)?", normalized
    ):
        return "audio:kinect usb audio"
    wrapped_name = re.match(r"^(?:microphone(?: array)?|input)\s*\((.+)\)$", normalized)
    if wrapped_name:
        normalized = wrapped_name.group(1).strip()
    normalized = re.sub(r"\s+\[(?:wasapi|directsound|mme|wdm-ks|asio)\]$", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return f"audio:{normalized}" if normalized else "audio:unknown"


def summarize_audio_devices(devices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group provider endpoints by normalized device name without losing endpoint indices."""
    grouped = {}
    for device in devices:
        name = device.get("name", "")
        identity = device.get("device_identity")
        if not identity:
            identity = audio_device_identity(name)
            if identity == "audio:unknown":
                identity = f"{identity}:{device.get('provider', 'unknown')}:{device.get('index', 'unknown')}"
        entry = grouped.setdefault(identity, {
            "device_identity": identity,
            "name": name or "Unknown audio input",
            "channels": 0,
            "providers": [],
            "endpoint_indices": [],
            "identity_confidence": "normalized_name",
            "is_kinect": False,
            "is_eye": False,
        })
        entry["channels"] = max(entry["channels"], int(device.get("channels", 0)))
        provider = device.get("provider")
        if provider and provider not in entry["providers"]:
            entry["providers"].append(provider)
        index = device.get("index")
        if index is not None and index not in entry["endpoint_indices"]:
            entry["endpoint_indices"].append(index)
        entry["is_kinect"] = entry["is_kinect"] or bool(device.get("is_kinect"))
        entry["is_eye"] = entry["is_eye"] or bool(device.get("is_eye"))
    return list(grouped.values())


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
        self.current_is_eye = False

        # Spatial Configuration for PS Eye
        self.MIC_DISTANCE_4CH = 0.06
        self.SOUND_SPEED = 343.0
        self.noise_floor = 0.005 # Baseline

    def verify_device_health(self, index: int, duration: float = 0.3) -> dict[str, Any]:
        """Performs a transient capture to verify real-time data flow."""
        if sd is None:
            return {"status": "UNAVAILABLE", "error": "sounddevice not installed", "rms": 0}

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
        if sd is None:
            return []

        try:
            raw = sd.query_devices()
        except Exception:
            return []

        try:
            hostapis = sd.query_hostapis()
        except Exception:
            hostapis = []
        providers = {
            index: hostapi.get("name", f"hostapi-{index}")
            for index, hostapi in enumerate(hostapis)
        }

        for i, d in enumerate(raw):
            name = d.get('name') or f"Audio input {i}"
            channels = int(d.get('max_input_channels') or 0)

            if channels <= 0:
                continue

            lowered_name = name.lower()
            is_kinect = "kinect" in lowered_name
            is_ps_eye = (
                "playstation" in lowered_name
                or "ps eye" in lowered_name
                or "eye toy" in lowered_name
            )

            devs.append({
                "index": i,
                "name": name,
                "channels": channels,
                "rate": int(d.get('default_samplerate') or 48000),
                "provider": providers.get(d.get("hostapi"), "unknown"),
                "device_identity": audio_device_identity(name),
                "is_eye": is_ps_eye,
                "is_kinect": is_kinect,
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
                    if is_speech and self.current_channels == 4 and self.current_is_eye:
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
        if sd is None:
            print("[AudioEngine] Start Error: sounddevice not installed")
            self.active = False
            return False

        try:
            device = next((d for d in self.devices if d["index"] == device_index), None)
            if not device:
                return False

            self.current_rate = device['rate']
            self.current_channels = device['channels']
            self.current_is_eye = bool(device.get("is_eye"))
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
