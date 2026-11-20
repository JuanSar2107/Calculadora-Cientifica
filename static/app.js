// Ejemplos que se pueden cargar con el botón "Cargar ejemplo"
const EJEMPLOS = [
  { nombre: "Teclado (largo)", magnitud: "longitud", unidad_fabricante: "cm", fabricante: 44.0,
    unidad_medicion: "cm", mediciones: [43.8, 44.1, 43.9] },
  { nombre: "Mouse (masa)", magnitud: "masa", unidad_fabricante: "g", fabricante: 95,
    unidad_medicion: "g", mediciones: [97, 96, 98] },
  { nombre: "Monitor (diagonal)", magnitud: "longitud", unidad_fabricante: "in", fabricante: 24,
    unidad_medicion: "cm", mediciones: [60.8, 61.0, 60.9] },
];
const VACIO = { nombre: "", magnitud: "longitud", unidad_fabricante: "cm", fabricante: "",
  unidad_medicion: "cm", mediciones: ["", "", ""] };

const contObjetos = document.getElementById("objetos");
const graficas = new Map(); // id de tarjeta -> { div, chart }
let siguienteId = 1;
let filtro = "todos"; // "todos" | "longitud" | "masa"
const NOMBRE_FILTRO = { longitud: "longitud", masa: "masa" };

// Objeto vacío según la pestaña activa (masa → g, longitud → cm)
function plantillaFiltro() {
  return filtro === "masa"
    ? { ...VACIO, magnitud: "masa", unidad_fabricante: "g", unidad_medicion: "g" }
    : { ...VACIO };
}

const css = getComputedStyle(document.documentElement);
const COLOR_FAB = css.getPropertyValue("--fab").trim();
const COLOR_REAL = css.getPropertyValue("--real").trim();
const COLOR_TEXTO = css.getPropertyValue("--suave").trim();
const COLOR_REJILLA = css.getPropertyValue("--borde").trim();

function opcionesUnidad(magnitud, seleccion) {
  return Object.keys(UNIDADES[magnitud].factores)
    .map(u => `<option value="${u}" ${u === seleccion ? "selected" : ""}>${u}</option>`)
    .join("");
}

// ---------- Tarjetas ----------
function crearTarjeta(ej = VACIO) {
  const card = document.createElement("article");
  card.className = "card";
  card.id = `obj-${siguienteId++}`;
  card.innerHTML = `
    <div class="card-head">
      <span class="chip">Objeto</span>
      <button class="btn-quitar" type="button" title="Quitar este objeto">✕ Quitar</button>
    </div>
    <div class="card-body">
      <label class="ancho">Nombre del objeto<input data-k="nombre" placeholder="Ej. Teclado (largo)" value="${escapar(ej.nombre)}"></label>
      <label>Magnitud
        <select data-k="magnitud">
          <option value="longitud" ${ej.magnitud === "longitud" ? "selected" : ""}>Longitud (m)</option>
          <option value="masa" ${ej.magnitud === "masa" ? "selected" : ""}>Masa (kg)</option>
        </select>
      </label>
      <label>Valor del fabricante<input data-k="fabricante" type="number" step="any" placeholder="0" value="${ej.fabricante}"></label>
      <label>Unidad fabricante<select data-k="unidad_fabricante">${opcionesUnidad(ej.magnitud, ej.unidad_fabricante)}</select></label>
      <label>Medición 1<input data-k="m0" type="number" step="any" placeholder="0" value="${ej.mediciones[0]}"></label>
      <label>Medición 2<input data-k="m1" type="number" step="any" placeholder="0" value="${ej.mediciones[1]}"></label>
      <label>Medición 3<input data-k="m2" type="number" step="any" placeholder="0" value="${ej.mediciones[2]}"></label>
      <label>Unidad mediciones<select data-k="unidad_medicion">${opcionesUnidad(ej.magnitud, ej.unidad_medicion)}</select></label>
      <div class="estado"></div>
    </div>`;

  card.querySelector('[data-k="magnitud"]').addEventListener("change", e => {
    const mag = e.target.value;
    const base = mag === "masa" ? "g" : "cm";
    card.querySelector('[data-k="unidad_fabricante"]').innerHTML = opcionesUnidad(mag, base);
    card.querySelector('[data-k="unidad_medicion"]').innerHTML = opcionesUnidad(mag, base);
  });
  card.querySelector(".btn-quitar").addEventListener("click", () => {
    card.remove();
    renumerar();
    calcular();
  });
  card.addEventListener("input", programarCalculo);
  card.addEventListener("change", programarCalculo);
  return card;
}

