import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Asegurar carpeta de modelos
os.makedirs('../app/ml/models', exist_ok=True)

df = pd.read_csv('tramites_historicos.csv')

le = LabelEncoder()
df['tipo_cod'] = le.fit_transform(df['tipo'])

features = ['tipo_cod', 'docs_adjuntos', 'edad_solicitante', 'plazo_dias', 'es_salud']
X = df[features]
y_prioridad = df['prioridad_real']
y_error = df['error']

X_train, X_test, yp_train, yp_test = train_test_split(X, y_prioridad, test_size=0.2)
_, _, ye_train, ye_test = train_test_split(X, y_error, test_size=0.2)

# Modelo de prioridad (regresión)
modelo_prioridad = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_prioridad.fit(X_train, yp_train)

# Modelo de error (clasificación)
modelo_error = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_error.fit(X_train, ye_train)

# Guardar
joblib.dump(modelo_prioridad, '../app/ml/models/modelo_prioridad.pkl')
joblib.dump(modelo_error, '../app/ml/models/modelo_error.pkl')
joblib.dump(le, '../app/ml/models/label_encoder.pkl')

print("Modelos guardados en app/ml/models/")