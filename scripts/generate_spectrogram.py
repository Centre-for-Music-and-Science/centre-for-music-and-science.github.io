#!/usr/bin/env python3
"""
Generate spectral JSON for the 3D hero visualisation.

Usage
-----
python generate_spectrogram.py <audio_file>
    [--output ../static/data/spectral_data.json]
"""

import argparse
import gzip
import json
from pathlib import Path

import numpy as np

DEFAULT_SAMPLE_RATE = 22050
DEFAULT_N_FFT = 2048
BUAP_DEFAULT_SAMPLE_RATE = 44100
BUAP_DEFAULT_N_FFT = 8192
BUAP_DEFAULT_SENSIBILITY_DB = 69.0
BUAP_DEFAULT_DISPLAY_MIN_DB = -40.0
BUAP_DEFAULT_DISPLAY_MAX_DB = 20.0


def build_payload(
    normalized_spectrogram: np.ndarray,
    *,
    duration: float,
    sample_rate: int,
    hop_length: int,
    n_mels: int,
    n_fft: int,
    decimals: int,
    freq_labels: list[float],
    analysis_extra: dict | None = None,
) -> dict:
    """Build a serializable payload from a normalized mel spectrogram."""
    actual_fps = sample_rate / hop_length
    n_frames = normalized_spectrogram.shape[1]
    frames = np.round(normalized_spectrogram, decimals).T.tolist()
    analysis = {
        "profile": "mel",
        "sampleRate": sample_rate,
        "hopLength": hop_length,
        "nFft": n_fft,
        "quantizeDecimals": decimals,
    }
    if analysis_extra:
        analysis.update(analysis_extra)
    return {
        "fps": round(actual_fps, 4),
        "duration": round(duration, 4),
        "nMels": n_mels,
        "nFrames": n_frames,
        "freqLabels": [round(f, 1) for f in freq_labels],
        "analysis": analysis,
        "frames": frames,
    }


def make_window(window_name: str, frame_length: int) -> np.ndarray:
    """Build a window that mirrors the BUAP spectrogram options."""
    if window_name == "None":
        return np.ones(frame_length, dtype=np.float64)
    if window_name == "Cosine":
        x = np.arange(frame_length, dtype=np.float64)
        return np.sin((np.pi * x) / frame_length)
    if window_name == "Hanning":
        x = np.arange(frame_length, dtype=np.float64)
        return 0.5 * (1 - np.cos((2 * np.pi * x) / frame_length))
    if window_name == "BH7":
        coeffs = np.array(
            [
                0.27105140069342,
                -0.43329793923448,
                0.21812299954311,
                -0.06592544638803,
                0.01081174209837,
                -0.00077658482522,
                0.00001388721735,
            ],
            dtype=np.float64,
        )
        x = np.arange(frame_length, dtype=np.float64)
        window = np.zeros(frame_length, dtype=np.float64)
        for j, c in enumerate(coeffs):
            window += c * np.cos((2 * np.pi * j * x) / frame_length)
        return window
    raise ValueError(f"Unsupported window: {window_name}")


def remap_linear_to_mel_axis(
    data: np.ndarray,
    freqs_hz: np.ndarray,
    *,
    f_min: float,
    f_max: float,
) -> tuple[np.ndarray, list[float]]:
    """Warp linear-bin magnitudes onto a mel-spaced axis without mel averaging."""
    n_bins = data.shape[1]
    mel_min = 1127.01048 * np.log(f_min / 700 + 1)
    mel_max = 1127.01048 * np.log(f_max / 700 + 1)
    mel_targets = np.linspace(mel_min, mel_max, n_bins)
    hz_targets = 700 * (np.exp(mel_targets / 1127.01048) - 1)
    remapped = np.empty_like(data)
    for idx in range(data.shape[0]):
        remapped[idx] = np.interp(hz_targets, freqs_hz, data[idx])
    return remapped, hz_targets.tolist()


def resample_frequency_bins(
    data: np.ndarray,
    freq_labels: list[float],
    target_bins: int,
) -> tuple[np.ndarray, list[float]]:
    """Resample per-frame frequency bins to reduce payload and mesh size."""
    if target_bins <= 1:
        raise ValueError("target_bins must be greater than 1.")
    if target_bins == data.shape[1]:
        return data, freq_labels

    src_idx = np.linspace(0.0, 1.0, data.shape[1])
    dst_idx = np.linspace(0.0, 1.0, target_bins)
    out = np.empty((data.shape[0], target_bins), dtype=np.float64)
    for idx in range(data.shape[0]):
        out[idx] = np.interp(dst_idx, src_idx, data[idx])
    new_freqs = np.interp(dst_idx, src_idx, np.asarray(freq_labels, dtype=np.float64))
    return out, new_freqs.tolist()


