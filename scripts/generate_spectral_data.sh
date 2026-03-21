#!/usr/bin/env bash
# Regenerate the spectral JSON data files used by the hero banner visualisation.
# Run from the repository root: ./scripts/generate_spectral_data.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

source .venv/bin/activate

COMMON_ARGS=(
  --profile buap_fft
  --fps 60
  --n-fft 8192
  --sample-rate 44100
  --window BH7
  --scale Mel
  --f-min 50
  --f-max 5000
  --target-bins 384
  --db-mapping range
  --display-min-db -40
  --display-max-db 20
  --decimals 3
)

python scripts/generate_spectrogram.py static/audio/berghain.mp3 \
  "${COMMON_ARGS[@]}" \
  --output static/data/berghain-spectral.json

python scripts/generate_spectrogram.py static/audio/fever.mp3 \
  "${COMMON_ARGS[@]}" \
  --output static/data/fever-spectral.json

python scripts/generate_spectrogram.py static/audio/bach-cello-suite-1.mp3 \
  "${COMMON_ARGS[@]}" \
  --output static/data/bach-cello-suite-1-spectral.json