function agregarObjeto(ej) {
  const card = crearTarjeta(ej);
  contObjetos.appendChild(card);
  renumerar();
  calcular();
  return card;
}

function renumerar() {
  const tarjetas = [...contObjetos.children];
  tarjetas.forEach((c, i) => {
    c.querySelector(".chip").textContent = `Objeto ${i + 1}`;
    // Siempre debe quedar al menos un objeto
    c.querySelector(".btn-quitar").style.visibility = tarjetas.length > 1 ? "visible" : "hidden";
  });
}

function leerObjeto(card) {
  const v = k => card.querySelector(`[data-k="${k}"]`).value;
  const nums = ["fabricante", "m0", "m1", "m2"].map(k => v(k));
  if (nums.some(n => n === "" || isNaN(Number(n)))) return null;
  return {
    nombre: v("nombre") || card.querySelector(".chip").textContent,
    magnitud: v("magnitud"),
    unidad_fabricante: v("unidad_fabricante"),
    unidad_medicion: v("unidad_medicion"),
    fabricante: Number(nums[0]),
    mediciones: nums.slice(1).map(Number),
  };
}

// ---------- Formato ----------
function fmt(x) {
  if (x === null || x === undefined) return "—";
  if (x === 0) return "0";
  const a = Math.abs(x);
  if (a < 1e-4 || a >= 1e6) return x.toExponential(4);
  return String(Number(x.toPrecision(6)));
}
function tex(x) {
  const s = fmt(x);
  const m = s.match(/^(-?[\d.]+)e([+-]\d+)$/);
  return m ? `${m[1]}\\times10^{${Number(m[2])}}` : s;
}
function claseError(e) {
  if (e === null) return "";
  return e <= 2 ? "ok" : e <= 5 ? "medio" : "alto";
}
function escapar(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function nombreDe(card) {
  return card.querySelector('[data-k="nombre"]').value || card.querySelector(".chip").textContent;
}
function magnitudDe(card) {
  return card.querySelector('[data-k="magnitud"]').value;
}

// ---------- Cálculo ----------
let temporizador;
function programarCalculo() {
  clearTimeout(temporizador);
  temporizador = setTimeout(calcular, 150);
}

async function calcular() {
  const tarjetas = [...contObjetos.children];
  const objetos = tarjetas.map(leerObjeto);
  tarjetas.forEach((c, i) => {
    c.querySelector(".estado").textContent = objetos[i] ? "" : "Completa el valor del fabricante y las 3 mediciones.";
  });

  const validos = objetos.map((o, i) => ({ o, i })).filter(x => x.o);
  let resultados = [];
  if (validos.length) {
    try {
      const resp = await fetch("/api/calcular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ objetos: validos.map(x => x.o) }),
      });
      resultados = (await resp.json()).resultados;
    } catch (e) {
      console.error(e);
      return;
    }
  }

  const porPos = new Array(tarjetas.length).fill(null);
  validos.forEach((x, k) => {
    const r = resultados[k];
    if (r && r.ok) porPos[x.i] = r;
    else if (r) tarjetas[x.i].querySelector(".estado").textContent = r.error;
  });

  aplicarFiltro(tarjetas, porPos);
}

