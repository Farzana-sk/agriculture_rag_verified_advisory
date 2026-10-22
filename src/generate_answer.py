import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import run_advisory
from stt import record_and_transcribe


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Voice/text agricultural advisory with answer verification."
    )
    parser.add_argument("--text", help="Farmer question as text. If omitted, microphone is used.")
    parser.add_argument("--duration", type=int, default=6, help="Microphone recording seconds.")
    args = parser.parse_args()

    if args.text:
        question = args.text
        language = None
    else:
        transcript = record_and_transcribe(duration=args.duration)
        question = transcript["text"]
        language = transcript.get("language")
        print("\n--- TRANSCRIBED QUESTION ---")
        print(question)

    result = run_advisory(question, language)
    print("\n--- GENERATED ANSWER ---")
    print(result["generated_answer"])
    print("\n--- ANSWER VERIFICATION ---")
    print(f"Trust score: {result['trust_score']}")
    print(f"Verdict: {result['verdict']} (tau >= {result['tau']})")
    print("\n--- FINAL ANSWER ---")
    print(result["final_answer"])
    print("\n--- SOURCES ---")
    print(json.dumps(result["sources"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
