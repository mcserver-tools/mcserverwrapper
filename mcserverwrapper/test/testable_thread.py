"""Code from https://gist.github.com/sbrugman/59b3535ebcd5aa0e2598293cfa58b6ab"""

import threading

class TestableThread(threading.Thread):
    """Wrapper around `threading.Thread` that propagates exceptions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exc = None

    def run(self):
        try:
            super().run()
        # pylint: disable-next=broad-exception-caught
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super().join(timeout)
        if self.exc:
            raise self.exc
