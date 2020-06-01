import argparse
import json
import jiwer
import textwrap
import regex


# jiwer.RemovePunctuation removes string.punctuation not all Unicode punctuation
class RemovePunctuation(jiwer.AbstractTransform):
    def process_string(self, s: str):
        return regex.sub(r"\p{P}", "", s)


# remove some differences that we don't care about for comparisons
transform = jiwer.Compose([
    jiwer.ToLowerCase(),
    RemovePunctuation(),
    jiwer.RemoveSpecificWords([
        "uh", "um", "ah", "hi", "alright", "all right", "well"]),
    jiwer.SubstituteWords({
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "check out": "checkout", "hard point": "hardpoint"}),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.SentencesToListOfWords(),
    jiwer.RemoveEmptyStrings()
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--cleaned", action="store_true")
    args = parser.parse_args()


    all_expected = []
    all_actual = []
    all_cleaned_actual = []
    with open(args.json_path) as json_file:
        for item in json.load(json_file):
            filename = item['filename']
            expected = item['expected']
            actual = item['cleaned_actual'] if args.cleaned else item['actual']
            all_expected.append(expected)
            all_actual.append(actual)

            if args.verbose:
                message = textwrap.dedent("""\
                {filename} WER={actual_wer:.2f}
                EXPECTED: {expected!r}
                ACTUAL:   {actual!r}
                """)
                print(message.format(
                    filename=filename,
                    expected=transform(expected),
                    actual=transform(actual),
                    actual_wer=jiwer.wer(
                        hypothesis=actual,
                        truth=expected,
                        truth_transform=transform,
                        hypothesis_transform=transform),
                ))

    message = textwrap.dedent("""\
    Overall:
    WER:  {actual[wer]:.2f}
    MER:  {actual[mer]:.2f}
    WIL:  {actual[wil]:.2f}
    WIP:  {actual[wip]:.2f}
    """)
    print(message.format(actual=jiwer.compute_measures(
        hypothesis=all_actual,
        truth=all_expected,
        truth_transform=transform,
        hypothesis_transform=transform),
    ))
