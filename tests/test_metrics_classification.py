from __future__ import annotations

import pytest

from api.core.metrics import _classify_error, _classify_status


class TestClassifyStatus:
    """Tests for _classify_status function."""

    def test_success_for_200(self) -> None:
        """200 should be classified as success."""
        assert _classify_status(200) == "success"

    def test_success_for_201(self) -> None:
        """201 should be classified as success."""
        assert _classify_status(201) == "success"

    def test_success_for_204(self) -> None:
        """204 should be classified as success."""
        assert _classify_status(204) == "success"

    def test_success_for_301(self) -> None:
        """301 should be classified as success."""
        assert _classify_status(301) == "success"

    def test_error_for_400(self) -> None:
        """400 should be classified as error."""
        assert _classify_status(400) == "error"

    def test_error_for_404(self) -> None:
        """404 should be classified as error."""
        assert _classify_status(404) == "error"

    def test_error_for_500(self) -> None:
        """500 should be classified as error."""
        assert _classify_status(500) == "error"

    def test_error_for_503(self) -> None:
        """503 should be classified as error."""
        assert _classify_status(503) == "error"


class TestClassifyError:
    """Tests for _classify_error function."""

    def test_validation_error_for_400(self) -> None:
        """400 should be classified as validation_error."""
        assert _classify_error(400) == "validation_error"

    def test_validation_error_for_422(self) -> None:
        """422 should be classified as validation_error."""
        assert _classify_error(422) == "validation_error"

    def test_user_error_for_401(self) -> None:
        """401 should be classified as user_error."""
        assert _classify_error(401) == "user_error"

    def test_user_error_for_403(self) -> None:
        """403 should be classified as user_error."""
        assert _classify_error(403) == "user_error"

    def test_user_error_for_404(self) -> None:
        """404 should be classified as user_error."""
        assert _classify_error(404) == "user_error"

    def test_user_error_for_409(self) -> None:
        """409 should be classified as user_error."""
        assert _classify_error(409) == "user_error"

    def test_internal_error_for_500(self) -> None:
        """500 should be classified as internal_error."""
        assert _classify_error(500) == "internal_error"

    def test_internal_error_for_502(self) -> None:
        """502 should be classified as internal_error."""
        assert _classify_error(502) == "internal_error"

    def test_internal_error_for_503(self) -> None:
        """503 should be classified as internal_error."""
        assert _classify_error(503) == "internal_error"
