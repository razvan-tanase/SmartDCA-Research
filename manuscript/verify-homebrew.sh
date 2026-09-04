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
if ! command -v latexmk >/dev/null 2>&1; then
  brew reinstall texlive
fi

if [ "$verification_mode" = "--build" ]; then
  exec python3.12 manuscript/build.py
fi

python3.12 -m unittest \
  tools.test_check_markdown_links \
  manuscript.tests.test_controls \
  manuscript.tests.test_release_check \
  manuscript.tests.test_manuscript_build \
  reproducibility.checks.check_financial_model_corrected_signal_foundations \
  reproducibility.checks.check_impossibility_safety_policy_architecture \
  reproducibility.checks.check_finite_arbitrary_horizon_boundaries \
  reproducibility.checks.check_dca_literature_synthesis \
  reproducibility.checks.check_corrected_mean_literature_synthesis \
  reproducibility.checks.check_computational_finance_statistics_literature_synthesis
python3.12 reproducibility/checks/check_pathwise_dca_dominance.py
python3.12 reproducibility/checks/check_epsilon_dca_safety_guardrail.py
python3.12 reproducibility/checks/check_guarded_corrected_mean_smartdca.py
python3.12 reproducibility/checks/check_two_purchase_dca_win_loss_boundary.py
python3.12 reproducibility/checks/check_three_purchase_corrected_mean_effect.py
python3.12 -m reproducibility.checks.check_arbitrary_horizon_accounting_verification
python3.12 -m reproducibility.checks.check_weak_single_valley_falsification
python3.12 -m reproducibility.checks.check_cash_single_crossing_mechanism
python3.12 -m reproducibility.checks.check_arbitrary_horizon_performance_boundary
python3.12 reproducibility/checks/check_arbitrary_horizon_publication_review.py
python3.12 manuscript/check_controls.py
python3.12 tools/check_markdown_links.py .
