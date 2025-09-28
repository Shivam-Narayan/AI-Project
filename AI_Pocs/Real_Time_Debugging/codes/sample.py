import sounddevice as sd

def list_audio_devices():
          devices = sd.query_devices()
          for i, device in enumerate(devices):
              print(f"Device Index {i}: {device['name']}")

      # List audio devices to find the correct device name
list_audio_devices()