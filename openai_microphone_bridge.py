#!/usr/bin/env python3
"""
OpenAI Microphone Bridge - CoolBits.ai
Conectare la OpenAI API + acces microfon pentru comunicare vocală
"""

import os
import sys
import json
import time
import threading
import pyaudio
import wave
import openai
from datetime import datetime
import requests
import subprocess


class OpenAIMicrophoneBridge:
    def __init__(self):
        self.openai_client = None
        self.microphone_active = False
        self.audio_stream = None
        self.pyaudio_instance = None
        self.recording_thread = None
        self.audio_frames = []

        # Configurații audio
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5

        # OpenAI API Key (din environment sau secrets)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        print("🎤 OpenAI Microphone Bridge initialized!")
        print(f"📡 OpenAI API Key: {'✅ Set' if self.openai_api_key else '❌ Missing'}")

    def setup_openai(self):
        """Configurează OpenAI client"""
        try:
            if not self.openai_api_key:
                print("❌ OpenAI API Key not found!")
                print("💡 Set OPENAI_API_KEY environment variable")
                return False

            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)

            # Test API connection
            response = self.openai_client.models.list()
            print("✅ OpenAI API connected successfully!")
            print(f"📊 Available models: {len(response.data)}")
            return True

        except Exception as e:
            print(f"❌ OpenAI setup failed: {e}")
            return False

    def setup_microphone(self):
        """Configurează microfonul"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Verifică microfonul disponibil
            device_count = self.pyaudio_instance.get_device_count()
            print(f"🎤 Audio devices found: {device_count}")

            # Găsește microfonul Logitech
            microphone_device = None
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info["maxInputChannels"] > 0:
                    print(f"🎤 Device {i}: {device_info['name']}")
                    if (
                        "logitech" in device_info["name"].lower()
                        or "c925e" in device_info["name"].lower()
                    ):
                        microphone_device = i
                        print(f"✅ Found Logitech microphone: {device_info['name']}")
                        break

            if microphone_device is None:
                print("⚠️ Logitech microphone not found, using default")
                microphone_device = None

            return True

        except Exception as e:
            print(f"❌ Microphone setup failed: {e}")
            return False

    def start_recording(self):
        """Începe înregistrarea audio"""
        try:
            self.audio_frames = []

            self.audio_stream = self.pyaudio_instance.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=None,  # Use default device
                frames_per_buffer=self.CHUNK,
            )

            self.microphone_active = True
            print("🎤 Recording started...")

            # Începe thread-ul de înregistrare
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()

        except Exception as e:
            print(f"❌ Recording failed: {e}")

    def _record_audio(self):
        """Thread pentru înregistrarea audio"""
        while self.microphone_active:
            try:
                data = self.audio_stream.read(self.CHUNK)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"❌ Recording error: {e}")
                break

    def stop_recording(self):
        """Oprește înregistrarea și salvează fișierul"""
        try:
            self.microphone_active = False

            if self.recording_thread:
                self.recording_thread.join()

            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()

            # Salvează audio-ul
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"

            with wave.open(filename, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b"".join(self.audio_frames))

            print(f"🎤 Recording saved: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Stop recording failed: {e}")
            return None

    def transcribe_audio(self, audio_file):
        """Transcrie audio-ul folosind OpenAI Whisper"""
        try:
            if not self.openai_client:
                print("❌ OpenAI client not initialized")
                return None

            with open(audio_file, "rb") as audio:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio, response_format="text"
                )

            print(f"📝 Transcription: {transcript}")
            return transcript

        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return None

    def send_to_openai(self, message):
        """Trimite mesajul la OpenAI pentru procesare"""
        try:
            if not self.openai_client:
                print("❌ OpenAI client not initialized")
                return None

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Much cheaper than gpt-4 ($0.15 vs $30 per 1M tokens)
                messages=[
                    {
                        "role": "system",
                        "content": "You are CoolBits.ai AI assistant. Respond in Romanian.",
                    },
                    {"role": "user", "content": message},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            reply = response.choices[0].message.content
            print(f"🤖 OpenAI Response: {reply}")
            return reply

        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return None

    def cleanup(self):
        """Curăță resursele"""
        try:
            if self.audio_stream:
                self.audio_stream.close()
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")


def main():
    """Funcția principală"""
    print("🚀 Starting OpenAI Microphone Bridge...")

    bridge = OpenAIMicrophoneBridge()

    # Setup OpenAI
    if not bridge.setup_openai():
        print("❌ Cannot proceed without OpenAI API")
        return

    # Setup Microphone
    if not bridge.setup_microphone():
        print("❌ Cannot proceed without microphone")
        return

    try:
        print("\n🎤 Microphone Bridge Ready!")
        print("📋 Commands:")
        print("  - Press ENTER to start recording")
        print("  - Press ENTER again to stop recording")
        print("  - Type 'quit' to exit")

        while True:
            command = input("\n🎤 Command: ").strip().lower()

            if command == "quit":
                break
            elif command == "":
                # Start recording
                print("🎤 Recording... (Press ENTER to stop)")
                bridge.start_recording()

                # Wait for stop command
                input()

                # Stop recording
                audio_file = bridge.stop_recording()

                if audio_file:
                    # Transcribe
                    transcript = bridge.transcribe_audio(audio_file)

                    if transcript:
                        # Send to OpenAI
                        response = bridge.send_to_openai(transcript)

                        if response:
                            print(f"\n🤖 CoolBits.ai Response: {response}")

            elif command == "test":
                # Test OpenAI connection
                test_response = bridge.send_to_openai("Test connection")
                if test_response:
                    print(f"✅ OpenAI test successful: {test_response}")

            elif command == "status":
                print(f"📊 Status:")
                print(
                    f"  - OpenAI: {'✅ Connected' if bridge.openai_client else '❌ Disconnected'}"
                )
                print(
                    f"  - Microphone: {'✅ Active' if bridge.microphone_active else '❌ Inactive'}"
                )
                print(
                    f"  - Audio devices: {bridge.pyaudio_instance.get_device_count() if bridge.pyaudio_instance else 'N/A'}"
                )

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

    finally:
        bridge.cleanup()
        print("👋 OpenAI Microphone Bridge stopped")


if __name__ == "__main__":
    main()
