from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],
)

# Definir el modelo de datos para el formulario de contacto
class ContactForm(BaseModel):
    nombre: str
    apellidos: str
    correo: str
    mensaje: str

# Lista en memoria para almacenar los registros de contacto
contactos = []

# Ruta POST para manejar el formulario de contacto
@app.post("/contacto")
async def handle_contact_form(form_data: ContactForm):
    # Agregar los datos del formulario a la lista de contactos
    contactos.append(form_data)
    return {"message": f"Gracias {form_data.nombre} {form_data.apellidos}, hemos recibido tu mensaje."}

# Ruta GET para visualizar todos los registros de contacto
@app.get("/contactos")
async def get_contactos():
    return contactos

