from __future__ import annotations

"""FossilScope bridge to the shared Sentinel Forge Web theme.

SRIC Core 0.5.15 owns the canonical tokens. The fallback exists only so an existing
FossilScope 0.5.14 installation can update the product before its shared runtime is
repaired/upgraded; clean 0.5.15 installs resolve the SRIC-owned constant.
"""

try:
    from sric.web_theme import SENTINEL_THEME_TOKENS_CSS as SENTINEL_THEME_TOKENS_CSS
except ModuleNotFoundError:
    SENTINEL_THEME_TOKENS_CSS = r'''
:root {
  color-scheme: dark;
  font-family: "Segoe UI Variable Text", "Segoe UI Variable", Aptos, Inter, ui-sans-serif,
    system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #0b0f14;
  color: #e7edf3;
  --page: #0b0f14;
  --rail: #0e141b;
  --surface: #121922;
  --surface-2: #161f29;
  --surface-3: #0f151d;
  --line: #283544;
  --line-soft: #202b38;
  --text: #e7edf3;
  --text-soft: #b5c0ca;
  --muted: #8796a6;
  --accent: #5aa9b8;
  --accent-strong: #70bdca;
  --accent-soft: #132b31;
  --approval: #d2a15d;
  --approval-soft: #271f14;
  --danger: #d77b73;
  --success: #74b58c;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --font-sans: "Segoe UI Variable Text", "Segoe UI Variable", Aptos, Inter, ui-sans-serif,
    system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "Cascadia Code", SFMono-Regular, Consolas, "Liberation Mono", ui-monospace, monospace;
}
* { box-sizing: border-box; }
html { background: var(--page); }
body { margin: 0; min-height: 100vh; background: var(--page); color: var(--text); font-family: var(--font-sans); }
a { color: inherit; }
button, input, textarea, select { font: inherit; }
button:focus-visible, input:focus-visible, textarea:focus-visible, select:focus-visible, a:focus-visible {
  outline: 2px solid var(--accent-strong); outline-offset: 2px;
}
'''.strip()