// ---------- Filtro por magnitud ----------
function aplicarFiltro(tarjetas, porPos) {
  const visible = tarjetas.map(c => filtro === "todos" || magnitudDe(c) === filtro);
  tarjetas.forEach((c, i) => { c.hidden = !visible[i]; });

  // Contadores en las pestañas
  const cuenta = { todos: tarjetas.length, longitud: 0, masa: 0 };
  tarjetas.forEach(c => cuenta[magnitudDe(c)]++);
  document.querySelectorAll(".subnav [data-filtro]").forEach(b => {
    b.querySelector(".cuenta").textContent = `(${cuenta[b.dataset.filtro]})`;
  });

  const vacio = document.getElementById("vacio-filtro");
  const hayVisibles = visible.some(Boolean);
  vacio.hidden = hayVisibles;
  vacio.textContent = hayVisibles ? "" :
    `No hay objetos de ${NOMBRE_FILTRO[filtro]}. Pulsa "Agregar objeto" para añadir uno.`;
  document.getElementById("titulo-filtro").textContent =
    filtro === "todos" ? "" : `· ${filtro === "masa" ? "Masa" : "Longitud"}`;

  const t = tarjetas.filter((_, i) => visible[i]);
  const r = porPos.filter((_, i) => visible[i]);
  pintarLista(t, r);
  pintarTabla(t, r);
  pintarGraficas(t, r);
  pintarFormulas(t, r);
}

function cambiarFiltro(nuevo) {
  filtro = nuevo;
  document.querySelectorAll(".subnav [data-filtro]").forEach(b => {
    const activo = b.dataset.filtro === nuevo;
    b.classList.toggle("activo", activo);
    b.setAttribute("aria-selected", activo);
  });
  calcular();
}

// ---------- Salidas ----------
function pintarLista(tarjetas, res) {
  document.getElementById("lista-objetos").innerHTML = tarjetas.map((c, i) => {
    const r = res[i];
    const pct = r && r.error_pct !== null ? `<span class="pct ${claseError(r.error_pct)}">${fmt(r.error_pct)} %</span>` : "";
    return `<li><a href="#${c.id}"><span>${escapar(nombreDe(c))}</span>${pct}</a></li>`;
  }).join("");
}

function pintarTabla(tarjetas, res) {
  document.getElementById("tabla-si").innerHTML = res.map((r, i) => {
    const nombre = escapar(nombreDe(tarjetas[i]));
    if (!r) return `<tr><td>${nombre}</td><td colspan="7" style="text-align:left;color:var(--suave)">Sin datos completos</td></tr>`;
    const u = r.unidad_si;
    const err = r.error_pct === null ? "—" : fmt(r.error_pct) + " %";
    return `<tr>
      <td>${nombre}</td>
      <td>${fmt(r.fabricante_si)} ${u}</td>
      ${r.mediciones_si.map(m => `<td>${fmt(m)} ${u}</td>`).join("")}
      <td><strong>${fmt(r.promedio_si)} ${u}</strong></td>
      <td>${r.diferencia_si >= 0 ? "+" : ""}${fmt(r.diferencia_si)} ${u}</td>
      <td class="${claseError(r.error_pct)}"><strong>${err}</strong></td>
    </tr>`;
  }).join("");
}

function nuevaGrafica() {
  const div = document.createElement("div");
  div.className = "grafica";
  div.innerHTML = `<h4></h4><div class="lienzo"><canvas></canvas></div>`;
  const chart = new Chart(div.querySelector("canvas"), {
    type: "bar",
    data: {
      labels: ["Fabricante", "Medición real (promedio)"],
      datasets: [{ data: [0, 0], backgroundColor: [COLOR_FAB, COLOR_REAL], borderRadius: 4, maxBarThickness: 70 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 250 },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => `${fmt(c.parsed.y)} ${c.chart.$unidad || ""}` } },
      },
      scales: {
        x: { ticks: { color: COLOR_TEXTO }, grid: { display: false } },
        y: { ticks: { color: COLOR_TEXTO }, grid: { color: COLOR_REJILLA },
             title: { display: true, color: COLOR_TEXTO, text: "" } },
      },
    },
  });
  return { div, chart };
}

