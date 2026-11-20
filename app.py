"""Magnitudes y medición — conversión a SI, promedio y % de error.

Ejecutar:  py app.py   y abrir http://127.0.0.1:5000
"""
import math

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Factores de conversión a la unidad base del SI (m para longitud, kg para masa)
UNIDADES = {
    "longitud": {
        "si": "m",
        "factores": {
            "mm": 0.001,
            "cm": 0.01,
            "m": 1.0,
            "km": 1000.0,
            "in": 0.0254,
            "ft": 0.3048,
        },
    },
    "masa": {
        "si": "kg",
        "factores": {
            "mg": 1e-6,
            "g": 0.001,
            "kg": 1.0,
            "lb": 0.45359237,
            "oz": 0.028349523125,
        },
    },
}


def a_si(valor, magnitud, unidad):
    return valor * UNIDADES[magnitud]["factores"][unidad]


def calcular_objeto(obj):
    """Convierte a SI y calcula promedio, desviación y % de error de un objeto."""
    magnitud = obj.get("magnitud", "longitud")
    if magnitud not in UNIDADES:
        raise ValueError(f"Magnitud desconocida: {magnitud}")
    factores = UNIDADES[magnitud]["factores"]
    u_fab = obj.get("unidad_fabricante")
    u_med = obj.get("unidad_medicion")
    if u_fab not in factores or u_med not in factores:
        raise ValueError("Unidad no válida para la magnitud elegida")

    fabricante = float(obj["fabricante"])
    mediciones = [float(m) for m in obj["mediciones"]]
    if len(mediciones) != 3:
        raise ValueError("Se necesitan exactamente 3 mediciones")

    fab_si = a_si(fabricante, magnitud, u_fab)
    med_si = [a_si(m, magnitud, u_med) for m in mediciones]
    n = len(med_si)
    promedio = sum(med_si) / n
    # Desviación estándar muestral (n - 1)
    desviacion = math.sqrt(sum((x - promedio) ** 2 for x in med_si) / (n - 1))
    diferencia = promedio - fab_si
    error_pct = abs(diferencia) / abs(fab_si) * 100 if fab_si != 0 else None

    return {
        "nombre": obj.get("nombre") or "Objeto",
        "magnitud": magnitud,
        "unidad_si": UNIDADES[magnitud]["si"],
        "factor_fabricante": factores[u_fab],
        "factor_medicion": factores[u_med],
        "unidad_fabricante": u_fab,
        "unidad_medicion": u_med,
        "fabricante": fabricante,
        "mediciones": mediciones,
        "fabricante_si": fab_si,
        "mediciones_si": med_si,
        "promedio_si": promedio,
        "desviacion_si": desviacion,
        "diferencia_si": diferencia,
        "rango_si": max(med_si) - min(med_si),
        "error_pct": error_pct,
    }


@app.route("/")
def index():
    return render_template("index.html", unidades=UNIDADES)


@app.post("/api/calcular")
def api_calcular():
    datos = request.get_json(silent=True) or {}
    resultados = []
    for obj in datos.get("objetos", []):
        try:
            resultados.append({"ok": True, **calcular_objeto(obj)})
        except (KeyError, TypeError, ValueError) as e:
            resultados.append({"ok": False, "error": str(e), "nombre": obj.get("nombre")})
    return jsonify(resultados=resultados)


if __name__ == "__main__":
    app.run(debug=True)
