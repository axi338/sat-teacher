import asyncio
import os
import unittest
from pathlib import Path

# Use a test database
os.environ["DATABASE_PATH"] = "data/test_bot.db"

import database as db
from config import BOT_USERNAME, CHANNELS, REQUIRED_REFERRALS
from services.referral_service import parse_referral_payload, process_referral_start


class TestReferralBot(unittest.TestCase):
    def setUp(self):
        # Clean up test database if exists
        test_db = Path("data/bot.db")
        # Ensure database is initialized
        asyncio.run(db.init_db())

    def test_channels_config(self):
        """Verify 3 channels are configured."""
        self.assertEqual(len(CHANNELS), 3)
        self.assertEqual(REQUIRED_REFERRALS, 3)

    def test_deep_link_parsing(self):
        """Verify ref_<id> deep link format parsing."""
        self.assertEqual(parse_referral_payload("ref_5129658601"), 5129658601)
        self.assertEqual(parse_referral_payload("5129658601"), 5129658601)
        self.assertIsNone(parse_referral_payload("invalid_link"))
        self.assertIsNone(parse_referral_payload(None))

    def test_database_and_credit_flow(self):
        async def run_flow():
            await db.init_db()

            # Create referrer user (User A)
            user_a = await db.create_user(1001, "User A", "user_a")
            self.assertEqual(user_a["telegram_id"], 1001)

            # User B enters via User A's referral link
            payload = "ref_1001"
            inviter_id = await process_referral_start(1002, payload)
            self.assertEqual(inviter_id, 1001)

            # User B created in DB with invited_by = 1001, but referral_credited = 0
            user_b = await db.create_user(1002, "User B", "user_b", invited_by=inviter_id)
            self.assertEqual(user_b["invited_by"], 1001)

            # Verify inviter count is still 0 before 3-channel verification
            inviter = await db.get_user(1001)
            self.assertEqual(inviter["referral_count"], 0)

            # User B verifies membership -> credit_referral called
            credited, new_count = await db.credit_referral(1001, 1002)
            self.assertTrue(credited)
            self.assertEqual(new_count, 1)

            # Check double credit prevention (User B try credit again)
            credited2, count2 = await db.credit_referral(1001, 1002)
            self.assertFalse(credited2)
            self.assertEqual(count2, 1)

            # Add 2 more referred users for User A
            for uid in [1003, 1004]:
                await db.create_user(uid, f"User {uid}", f"user_{uid}", invited_by=1001)
                await db.credit_referral(1001, uid)

            inviter_updated = await db.get_user(1001)
            self.assertEqual(inviter_updated["referral_count"], 3)

            stats = await db.get_campaign_stats()
            self.assertGreaterEqual(stats["total_users"], 4)
            self.assertGreaterEqual(stats["users_with_3_referrals"], 1)

        asyncio.run(run_flow())


if __name__ == "__main__":
    unittest.main()
