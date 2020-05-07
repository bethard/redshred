from vosk import Model, KaldiRecognizer
import sys
import json
import os
import wave

model = Model("vosk-model-en-us-aspire-0.2")

for path in sys.argv[1:]:
    print(path)

    wf = wave.open(path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    while True:
        data = wf.readframes(1000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    res = json.loads(rec.FinalResult())
    print(res["text"])