def compute_buap_style_array(
    y: np.ndarray,
    sr: int,
    *,
    n_fft: int,
    hop_length: int,
    window_name: str,
    f_min: float,
    f_max: float,
    scale: str,
) -> tuple[np.ndarray, list[float]]:
    """Compute FFT-bin magnitudes following BUAP spectrogram math."""
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)))

    frame_count = 1 + (len(y) - n_fft) // hop_length
    end = (frame_count - 1) * hop_length + n_fft
    y_proc = y[:end]
    frames = np.lib.stride_tricks.sliding_window_view(y_proc, n_fft)[::hop_length]

    frame_means = frames.mean(axis=1, keepdims=True)
    centered = frames - frame_means
    window = make_window(window_name, n_fft)
    framed = centered * window[np.newaxis, :]

    fft = np.fft.rfft(framed, n=n_fft, axis=1)
    power = np.maximum(np.real(fft) ** 2 + np.imag(fft) ** 2, 1e-20)
    magnitudes_db = 10 * np.log10(power) - 20.0

    freqs_hz = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    mask = (freqs_hz >= f_min) & (freqs_hz <= f_max)
    cropped = magnitudes_db[:, mask]
    cropped_freqs = freqs_hz[mask]
    if cropped.shape[1] == 0:
        raise ValueError("No FFT bins remain after applying f_min/f_max.")

    if scale == "Mel":
        warped, warped_freqs = remap_linear_to_mel_axis(
            cropped,
            cropped_freqs,
            f_min=f_min,
            f_max=f_max,
        )
        return warped, warped_freqs
    return cropped, cropped_freqs.tolist()


def normalize_db_values(
    magnitudes_db: np.ndarray,
    *,
    mode: str,
    sensibility_db: float,
    display_min_db: float,
    display_max_db: float,
) -> np.ndarray:
    """Normalize dB magnitudes to [0, 1] for visualization."""
    if mode == "sensibility":
        return np.clip(magnitudes_db / sensibility_db, 0.0, 1.0)
    if mode == "range":
        denom = max(display_max_db - display_min_db, 1e-9)
        return np.clip((magnitudes_db - display_min_db) / denom, 0.0, 1.0)
    raise ValueError(f"Unsupported db mapping mode: {mode}")


