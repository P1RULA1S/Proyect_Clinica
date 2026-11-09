from contextlib import contextmanager

from database import Paciente, create_session


FORM_FIELDS = (
    "cedula", "nombre_completo", "edad", "peso", "estatura", "ritmo_cardiaco", "presion",
    "tamano_seno", "tipo_somatico", "ciclo_menstrual", "terapia_hormonal", "lactancia",
    "anticonceptivos", "gen_abuela_materna", "gen_abuela_paterna", "gen_mama", "gen_hermana",
    "molestia_masa", "molestia_hinchazon", "molestia_dolor", "secrecion_sanguinolenta",
    "piel_enrojecimiento_seno", "diagnostico_dx", "observaciones",
)


@contextmanager
def session_scope():
    session = create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def buscar_por_cedula(cedula):
    with session_scope() as session:
        return session.query(Paciente).filter(Paciente.cedula == cedula.strip()).first()


def guardar_paciente(patient_id, values):
    with session_scope() as session:
        paciente = session.get(Paciente, patient_id) if patient_id else None
        if paciente is None:
            paciente = session.query(Paciente).filter(Paciente.cedula == values["cedula"]).first()
        if paciente is None:
            paciente = Paciente()
            session.add(paciente)

        for field in FORM_FIELDS:
            if field in values:
                setattr(paciente, field, values[field])
        session.flush()
        return paciente.id


def cargar_paciente(patient_id):
    with session_scope() as session:
        paciente = session.get(Paciente, patient_id)
        if paciente is None:
            return None
        return {field: getattr(paciente, field) for field in FORM_FIELDS}
