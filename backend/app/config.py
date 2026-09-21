import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class ClinicSettings(BaseModel):
    BASE_DIR: Path = BASE_DIR
    clinic_name: str = os.getenv("CLINIC_NAME", "Clínica Dental Sonrisas")
    clinic_address: str = os.getenv("CLINIC_ADDRESS", "Av. Principal 123, Consultorio 402")
    clinic_phone: str = os.getenv("CLINIC_PHONE", "+1 234 567 8900")
    business_hours_start: int = int(os.getenv("BUSINESS_HOURS_START", "9"))  # 09:00
    business_hours_end: int = int(os.getenv("BUSINESS_HOURS_END", "19"))    # 19:00
    slot_duration_minutes: int = int(os.getenv("SLOT_DURATION_MINUTES", "45"))
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    google_credentials_file: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    backend_port: int = int(os.getenv("PORT", "8000"))

settings = ClinicSettings()
