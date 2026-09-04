#!/bin/sh
set -eu

verification_mode="${1:-verify}"
case "$verification_mode" in
  verify | --build)
    ;;
  --help)
    echo "usage: $0 [--build]"
    exit 0
    ;;
  *)
    echo "usage: $0 [--build]" >&2
    exit 2
    ;;
esac

# Keep installation and verification in one process. Some managed agent
# sandboxes discard Homebrew's /opt changes after the next process exits.
brew install python@3.12 texlive poppler

if [ "$verification_mode" = "--build" ]; then
  exec python3.12 manuscript/build.py
fi

python3.12 -m unittest \
  tools.test_check_markdown_links \
  manuscript.tests.test_controls \
  manuscript.tests.test_release_check \
  manuscript.tests.test_manuscript_build \
  reproducibility.checks.check_dca_literature_synthesis \
  reproducibility.checks.check_corrected_mean_literature_synthesis \
  reproducibility.checks.check_computational_finance_statistics_literature_synthesis
python3.12 manuscript/check_controls.py
python3.12 tools/check_markdown_links.py .
