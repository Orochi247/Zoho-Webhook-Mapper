"""
Setup:
    pip install playwright
 
Run:
    python webhook_mapper.py keys.json              # all rows
    python webhook_mapper.py keys.json --start 40   # resume from row index 40 (0-based)
    python webhook_mapper.py keys.json --limit 3    # test on 3 rows first
"""
import argparse
import json
from pathlib import Path
 
from playwright.sync_api import sync_playwright
 
WEBHOOK_URL = (
    "https://forms.zoho.com/houzeo/form/"
    "NMGreaterAlbuquerqueAORSWMLSMLSDataInputForm/integrate"
)
LEFT_INPUT = "input[name='webhookentityname']"
BROWSER_CHANNEL = "chrome"          # "chrome" or "msedge" (uses the browser already installed)
PROFILE_DIR = "./zoho_profile"      # keeps your login/MFA session between runs
FAILED_LOG = Path("failed_rows.txt")
TYPE_DELAY_MS = 5                   # per-keystroke delay; raise if autofill misses
SETTLE_MS = 250                     # wait after each row so Zoho can autofill the dropdown
 
 
def load_keys(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.keys())
    if isinstance(data, list):
        return [str(k) for k in data]
    raise ValueError("JSON must be an object or a list")
 
 
def fill_row(page, index, key):
    box = page.locator(LEFT_INPUT).nth(index)
    box.scroll_into_view_if_needed()
    box.click()
    box.press("Control+A")
    box.press("Delete")
    box.press_sequentially(key, delay=TYPE_DELAY_MS)  # real key events -> onkeyup fires
    box.press("Tab")                                   # blur/change so autofill triggers
    page.wait_for_timeout(SETTLE_MS)
 
    if box.input_value() != key:
        raise RuntimeError(f"value mismatch, got {box.input_value()!r}")
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
 
    keys = load_keys(args.json_file)[args.start:]
    if args.limit:
        keys = keys[: args.limit]
 
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE_DIR, channel=BROWSER_CHANNEL, headless=False
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(WEBHOOK_URL)
 
        input("Log in if needed, open the Webhooks configuration, then press Enter...")
 
        rows = page.locator(LEFT_INPUT).count()
        needed = args.start + len(keys)
        print(f"Found {rows} rows on the page, need {needed}.")
        if rows < needed:
            print("WARNING: fewer rows than keys; extra keys will be logged as failed.")
 
        for offset, key in enumerate(keys):
            index = args.start + offset
            try:
                fill_row(page, index, key)
                print(f"[ok]   {index}: {key}")
            except Exception as e:
                print(f"[FAIL] {index}: {key} ({e})")
                with FAILED_LOG.open("a", encoding="utf-8") as f:
                    f.write(f"{index}\t{key}\n")
 
        input("Review the page, SAVE the webhook manually, then press Enter to close...")
        ctx.close()
 
 
if __name__ == "__main__":
    main()