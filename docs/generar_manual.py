"""Genera static/manual.pdf (manual de uso de MediLab).

Uso:  py docs/generar_manual.py
Requiere: reportlab  (py -m pip install reportlab)
"""
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

RAIZ = Path(__file__).resolve().parent.parent
CAPTURAS = RAIZ / "docs" / "capturas"
SALIDA = RAIZ / "static" / "manual.pdf"

ROJO = colors.HexColor("#db3f59")
GRIS_NAV = colors.HexColor("#3d3d3d")
TEAL = colors.HexColor("#12968f")
TEXTO = colors.HexColor("#2d2d33")
SUAVE = colors.HexColor("#6b6b75")
BORDE = colors.HexColor("#e2e2e6")
FONDO = colors.HexColor("#f7f7f9")

# ---------- Fuentes (Arial si existe; si no, Helvetica) ----------
FUENTES = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
try:
    pdfmetrics.registerFont(TTFont("Arial", str(FUENTES / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(FUENTES / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(FUENTES / "ariali.ttf")))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")
    F, FB = "Arial", "Arial-Bold"
except Exception:
    F, FB = "Helvetica", "Helvetica-Bold"

# ---------- Estilos ----------
s_normal = ParagraphStyle("normal", fontName=F, fontSize=10.5, leading=15, textColor=TEXTO, spaceAfter=6)
s_h1 = ParagraphStyle("h1", fontName=FB, fontSize=18, leading=22, textColor=ROJO, spaceBefore=14, spaceAfter=10, keepWithNext=1)
s_h2 = ParagraphStyle("h2", fontName=FB, fontSize=13, leading=17, textColor=TEXTO, spaceBefore=12, spaceAfter=6, keepWithNext=1)
s_vineta = ParagraphStyle("vineta", parent=s_normal, leftIndent=14, bulletIndent=2, spaceAfter=3)
s_pie = ParagraphStyle("pie", parent=s_normal, fontSize=8.5, leading=11, textColor=SUAVE, alignment=TA_CENTER)
s_celda = ParagraphStyle("celda", parent=s_normal, fontSize=9.5, leading=12.5, spaceAfter=0)
s_celda_b = ParagraphStyle("celda_b", parent=s_celda, fontName=FB, textColor=colors.white)
s_formula = ParagraphStyle("formula", parent=s_normal, fontName=FB, fontSize=11.5, alignment=TA_CENTER,
                           spaceBefore=4, spaceAfter=4)
s_nota = ParagraphStyle("nota", parent=s_normal, fontSize=9.5, leading=13.5, spaceAfter=0)
s_portada_t = ParagraphStyle("pt", fontName=FB, fontSize=30, leading=36, textColor=TEXTO)
s_portada_s = ParagraphStyle("ps", fontName=F, fontSize=14, leading=20, textColor=SUAVE)

ANCHO_UTIL = A4[0] - 4 * cm


def P(texto, estilo=s_normal):
    return Paragraph(texto, estilo)


def vinetas(items):
    return [Paragraph(t, s_vineta, bulletText="•") for t in items]


def pasos(items):
    return [Paragraph(t, s_vineta, bulletText=f"{i}.") for i, t in enumerate(items, 1)]


def tabla(filas, anchos, cabecera=True):
    datos = [[Paragraph(str(c), s_celda_b if (cabecera and r == 0) else s_celda) for c in fila]
             for r, fila in enumerate(filas)]
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.6, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if cabecera:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), GRIS_NAV))
    t.setStyle(TableStyle(estilo))
    return t


def captura(nombre, pie, ancho=10.5 * cm):
    ruta = CAPTURAS / nombre
    if not ruta.exists():
        return [P(f"<i>[Falta la captura {nombre}]</i>")]
    img = Image(str(ruta))
    escala = ancho / img.imageWidth
    img.drawWidth, img.drawHeight = ancho, img.imageHeight * escala
    marco = Table([[img]], colWidths=[ancho + 6], hAlign="CENTER")
    marco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, BORDE),
                               ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                               ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return [Spacer(1, 4), KeepTogether([marco, Spacer(1, 4), P(pie, s_pie)]), Spacer(1, 8)]


