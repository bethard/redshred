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
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.SentencesToListOfWords(),
    jiwer.RemoveEmptyStrings()
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    args = parser.parse_args()


    all_expected = []
    all_actual = []
    all_cleaned_actual = []
    with open(args.json_path) as json_file:
        for item in json.load(json_file):
            filename = item['filename']
            expected = item['expected']
            actual = item['actual']
            cleaned = item['cleaned_actual']
            all_expected.append(expected)
            all_actual.append(actual)
            all_cleaned_actual.append(cleaned)

            message = textwrap.dedent("""\
            {filename}
            EXPECTED:      {expected!r}
            ACTUAL:   {actual_wer:.2f} {actual!r}
            CLEANED:  {cleaned_actual_wer:.2f} {cleaned!r}
            """)
            jiwer_kwargs = dict(truth=expected,
                                truth_transform=transform,
                                hypothesis_transform=transform)
            print(message.format(
                filename=filename,
                expected=transform(expected),
                actual=transform(actual),
                cleaned=transform(cleaned),
                actual_wer=jiwer.wer(
                    hypothesis=actual, **jiwer_kwargs),
                cleaned_actual_wer=jiwer.wer(
                    hypothesis=cleaned, **jiwer_kwargs),
            ))

    jiwer_kwargs = dict(truth=all_expected,
                        truth_transform=transform,
                        hypothesis_transform=transform)
    message = textwrap.dedent("""\
    Overall:
    ACTUAL  WER:  {actual[wer]:.2f}
    CLEANED WER:  {cleaned[wer]:.2f}
    ACTUAL  MER:  {actual[mer]:.2f}
    CLEANED MER:  {cleaned[mer]:.2f}
    ACTUAL  WIL:  {actual[wil]:.2f}
    CLEANED WIL:  {cleaned[wil]:.2f}
    ACTUAL  WIP:  {actual[wip]:.2f}    
    CLEANED WIP:  {cleaned[wip]:.2f}
    """)
    print(message.format(
        actual=jiwer.compute_measures(
            hypothesis=all_actual, **jiwer_kwargs),
        cleaned=jiwer.compute_measures(
            hypothesis=all_cleaned_actual, **jiwer_kwargs),
    ))
