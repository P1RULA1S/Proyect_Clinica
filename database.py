from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Paciente(Base):
    __tablename__ = 'pacientes'
    
    # Datos Principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String, unique=True, nullable=False) # Equivale a CURP/Número de paciente
    nombre_completo = Column(String, nullable=False)
    edad = Column(Integer)
    peso = Column(Float)
    estatura = Column(Float)
    ritmo_cardiaco = Column(Integer)
    presion = Column(String)
    hijos = Column(Integer)

    # Características Físicas y Ginecológicas
    tamano_seno = Column(String) # A, B, C, D, DD
    tipo_somatico = Column(String) # Ecto, Meso, Endo
    ciclo_menstrual = Column(String) # Asintomática, Síntomas, Folicular, Ovulación, Lútea
    menarca = Column(Integer)
    gestaciones = Column(Integer)
    terapia_hormonal = Column(Boolean, default=False)
    lactancia = Column(Boolean, default=False)
    interrupcion_embarazo = Column(Boolean, default=False)
    anticonceptivos = Column(Boolean, default=False)

    # Carga Genética (Familiares con antecedentes)
    gen_abuela_paterna = Column(Boolean, default=False)
    gen_abuela_materna = Column(Boolean, default=False)
    gen_papa = Column(Boolean, default=False)
    gen_mama = Column(Boolean, default=False)
    gen_hermana = Column(Boolean, default=False)
    gen_tios = Column(Boolean, default=False)

    # Molestias y Síntomas
    molestia_masa = Column(Boolean, default=False)
    molestia_hinchazon = Column(Boolean, default=False)
    molestia_irritacion = Column(Boolean, default=False)
    molestia_hoyuelos = Column(Boolean, default=False)
    molestia_dolor = Column(Boolean, default=False)
    molestia_retraccion = Column(Boolean, default=False)
    
    # Cambios en la piel
    piel_enrojecimiento_pezon = Column(Boolean, default=False)
    piel_enrojecimiento_seno = Column(Boolean, default=False)
    piel_escamosa_pezon = Column(Boolean, default=False)
    piel_escamosa_seno = Column(Boolean, default=False)

    # Secreción
    secrecion_amarilla = Column(Boolean, default=False)
    secrecion_verde = Column(Boolean, default=False)
    secrecion_blanca = Column(Boolean, default=False)
    secrecion_sanguinolenta = Column(Boolean, default=False)
    secrecion_otra = Column(Boolean, default=False)

    # Hábitos
    habito_actividad_fisica = Column(Boolean, default=False)
    habito_alcohol = Column(Boolean, default=False)
    habito_fuma = Column(Boolean, default=False)
    habito_nocturno = Column(Boolean, default=False)
    habito_drogas = Column(Boolean, default=False)
    habito_quimicos = Column(Boolean, default=False)

    # Observaciones Médicas
    diagnostico_dx = Column(Text)
    observaciones = Column(Text)
    fecha_ultimo_estudio = Column(String)

    capturas = relationship("Captura", back_populates="paciente", cascade="all, delete-orphan")


class Captura(Base):
    __tablename__ = "capturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    camara = Column(String, nullable=False)
    ruta_archivo = Column(String, nullable=False)
    creada_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    paciente = relationship("Paciente", back_populates="capturas")


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
CAPTURES_DIR = STORAGE_DIR / "capturas"
DATABASE_PATH = STORAGE_DIR / "clinica_termografia.db"
STORAGE_DIR.mkdir(exist_ok=True)
CAPTURES_DIR.mkdir(exist_ok=True)

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,
    connect_args={"check_same_thread": False, "timeout": 30},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db():
    Base.metadata.create_all(engine)


def create_session():
    return SessionLocal()


init_db()