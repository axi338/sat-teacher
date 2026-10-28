"""
Central translations module.
Usage: from translations import T, get_lang
       text = T[lang]["welcome"]
"""
from __future__ import annotations

T: dict[str, dict[str, str]] = {
    "uz": {
        # ── Onboarding ─────────────────────────────────────────────────────
        "choose_language": (
            "🌐 <b>Tilni tanlang / Choose your language</b>"
        ),
        "language_set": "✅ Til tanlandi: <b>O'zbekcha</b>",

        # ── Welcome ────────────────────────────────────────────────────────
        "welcome": (
            "<b>SAT ni 0 dan o'rganish — To'liq Kurs 🎓</b>\n\n"
            "Salom! Bu bot orqali siz <b>SAT ni noldan o'rganishga "
            "mo'ljallangan to'liq kursga</b> kirish huquqini olishingiz mumkin.\n\n"
            "Kursda nima bor?\n"
            "📖 Reading, Writing va Math bo'limlari\n"
            "🎯 Boshlang'ichdan yuqori darajagacha tushuntirishlar\n"
            "📝 Mashqlar, testlar va tahlillar\n\n"
            "<b>Kursga kirish — bepul. Faqat 3 ta do'stingizni taklif qiling.</b>\n\n"
            "<b>Qanday ishlaydi:</b>\n\n"
            "1️⃣ Quyidagi 4 ta kanalga a'zo bo'ling\n"
            "2️⃣ O'z shaxsiy havola orqali 3 do'stingizni taklif qiling\n"
            "3️⃣ Do'stlaringiz a'zo bo'lgach, "
            "<b>kursga kirish havolasi avtomatik yuboriladi 🎉</b>\n\n"
            "Boshlash uchun pastdagi tugmani bosing 👇"
        ),
        "referred_welcome": (
            "👋 <b>Siz do'stingiz taklifi orqali keldingiz!</b>\n\n"
            "Siz ham <b>SAT ni 0 dan o'rganishga to'liq kursga</b> "
            "bepul kirish huquqini olishingiz mumkin.\n\n"
            "Buning uchun avval quyidagi 4 ta kanalga a'zo bo'ling — "
            "a'zoligingiz tasdiqlanса, do'stingiz ham kredit oladi. ✅"
        ),

        # ── Dashboard ──────────────────────────────────────────────────────
        "dashboard": (
            "🎓 <b>SAT ni 0 dan o'rganish — To'liq Kurs</b>\n\n"
            "Kursga kirish uchun <b>{n} ta do'stingizni</b> taklif qiling.\n\n"
            "<b>Sizning natijangiz:</b>\n{bar}\n\n"
            "Taklif hisobga olinishi uchun do'stingiz:\n"
            "✅ Sizning havolangiz orqali botga kirishi kerak\n"
            "✅ 4 ta kanalga a'zo bo'lishi kerak\n\n"
            "<b>Sizning shaxsiy havola:</b>\n{link}"
        ),

        # ── Referral status ────────────────────────────────────────────────
        "status_header": "🎓 <b>SAT ni 0 dan o'rganish — To'liq Kurs</b>",
        "status_progress_title": "<b>Taklif natijalari</b>",
        "status_verified": "✅ Do'st {n} — Tasdiqlandi ({label})",
        "status_pending": "⏳ Do'st {n} — Kutilmoqda ({label})",
        "status_waiting": "⏳ Do'st {n} — Kutilmoqda",
        "status_need_more": "<b>Yana {n} ta muvaffaqiyatli taklif kerak!</b>",
        "status_channel_note": "Do'stingiz 4 ta kanalga a'zo bo'lsagina taklif hisobga olinadi.",
        "status_complete": "🎉 <b>Barcha taklif to'liq — kursga kirish havolasi tayyor!</b>",
        "not_started": "Iltimos, avval /start ni bosing.",

        # ── Channels step ──────────────────────────────────────────────────
        "channels_step": (
            "📋 <b>1-qadam — Kanallarga a'zo bo'ling</b>\n\n"
            "Quyidagi 4 ta kanalga a'zo bo'ling:\n\n"
            "<b>1. Salohiddin SAT</b>\n"
            "<b>2. You Can Do It</b>\n"
            "<b>3. SAT Valley</b>\n"
            "<b>4. SAT Humoyunbek</b>\n\n"
            "A'zo bo'lgach, pastga qaytib bosing:\n"
            "<b>✅ A'zolikni tekshirish</b>"
        ),

        # ── Almost there ───────────────────────────────────────────────────
        "almost_there_single": (
            "⏳ <b>Sal qoldi!</b>\n\n"
            "Hali <b>{ch}</b> kanaliga a'zo bo'lmagansiz — "
            "shu sababli taklif hisobga olinmadi.\n\n"
            "A'zo bo'lib, keyin pastdagi tugmani bosing: "
            "<b>✅ A'zolikni tekshirish</b>\n\n"
            "4 ta kanal tasdiqlangach, taklif avtomatik hisobga olinadi."
        ),
        "almost_there_multi": (
            "⏳ <b>Sal qoldi!</b>\n\n"
            "Hali quyidagi kanallarga a'zo bo'lmagansiz: {ch} — "
            "shu sababli taklif hisobga olinmadi.\n\n"
            "A'zo bo'lib, keyin pastdagi tugmani bosing: "
            "<b>✅ A'zolikni tekshirish</b>\n\n"
            "4 ta kanal tasdiqlangach, taklif avtomatik hisobga olinadi."
        ),

        # ── Unlock ─────────────────────────────────────────────────────────
        "unlock_success": (
            "🎉 <b>Tabriklaymiz! Kursga kirishingiz ochildi!</b>\n\n"
            "Siz muvaffaqiyatli <b>{n} ta do'stingizni</b> taklif qildingiz.\n\n"
            "Quyidagi <b>shaxsiy bir martalik havola</b> faqat siz uchun:\n\n"
            "🔗 {link}\n\n"
            "⚠️ Bu havola faqat bir marta ishlatiladi. Hoziroq bosing va kursga kiring!"
        ),
        "access_link_resend": (
            "🔗 <b>Sizning kursga kirish havolangiz:</b>\n\n"
            "{link}\n\n"
            "Bu shaxsiy havolangiz. Agar hali kirmagansiz, hoziroq bosing."
        ),
        "post_reward": (
            "🚀 <b>Do'stlaringizga ham ayting!</b>\n\n"
            "Ular ham SAT kursini bepul o'rganishlari mumkin — "
            "shaxsiy havolangizni ulashing va ularga yordam bering."
        ),

        # ── Membership confirmed ───────────────────────────────────────────
        "membership_confirmed_unlocked": (
            "✅ <b>A'zolik tasdiqlandi.</b>\n\n"
            "Siz allaqachon kursga kirish havolasini oldingiz!"
        ),
        "membership_confirmed": (
            "✅ <b>A'zolik tasdiqlandi.</b>\n\n"
            "{dashboard}"
        ),

        # ── Buttons ────────────────────────────────────────────────────────
        "btn_get_link":   "🎓 Kursga kirish havolasini olish",
        "btn_invite":     "📤 Do'stlarni taklif qilish",
        "btn_progress":   "🔄 Natijamni ko'rish",
        "btn_channels":   "📋 Kanallar ro'yxati",
        "btn_check":      "✅ A'zolikni tekshirish",
        "btn_refresh":    "🔄 Natijani yangilash",
        "btn_more":       "📤 Yana do'st taklif qilish",
        "btn_unlock":     "🎓 Kursga kirish havolasini olish",
        "btn_explore":    "🚀 SAT Valley ni ko'rish",
        "btn_join_sat":   "📢 SAT Valley ga qo'shilish",
        "btn_join_ch":    "📋 Kanallarga a'zo bo'lish",
        "btn_lang_uz":    "🇺🇿 O'zbekcha",
        "btn_lang_en":    "🇬🇧 English",
    },

    "en": {
        # ── Onboarding ─────────────────────────────────────────────────────
        "choose_language": (
            "🌐 <b>Tilni tanlang / Choose your language</b>"
        ),
        "language_set": "✅ Language set: <b>English</b>",

        # ── Welcome ────────────────────────────────────────────────────────
        "welcome": (
            "<b>SAT Full Course — From Zero to Success 🎓</b>\n\n"
            "Welcome! Through this bot you can unlock access to our "
            "<b>complete SAT course designed for absolute beginners.</b>\n\n"
            "What's inside the course?\n"
            "📖 All sections: Reading, Writing & Math\n"
            "🎯 Step-by-step explanations from basics to advanced\n"
            "📝 Practice questions, tests & detailed breakdowns\n\n"
            "<b>Access is completely free — just invite 3 friends.</b>\n\n"
            "<b>How it works:</b>\n\n"
            "1️⃣ Join all 4 required channels below\n"
            "2️⃣ Share your personal invite link with 3 friends\n"
            "3️⃣ Once your friends join, "
            "<b>your course access link is sent automatically 🎉</b>\n\n"
            "Tap the button below to get started 👇"
        ),
        "referred_welcome": (
            "👋 <b>You were invited by a friend!</b>\n\n"
            "You can also get free access to the "
            "<b>SAT Full Course from Scratch.</b>\n\n"
            "First, join all 4 required channels below — "
            "once verified, your friend gets credit too. ✅"
        ),

        # ── Dashboard ──────────────────────────────────────────────────────
        "dashboard": (
            "🎓 <b>SAT Full Course — From Zero to Success</b>\n\n"
            "Invite <b>{n} friends</b> to unlock your course access.\n\n"
            "<b>Your progress:</b>\n{bar}\n\n"
            "For a referral to count, your friend must:\n"
            "✅ Open this bot through your personal invite link\n"
            "✅ Join all 4 required channels\n\n"
            "<b>Your personal invite link:</b>\n{link}"
        ),

        # ── Referral status ────────────────────────────────────────────────
        "status_header": "🎓 <b>SAT Full Course — From Zero to Success</b>",
        "status_progress_title": "<b>Referral Progress</b>",
        "status_verified": "✅ Friend {n} — Verified ({label})",
        "status_pending": "⏳ Friend {n} — Pending ({label})",
        "status_waiting": "⏳ Friend {n} — Waiting",
        "status_need_more": "<b>{n} more successful referral{s} needed!</b>",
        "status_channel_note": "Your friend must join all 4 channels for the referral to count.",
        "status_complete": "🎉 <b>All referrals complete — your access link is ready!</b>",
        "not_started": "Please send /start first.",

        # ── Channels step ──────────────────────────────────────────────────
        "channels_step": (
            "📋 <b>Step 1 — Join the required channels</b>\n\n"
            "Join all 4 channels below:\n\n"
            "<b>1. Salohiddin SAT</b>\n"
            "<b>2. You Can Do It</b>\n"
            "<b>3. SAT Valley</b>\n"
            "<b>4. SAT Humoyunbek</b>\n\n"
            "After joining all four, return here and tap:\n"
            "<b>✅ Check My Membership</b>"
        ),

        # ── Almost there ───────────────────────────────────────────────────
        "almost_there_single": (
            "⏳ <b>Almost there!</b>\n\n"
            "You still haven't joined the <b>{ch}</b> channel — "
            "so this referral hasn't been counted yet.\n\n"
            "Join the remaining channel(s), then tap: "
            "<b>✅ Check My Membership</b>\n\n"
            "Once all 4 are confirmed, the referral will be added automatically."
        ),
        "almost_there_multi": (
            "⏳ <b>Almost there!</b>\n\n"
            "You still haven't joined: {ch} — "
            "so this referral hasn't been counted yet.\n\n"
            "Join the remaining channel(s), then tap: "
            "<b>✅ Check My Membership</b>\n\n"
            "Once all 4 are confirmed, the referral will be added automatically."
        ),

        # ── Unlock ─────────────────────────────────────────────────────────
        "unlock_success": (
            "🎉 <b>Congratulations! Your course access is unlocked!</b>\n\n"
            "You've successfully invited <b>{n} friends.</b>\n\n"
            "Here is your <b>personal one-time access link</b> — for you only:\n\n"
            "🔗 {link}\n\n"
            "⚠️ This link can only be used once. Tap it now to join the course!"
        ),
        "access_link_resend": (
            "🔗 <b>Your course access link:</b>\n\n"
            "{link}\n\n"
            "This is your personal link. If you haven't joined yet, tap it now."
        ),
        "post_reward": (
            "🚀 <b>Spread the word!</b>\n\n"
            "Your friends can also get free SAT course access — "
            "share your personal link and help them get started."
        ),

        # ── Membership confirmed ───────────────────────────────────────────
        "membership_confirmed_unlocked": (
            "✅ <b>Membership confirmed.</b>\n\n"
            "You've already received your course access link!"
        ),
        "membership_confirmed": (
            "✅ <b>Membership confirmed.</b>\n\n"
            "{dashboard}"
        ),

        # ── Buttons ────────────────────────────────────────────────────────
        "btn_get_link":   "🎓 Get Course Access Link",
        "btn_invite":     "📤 Invite Friends",
        "btn_progress":   "🔄 Check My Progress",
        "btn_channels":   "📋 Required Channels",
        "btn_check":      "✅ Check My Membership",
        "btn_refresh":    "🔄 Refresh Status",
        "btn_more":       "📤 Invite More Friends",
        "btn_unlock":     "🎓 Get Course Access Link",
        "btn_explore":    "🚀 Explore SAT Valley",
        "btn_join_sat":   "📢 Join SAT Valley",
        "btn_join_ch":    "📋 Join Required Channels",
        "btn_lang_uz":    "🇺🇿 O'zbekcha",
        "btn_lang_en":    "🇬🇧 English",
    },
}


def get_lang(user: dict | None) -> str:
    """Return user's saved language, defaulting to 'uz'."""
    if not user:
        return "uz"
    return user.get("lang") or "uz"
