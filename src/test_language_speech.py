import unittest

try:
    from .language import prepare_speech_text, spoken_summary, telugu_numbers_to_words
except ImportError:  # pragma: no cover - script execution support
    from language import prepare_speech_text, spoken_summary, telugu_numbers_to_words


class TeluguSpeechTests(unittest.TestCase):
    def test_numbers_are_spoken_as_telugu_words(self):
        examples = {
            "25": "ఇరవై ఐదు",
            "1.5": "ఒకటి పాయింట్ ఐదు",
            "1,25,000": "ఒక లక్ష ఇరవై ఐదు వేలు",
            "1,234,567": "పన్నెండు లక్షల ముప్పై నాలుగు వేల ఐదు వందల అరవై ఏడు",
            "100000000": "పది కోట్లు",
        }
        for digits, expected in examples.items():
            with self.subTest(digits=digits):
                self.assertEqual(telugu_numbers_to_words(digits), expected)
        self.assertEqual(prepare_speech_text("25", "te"), "ఇరవై ఐదు")

    def test_ranges_percentages_and_agriculture_units_are_speakable(self):
        self.assertEqual(
            prepare_speech_text("విత్తన మోతాదు 15-20 kg/ha.", "te"),
            "విత్తన మోతాదు పదిహేను నుండి ఇరవై కిలోలు ప్రతి హెక్టారుకు",
        )
        self.assertEqual(
            prepare_speech_text("మందు 1.5% కలపండి.", "te"),
            "మందు ఒకటి పాయింట్ ఐదు శాతం కలపండి",
        )

    def test_telugu_bullet_lists_have_spoken_pauses_and_no_markdown(self):
        answer = "విత్తన రకం **TCG 1704** ఎంచుకోండి.\n- **TCG 1706** కూడా మంచిది."
        self.assertEqual(
            prepare_speech_text(answer, "te"),
            "విత్తన రకం TCG 1704 ఎంచుకోండి. TCG 1706 కూడా మంచిది",
        )

    def test_english_fallback_is_not_read_in_a_telugu_voice(self):
        unavailable = "క్షమించండి, ఈ సమాధానాన్ని తెలుగులో వినిపించలేకపోతున్నాను. తెరపై చదవండి."
        self.assertEqual(prepare_speech_text("Apply 25 kg/ha.", "te"), unavailable)
        self.assertEqual(spoken_summary("Apply 25 kg/ha after 15-20 days.", "te"), unavailable)

    def test_unverified_translation_notice_does_not_read_english_answer(self):
        text = "ఖచ్చితమైన తెలుగు అనువాదం సాధ్యం కాలేదు. ఇంగ్లీష్ సమాధానం: apply 25 kg."
        spoken = spoken_summary(text, "te")
        self.assertNotIn("ఇంగ్లీష్ సమాధానం", spoken)
        self.assertNotIn("apply", spoken)


if __name__ == "__main__":
    unittest.main()
