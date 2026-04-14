from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.schemas.contact import ContactResponse, ContactSubmission
from app.services.contact_mail_service import ContactMailService, ContactSendError

router = APIRouter(prefix="/api/contact", tags=["contact"])


def get_contact_service(
    settings: Settings = Depends(get_settings),
) -> ContactMailService:
    return ContactMailService(settings)


@router.post(
    "",
    response_model=ContactResponse,
)
async def create_contact(
    company_name: str = Form(...),
    person_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
    contact_service: ContactMailService = Depends(get_contact_service),
):
    submission = ContactSubmission(
        company_name=company_name.strip(),
        person_name=person_name.strip(),
        email=email.strip(),
        phone=phone.strip(),
        message=message.strip(),
    )

    if not all(
        [
            submission.company_name,
            submission.person_name,
            submission.email,
            submission.phone,
            submission.message,
        ]
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "INVALID_CONTACT_FORM",
                    "message": "入力内容を確認してください。",
                }
            },
        )

    try:
        await contact_service.send_contact_emails(submission)
    except ContactSendError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "CONTACT_SEND_FAILED",
                    "message": "お問い合わせの送信に失敗しました。時間をおいて再度お試しください。",
                }
            },
        )

    return {
        "data": {
            "sent": True,
            "message": "お問い合わせを受け付けました。",
        }
    }
