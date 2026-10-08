import os
import sys

# Ensure utf-8 stdout on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from streamlit.testing.v1 import AppTest


def run_stress_tests():
    print("=== STARTING QA STRESS TESTS ACROSS FILTERS & TABS ===")
    tabs = ["Executive Overview", "Channel Insights", "Campaign Drill-Down", "Budget Optimiser"]

    test_cases = [
        {"name": "Default Baseline", "platforms": None, "empty": False},
        {"name": "Single Platform (Email)", "platforms": ["Email"], "empty": False},
        {"name": "Single Platform (Google)", "platforms": ["Google"], "empty": False},
        {"name": "Single Platform (LinkedIn)", "platforms": ["LinkedIn"], "empty": False},
        {"name": "Empty Platform Selection", "platforms": [], "empty": True},
        {"name": "Exclude Outliers Active", "outliers": True, "empty": False},
    ]

    total_tested = 0
    failures = []

    for tc in test_cases:
        case_name = tc["name"]
        print(f"\n--- Testing Scenario: {case_name} ---")
        for tab in tabs:
            total_tested += 1
            try:
                main_path = os.path.abspath("app/main.py")
                at = AppTest.from_file(main_path, default_timeout=35)
                at.run()

                # Set filters if applicable
                if "platforms" in tc and tc["platforms"] is not None:
                    # Find platform multiselect
                    for ms in at.multiselect:
                        if ms.label == "Platform":
                            ms.set_value(tc["platforms"]).run()
                            break

                if "outliers" in tc:
                    for tg in at.toggle:
                        if "Outliers" in tg.label:
                            tg.set_value(tc["outliers"]).run()
                            break

                # Switch tab
                for r in at.radio:
                    if "Executive Overview" in r.options:
                        r.set_value(tab).run()
                        break

                # Check for exceptions
                exc_count = len(at.exception)
                if exc_count > 0:
                    err_msgs = [e.message for e in at.exception]
                    print(f"  [FAIL] Tab '{tab}': {exc_count} exception(s) -> {err_msgs}")
                    failures.append((case_name, tab, err_msgs))
                else:
                    print(f"  [PASS] Tab '{tab}' rendered without exceptions.")
            except Exception as e:
                print(f"  [CRASH] Tab '{tab}' crashed test harness: {e!s}")
                failures.append((case_name, tab, [str(e)]))

    print(f"\n=== QA STRESS TEST COMPLETE: {total_tested - len(failures)}/{total_tested} Passed ===")
    if failures:
        print(f"Encountered {len(failures)} failures:")
        for case, tab, msgs in failures:
            print(f"  - {case} | {tab}: {msgs}")
        sys.exit(1)
    else:
        print("ALL SCENARIOS PASSED WITH ZERO CRASHES!")


if __name__ == "__main__":
    run_stress_tests()
