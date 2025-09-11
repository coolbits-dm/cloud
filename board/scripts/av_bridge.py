#!/usr/bin/env python3
"""
Audio-Video Bridge
Mic/cam capture & simple streaming hooks for oCopilot Board Orchestrator
"""

import argparse
import cv2
import logging
import sounddevice as sd
import numpy as np
import wave
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AudioVideoBridge:
    def __init__(self, runtime_dir="runtime"):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(exist_ok=True)

        # Audio settings
        self.sample_rate = 48000
        self.channels = 2
        self.dtype = np.float32

        # Video settings
        self.camera_index = 0
        self.frame_width = 1920
        self.frame_height = 1080

    def list_audio_devices(self):
        """List available audio devices"""
        try:
            devices = sd.query_devices()
            logger.info("🎙️ Available audio devices:")

            for i, device in enumerate(devices):
                logger.info(
                    f"  {i}: {device['name']} - {device['max_input_channels']} input channels"
                )

        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")

    def list_camera_devices(self):
        """List available camera devices"""
        try:
            logger.info("📹 Available camera devices:")

            for i in range(10):  # Check first 10 indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        height, width = frame.shape[:2]
                        logger.info(f"  {i}: Camera {i} - {width}x{height}")
                    cap.release()

        except Exception as e:
            logger.error(f"Error listing camera devices: {e}")

    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        try:
            logger.info(f"🎙️ Recording audio for {duration} seconds...")

            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            )

            sd.wait()  # Wait until recording is finished

            # Save to WAV file
            output_file = self.runtime_dir / "mic_last.wav"

            with wave.open(str(output_file), "wb") as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)

                # Convert float32 to int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())

            logger.info(f"✅ Audio saved to: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Audio recording error: {e}")
            return None

    def capture_frame(self):
        """Capture a single frame from camera"""
        try:
            logger.info("📹 Capturing camera frame...")

            # Initialize camera
            cap = cv2.VideoCapture(self.camera_index)

            if not cap.isOpened():
                logger.error(f"Could not open camera {self.camera_index}")
                return None

            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

            # Capture frame
            ret, frame = cap.read()

            if ret:
                # Save frame
                output_file = self.runtime_dir / "cam_last.jpg"
                cv2.imwrite(str(output_file), frame)

                logger.info(f"✅ Frame saved to: {output_file}")
                logger.info(f"📊 Frame size: {frame.shape[1]}x{frame.shape[0]}")

                cap.release()
                return str(output_file)
            else:
                logger.error("Failed to capture frame")
                cap.release()
                return None

        except Exception as e:
            logger.error(f"Camera capture error: {e}")
            return None

    def test_audio_level(self):
        """Test audio input level"""
        try:
            logger.info("🎙️ Testing audio input level...")

            # Record 1 second of audio
            duration = 1
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
            )

            sd.wait()

            # Calculate RMS level
            rms = np.sqrt(np.mean(audio_data**2))
            level_db = 20 * np.log10(rms + 1e-10)  # Avoid log(0)

            logger.info(f"📊 Audio level: {level_db:.1f} dB")

            if level_db > -20:
                logger.info("✅ Good audio level detected")
            elif level_db > -40:
                logger.info("⚠️ Low audio level")
            else:
                logger.info("❌ Very low audio level - check microphone")

            return level_db

        except Exception as e:
            logger.error(f"Audio level test error: {e}")
            return None

    def test_camera_resolution(self):
        """Test camera resolution capabilities"""
        try:
            logger.info("📹 Testing camera resolution...")

            cap = cv2.VideoCapture(self.camera_index)

            if not cap.isOpened():
                logger.error(f"Could not open camera {self.camera_index}")
                return None

            # Test different resolutions
            resolutions = [
                (1920, 1080),  # Full HD
                (1280, 720),  # HD
                (640, 480),  # VGA
                (320, 240),  # QVGA
            ]

            supported_resolutions = []

            for width, height in resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                # Check actual resolution
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if actual_width == width and actual_height == height:
                    supported_resolutions.append((width, height))
                    logger.info(f"✅ {width}x{height} supported")
                else:
                    logger.info(
                        f"❌ {width}x{height} -> {actual_width}x{actual_height}"
                    )

            cap.release()

            logger.info(f"📊 Supported resolutions: {len(supported_resolutions)}")
            return supported_resolutions

        except Exception as e:
            logger.error(f"Camera resolution test error: {e}")
            return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Audio-Video Bridge")
    parser.add_argument("--record-audio", type=int, help="Record audio for N seconds")
    parser.add_argument(
        "--capture-frame", action="store_true", help="Capture camera frame"
    )
    parser.add_argument(
        "--test-audio", action="store_true", help="Test audio input level"
    )
    parser.add_argument(
        "--test-camera", action="store_true", help="Test camera resolution"
    )
    parser.add_argument("--list-audio", action="store_true", help="List audio devices")
    parser.add_argument(
        "--list-camera", action="store_true", help="List camera devices"
    )

    args = parser.parse_args()

    bridge = AudioVideoBridge()

    if args.list_audio:
        bridge.list_audio_devices()
    elif args.list_camera:
        bridge.list_camera_devices()
    elif args.record_audio:
        bridge.record_audio(args.record_audio)
    elif args.capture_frame:
        bridge.capture_frame()
    elif args.test_audio:
        bridge.test_audio_level()
    elif args.test_camera:
        bridge.test_camera_resolution()
    else:
        # Run basic tests
        logger.info("🔍 Running AV bridge tests...")
        bridge.list_audio_devices()
        bridge.list_camera_devices()
        bridge.test_audio_level()
        bridge.test_camera_resolution()
        logger.info("✅ AV bridge tests completed")


if __name__ == "__main__":
    main()
