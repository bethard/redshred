import glob
import os

from google.cloud import speech_v1p1beta1 as speech
from google.protobuf import json_format

root_dir = os.path.dirname(__file__)
[key_json] = glob.glob(os.path.join(root_dir, "*service_account*.json"))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_json

client = speech.SpeechClient()

config = dict(
    language_code="en-US",
    sample_rate_hertz=44100,
    audio_channel_count=2,
    model="default",
    speech_contexts=[
        dict(
            phrases=[
                "radar",
                "accordance",
                "log",
                "logging",
                "out",
                "man",
                "number",
                "task",
                "step",
                "check",
                "list",
                "side",
                "nose",
                "door",
                "landing",
                "applying",
                "on the",
                "we are",
                "we have",
                "revision",
                "staff",
                "sergeant",
                "closed",
                "inspected",
                "kansas",
                "alpha",
                "e v s",
                "h s",
            ],
            boost=10,
        ),
        dict(
            phrases=[
                "hour",
                "dash",
            ],
            boost=5,
        ),
    ],
    #enable_word_time_offsets=True,
)

wav_dir = os.path.join(root_dir, "REDSHREAD VOICE RECORDINGS")
json_dir = os.path.join(root_dir, "json")
if not os.path.exists(json_dir):
    os.makedirs(json_dir)

paths = [(dirpath, filename)
         for dirpath, dirnames, filenames in os.walk(wav_dir)
         for filename in filenames
         if filename.endswith(".wav")]

for dirpath, filename in sorted(paths):
    wav_path = os.path.join(dirpath, filename)
    print(wav_path)
    with open(wav_path, "rb") as f:
        content = f.read()

    audio = dict(content=content)
    response = client.recognize(config, audio)
    for result in response.results:
        print(result.alternatives[0].transcript)
    json_path = os.path.join(json_dir, filename.replace(".wav", ".json"))
    with open(json_path, 'w') as json_file:
        json_file.write(json_format.MessageToJson(response))
