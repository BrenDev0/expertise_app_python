import os
import smtplib
from email.message import EmailMessage
from typing import Dict, Any
from src.core.services.webtoken_service import WebTokenService
from fastapi import HTTPException
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler


class EmailService:
    __MODULE = "email.service"
    def __init__(self):
        self.host = os.getenv("MAILER_HOST")
        self.port = int(os.getenv("MAILER_PORT", 587))
        self.user = os.getenv("MAILER_USER")
        self.password = os.getenv("MAILER_PASSWORD")
        self.from_addr = "postmaster@ginrealestate.mx"

    def send(self, email: Dict[str, Any]) -> None:
      
        msg = EmailMessage()
        msg["From"] = email["from"]
        msg["To"] = email["to"]
        msg["Subject"] = email["subject"]
        msg.set_content(email["html"], subtype="html")
        msg["X-Mailgun-Track"] = "no"

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Unable to send email")


    @service_error_handler(module=__MODULE)
    def handle_request(self, email: str, type_: str, webtoken_service: WebTokenService, invitation_id: UUID = None) -> str:
        if type_ == "INVITE":
            token = webtoken_service.generate_token(
                {"verification_code": str(invitation_id)}, "1d"
            )
            email_payload = self.invitation_email_builder(email, invitation_id)
            self.send(email_payload)
            return token

        code = int(1000 + os.urandom(2)[0] % 900000)
        token = webtoken_service.generate_token(
            {"verification_code": code}, "15m"
        )

        if type_ == "UPDATE":
            email_payload = self.update_email_builder(email, code)
        elif type_ == "RECOVERY":
            email_payload = self.account_recovery_email_builder(email, code)
        elif type_ == "NEW":
            email_payload = self.verification_email_builder(email, code)

        self.send(email_payload)
        return token
    
    def invitation_email_builder(self, email: str, token: str) -> dict:
        invite_url = f"https://expertise-ai-tan.vercel.app/invitation?token={token}"
        html = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Invitación a Expertise</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        color: #333;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                    }}
                    .button:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>¡Te han invitado a Expertise!</h2>
                    <p>Hola,</p>
                    <p>Has sido invitado a unirte a Expertise, una plataforma revolucionaria que integra inteligencia
                    artificial avanzada con acceso a expertos físicos, diseñada para optimizar las
                    decisiones empresariales y la gestión estratégica de negocios de cualquier
                    tamaño.
                    </p>
                    <p>Para aceptar la invitación y crear tu perfil, haz clic en el siguiente enlace:</p>
                    <a href="{invite_url}" class="button" style="color: #ffffff; text-decoration: none;">Unirse a Expertise</a>
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    <p>¡Esperamos verte pronto en Expertise!</p>
                    <p>Saludos,<br>El equipo de Expertise</p>
                </div>
            </body>
            </html>
            """
        return {
            "from": self.from_addr,
            "to": email,
            "subject": "¡Bienvenido a Expertise! Tu invitación está aquí",
            "html": html
        }

    def verification_email_builder(self, email: str, verification_code: int) -> Dict[str, Any]:
        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificación</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .code {{ font-size: 24px; font-weight: bold; color: #007bff; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Verificación de tu correo electrónico</h2>
                <p>Hola,</p>
                <p>Gracias por registrarte en nuestra plataforma. Para verificar tu dirección de correo electrónico, ingresa el siguiente código en la página de verificación:</p>
                <div class="code">{verification_code}</div>
                <p>Este código expirará en 15 minutos. Si no solicitaste este código, por favor ignora este correo.</p>
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                <p>¡Esperamos verte pronto!</p>
                <p>Saludos,<br>El equipo de Expertise</p>
            </div>
        </body>
        </html>"""
        return {
            "from": self.from_addr,
            "to": email,
            "subject": "Verificar Correo Electrónico",
            "html": html
        }

    def account_recovery_email_builder(self, email: str, verification_code: int) -> Dict[str, Any]:
        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de Cuenta</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .code {{ font-size: 24px; font-weight: bold; color: #007bff; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Recuperación de Cuenta</h2>
                <p>Hola,</p>
                <p>Recibimos una solicitud para recuperar tu cuenta. Si fuiste tú quien hizo esta solicitud, ingresa el siguiente código en la página de verificación:</p>
                <div class="code">{verification_code}</div>
                <p>Este código expirará en 15 minutos. Si no solicitaste este código, por favor ignora este correo.</p>
                <p>Si tienes alguna pregunta o problemas, no dudes en contactarnos.</p>
                <p>¡Gracias por usar nuestra plataforma!</p>
                <p>Saludos,<br>El equipo de Expertise</p>
            </div>
        </body>
        </html>"""
        return {
            "from": self.from_addr,
            "to": email,
            "subject": "Recupera tu cuenta de Expertise con este enlace",
            "html": html
        }

    def update_email_builder(self, email: str, verification_code: int) -> Dict[str, Any]:
        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificación</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .code {{ font-size: 24px; font-weight: bold; color: #007bff; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f4f4f4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Verificación de tu correo electrónico</h2>
                <p>Hola,</p>
                <p>Recibimos una solicitud para cambiar tu dirección de correo electrónico. Para completar este proceso, por favor ingresa el siguiente código en la página de verificación:</p>
                <div class="code">{verification_code}</div>
                <p>Este código expirará en 15 minutos. Si no solicitaste este código, por favor ignora este correo.</p>
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                <p>¡Esperamos verte pronto!</p>
                <p>Saludos,<br>El equipo de Expertise</p>
            </div>
        </body>
        </html>"""
        return {
            "from": self.from_addr,
            "to": email,
            "subject": "Verificar Correo Electrónico",
            "html": html
        }