def recuadro(texto, color=TEAL, titulo="Consejo"):
    t = Table([[Paragraph(f"<b>{titulo}:</b> {texto}", s_nota)]], colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 8)]


def formula(texto):
    t = Table([[Paragraph(texto, s_formula)]], colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, BORDE), ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return [t, Spacer(1, 6)]


# ---------- Decoración de página ----------
def fondo_pagina(c, doc):
    ancho, alto = A4
    c.saveState()
    c.setFillColor(ROJO)
    c.rect(0, alto - 1.1 * cm, ancho, 1.1 * cm, stroke=0, fill=1)
    c.setFillColor(GRIS_NAV)
    c.rect(0, alto - 1.45 * cm, ancho, 0.35 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(FB, 11)
    c.drawString(2 * cm, alto - 0.72 * cm, "MediLab · Manual de uso")
    c.setFont(F, 9)
    c.drawRightString(ancho - 2 * cm, alto - 0.72 * cm, "Magnitudes y medición")
    c.setFillColor(SUAVE)
    c.setFont(F, 8.5)
    c.drawCentredString(ancho / 2, 1.1 * cm, f"Página {doc.page}")
    c.restoreState()


def portada(c, doc):
    ancho, alto = A4
    c.saveState()
    c.setFillColor(ROJO)
    c.rect(0, alto - 9 * cm, ancho, 9 * cm, stroke=0, fill=1)
    c.setFillColor(GRIS_NAV)
    c.rect(0, alto - 9.6 * cm, ancho, 0.6 * cm, stroke=0, fill=1)
    # Logo
    c.setFillColor(colors.white)
    c.roundRect(2 * cm, alto - 4.2 * cm, 2.2 * cm, 1.6 * cm, 6, stroke=0, fill=1)
    c.setFillColor(ROJO)
    c.setFont(FB, 30)
    c.drawCentredString(3.1 * cm, alto - 3.75 * cm, "SI")
    c.setFillColor(colors.white)
    c.setFont(FB, 34)
    c.drawString(4.7 * cm, alto - 3.85 * cm, "MediLab")
    c.setFont(F, 14)
    c.drawString(2 * cm, alto - 6.2 * cm, "Calculadora de mediciones · Conversión a SI y porcentaje de error")
    c.restoreState()


# ---------- Contenido ----------
def contenido():
    h = []

    # Portada
    h += [Spacer(1, 8.4 * cm), P("Manual de uso", s_portada_t), Spacer(1, 6),
          P("Guía detallada para usar la página web y entender todo lo que muestra.", s_portada_s),
          Spacer(1, 0.7 * cm)]
    h.append(tabla([
        ["Tema", "Experimento", "Materiales", "Comprobación y producto"],
        ["1. Magnitudes y medición", "Medición y conversión de dimensiones de periféricos o equipos",
         "Cinta métrica, regla, balanza, calculadora",
         "Medir tres objetos; repetir cada medición y comparar. Producto: tabla en SI y análisis de diferencias."],
    ], [3.4 * cm, 4.4 * cm, 3.6 * cm, ANCHO_UTIL - 11.4 * cm]))
    h += [Spacer(1, 0.5 * cm), P("<b>Contenido</b>", s_h2)]
    h += pasos(["¿Qué es MediLab?", "Partes de la pantalla", "Ingresar los datos de un objeto",
                "Agregar, quitar y cargar ejemplos", "Pestañas Todos · Longitud · Masa",
                "Tabla de resultados en SI", "Gráficas: fabricante vs. medición real",
                "Fórmulas y ejemplo resuelto", "Unidades disponibles", "Problemas frecuentes",
                "Consejos para medir bien"])
    h.append(PageBreak())

    # 1
    h += [P("1. ¿Qué es MediLab?", s_h1),
          P("MediLab es una página web que te ayuda con la práctica de <b>Magnitudes y medición</b>. "
            "Tú mides un objeto tres veces (por ejemplo, el largo de un teclado o la masa de un mouse) y escribes "
            "también el valor que indica el fabricante. La página hace todo lo demás al instante:"),
          *vinetas(["<b>Convierte</b> todos los valores al Sistema Internacional (SI): metros (m) para longitud "
                    "y kilogramos (kg) para masa.",
                    "Calcula el <b>promedio</b> de tus tres mediciones.",
                    "Calcula la <b>diferencia</b> y el <b>porcentaje de error</b> respecto al valor del fabricante.",
                    "Dibuja una <b>gráfica de barras</b> que compara el valor del fabricante con tu medición real.",
                    "Muestra las <b>fórmulas</b> usadas, con tus propios números sustituidos paso a paso."]),
          P("No hay que pulsar ningún botón de «calcular»: los resultados se actualizan mientras escribes."),
          *recuadro("El manual siempre está disponible desde el botón <b>Manual de uso</b>, en la esquina "
                    "superior derecha de la página.", titulo="Dónde está este manual")]

    # 2
    h += [P("2. Partes de la pantalla", s_h1),
          *captura("1_datos.jpg", "Figura 1. Vista general de la página con tres objetos cargados."),
          tabla([
              ["Zona", "Qué es y para qué sirve"],
              ["Barra roja (arriba)", "Logo de MediLab y accesos directos: <b>Datos</b>, <b>Tabla SI</b>, "
               "<b>Gráficas</b> y <b>Fórmulas</b>. Al pulsar uno, la página baja hasta esa sección. La barra "
               "se queda fija al hacer scroll. A la derecha está el botón <b>Manual de uso</b>."],
              ["Barra gris (pestañas)", "Pestañas <b>Todos</b>, <b>Longitud</b> y <b>Masa</b>. Filtran qué "
               "objetos se ven. El número entre paréntesis indica cuántos objetos hay de cada tipo."],
              ["Ruta de navegación", "Texto «Laboratorio &gt; Magnitudes y medición &gt; Calculadora de "
               "mediciones». Solo indica en qué parte estás."],
              ["Menú lateral (izquierda)", "Lista de <b>Objetos medidos</b> con su porcentaje de error. Al hacer "
               "clic en un objeto, la página baja hasta su tarjeta. Incluye el enlace <b>+ Agregar objeto</b> "
               "y un resumen del experimento, los materiales y el producto."],
              ["Panel «Datos de los objetos»", "Aquí escribes los datos. Cada objeto tiene su propia tarjeta."],
              ["Panel «Tabla de resultados en SI»", "Todos los valores convertidos a SI y los resultados."],
              ["Panel «Fabricante vs. medición real»", "Una gráfica de barras por objeto."],
              ["Panel «Fórmulas utilizadas»", "Fórmulas generales y su sustitución con tus datos."],
          ], [4.4 * cm, ANCHO_UTIL - 4.4 * cm]),
          *recuadro("En un celular, el menú lateral pasa arriba del contenido y el botón del manual muestra "
                    "solo su icono.", titulo="En pantallas pequeñas")]

    # 3
    h += [P("3. Ingresar los datos de un objeto", s_h1),
          P("Al abrir la página aparece una sola tarjeta: <b>Objeto 1</b>. Cada tarjeta tiene estos campos:"),
          tabla([
              ["Campo", "Qué escribir", "Ejemplo"],
              ["Nombre del objeto", "Un nombre que identifique el objeto y lo que mediste. Es opcional; si lo "
               "dejas vacío se usa «Objeto 1», «Objeto 2»…", "Teclado (largo)"],
              ["Magnitud", "<b>Longitud (m)</b> si mediste con regla o cinta métrica; <b>Masa (kg)</b> si "
               "usaste la balanza. Al cambiarla, las unidades disponibles cambian solas.", "Longitud (m)"],
              ["Valor del fabricante", "El dato oficial: lo que dice la caja, la etiqueta o la ficha técnica "
               "del producto.", "44"],
              ["Unidad fabricante", "La unidad en que viene el dato del fabricante.", "cm"],
              ["Medición 1, 2 y 3", "Las tres veces que mediste tú el mismo objeto.", "43,8 · 44,1 · 43,9"],
              ["Unidad mediciones", "La unidad que marcaba tu instrumento. Puede ser distinta a la del "
               "fabricante; la página convierte ambas a SI.", "cm"],
          ], [3.6 * cm, ANCHO_UTIL - 6.6 * cm, 3 * cm]),
          Spacer(1, 8),
          P("<b>Paso a paso</b>", s_h2),
          *pasos(["Escribe el nombre del objeto.",
                  "Elige la magnitud: longitud o masa.",
                  "Escribe el valor del fabricante y elige su unidad.",
                  "Escribe tus tres mediciones y elige la unidad en que las tomaste.",
                  "Mira los resultados: la tabla, la gráfica y las fórmulas se actualizan al momento."]),
          *recuadro("Un monitor «de 24 pulgadas» se mide en la diagonal. Puedes poner <b>24</b> con unidad "
                    "<b>in</b> como valor del fabricante, y tus mediciones en <b>cm</b>. MediLab convierte las dos "
                    "a metros antes de comparar.", titulo="Ejemplo con unidades distintas"),
          *recuadro("Si falta algún número, la tarjeta muestra en rojo: «Completa el valor del fabricante y "
                    "las 3 mediciones». Ese objeto aparece como «Sin datos completos» hasta que lo rellenes.",
                    color=ROJO, titulo="Datos incompletos"),
          P("Los decimales se escriben con punto o con coma, según la configuración de tu navegador "
            "(por ejemplo, 43,8 o 43.8).")]

    # 4
    h += [P("4. Agregar, quitar y cargar ejemplos", s_h1),
          tabla([
              ["Botón", "Dónde está", "Qué hace"],
              ["+ Agregar objeto", "Debajo de las tarjetas y en el menú lateral",
               "Crea una tarjeta nueva y vacía al final, y pone el cursor en el campo «Nombre». Si estás en la "
               "pestaña <b>Masa</b>, el objeto nuevo ya viene como masa en gramos; si no, como longitud en cm."],
              ["× Quitar", "Esquina superior derecha de cada tarjeta",
               "Elimina ese objeto junto con su fila de la tabla, su gráfica y sus fórmulas. Siempre queda al "
               "menos un objeto, por eso el botón se oculta cuando solo hay uno."],
              ["Cargar ejemplo", "Junto a «+ Agregar objeto»",
               "Reemplaza todo por tres objetos de ejemplo (teclado, mouse y monitor). Útil para ver cómo "
               "funciona la página. <b>Atención:</b> borra los datos que hayas escrito."],
          ], [3.3 * cm, 4 * cm, ANCHO_UTIL - 7.3 * cm]),
          *recuadro("Los datos no se guardan al recargar ni al cerrar la página. Anota tus mediciones o copia "
                    "la tabla antes de salir.", color=ROJO, titulo="Importante")]

    # 5
    h += [P("5. Pestañas Todos · Longitud · Masa", s_h1),
          P("La barra gris bajo la barra roja sirve para filtrar los objetos por magnitud:"),
          *vinetas(["<b>Todos</b>: muestra todos los objetos.",
                    "<b>Longitud</b>: solo los objetos de longitud.",
                    "<b>Masa</b>: solo los objetos de masa. Funciona como una sección exclusiva para la balanza."]),
          P("El filtro afecta a <b>todo</b>: tarjetas, menú lateral, tabla, gráficas y fórmulas. El título del "
            "panel cambia, por ejemplo, a «Datos de los objetos · Masa». Si en una pestaña no hay objetos, "
            "aparece un aviso para que agregues uno."),
          *captura("5_masa.jpg", "Figura 2. Pestaña «Masa» activa: solo se ve el mouse."),
          *recuadro("El número de la etiqueta («Objeto 2») es la posición del objeto en la lista completa. Por "
                    "eso, dentro de un filtro, la numeración puede saltar.", titulo="Nota")]

    # 6
    h += [P("6. Tabla de resultados en SI", s_h1),
          P("Es el producto principal de la práctica. Tiene una fila por objeto con todos los valores ya "
            "convertidos a la unidad del SI. Si la tabla no cabe en la pantalla, se desplaza hacia los lados."),
          *captura("2_tabla.jpg", "Figura 3. Tabla de resultados en SI."),
          tabla([
              ["Columna", "Significado"],
              ["Objeto", "Nombre del objeto."],
              ["Fabricante", "Valor del fabricante convertido a SI (m o kg)."],
              ["Medición 1, 2, 3", "Cada una de tus mediciones convertida a SI."],
              ["Promedio", "Media de las tres mediciones: tu «medición real»."],
              ["Diferencia", "Promedio menos valor del fabricante. Positiva (+): mediste más que el fabricante. "
               "Negativa (−): mediste menos."],
              ["% Error", "Diferencia relativa respecto al fabricante, en porcentaje."],
          ], [3.6 * cm, ANCHO_UTIL - 3.6 * cm]),
          P("<b>Colores del porcentaje de error</b>", s_h2),
          tabla([
              ["Color", "Rango", "Interpretación"],
              ["<font color='#1f9d55'><b>Verde</b></font>", "0 % a 2 %", "Muy buena concordancia con el fabricante."],
              ["<font color='#c98a00'><b>Amarillo</b></font>", "más de 2 % hasta 5 %",
               "Diferencia moderada: revisa el instrumento o la técnica de medición."],
              ["<font color='#d33a4f'><b>Rojo</b></font>", "más de 5 %",
               "Diferencia grande: puede haber un error de medición, de unidad o de dato."],
          ], [2.6 * cm, 3.8 * cm, ANCHO_UTIL - 6.4 * cm]),
          P("Los mismos colores aparecen en el menú lateral y en el título de cada gráfica.")]

    # 7
    h += [P("7. Gráficas: fabricante vs. medición real", s_h1),
          P("Cada objeto tiene su propia gráfica de barras. Se hace una gráfica por objeto porque cada uno puede "
            "estar en una magnitud distinta (no tiene sentido comparar metros con kilogramos en el mismo eje)."),
          *vinetas(["<b>Barra gris</b>: valor del fabricante.",
                    "<b>Barra verde azulada</b>: medición real (el promedio de tus tres mediciones).",
                    "<b>Título</b>: nombre del objeto y su porcentaje de error con el color correspondiente.",
                    "<b>Eje vertical</b>: la magnitud y su unidad SI, por ejemplo «longitud (m)».",
                    "Si pasas el mouse sobre una barra, aparece su valor exacto."]),
          *captura("3_graficas.jpg", "Figura 4. Gráficas de barras de los tres objetos de ejemplo."),
          *recuadro("El eje vertical <b>no empieza en cero</b>. Se hace así para que se noten diferencias pequeñas "
                    "(por ejemplo, 0,440 m frente a 0,439 m). Por eso una barra puede verse mucho más alta que "
                    "la otra aunque la diferencia real sea pequeña: fíjate siempre en los números del eje y en el "
                    "porcentaje de error.", color=ROJO, titulo="Cómo leer la gráfica")]

    # 8
    h += [P("8. Fórmulas y ejemplo resuelto", s_h1),
          P("La sección <b>Fórmulas utilizadas</b> muestra arriba las tres fórmulas generales y debajo, en "
            "<b>Sustitución con tus datos</b>, las mismas fórmulas con los números de cada objeto."),
          *captura("4_formulas.jpg", "Figura 5. Fórmulas generales y sustitución con los datos de cada objeto.",
                   ancho=9.5 * cm),
          P("<b>Las fórmulas</b>", s_h2),
          P("<b>Conversión a SI</b>: se multiplica el valor por el factor de su unidad (ver sección 9)."),
          *formula("x<sub>SI</sub> = x × f<sub>unidad</sub>"),
          P("<b>Promedio</b>: la suma de las tres mediciones dividida entre 3."),
          *formula("x̄ = (x<sub>1</sub> + x<sub>2</sub> + x<sub>3</sub>) / 3"),
          P("<b>Porcentaje de error</b>: diferencia absoluta respecto al fabricante, en porcentaje."),
          *formula("%E = |x̄ − x<sub>fab</sub>| / x<sub>fab</sub> × 100"),
          P("Ejemplo resuelto: masa de un mouse", s_h2),
          P("Fabricante: 95 g. Mediciones con la balanza: 97 g, 96 g y 98 g."),
          *pasos(["<b>Conversión</b>: 1 g = 0,001 kg. Fabricante: 95 × 0,001 = <b>0,095 kg</b>. "
                  "Mediciones: 0,097 kg; 0,096 kg; 0,098 kg.",
                  "<b>Promedio</b>: (0,097 + 0,096 + 0,098) / 3 = <b>0,097 kg</b>.",
                  "<b>Diferencia</b>: 0,097 − 0,095 = <b>+0,002 kg</b> (mediste más que el fabricante).",
                  "<b>% de error</b>: |0,097 − 0,095| / 0,095 × 100 = <b>2,105 %</b> → color amarillo."]),
          *recuadro("Si el valor del fabricante es 0, el porcentaje de error no se puede calcular (sería una "
                    "división entre cero) y la página muestra «—».", titulo="Caso especial")]

    # 9
    h += [P("9. Unidades disponibles", s_h1),
          P("Estas son las unidades que puedes elegir y el factor por el que se multiplican para pasar a SI:"),
          tabla([
              ["Longitud", "Factor a metros (m)", "Masa", "Factor a kilogramos (kg)"],
              ["mm (milímetro)", "0,001", "mg (miligramo)", "0,000001"],
              ["cm (centímetro)", "0,01", "g (gramo)", "0,001"],
              ["m (metro)", "1", "kg (kilogramo)", "1"],
              ["km (kilómetro)", "1000", "lb (libra)", "0,45359237"],
              ["in (pulgada)", "0,0254", "oz (onza)", "0,028349523125"],
              ["ft (pie)", "0,3048", "", ""],
          ], [3.6 * cm, ANCHO_UTIL / 2 - 3.6 * cm, 3.6 * cm, ANCHO_UTIL / 2 - 3.6 * cm]),
          P("Los resultados se muestran con hasta 6 cifras significativas. Los valores muy pequeños o muy grandes "
            "se escriben en notación científica.")]

    # 10
    h += [P("10. Problemas frecuentes", s_h1),
          tabla([
              ["Problema", "Solución"],
              ["Aparece «Completa el valor del fabricante y las 3 mediciones».",
               "Falta un número o hay texto en un campo numérico. Revisa los cuatro valores."],
              ["El objeto que agregué desapareció.",
               "Estás en una pestaña filtrada (por ejemplo, <b>Masa</b>) y el objeto es de otra magnitud. "
               "Pulsa <b>Todos</b> en la barra gris."],
              ["El % de error es enorme (por ejemplo, 900 %).",
               "Casi siempre es un error de unidades: revisa que la unidad del fabricante y la de las mediciones "
               "sean las correctas (cm frente a mm, g frente a kg)."],
              ["Las barras de la gráfica se ven muy diferentes.",
               "El eje no empieza en cero. Mira los valores del eje y el % de error para saber la diferencia real."],
              ["No puedo quitar el único objeto.",
               "Es normal: siempre debe haber al menos uno. Cambia sus datos o usa «Cargar ejemplo»."],
              ["Recargué la página y perdí los datos.",
               "La página no guarda los datos. Vuelve a escribirlos y anótalos antes de cerrar."],
          ], [6 * cm, ANCHO_UTIL - 6 * cm])]

    # 11
    h += [P("11. Consejos para medir bien", s_h1),
          *vinetas(["Mide siempre <b>el mismo lado</b> del objeto y apunta qué mediste (largo, ancho, diagonal…) "
                    "en el nombre.",
                    "Coloca la regla o cinta desde el <b>cero</b> y mira la escala de frente, no en diagonal "
                    "(error de paralaje).",
                    "Antes de pesar, comprueba que la balanza marque <b>cero</b> sin nada encima (tara).",
                    "Haz las tres mediciones de forma independiente: retira y vuelve a colocar el instrumento "
                    "cada vez.",
                    "Usa la unidad más pequeña que permita tu instrumento (mm en la regla, g en la balanza).",
                    "Busca el valor del fabricante en la ficha técnica oficial del producto."]),
          *recuadro("Para el informe, copia la <b>Tabla de resultados en SI</b> y comenta el porcentaje de error "
                    "de cada objeto: ¿fue verde, amarillo o rojo? ¿Por qué crees que hubo diferencia?",
                    titulo="Para presentar")]
    return h


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2.3 * cm, bottomMargin=2 * cm,
                            title="MediLab · Manual de uso", author="MediLab",
                            subject="Manual de uso de la calculadora de mediciones")
    doc.build(contenido(), onFirstPage=portada, onLaterPages=fondo_pagina)
    print(f"Manual generado: {SALIDA}")


if __name__ == "__main__":
    main()