function pintarGraficas(tarjetas, res) {
  const cont = document.getElementById("graficas");
  const ids = new Set(tarjetas.map(c => c.id));
  // Eliminar gráficas de objetos quitados
  for (const [id, g] of graficas) {
    if (!ids.has(id)) { g.chart.destroy(); g.div.remove(); graficas.delete(id); }
  }
  tarjetas.forEach((card, i) => {
    if (!graficas.has(card.id)) graficas.set(card.id, nuevaGrafica());
    const { div, chart } = graficas.get(card.id);
    cont.appendChild(div); // mantiene el orden de las tarjetas
    const r = res[i];
    const titulo = div.querySelector("h4");
    if (!r) {
      titulo.textContent = `${nombreDe(card)}: sin datos`;
      chart.data.datasets[0].data = [0, 0];
      chart.update();
      return;
    }
    const err = r.error_pct === null ? "—" : fmt(r.error_pct) + " %";
    titulo.innerHTML = `${escapar(nombreDe(card))} · error <span class="${claseError(r.error_pct)}">${err}</span>`;
    const a = r.fabricante_si, b = r.promedio_si;
    const lo = Math.min(a, b), hi = Math.max(a, b);
    const margen = Math.max((hi - lo) * 1.5, Math.abs(hi) * 0.02);
    chart.$unidad = r.unidad_si;
    chart.data.datasets[0].data = [a, b];
    chart.options.scales.y.min = lo >= 0 ? Math.max(0, lo - margen) : lo - margen;
    chart.options.scales.y.max = hi + margen * 0.5;
    chart.options.scales.y.title.text = `${r.magnitud} (${r.unidad_si})`;
    chart.update();
  });
}

function pintarFormulas(tarjetas, res) {
  const cont = document.getElementById("formulas-objetos");
  cont.innerHTML = "";
  res.forEach((r, i) => {
    const box = document.createElement("div");
    box.className = "sustitucion";
    const nombre = escapar(nombreDe(tarjetas[i]));
    if (!r) {
      box.innerHTML = `<h4>${nombre}</h4><p class="nota">Sin datos completos.</p>`;
      cont.appendChild(box);
      return;
    }
    const u = `\\,\\text{${r.unidad_si}}`;
    const [m1, m2, m3] = r.mediciones_si.map(tex);
    const lineas = [
      `x_{fab} = ${tex(r.fabricante)}\\,\\text{${r.unidad_fabricante}} \\times ${tex(r.factor_fabricante)} = ${tex(r.fabricante_si)}${u}`,
      `x_i = (${r.mediciones.map(tex).join(",\\ ")})\\,\\text{${r.unidad_medicion}} \\times ${tex(r.factor_medicion)} = (${m1},\\ ${m2},\\ ${m3})${u}`,
      `\\bar{x} = \\dfrac{${m1} + ${m2} + ${m3}}{3} = ${tex(r.promedio_si)}${u}`,
      r.error_pct === null
        ? `\\%E \\text{ no definido (valor del fabricante = 0)}`
        : `\\%E = \\dfrac{|${tex(r.promedio_si)} - ${tex(r.fabricante_si)}|}{${tex(r.fabricante_si)}} \\times 100 = ${tex(r.error_pct)}\\,\\%`,
    ];
    box.innerHTML = `<h4>${nombre}</h4>` + lineas.map(() => `<div class="linea"></div>`).join("");
    box.querySelectorAll(".linea").forEach((el, k) =>
      katex.render(lineas[k], el, { throwOnError: false, displayMode: true }));
    cont.appendChild(box);
  });
}

// ---------- Inicio ----------
document.querySelectorAll("[data-tex]").forEach(el =>
  katex.render(el.dataset.tex, el, { throwOnError: false, displayMode: true }));

document.querySelectorAll("[data-agregar]").forEach(btn =>
  btn.addEventListener("click", () => {
    const card = agregarObjeto(plantillaFiltro());
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    card.querySelector('[data-k="nombre"]').focus({ preventScroll: true });
  }));

document.getElementById("btn-ejemplo").addEventListener("click", () => {
  contObjetos.innerHTML = "";
  EJEMPLOS.forEach(ej => contObjetos.appendChild(crearTarjeta(ej)));
  renumerar();
  calcular();
});

// Arranca con un solo objeto
agregarObjeto(EJEMPLOS[0]);

document.querySelectorAll(".subnav [data-filtro]").forEach(b =>
  b.addEventListener("click", () => cambiarFiltro(b.dataset.filtro)));
