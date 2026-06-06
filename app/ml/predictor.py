import joblib
from pathlib import Path

MODEL_DIR = Path(__file__).parent / "models"

modelo_prioridad = joblib.load(MODEL_DIR / "modelo_prioridad.pkl")
modelo_error = joblib.load(MODEL_DIR / "modelo_error.pkl")
label_encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")


def predecir_prioridad(tipo: str, docs: int, edad: int, plazo: int, es_salud: bool) -> float:
    tipo_str = tipo.value if hasattr(tipo, 'value') else str(tipo)
    tipo_cod = label_encoder.transform([tipo_str])[0]
    X = [[tipo_cod, docs, edad, plazo, int(es_salud)]]
    return float(modelo_prioridad.predict(X)[0])

def predecir_error(tipo: str, docs: int, edad: int, plazo: int, es_salud: bool) -> float:
    tipo_str = tipo.value if hasattr(tipo, 'value') else str(tipo)
    tipo_cod = label_encoder.transform([tipo_str])[0]
    X = [[tipo_cod, docs, edad, plazo, int(es_salud)]]
    return float(modelo_error.predict_proba(X)[0][1])