"""Select the application frame on local Streamlit and Community Cloud.

Cloud can wrap the actual app in an iframe. This adapter keeps test selectors
inside the app while download events and screenshots use its browser page.
"""
import time

class BrowserApp:
    def __init__(self, page):
        self.page = page
        self.frame = page.main_frame

    def goto(self, url, **kwargs):
        self.page.goto(url, wait_until='domcontentloaded', timeout=45000)
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            for frame in self.page.frames:
                try:
                    if frame.get_by_role('heading', name='Universal Data Automation Toolkit', exact=True).count():
                        self.frame = frame
                        return
                except Exception:
                    # A redirect or iframe replacement may detach a frame.
                    continue
            self.page.wait_for_timeout(250)
        raise RuntimeError('The app did not render its expected heading. Check deployment logs or reboot the hosted app.')

    def __getattr__(self, name):
        if name in {'expect_download', 'screenshot', 'wait_for_timeout'}:
            return getattr(self.page, name)
        return getattr(self.frame, name)
