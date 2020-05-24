import glob
import os
import argparse

from google.cloud import speech_v1p1beta1 as speech
from google.protobuf import json_format

root_dir = os.path.dirname(__file__)
[key_json] = glob.glob(os.path.join(root_dir, "*service_account*.json"))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_json

client = speech.SpeechClient()

config = dict(
    language_code="en-US",
    audio_channel_count=2,
    model="default",
    speech_contexts=[
        dict(
            phrases=[
                # what Vader gets recognized as
                "radar",
                # phrases about following procedures
                "accordance",
                "shall",
                "log",
                "logging",
                "out",
                "task",
                "step",
                "steps",
                "check",
                "list",
                "closed",
                "inspected",
                "revision",
                "tack",
                "warning",
                "read off",
                "notes",
                # phrases about personnel
                "staff",
                "sergeant",
                "man",
                "number",
                # phrases about airplane maintenance
                "side",
                "nose",
                "door",
                "landing",
                "candidate",
                "fault",
                "applying",
                "prepare",
                "wrench",
                "circuits",
                "leads",
                "electrical",
                "bonding",
                "mating",
                "relay",
                "tag",
                "tagged",
                "nuts",
                "studs",
                "e v s",
                "h s",
            ],
            boost=10,
        ),
        dict(
            phrases=[
                # phrases that should be above
                # but are confused with common words
                "hour",
                "dash",
                "torque",
                # NATO phonetic alphabet
                "Alfa",
                "Bravo",
                "Charlie",
                "Delta",
                "Echo",
                "Foxtrot",
                "Golf",
                "Hotel",
                "India",
                "Juliett",
                "Kilo",
                "Lima",
                "Mike",
                "November",
                "Oscar",
                "Papa",
                "Quebec",
                "Romeo",
                # "Sierra", # can't boost this; it sounds too much like zero
                "Tango",
                "Uniform",
                "Victor",
                "Whiskey",
                "X-ray",
                "Yankee",
                "Zulu",
                # boost numbers
                "$OPERAND",
                "0",
            ],
            boost=5,
        ),
    ],
    #enable_word_time_offsets=True,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wav_dir")
    parser.add_argument("json_dir", nargs='?', default="json")
    parser.add_argument("--expected-dir")
    parser.add_argument("--expected-encoding", default="utf8")
    parser.add_argument("--only", dest="patterns", metavar="PATTERN", nargs='+')
    args = parser.parse_args()

    if not os.path.exists(args.json_dir):
        os.makedirs(args.json_dir)

    paths = [(dirpath, filename)
             for dirpath, dirnames, filenames in os.walk(args.wav_dir)
             for filename in filenames
             if not args.patterns or any(p in filename for p in args.patterns)
             if filename.endswith(".wav")]

    for dirpath, filename in sorted(paths):
        wav_path = os.path.join(dirpath, filename)
        if args.expected_dir:
            txt_filename = filename.replace(".wav", ".txt")
            txt_path = os.path.join(args.expected_dir, txt_filename)
            if os.path.exists(txt_path):
                with open(txt_path, encoding=args.expected_encoding) as f:
                    print(filename + " EXPECTED:")
                    print(f.read())

        with open(wav_path, "rb") as f:
            content = f.read()

        audio = dict(content=content)
        response = client.recognize(config, audio)
        print(filename + " TRANSCRIBED:")
        for result in response.results:
            print(result.alternatives[0].transcript)
        json_path = os.path.join(args.json_dir, filename.replace(".wav", ".json"))
        with open(json_path, 'w') as json_file:
            json_file.write(json_format.MessageToJson(response))

        print()
