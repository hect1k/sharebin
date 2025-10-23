import datetime

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import NameEmail

from app.core.config import Settings
from app.models.models import User

settings = Settings()

conf = ConnectionConfig(
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_verification_email(user: User, url: str):
    content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Verification - shareb.in</title>
        </head>
        <body style="background-color: #efefef; margin: 0; padding: 0;">
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1C1E21; background-color: #F4F6F8; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #D8DAE0; border-radius: 8px;">

                <div style="text-align: center; padding-bottom: 20px; border-bottom: 1px solid #D8DAE0;">
                    <a href="{settings.DOMAIN}" title="shareb.in homepage">
                        <img src="{settings.DOMAIN}/static/og-image.jpg" alt="shareb.in Logo" style="max-width: 100px; height: auto; border-radius: 4px;">
                    </a>
                    <h1 style="color: #1C1E21; font-size: 24px; margin-top: 10px; margin-bottom: 0;">Account Verification</h1>
                </div>

                <div style="padding-top: 20px;">
                    <p style="margin-bottom: 15px;">Hello {user.name},</p>

                    <p style="margin-bottom: 20px;">Thank App you for registering with <a title="shareb.in homepage" href="{settings.DOMAIN}" style="color: #008f4c; text-decoration: none;">shareb.in</a>. To complete your account setup and start sharing files, please verify your email address.</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{url}" style="background-color: #008f4c; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; border: 1px solid #008f4c;">
                            VERIFY MY ACCOUNT
                        </a>
                    </div>

                    <p style="font-size: 14px; text-align: center; color: #606770; margin-top: 20px; margin-bottom: 5px;">
                        If the button above does not work, copy and paste the entire link below:
                    </p>
                    <p style="font-size: 12px; text-align: center; color: #008f4c; word-break: break-all; margin-top: 5px; margin-bottom: 30px; background-color: #efefef; padding: 10px; border-radius: 4px; border: 1px solid #D8DAE0;">
                         <a href="{url}" style="color: #008f4c; text-decoration: none;">{url}</a>
                    </p>

                    <p style="margin-top: 20px; border-top: 1px solid #D8DAE0; padding-top: 20px; font-style: italic; color: #D83C3C;">
                        <b>Important: This verification link will expire in {settings.JWT_EXPIRE_MINUTES} minutes for security reasons.</b>
                    </p>

                    <p style="margin-top: 20px; border-top: 1px solid #D8DAE0; padding-top: 20px; font-style: italic; color: #606770;">
                        This single step secures your account and unlocks features, including larger file uploads and extended expiry times.
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #D8DAE0; font-size: 12px; color: #606770; text-align: center;">
                    <p style="margin: 0;">
                        If you did not create an account on shareb.in, please safely ignore and delete this email.
                    </p>
                    <p style="margin-top: 10px;">
                        <a title="shareb.in homepage" href="{settings.DOMAIN}" style="color: #606770; text-decoration: none;">shareb.in</a> &copy; {datetime.datetime.now().year}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    message = MessageSchema(
        subject="Welcome to shareb.in! Please verify your account",
        recipients=[NameEmail(user.name, user.email)],
        body=content,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending verification email to {user.email}: {e}")
        raise e


async def send_password_reset_mail(user: User, url: str):
    content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - shareb.in</title>
        </head>
        <body style="background-color: #efefef; margin: 0; padding: 0;">
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1C1E21; background-color: #F4F6F8; max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #D8DAE0; border-radius: 8px;">
                
                <div style="text-align: center; padding-bottom: 20px; border-bottom: 1px solid #D8DAE0;">
                    <a href="{settings.DOMAIN}" title="shareb.in homepage">
                        <img src="{settings.DOMAIN}/static/og-image.jpg" alt="shareb.in Logo" style="max-width: 100px; height: auto; border-radius: 4px;">
                    </a>
                    <h1 style="color: #1C1E21; font-size: 24px; margin-top: 10px; margin-bottom: 0;">Password Reset Request</h1>
                </div>

                <div style="padding-top: 20px;">
                    <p style="margin-bottom: 15px;">Hello {user.name},</p>

                    <p style="margin-bottom: 20px;">You recently requested to reset your password for your <a title="shareb.in homepage" href="{settings.DOMAIN}" style="color: #008f4c; text-decoration: none;">shareb.in</a> account. Click the button below to proceed.</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{url}" style="background-color: #008f4c; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; border: 1px solid #008f4c;">
                            RESET PASSWORD
                        </a>
                    </div>

                    <p style="font-size: 14px; text-align: center; color: #606770; margin-top: 20px; margin-bottom: 5px;">
                        If the button above doesn't work, copy and paste the entire link below:
                    </p>
                    <p style="font-size: 12px; text-align: center; color: #008f4c; word-break: break-all; margin-top: 5px; margin-bottom: 30px; background-color: #efefef; padding: 10px; border-radius: 4px; border: 1px solid #D8DAE0;">
                         <a href="{url}" style="color: #008f4c; text-decoration: none;">{url}</a>
                    </p>

                    <p style="margin-top: 20px; border-top: 1px solid #D8DAE0; padding-top: 20px; font-style: italic; color: #D83C3C;">
                        <b>Important: This password reset link will expire in {settings.JWT_EXPIRE_MINUTES} minutes for security reasons.</b>
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #D8DAE0; font-size: 12px; color: #606770; text-align: center;">
                    <p style="margin: 0;">
                        If you did not request a password reset, please safely ignore and delete this email.
                    </p>
                    <p style="margin-top: 10px;">
                        <a title="shareb.in homepage" href="{settings.DOMAIN}" style="color: #606770; text-decoration: none;">shareb.in</a> &copy; {datetime.datetime.now().year}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    message = MessageSchema(
        subject="Password Reset Link for your shareb.in Account",
        recipients=[NameEmail(user.name, user.email)],
        body=content,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending verification email to {user.email}: {e}")
        raise e
