import glob
import json
import os

from google.cloud import speech_v1
from google.protobuf import json_format

root_dir = os.path.dirname(__file__)
[key_json] = glob.glob(os.path.join(root_dir, "*service_account*.json"))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_json

client = speech_v1.SpeechClient()

config = dict(
    language_code="en-US",
    sample_rate_hertz=44100,
    audio_channel_count=2,
    model="default",
    speech_contexts=[
        dict(phrases=[
            "radar",
            "sergeant",
            "log",
            "following",
            "close",
            "inspect",
            "inspection",
            "revision",
            "complete",
            "in accordance with",
            "in compliance with",
            "step",
            "task",
            "checklist",
            "aircraft",
            "nose",
            "landing gear door",
        ])
    ],
    #enable_word_time_offsets=True,
)

wav_dir = os.path.join(root_dir, "REDSHREAD VOICE RECORDINGS")
json_dir = os.path.join(root_dir, "json")
if not os.path.exists(json_dir):
    os.makedirs(json_dir)
for dirpath, dirnames, filenames in os.walk(wav_dir):
    for filename in filenames:
        if not filename.endswith(".wav"):
            continue

        wav_path = os.path.join(dirpath, filename)
        print(wav_path)
        with open(wav_path, "rb") as f:
            content = f.read()

        audio = dict(content=content)
        response = client.recognize(config, audio)
        print(response)
        json_path = os.path.join(json_dir, filename.replace(".wav", ".json"))
        with open(json_path, 'w') as json_file:
            json_file.write(json_format.MessageToJson(response))
