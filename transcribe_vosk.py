from vosk import Model, KaldiRecognizer
import sys
import json
import os

model = Model("vosk-model-en-us-aspire-0.2")

for path in sys.argv[1:]:
    rec = KaldiRecognizer(model, 44100)

    print(path)
    wf = open(path, "rb")
    wf.read(44) # skip header

    while True:
        data = wf.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print(res['text'])

    res = json.loads(rec.FinalResult())
    print(res['text'])
