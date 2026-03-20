from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from loguru import logger

from app.services.link_service import (
    _ALPHABET,
    _SHORT_ID_LENGTH,
    _generate_short_id,
    create_link,
    get_link_by_short_id,
    increment_clicks,
)


class TestGenerateShortId(unittest.TestCase):
    def test_correct_length(self) -> None:
        short_id = _generate_short_id()
        logger.debug("Generated short_id: '{}' (length={})", short_id, len(short_id))
        self.assertEqual(len(short_id), _SHORT_ID_LENGTH)

    def test_only_allowed_characters(self) -> None:
        for _ in range(50):
            short_id = _generate_short_id()
            self.assertTrue(
                all(c in _ALPHABET for c in short_id),
                f"Unexpected character in short_id: {short_id}",
            )

    def test_generates_unique_ids(self) -> None:
        ids = {_generate_short_id() for _ in range(200)}
        logger.debug("Unique IDs generated: {}/200", len(ids))
        self.assertGreater(len(ids), 190)


class TestCreateLink(unittest.IsolatedAsyncioTestCase):
    async def test_adds_and_commits(self) -> None:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()

        with patch("app.services.link_service._generate_short_id", return_value="abc12345"):
            result = await create_link(mock_session, "https://example.com")

        logger.debug("create_link called add/commit/refresh — all asserted")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    async def test_rollback_on_commit_error(self) -> None:
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit.side_effect = RuntimeError("db error")

        with self.assertRaises(RuntimeError):
            await create_link(mock_session, "https://example.com")

        logger.debug("RuntimeError on commit triggered rollback as expected")
        mock_session.rollback.assert_awaited_once()


class TestGetLinkByShortId(unittest.IsolatedAsyncioTestCase):
    async def test_returns_link_when_found(self) -> None:
        mock_session = AsyncMock()
        mock_link = MagicMock()
        mock_link.short_id = "abc12345"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_session.execute.return_value = mock_result

        result = await get_link_by_short_id(mock_session, "abc12345")

        logger.debug("get_link_by_short_id('abc12345') returned link with short_id='{}'", result.short_id)
        self.assertEqual(result, mock_link)
        mock_session.execute.assert_awaited_once()

    async def test_returns_none_when_not_found(self) -> None:
        mock_session = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await get_link_by_short_id(mock_session, "notexist")

        logger.debug("get_link_by_short_id('notexist') correctly returned None")
        self.assertIsNone(result)


class TestIncrementClicks(unittest.IsolatedAsyncioTestCase):
    async def test_increments_and_commits(self) -> None:
        mock_session = AsyncMock()
        mock_link = MagicMock()
        mock_link.clicks = 5

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_session.execute.return_value = mock_result

        result = await increment_clicks(mock_session, "abc12345")

        logger.debug("clicks incremented: 5 -> {}", mock_link.clicks)
        self.assertEqual(mock_link.clicks, 6)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        self.assertEqual(result, mock_link)

    async def test_returns_none_when_link_missing(self) -> None:
        mock_session = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await increment_clicks(mock_session, "ghost")

        logger.debug("increment_clicks('ghost') returned None, commit not called")
        self.assertIsNone(result)
        mock_session.commit.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
