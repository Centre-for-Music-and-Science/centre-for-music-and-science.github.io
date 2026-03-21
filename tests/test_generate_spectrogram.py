import unittest

import numpy as np

from scripts.generate_spectrogram import build_payload
from scripts.generate_spectrogram import normalize_db_values


class BuildPayloadTests(unittest.TestCase):
    def test_build_payload_records_analysis_metadata_and_rounding(self):
        spectrogram = np.array(
            [
                [0.1234, 0.9876],
                [0.3333, 0.6666],
            ]
        )

        payload = build_payload(
            spectrogram,
            duration=1.23456,
            sample_rate=22050,
            hop_length=367,
            n_mels=2,
            n_fft=1024,
            decimals=3,
            freq_labels=[100.123, 200.987],
        )

        self.assertEqual(payload["nMels"], 2)
        self.assertEqual(payload["nFrames"], 2)
        self.assertEqual(payload["duration"], 1.2346)
        self.assertEqual(payload["analysis"]["sampleRate"], 22050)
        self.assertEqual(payload["analysis"]["hopLength"], 367)
        self.assertEqual(payload["analysis"]["nFft"], 1024)
        self.assertEqual(payload["analysis"]["quantizeDecimals"], 3)
        self.assertEqual(payload["freqLabels"], [100.1, 201.0])
        self.assertEqual(
            payload["frames"],
            [
                [0.123, 0.333],
                [0.988, 0.667],
            ],
        )

    def test_normalize_db_values_range_mode_keeps_upper_bands_visible(self):
        db = np.array(
            [
                [-30.0, -10.0, 10.0],
                [-20.0, -5.0, 5.0],
            ]
        )
        out = normalize_db_values(
            db,
            mode="range",
            sensibility_db=69.0,
            display_min_db=-40.0,
            display_max_db=20.0,
        )
        self.assertGreater(out[0, 0], 0.0)
        self.assertGreater(out[0, 1], out[0, 0])
        self.assertGreater(out[0, 2], out[0, 1])


if __name__ == "__main__":
    unittest.main()