def generate_spectrogram(
    audio_path: str,
    output_path: str,
    *,
    target_fps: int = 30,
    n_mels: int = 128,
    n_fft: int = DEFAULT_N_FFT,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    decimals: int = 2,
):
    import librosa

    print(f"Loading audio: {audio_path}")
    y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"  Sample rate: {sr}, Duration: {duration:.1f}s")

    hop_length = max(1, int(sr / target_fps))
    print(f"  Hop length: {hop_length} (targeting {target_fps} fps)")
    print(
        f"  n_fft: {n_fft}, mel bands: {n_mels}, decimals: {decimals}"
    )

    print("Computing mel spectrogram...")
    spectrogram = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=n_fft,
        n_mels=n_mels,
        hop_length=hop_length,
        fmax=sr / 2,
    )
    spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

    s_min = spectrogram_db.min()
    s_max = spectrogram_db.max()
    spectrogram_norm = (spectrogram_db - s_min) / (s_max - s_min)

    actual_fps = sr / hop_length
    n_frames = spectrogram_norm.shape[1]
    print(f"  Frames: {n_frames}, Actual FPS: {actual_fps:.2f}")

    mel_freqs = librosa.mel_frequencies(n_mels=n_mels, fmax=sr / 2).tolist()
    payload = build_payload(
        spectrogram_norm,
        duration=duration,
        sample_rate=sr,
        hop_length=hop_length,
        n_mels=n_mels,
        n_fft=n_fft,
        decimals=decimals,
        freq_labels=mel_freqs,
        analysis_extra={"profile": "mel"},
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing JSON to {out} ...")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"  Output size: {size_mb:.2f} MB")

    gz_path = out.with_suffix(".json.gz")
    with gzip.open(gz_path, "wt") as f:
        json.dump(payload, f, separators=(",", ":"))
    gz_mb = gz_path.stat().st_size / (1024 * 1024)
    print(f"  Gzipped size: {gz_mb:.2f} MB")
    print("Done.")


def generate_buap_profile(
    audio_path: str,
    output_path: str,
    *,
    target_fps: int = 60,
    n_fft: int = BUAP_DEFAULT_N_FFT,
    sample_rate: int = BUAP_DEFAULT_SAMPLE_RATE,
    decimals: int = 3,
    sensibility_db: float = BUAP_DEFAULT_SENSIBILITY_DB,
    window_name: str = "BH7",
    f_min: float = 50.0,
    f_max: float = 10000.0,
    scale: str = "Mel",
    target_bins: int | None = None,
    db_mapping: str = "range",
    display_min_db: float = BUAP_DEFAULT_DISPLAY_MIN_DB,
    display_max_db: float = BUAP_DEFAULT_DISPLAY_MAX_DB,
):
    """Generate a BUAP-style FFT spectrogram payload for the 3D terrain."""
    import librosa

    print(f"Loading audio: {audio_path}")
    y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"  Sample rate: {sr}, Duration: {duration:.1f}s")

    hop_length = max(1, int(sr / target_fps))
    print(f"  Hop length: {hop_length} (targeting {target_fps} fps)")
    print(
        "  BUAP profile: "
        f"n_fft={n_fft}, window={window_name}, scale={scale}, "
        f"f_min={f_min}, f_max={f_max}, sensibility={sensibility_db} dB"
    )
    if db_mapping == "range":
        print(
            "  dB display range: "
            f"{display_min_db} to {display_max_db} dB"
        )
    else:
        print("  dB mapping: sensibility clipping")

    magnitudes_db, freq_labels = compute_buap_style_array(
        y,
        sr,
        n_fft=n_fft,
        hop_length=hop_length,
        window_name=window_name,
        f_min=f_min,
        f_max=f_max,
        scale=scale,
    )
    if target_bins is not None and target_bins < magnitudes_db.shape[1]:
        magnitudes_db, freq_labels = resample_frequency_bins(
            magnitudes_db,
            freq_labels,
            target_bins,
        )

    normalized = normalize_db_values(
        magnitudes_db,
        mode=db_mapping,
        sensibility_db=sensibility_db,
        display_min_db=display_min_db,
        display_max_db=display_max_db,
    ).T
    payload = build_payload(
        normalized,
        duration=duration,
        sample_rate=sr,
        hop_length=hop_length,
        n_mels=normalized.shape[0],
        n_fft=n_fft,
        decimals=decimals,
        freq_labels=freq_labels,
        analysis_extra={
            "profile": "buap_fft",
            "window": window_name,
            "scale": scale,
            "fMin": f_min,
            "fMax": f_max,
            "sensibilityDb": sensibility_db,
            "dbMapping": db_mapping,
            "displayMinDb": display_min_db,
            "displayMaxDb": display_max_db,
        },
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing JSON to {out} ...")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"  Output size: {size_mb:.2f} MB")

    gz_path = out.with_suffix(".json.gz")
    with gzip.open(gz_path, "wt") as f:
        json.dump(payload, f, separators=(",", ":"))
    gz_mb = gz_path.stat().st_size / (1024 * 1024)
    print(f"  Gzipped size: {gz_mb:.2f} MB")
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate spectrogram JSON from audio"
    )
    parser.add_argument(
        "audio_file",
        help="Path to audio file (MP3, WAV, etc.)",
    )
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).parent.parent
            / "static"
            / "data"
            / "spectral_data.json"
        ),
        help="Output JSON path",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Target frames per second",
    )
    parser.add_argument(
        "--n-mels",
        type=int,
        default=128,
        help="Number of mel bands",
    )
    parser.add_argument(
        "--n-fft",
        type=int,
        default=DEFAULT_N_FFT,
        help="FFT window size",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help="Analysis sample rate",
    )
    parser.add_argument(
        "--decimals",
        type=int,
        default=2,
        help="Decimal places to keep in output frames",
    )
    parser.add_argument(
        "--profile",
        choices=["mel", "buap_fft"],
        default="mel",
        help="Spectrogram computation profile",
    )
    parser.add_argument(
        "--window",
        choices=["None", "Cosine", "Hanning", "BH7"],
        default="BH7",
        help="Window type used by the BUAP FFT profile",
    )
    parser.add_argument(
        "--scale",
        choices=["Linear", "Mel"],
        default="Mel",
        help="Frequency axis for the BUAP FFT profile",
    )
    parser.add_argument(
        "--f-min",
        type=float,
        default=50.0,
        help="Minimum frequency (Hz) for the BUAP FFT profile",
    )
    parser.add_argument(
        "--f-max",
        type=float,
        default=10000.0,
        help="Maximum frequency (Hz) for the BUAP FFT profile",
    )
    parser.add_argument(
        "--sensibility-db",
        type=float,
        default=BUAP_DEFAULT_SENSIBILITY_DB,
        help="dB sensibility scaling for BUAP FFT profile",
    )
    parser.add_argument(
        "--target-bins",
        type=int,
        default=None,
        help="Optional number of frequency bins to keep in BUAP FFT profile",
    )
    parser.add_argument(
        "--db-mapping",
        choices=["range", "sensibility"],
        default="range",
        help="Normalization strategy for BUAP FFT profile",
    )
    parser.add_argument(
        "--display-min-db",
        type=float,
        default=BUAP_DEFAULT_DISPLAY_MIN_DB,
        help="Lower bound for dB range normalization",
    )
    parser.add_argument(
        "--display-max-db",
        type=float,
        default=BUAP_DEFAULT_DISPLAY_MAX_DB,
        help="Upper bound for dB range normalization",
    )
    args = parser.parse_args()
    if args.profile == "mel":
        generate_spectrogram(
            args.audio_file,
            args.output,
            target_fps=args.fps,
            n_mels=args.n_mels,
            n_fft=args.n_fft,
            sample_rate=args.sample_rate,
            decimals=args.decimals,
        )
    else:
        generate_buap_profile(
            args.audio_file,
            args.output,
            target_fps=args.fps,
            n_fft=args.n_fft,
            sample_rate=args.sample_rate,
            decimals=args.decimals,
            sensibility_db=args.sensibility_db,
            window_name=args.window,
            f_min=args.f_min,
            f_max=args.f_max,
            scale=args.scale,
            target_bins=args.target_bins,
            db_mapping=args.db_mapping,
            display_min_db=args.display_min_db,
            display_max_db=args.display_max_db,
        )
