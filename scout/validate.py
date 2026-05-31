"""Website URL verification.

Before surfacing a link to investors, we confirm the domain resolves and returns
a successful HTTP response. Invalid URLs are cleared so the dashboard never
shows DNS errors or dead links.
"""

from __future__ import annotations

import urllib.error
import urllib.request

DEFAULT_UA = "AI-Incorporation-Scout/1.0 (link-validator)"


def verify_url(url: str | None, timeout: int = 10, user_agent: str = DEFAULT_UA) -> bool:
    """Return True if `url` is reachable (DNS + HTTP 2xx/3xx)."""
    if not url or not url.strip():
        return False
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    headers = {"User-Agent": user_agent}
    try:
        req = urllib.request.Request(url, method="HEAD", headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as exc:
        if exc.code in (405, 403):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return 200 <= resp.status < 400
            except Exception:
                return False
        return False
    except Exception:
        return False


def verify_company_website(company, *, clear_on_fail: bool = True) -> bool:
    """Validate `company.website`, set `website_verified`, optionally clear bad URL."""
    ok = verify_url(company.website)
    company.website_verified = ok
    if not ok and clear_on_fail:
        company.website = None
    return ok
