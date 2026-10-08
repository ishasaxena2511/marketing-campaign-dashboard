"""
Automated Executive Screenshot Tool for Marketing Campaign Intelligence Dashboard
Captures high-resolution, production-grade screenshots using Playwright Chromium (1920x1200 @ 2x DPR).
Saves outputs directly to the existing `screenshots/` directory without deleting existing files.
"""

import sys
import time
import subprocess
import urllib.request
from pathlib import Path

# Ensure UTF-8 stdout
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = REPO_ROOT / "screenshots"
PORT = 8599
BASE_URL = f"http://localhost:{PORT}"


def wait_for_server(url: str, timeout: int = 60) -> bool:
    """Poll Streamlit server health endpoint until ready."""
    print(f"Waiting for Streamlit app to start on {url} (timeout {timeout}s)...")
    start_time = time.time()
    health_url = f"{url}/_stcore/health"
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as resp:
                if resp.status == 200:
                    print(f"Streamlit server is ready on {url} (took {time.time() - start_time:.1f}s)")
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def wait_for_streamlit_ready(page, timeout_ms: int = 35000):
    """
    Ensures Streamlit execution is complete:
    - Waits for status widget running indicator to disappear
    - Waits for spinners and skeletons to detach
    - Waits for all Plotly charts to mount and render SVG layers
    - Adds a 1.5s buffer for CSS transitions and animations
    """
    page.wait_for_function(
        """() => {
            const status = document.querySelector('[data-testid="stStatusWidget"]');
            const spinner = document.querySelector('.stSpinner');
            const skeleton = document.querySelector('[data-testid="stSkeleton"]');
            const isRunning = status && (status.innerText.includes("Running") || status.getAttribute("aria-live") === "polite");
            return !isRunning && !spinner && !skeleton;
        }""",
        timeout=timeout_ms,
    )

    # Ensure Plotly charts have rendered their SVG layer
    page.wait_for_function(
        """() => {
            const plots = document.querySelectorAll('.js-plotly-plot');
            if (plots.length === 0) return true;
            for (const p of plots) {
                if (!p.querySelector('.plot-container') && !p.querySelector('svg')) return false;
            }
            return true;
        }""",
        timeout=timeout_ms,
    )

    page.wait_for_timeout(1500)


def scroll_entire_page(page):
    """Scroll through the page smoothly to trigger lazy mounting of all Plotly charts."""
    page.evaluate(
        """async () => {
            const scroller = document.querySelector('section[data-testid="stMain"]') ||
                             document.querySelector('[data-testid="stAppViewContainer"]') ||
                             window;
            const total = scroller.scrollHeight || document.body.scrollHeight;
            for (let y = 0; y < total; y += 400) {
                if (scroller.scrollTo) scroller.scrollTo(0, y);
                else window.scrollTo(0, y);
                await new Promise(r => setTimeout(r, 60));
            }
            if (scroller.scrollTo) scroller.scrollTo(0, 0);
            else window.scrollTo(0, 0);
        }"""
    )
    page.wait_for_timeout(1000)


def capture_full_dashboard(page, output_path: Path):
    """
    Captures the entire dashboard without cropping.
    Temporarily expands viewport height to match content scroll height.
    """
    scroll_entire_page(page)
    wait_for_streamlit_ready(page)

    # Determine full content height
    content_height = page.evaluate(
        """() => {
            const el = document.querySelector('[data-testid="stAppViewBlockContainer"]') ||
                       document.querySelector('section[data-testid="stMain"]') ||
                       document.body;
            return Math.max(el.scrollHeight, document.body.scrollHeight, 1200);
        }"""
    )

    orig_viewport = page.viewport_size
    target_height = int(content_height) + 120
    page.set_viewport_size({"width": 1920, "height": target_height})
    page.wait_for_timeout(1000)

    # Capture page
    page.screenshot(path=str(output_path), full_page=True)

    # Restore viewport
    page.set_viewport_size(orig_viewport)
    page.wait_for_timeout(500)


