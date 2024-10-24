from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Ajustamos los nombres de los campos para coincidir con el frontend
class ContactForm(BaseModel):
    nombre: str = Field(..., title="Nombre", min_length=2, max_length=50)
    apellidos: str = Field(..., title="Apellidos", min_length=2, max_length=50)
    correo: EmailStr
    mensaje: str = Field(..., title="Mensaje", min_length=10, max_length=500)

def send_verification_email(form_data: ContactForm, email_to: str, subject: str):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_to
        msg['Subject'] = subject

        html_body = fhtml_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                    color: #333333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 10px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 20px;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .content h2 {{
                    color: #2c3e50;
                    margin-bottom: 20px;
                }}
                .message {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #dddddd;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #888888;
                }}
                .footer a {{
                    color: #2c3e50;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    Confirmación de Contacto
                </div>
                <div class="content">
                    <h2>Hola {form_data.nombre} {form_data.apellidos},</h2>
                    <p>Gracias por contactarnos. Hemos recibido tu mensaje:</p>
                    <div class="message">
                        <strong>Tu mensaje:</strong>
                        <p>{form_data.mensaje}</p>
                    </div>
                    <p>Nos pondremos en contacto contigo pronto.</p>
                </div>
                <div class="footer">
                    <p>Este es un correo automático, por favor no respondas.</p>
                    <p><a href="https://tu-sitio-web.com">Visita nuestro sitio web</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server.sendmail(SENDER_EMAIL, email_to, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación: {e}")
        raise HTTPException(status_code=500, detail="Error de autenticación al enviar el correo")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Error al enviar el correo")



@app.post("/contacto")
async def contact_form(form_data: ContactForm, background_tasks: BackgroundTasks):
    try:
        subject = "Verificación de correo electrónico"
        background_tasks.add_task(send_verification_email, form_data, form_data.correo, subject)
        return {"message": "Formulario recibido. Se ha enviado un correo de verificación."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar el formulario")
