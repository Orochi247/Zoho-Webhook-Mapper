# Zoho Forms Webhook Mapper

Automates filling the **Parameter Name** column (left side) of the Zoho Forms webhook configuration page, one row at a time, from a JSON file. The right-hand field dropdown is left alone, since Zoho autofills it.

Built with [Playwright](https://playwright.dev/python/) and your already-installed Chrome or Edge, so no browser download is needed.

## How it works

1. You provide a JSON file containing the parameter names (keys).
2. The script opens Chrome with its own profile, so you log into Zoho once and the session is remembered.
3. You open the webhook configuration page and press Enter in the terminal.
4. The script fills each Parameter Name box in order, firing the same key events a real person would, so Zoho's autofill triggers.
5. You review the result and click **Save** yourself. The script never saves.

## Requirements

- Python 3.8+
- Google Chrome (or Microsoft Edge) installed
- A Zoho Forms account with access to the form's **Integrations > Webhooks** page

## Setup

```bash
pip install playwright
```

You do **not** need to run `playwright install`, because the script uses the browser already on your machine.

Open `zoho_webhook_mapper.py` and set these at the top if needed:

| Setting | Default | Purpose |
| --- | --- | --- |
| `WEBHOOK_URL` | the NC Doorify MLS form's integrate page | Page opened on launch |
| `BROWSER_CHANNEL` | `"chrome"` | Use `"msedge"` for Edge |
| `TYPE_DELAY_MS` | `5` | Delay per keystroke; raise it if autofill misses |
| `SETTLE_MS` | `250` | Wait after each row so Zoho can autofill the dropdown |

## Input JSON

The script accepts either format and uses only the keys, in order.

**Plain list**

```json
[
  "General_Features_Showing_Requirements",
  "Basic_Features_Appliances",
  "Basic_Features_Lot_Features"
]
```

**Object** (values are ignored)

```json
{
  "General_Features_Showing_Requirements": "Showing Requirements",
  "Basic_Features_Appliances": "Appliances"
}
```

Nested JSON is not flattened. Only top-level keys are used.

## Usage

Always test on a few rows first:

```bash
python zoho_webhook_mapper.py keys.json --limit 3
```

Then run the full file:

```bash
python zoho_webhook_mapper.py keys.json
```

| Option | Meaning |
| --- | --- |
| `--start N` | Start at row index N (0-based). Use this to resume or skip rows above the ones you want to fill. |
| `--limit N` | Only process N keys. Useful for testing. |

When prompted:

1. Log into Zoho in the browser window that opens (first run only).
2. Open the form's Webhooks configuration.
3. Press Enter in the terminal to start.
4. When it finishes, review the page, click **Save** in Zoho, then press Enter to close.

## Output

- Progress is printed per row as `[ok]` or `[FAIL]`.
- Failed rows are appended to `failed_rows.txt` as `index<TAB>key`.
- The script reports how many rows it found on the page against how many keys you supplied. If there are fewer rows than keys, the extra keys are logged as failed.

## Important notes

- **Row order matters.** The script starts at the first Parameter Name box on the page (`input[name='webhookentityname']`). If rows above the ones you want exist, use `--start`.
- **Test on a copy** of the webhook or form before running on production.
- **The profile folder holds your login session.** `zoho_profile/` contains cookies for your Zoho account. Never commit it or share it. See `.gitignore`.
- **Not suited to hosting.** The script drives a browser that is logged into your account, so run it locally rather than on a public server.
- Zoho can change its page structure. If the key boxes stop being found, update the `LEFT_INPUT` selector.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `playwright install chromium` fails with a download error | Not needed. The script uses installed Chrome or Edge. This error is usually a firewall, proxy or VPN issue. |
| Chrome does not launch | Close any Chrome windows using the `zoho_profile` folder, then retry. |
| Dropdown does not autofill | Increase `TYPE_DELAY_MS` and `SETTLE_MS`. |
| `value mismatch` errors | Same as above. Zoho may be rewriting the field while typing. |
| Keys land in the wrong rows | Check which row is first on the page and use `--start N`. |

## Disclaimer

This is an unofficial helper and is not affiliated with Zoho. Use it only on accounts and forms you are authorized to edit.
