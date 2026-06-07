"""
AdBlock plugin — blocks requests to known ad/tracker domains.

Usage:
    from plugins.adblock import AdBlockPlugin
    browser.plugin_manager.register(AdBlockPlugin())
"""

from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from core.plugin import BrowserPlugin


# Minimal built-in blocklist — extend as needed
DEFAULT_BLOCKLIST = [
    "doubleclick.net",
    "googlesyndication.com",
    "googletagmanager.com",
    "googletagservices.com",
    "adservice.google.com",
    "amazon-adsystem.com",
    "ads.twitter.com",
    "advertising.com",
    "outbrain.com",
    "taboola.com",
    "adsafeprotected.com",
    "moatads.com",
    "scorecardresearch.com",
    "facebook.com/tr",
    "pixel.facebook.com",
]


class _AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocklist: list[str]):
        super().__init__()
        self.blocklist = blocklist
        self.blocked_count = 0

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl().toString()
        for domain in self.blocklist:
            if domain in url:
                info.block(True)
                self.blocked_count += 1
                return


class AdBlockPlugin(BrowserPlugin):
    name = "adblock"
    version = "1.0.0"
    description = "Blocks requests to known ad and tracker domains."

    def __init__(self, extra_domains: list[str] | None = None):
        self.blocklist = DEFAULT_BLOCKLIST + (extra_domains or [])
        self._interceptor: _AdBlockInterceptor | None = None

    def on_load(self, browser) -> None:
        self._interceptor = _AdBlockInterceptor(self.blocklist)
        browser.tab_manager.profile.setUrlRequestInterceptor(self._interceptor)
        print(f"[adblock] Active — blocking {len(self.blocklist)} domains")

    @property
    def blocked_count(self) -> int:
        return self._interceptor.blocked_count if self._interceptor else 0
