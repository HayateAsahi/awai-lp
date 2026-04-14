from __future__ import annotations

import httpx

from app.core.config import Settings
from app.schemas.contact import ContactSubmission


class ContactSendError(Exception):
    pass


class ContactMailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_contact_emails(self, submission: ContactSubmission) -> None:
        async with httpx.AsyncClient(
            base_url="https://api.resend.com",
            timeout=15.0,
            headers={
                "Authorization": f"Bearer {self.settings.resend_api_key}",
                "Content-Type": "application/json",
            },
        ) as client:
            await self._send_admin_notification(client, submission)
            await self._send_auto_reply(client, submission)

    async def _send_admin_notification(
        self, client: httpx.AsyncClient, submission: ContactSubmission
    ) -> None:
        payload = {
            "from": self.settings.contact_from_email,
            "to": [self.settings.contact_to_email],
            "subject": "【あわいコンサルティング】LPからお問い合わせがありました",
            "text": (
                "LPのお問い合わせフォームから新しいお問い合わせが届きました。\n\n"
                f"会社名：{submission.company_name}\n"
                f"担当者名：{submission.person_name}\n"
                f"メールアドレス：{submission.email}\n"
                f"電話番号：{submission.phone}\n\n"
                "お問い合わせ内容：\n"
                f"{submission.message}\n"
            ),
        }
        await self._post_email(client, payload)

    async def _send_auto_reply(
        self, client: httpx.AsyncClient, submission: ContactSubmission
    ) -> None:
        payload = {
            "from": self.settings.contact_from_email,
            "to": [submission.email],
            "subject": "【株式会社あわいコンサルティング】お問い合わせありがとうございます",
            "text": (
                "※このメールはシステムからの自動返信です\n\n"
                "お世話になっております。\n"
                "株式会社あわいコンサルティングでございます。\n\n"
                "この度はお問い合わせいただき、誠にありがとうございます。\n"
                "以下の内容でお問い合わせを受け付けいたしました。\n\n"
                "ーーーーーーーーーーー\n"
                f"会社名：{submission.company_name}\n"
                f"担当者名：{submission.person_name}\n"
                f"メールアドレス：{submission.email}\n"
                f"電話番号：{submission.phone}\n\n"
                "お問い合わせ内容：\n"
                f"{submission.message}\n"
                "ーーーーーーーーーーー\n\n"
                "内容を確認のうえ、1営業日以内に担当者よりご連絡させていただきます。\n"
                "今しばらくお待ちくださいますようお願いいたします。\n"
            ),
        }
        await self._post_email(client, payload)

    async def _post_email(self, client: httpx.AsyncClient, payload: dict) -> None:
        try:
            response = await client.post("/emails", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ContactSendError("Failed to send contact email") from exc