def capture_kpi_section(page, output_path: Path) -> bool:
    """Captures just the dual-tier KPI cards section."""
    cards = page.locator(".kpi-card")
    count = cards.count()
    if count == 0:
        print("  [WARN] No .kpi-card elements found.")
        return False

    cards.first.scroll_into_view_if_needed()
    page.wait_for_timeout(600)

    boxes = []
    for i in range(count):
        b = cards.nth(i).bounding_box()
        if b:
            boxes.append(b)

    if not boxes:
        return False

    pad = 16
    min_x = max(0, min(b["x"] for b in boxes) - pad)
    min_y = max(0, min(b["y"] for b in boxes) - pad)
    max_x = max(b["x"] + b["width"] for b in boxes) + pad
    max_y = max(b["y"] + b["height"] for b in boxes) + pad

    page.screenshot(
        path=str(output_path),
        clip={"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y},
    )
    return True


def capture_card_container(page, title_text: str, output_path: Path, extra_wait_ms: int = 700) -> bool:
    """Locates an executive card container by its title and captures it."""
    title_loc = page.locator(f'.exec-card-title:has-text("{title_text}"), .card-title:has-text("{title_text}")')
    if title_loc.count() == 0:
        title_loc = page.locator(f'*:has-text("{title_text}")')

    if title_loc.count() == 0:
        print(f"  [WARN] Title '{title_text}' not found.")
        return False

    el = title_loc.first
    container = el.locator('xpath=ancestor::div[@data-testid="stVerticalBlockBorderWrapper"]').first
    if container.count() == 0:
        container = el.locator('xpath=ancestor::div[contains(@class, "stVerticalBlock") or @data-testid="stVerticalBlockBorderWrapper"][1]')

    target = container if container.count() > 0 else el
    target.scroll_into_view_if_needed()
    page.wait_for_timeout(extra_wait_ms)
    target.screenshot(path=str(output_path))
    return True


def capture_combined_cards(page, title1: str, title2: str, output_path: Path) -> bool:
    """Captures two adjacent card sections in one combined screenshot."""
    t1 = page.locator(f'.exec-card-title:has-text("{title1}")').first
    t2 = page.locator(f'.exec-card-title:has-text("{title2}")').first
    if t1.count() > 0 and t2.count() > 0:
        c1 = t1.locator('xpath=ancestor::div[@data-testid="stVerticalBlockBorderWrapper"]').first
        c2 = t2.locator('xpath=ancestor::div[@data-testid="stVerticalBlockBorderWrapper"]').first
        if c1.count() > 0 and c2.count() > 0:
            c1.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            c2.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
            b1 = c1.bounding_box()
            b2 = c2.bounding_box()
            if b1 and b2:
                pad = 12
                min_x = max(0, min(b1["x"], b2["x"]) - pad)
                min_y = max(0, min(b1["y"], b2["y"]) - pad)
                max_x = max(b1["x"] + b1["width"], b2["x"] + b2["width"]) + pad
                max_y = max(b1["y"] + b1["height"], b2["y"] + b2["height"]) + pad
                page.screenshot(
                    path=str(output_path),
                    clip={"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y},
                )
                return True
    return capture_card_container(page, title1, output_path)


def run_capture_suite():
    """Main execution routine generating all 12 screenshots."""
    print("=" * 70)
    print("STARTING AUTOMATED SCREENSHOT SUITE")
    print(f"Output directory: {SCREENSHOTS_DIR}")
    print("=" * 70)

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app/main.py",
        "--server.headless",
        "true",
        "--server.port",
        str(PORT),
    ]

    print(f"Launching Streamlit on port {PORT}: {' '.join(streamlit_cmd)}")
    proc = subprocess.Popen(
        streamlit_cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    results = []
    overall_success = True

    try:
        if not wait_for_server(BASE_URL, timeout=60):
            print("ERROR: Streamlit server failed to start within 60s timeout.")
            return False

        with sync_playwright() as p:
            print("Launching Headless Chromium (1920x1200 @ 2x DPR)...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1200},
                device_scale_factor=2,
            )
            page = context.new_page()

            print(f"Navigating to {BASE_URL}...")
            page.goto(BASE_URL, wait_until="networkidle")

            # CRITICAL: Wait for initial dashboard widgets to fully mount
            print("Waiting for dashboard widgets to mount...")
            page.wait_for_selector(".kpi-card", timeout=45000)
            wait_for_streamlit_ready(page)
            print("Dashboard mounted successfully!")

            # -------------------------------------------------------------
            # 01_full_dashboard.png (Executive Overview, full page)
            # -------------------------------------------------------------
            print("\nCapturing 01_full_dashboard.png...")
            f1 = SCREENSHOTS_DIR / "01_full_dashboard.png"
            # Pre-scroll down to trigger regional map and charts
            scroll_entire_page(page)
            page.wait_for_timeout(3000)
            capture_full_dashboard(page, f1)
            results.append(("01_full_dashboard.png", f1.stat().st_size if f1.exists() else 0, f1.exists()))

            # -------------------------------------------------------------
            # 02_kpi_cards.png (just the KPI section)
            # -------------------------------------------------------------
            print("Capturing 02_kpi_cards.png...")
            f2 = SCREENSHOTS_DIR / "02_kpi_cards.png"
            s2 = capture_kpi_section(page, f2)
            results.append(("02_kpi_cards.png", f2.stat().st_size if f2.exists() else 0, s2 and f2.exists()))

            # -------------------------------------------------------------
            # 03_campaign_performance.png (campaign ROI + revenue charts)
            # -------------------------------------------------------------
            print("Capturing 03_campaign_performance.png...")
            f3 = SCREENSHOTS_DIR / "03_campaign_performance.png"
            s3 = capture_combined_cards(page, "CAMPAIGN ROI ANALYSIS", "TOP 10 REVENUE DRIVERS", f3)
            results.append(("03_campaign_performance.png", f3.stat().st_size if f3.exists() else 0, s3 and f3.exists()))

            # -------------------------------------------------------------
            # 04_platform_comparison.png (platform performance section)
            # -------------------------------------------------------------
            print("Capturing 04_platform_comparison.png...")
            f4 = SCREENSHOTS_DIR / "04_platform_comparison.png"
            s4 = capture_card_container(page, "PLATFORM PERFORMANCE COMPARISON", f4)
            results.append(("04_platform_comparison.png", f4.stat().st_size if f4.exists() else 0, s4 and f4.exists()))

            # -------------------------------------------------------------
            # 05_conversion_funnel.png (funnel chart)
            # -------------------------------------------------------------
            print("Capturing 05_conversion_funnel.png...")
            f5 = SCREENSHOTS_DIR / "05_conversion_funnel.png"
            s5 = capture_card_container(page, "CONVERSION FUNNEL EFFICIENCY", f5)
            results.append(("05_conversion_funnel.png", f5.stat().st_size if f5.exists() else 0, s5 and f5.exists()))

            # -------------------------------------------------------------
            # 06_spend_vs_revenue.png (spend vs revenue chart)
            # -------------------------------------------------------------
            print("Capturing 06_spend_vs_revenue.png...")
            f6 = SCREENSHOTS_DIR / "06_spend_vs_revenue.png"
            s6 = capture_card_container(page, "MARKETING SPEND VS GROSS REVENUE", f6)
            results.append(("06_spend_vs_revenue.png", f6.stat().st_size if f6.exists() else 0, s6 and f6.exists()))

            # -------------------------------------------------------------
            # 07_audience_segments.png (audience analysis)
            # -------------------------------------------------------------
            print("Capturing 07_audience_segments.png...")
            f7 = SCREENSHOTS_DIR / "07_audience_segments.png"
            scroll_entire_page(page)
            s7 = capture_card_container(page, "AUDIENCE PERSONA EFFICIENCY", f7)
            results.append(("07_audience_segments.png", f7.stat().st_size if f7.exists() else 0, s7 and f7.exists()))

            # -------------------------------------------------------------
            # 08_regional_map.png (India regional map)
            # -------------------------------------------------------------
            print("Capturing 08_regional_map.png...")
            f8 = SCREENSHOTS_DIR / "08_regional_map.png"
            title8 = page.locator('.exec-card-title:has-text("REGIONAL PERFORMANCE MAP")').first
            title8.scroll_into_view_if_needed()
            page.wait_for_timeout(3500)
            s8 = capture_card_container(page, "REGIONAL PERFORMANCE MAP (INDIA)", f8, extra_wait_ms=1000)
            results.append(("08_regional_map.png", f8.stat().st_size if f8.exists() else 0, s8 and f8.exists()))

            # -------------------------------------------------------------
            # 09_filtered_view.png (apply sidebar filter e.g. Platform = Google only)
            # -------------------------------------------------------------
            print("Capturing 09_filtered_view.png (Filtering Platform to Google only)...")
            f9 = SCREENSHOTS_DIR / "09_filtered_view.png"
            try:
                sidebar = page.locator('section[data-testid="stSidebar"]')
                plat_ms = sidebar.locator('div[data-testid="stMultiSelect"]').first

                # Clear all current selections
                clear_btn = plat_ms.locator('[aria-label="Clear all"]')
                if clear_btn.count() > 0:
                    clear_btn.first.click()
                    page.wait_for_timeout(800)

                # Focus input and open dropdown options
                input_box = plat_ms.locator('input')
                input_box.click()
                page.wait_for_timeout(500)

                # Select Google
                options = page.locator('li[role="option"], div[role="option"]')
                for i in range(options.count()):
                    if options.nth(i).inner_text().strip() == "Google":
                        options.nth(i).click()
                        break
                page.wait_for_timeout(500)
                
                # Click outside to blur input and trigger Streamlit rerun
                sidebar.locator('*:has-text("CAMPAIGN FILTERS")').first.click()
                wait_for_streamlit_ready(page)
                page.wait_for_timeout(2500)

                capture_full_dashboard(page, f9)
                results.append(("09_filtered_view.png", f9.stat().st_size if f9.exists() else 0, f9.exists()))

                # Reset filters back to default
                reset_btn = page.locator('button:has-text("Reset All Filters")')
                if reset_btn.count() > 0:
                    reset_btn.first.click()
                    wait_for_streamlit_ready(page)
            except Exception as e:
                print(f"  [WARN] Filter interaction error: {e}")
                capture_full_dashboard(page, f9)
                results.append(("09_filtered_view.png", f9.stat().st_size if f9.exists() else 0, f9.exists()))

            # -------------------------------------------------------------
            # 10_channel_insights.png (Channel Insights page)
            # -------------------------------------------------------------
            print("Capturing 10_channel_insights.png...")
            f10 = SCREENSHOTS_DIR / "10_channel_insights.png"
            tab_channels = page.locator('[data-testid="stTab"]:has-text("Channel Insights")')
            if tab_channels.count() > 0:
                tab_channels.first.click()
                wait_for_streamlit_ready(page)
                capture_full_dashboard(page, f10)
                results.append(("10_channel_insights.png", f10.stat().st_size if f10.exists() else 0, f10.exists()))
            else:
                print("  [WARN] Channel Insights tab not found.")
                results.append(("10_channel_insights.png", 0, False))

            # -------------------------------------------------------------
            # 11_campaign_drilldown.png (Campaign Drill-down page)
            # -------------------------------------------------------------
            print("Capturing 11_campaign_drilldown.png...")
            f11 = SCREENSHOTS_DIR / "11_campaign_drilldown.png"
            tab_drilldown = page.locator('[data-testid="stTab"]:has-text("Campaign Drill-Down")')
            if tab_drilldown.count() > 0:
                tab_drilldown.first.click()
                wait_for_streamlit_ready(page)
                capture_full_dashboard(page, f11)
                results.append(("11_campaign_drilldown.png", f11.stat().st_size if f11.exists() else 0, f11.exists()))
            else:
                print("  [WARN] Campaign Drill-Down tab not found.")
                results.append(("11_campaign_drilldown.png", 0, False))

            # -------------------------------------------------------------
            # 12_budget_optimiser.png (Budget Optimiser page)
            # -------------------------------------------------------------
            print("Capturing 12_budget_optimiser.png...")
            f12 = SCREENSHOTS_DIR / "12_budget_optimiser.png"
            tab_optimizer = page.locator('[data-testid="stTab"]:has-text("Budget Optimiser")')
            if tab_optimizer.count() > 0:
                tab_optimizer.first.click()
                wait_for_streamlit_ready(page)
                capture_full_dashboard(page, f12)
                results.append(("12_budget_optimiser.png", f12.stat().st_size if f12.exists() else 0, f12.exists()))
            else:
                print("  [WARN] Budget Optimiser tab not found.")
                results.append(("12_budget_optimiser.png", 0, False))

            browser.close()

    except Exception as e:
        print(f"\n[FATAL ERROR] An unhandled exception occurred: {e}")
        overall_success = False
    finally:
        print("\nShutting down background Streamlit process...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        print("Streamlit process terminated.")

    # -------------------------------------------------------------
    # Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SCREENSHOT CAPTURE SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Filename':<32} {'Size':<16} {'Status':<12}")
    print("-" * 70)

    for fname, size, ok in results:
        size_str = f"{size / 1024:.1f} KB" if size > 0 else "0 KB"
        status_str = "SUCCESS" if ok and size > 0 else "FAILED"
        if not ok or size == 0:
            overall_success = False
        print(f"{fname:<32} {size_str:<16} {status_str:<12}")

    print("=" * 70)

    if overall_success and len(results) == 12:
        print("ALL 12 SCREENSHOTS CAPTURED AND VERIFIED SUCCESSFULLY!\n")
        return True
    else:
        print("ERROR: One or more screenshots failed to capture properly.\n")
        return False


if __name__ == "__main__":
    success = run_capture_suite()
    sys.exit(0 if success else 1)
