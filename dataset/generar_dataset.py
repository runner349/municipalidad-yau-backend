import pandas as pd
import numpy as np

np.random.seed(42)
n = 1000

tipos = [
    "licencia_construccion",
    "licencia_funcionamiento",
    "permiso_transporte",
    "queja_vecinal",
    "certificado_domicilio",
    "partida_nacimiento",
    "autorizacion_sanitaria",
    "duplicado_dni",
    "exoneracion_tributaria",
    "otro"
]

# Generación base
df = pd.DataFrame({
    'tipo': np.random.choice(tipos, n),
    'docs_adjuntos': np.random.poisson(3, n),
    'edad_solicitante': np.random.randint(18, 80, n),
    'plazo_dias': np.random.choice([1, 3, 5, 10, 15, 30], n),
    'es_salud': np.random.choice([0, 1], n, p=[0.8, 0.2])
})

# Reglas de prioridad (valores 1-10)
prioridad = np.full(n, 5)  # base media

# Alta prioridad si:
# - autorizacion_sanitaria + es_salud + plazo <= 5
mask1 = (df['tipo'] == 'autorizacion_sanitaria') & (df['es_salud'] == 1) & (df['plazo_dias'] <= 5)
prioridad[mask1] = np.random.randint(8, 11, mask1.sum())

# - queja_vecinal + plazo <= 3
mask2 = (df['tipo'] == 'queja_vecinal') & (df['plazo_dias'] <= 3)
prioridad[mask2] = np.random.randint(8, 11, mask2.sum())

# - partida_nacimiento o duplicado_dni (trámites simples) -> prioridad baja
mask3 = df['tipo'].isin(['partida_nacimiento', 'duplicado_dni'])
prioridad[mask3] = np.random.randint(1, 4, mask3.sum())

# - licencias o permisos con plazo <= 5 -> prioridad alta
mask4 = (df['tipo'].isin(['licencia_construccion', 'licencia_funcionamiento', 'permiso_transporte'])) & (df['plazo_dias'] <= 5)
prioridad[mask4] = np.random.randint(7, 10, mask4.sum())

# - mucho documentos también sube prioridad (trámite complejo)
mask5 = (df['docs_adjuntos'] >= 6)
prioridad[mask5] = np.clip(prioridad[mask5] + 2, 1, 10)

# - exoneracion_tributaria con plazo largo -> baja
mask6 = (df['tipo'] == 'exoneracion_tributaria') & (df['plazo_dias'] >= 15)
prioridad[mask6] = np.random.randint(1, 4, mask6.sum())

df['prioridad_real'] = prioridad

# Reglas de error (probabilidad de que tenga error)
error_prob = np.full(n, 0.1)
# Más docs -> más probabilidad de error
error_prob = np.clip(error_prob + df['docs_adjuntos'] * 0.02, 0, 0.9)
# Trámites complejos: licencias y autorizacion sanitaria
mask_err = df['tipo'].isin(['licencia_construccion', 'licencia_funcionamiento', 'autorizacion_sanitaria'])
error_prob[mask_err] += 0.15
# Trámites simples: menor error
mask_simple = df['tipo'].isin(['certificado_domicilio', 'duplicado_dni'])
error_prob[mask_simple] *= 0.5
# Edad muy avanzada + muchos docs puede generar error
mask_edad = (df['edad_solicitante'] > 70) & (df['docs_adjuntos'] > 4)
error_prob[mask_edad] += 0.2

error_prob = np.clip(error_prob, 0, 1)
df['error'] = (error_prob > 0.4).astype(int)  # umbral para clasificación binaria

df.to_csv('tramites_historicos.csv', index=False)
print("Dataset generado con reglas realistas.")