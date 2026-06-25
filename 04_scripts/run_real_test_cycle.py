#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd):
    print("==>", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--cycle-name", required=True)
    parser.add_argument("--reviewer", default="leoserro39")
    parser.add_argument("--review-note", default="Approved only for controlled pilot measurement. No canonical promotion, no branch mutation, no automatic sync.")
    parser.add_argument("--min-measurements", default="3")
    args = parser.parse_args()

    proposal_name = args.cycle_name + "_proposal"
    measurement_name = args.cycle_name + "_measurement"
    decision_name = args.cycle_name + "_promotion_decision"

    run([
        "python",
        "04_scripts/check_real_source_readiness.py",
        "--source",
        args.source,
        "--source-name",
        args.source_name,
    ])

    run([
        "python",
        "04_scripts/run_real_source_intake.py",
        "--source",
        args.source,
        "--source-name",
        args.source_name,
    ])

    run([
        "python",
        "04_scripts/run_real_evidence_proposal.py",
        "--intake-report",
        "05_outputs/reports/real_source_intake_report.json",
        "--proposal-name",
        proposal_name,
    ])

    run([
        "python",
        "04_scripts/run_real_human_review.py",
        "--proposal-report",
        "05_outputs/reports/real_evidence_proposal_report.json",
        "--decision",
        "APPROVED_FOR_PILOT",
        "--reviewer",
        args.reviewer,
        "--note",
        args.review_note,
    ])

    run([
        "python",
        "04_scripts/run_real_pilot_measurement.py",
        "--intake-report",
        "05_outputs/reports/real_source_intake_report.json",
        "--review-report",
        "05_outputs/reports/real_human_review_report.json",
        "--measurement-name",
        measurement_name,
    ])

    run([
        "python",
        "04_scripts/run_real_promotion_decision.py",
        "--review-report",
        "05_outputs/reports/real_human_review_report.json",
        "--measurements-dir",
        "05_outputs/real_tests/pilot_measurements",
        "--decision-name",
        decision_name,
        "--measurement-prefix",
        measurement_name,
        "--min-measurements",
        args.min_measurements,
    ])

    run([
        "python",
        "04_scripts/build_real_test_cycle_snapshot.py",
        "--cycle-name",
        args.cycle_name,
    ])

    run([
        "python",
        "04_scripts/validate_mesh.py",
    ])

    print("REAL_TEST_CYCLE_RUNNER_DONE")
    print("cycle_name:", args.cycle_name)
    print("canonical_effect: gated outputs only")


if __name__ == "__main__":
    main()
