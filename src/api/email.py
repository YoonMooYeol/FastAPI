
from fastapi import APIRouter, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from schema.response import EmailSchema


router = APIRouter(prefix="/email")

# FastAPI-Mail 설정
conf = ConnectionConfig(
    MAIL_USERNAME="test@example.com",
    MAIL_PASSWORD="password",
    MAIL_FROM="test@example.com",
    MAIL_FROM_NAME="Test App",
    MAIL_SERVER="127.0.0.1",
    MAIL_PORT=1025,
    MAIL_STARTTLS=False,  # 최신 버전에서 사용되는 필드
    MAIL_SSL_TLS=False,  # 최신 버전에서 사용되는 필드
    USE_CREDENTIALS=False,  # Mailhog에서는 인증 필요 없음  # 절대 경로 사용
)

@router.post("/send/")
async def send_email(email: EmailSchema):

    message = MessageSchema(
        subject=email.subject,
        recipients=email.recipients,
        body=email.body,
        subtype="html",
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
