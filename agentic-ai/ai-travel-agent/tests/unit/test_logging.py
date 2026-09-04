import logging as stdlib_logging

import pytest

from app.common.utils import logging


class TestLifecycleLogging:
    def test_info_is_the_default_level(self, caplog):
        class Service:
            @logging
            def run(self):
                return "done"

        with caplog.at_level(stdlib_logging.INFO, logger=Service.run.__module__):
            result = Service().run()

        assert result == "done"
        assert "Entering" in caplog.messages[0]
        assert "Completed" in caplog.messages[1]
        assert all(record.levelno == stdlib_logging.INFO for record in caplog.records)

    def test_level_can_be_overridden(self, caplog):
        class Service:
            @logging(level=stdlib_logging.DEBUG)
            def run(self):
                return "done"

        with caplog.at_level(stdlib_logging.DEBUG, logger=Service.run.__module__):
            Service().run()

        assert all(record.levelno == stdlib_logging.DEBUG for record in caplog.records)

    def test_errors_are_logged_and_reraised(self, caplog):
        class Service:
            @logging
            def run(self):
                raise ValueError("failure")

        with caplog.at_level(stdlib_logging.DEBUG, logger=Service.run.__module__):
            with pytest.raises(ValueError, match="failure"):
                Service().run()

        assert "Failed" in caplog.messages[1]
