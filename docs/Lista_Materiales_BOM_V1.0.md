# Lista de Materiales (BOM) — Acordeón Mic (V1.0)

**Versión:** 1.0 · **Fecha:** 2026-09-09 · **Base:** `Hardware_PCB/inventario_enriquecido.csv` (regenerado 2026-09-08: 42 refs / 25 valores únicos) + `../Arquitectura_Hardware.md` V1.1 (post-Red Team) · **Refs:** `Diagrama_Conexiones_V1.0.md`

Lista oficial de componentes para ensamblar el sistema de 3 micrófonos internos para acordeón: cápsulas → sumador activo OPA1642 → driver balanceado TLE2072 → XLR, alimentado **100 % del Phantom +48 V** de la consola. Diseño Touring Grade validado en SPICE (8/8 PASS). **42 piezas / 25 valores únicos.**

> **Presupuesto phantom (regla de compra):** disponible ~10.2 mA vs consumo 9.39 mA (92 %, margen 0.85 mA). Por eso la pareja de op-amps está **FIJADA: U1 OPA1642 + U2 TLE2072**. Prohibido TL072, NE5532 o 2× OPA1642 (colapsan el riel a <8 V). ⚠️ En la rodilla del zener el raíl puede caer a ~11.4 V — es comportamiento normal, no falla.

> **Sourcing honesto:** solo U1/U2/Q_MUTE tienen código LCSC; el resto del inventario es THT genérico `MANUAL_REQUIRED`. **Este documento —no el CSV— es la guía de compra**: las specs críticas (tolerancia, dieléctrico, potencia) viven en la columna *Notas*.

## 1. Cápsulas de Micrófono (etapa de entrada)

| Cantidad | Referencia | Componente | Montaje | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **3** | MIC1–MIC3 | **Primo EM289** (alt. EM189T) | Cápsula THT | Captura de lengüetas dentro del fuelle | **≥128 dB SPL** (el fuelle genera 120–127 dB internos). Espaciadas 10–12" en el treble grille; requieren shock mount (§8). |

## 2. Semiconductores Activos (IC & Transistor)

| Cantidad | Referencia | Componente | Encapsulado | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **1** | U1 | **OPA1642** | SOIC-8 **+ adaptador a DIP-8** | A: sumador activo · B: LPF + buffer HOT | JFET, 5.4 mA. **No sustituir** (budget phantom). LCSC [201728](https://jlcpcb.com/partdetail/201728). |
| **1** | U2 | **TLE2072** | **DIP-8 + zócalo** | A: driver balanceado COLD · B: seguidor V_BIAS | Elegido por drive y 3.6 mA máx. **No sustituir**. LCSC [1346615](https://jlcpcb.com/partdetail/1346615). |
| **1** | Q_MUTE | **J111** | TO-92 | Mute anti-pop: shunt diferencial D→HOT / S→COLD | JFET. ⚠️ **Pinout variable por fabricante — verificar datasheet antes de soldar.** Pop medido 92 mV. LCSC [274642](https://jlcpcb.com/partdetail/274642). |

## 3. Diodos (F.A. Phantom)

| Cantidad | Referencia | Componente | Encapsulado | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **1** | D_ZENER_12V | **1N4742A** | DO-41 (THT) | Zener 12 V del riel interno | Regula la extracción phantom (12.3 V en SPICE). |

> **⚠️ SIN TVS en XLR 2/3 (decisión firmada):** las P6KE12CA originales fueron **eliminadas** (ECO Red Team 2026-08-21: avalanchan en continua sobre el +48 V del phantom y roban ~9.7 mA). La protección de línea es el bloqueo bipolar 47 µF/63 V + ferritas + ground lift; la renuncia a ESD directa en conector está documentada. No re-añadir nunca TVS de standoff < 48 V en estas líneas (rules/7 §7.17).

## 4. Electromecánica (Conectores y Controles)

| Cantidad | Referencia | Componente | Montaje | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **1** | XLR_OUT | **Neutrik NC3MAH** | THT | Salida balanceada al PA | Por los pines 2/3 retorna el +48 V que alimenta todo el sistema. |
| **1** | RV_VOL | **Pot 10 kΩ Audio (log)** | Panel (no PCB) | Volumen | **Audio taper, NO lineal.** Referencia física: TS-1902A (ECO 08-22). ⚠️ Pin 1 (inferior) a **V_BIAS (+6 V), NUNCA a GND** — a GND produce click y quiebra el HPF. |
| **1** | SW_GROUND_LIFT | **Switch SPDT** | THT | Ground lift audio↔chasis | Trabaja CON la red R_GLIFT 100 Ω 1 W + C_GLIFT Y-Class en serie a chasis — nunca puente directo. |

## 5. Capacitores

| Cantidad | Referencia | Valor / Voltaje | Dieléctrico | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **3** | C_MIC1–3_AC | **100 nF** | **Film** | Bloqueo DC de cápsulas + HPF 159 Hz | Triple propósito: bloquea el DC de bias, el DC shift destructivo del fuelle y descarta bajos no deseados. **No subir a 1 µF+** (rompe el HPF de 159 Hz). |
| **1** | C_LPF | **3.3 nF** | **C0G/NP0** | LPF anti-hiss 14.6 kHz (con R_LPF 3.3 kΩ) | **C0G/NP0 obligatorio** — con X7R/Y5V la Fc baila ±8 kHz a 60 °C (rules/7 §7.5). |
| **2** | C_BLOCK_HOT/COLD | **47 µF / 63 V** | **Bipolar** (no polarizado) | Bloqueo DC de la salida balanceada (anti-phantom) | Soportan el retorno del +48 V. Jamás electrolítico polarizado. |
| **1** | C_FILTER_12V | **100 µF / 25 V** | Electrolítico | Filtro del riel 12 V | Filtra el zener de la extracción phantom. |
| **1** | C_VBIAS_FILTER | **10 µF** | Electrolítico | Filtro del riel V_BIAS (+6 V) | Montado en el **rail**, no en la referencia del seguidor U2B. |
| **2** | C_DEC_HF1–2 | **100 nF** | Cerámico X7R | Desacoplo HF de alimentación | Uno pegado a cada IC (U1 y U2). Aquí X7R es correcto. |
| **1** | C_GLIFT | **10 nF / 250 V** | **Y-Class** (seguridad) | Camino AC del ground lift a chasis | Y-Class obligatorio — es el único puente audio↔chasis. |
| **1** | C_GATE_MUTE | **1 µF** | Film | Red de gate del mute (τ ≈ 1 s con R_GATE_MUTE 1 MΩ) | Carga lenta del gate del J111 = encendido sin pop. |

## 6. Resistencias

| Cantidad | Referencia | Valor | Potencia / Tol | Función | Notas |
|:---:|:---|:---|:---|:---|:---|
| **3** | R_MIC1–3_BIAS | **33 kΩ** | 1/4 W | Bias de cada cápsula desde V_BIAS | Garantiza ~2.4 V en la cápsula (nunca >5 V). |
| **3** | R_MIC1–3_SUM | **10 kΩ** | 1/4 W | Entradas del sumador inversor (U1A) | Con R_SUM_FB 30 kΩ → ganancia de mezcla −3× por canal. |
| **1** | R_SUM_FB | **30 kΩ** | 1/4 W — 1 % | Feedback del sumador (U1A) | Fija la ganancia total de la mezcla. |
| **2** | R_INV_IN, R_INV_FB | **10 kΩ** | 1/4 W — **1 % matched** | Inversor COLD (U2A) | Ganancia −1×; el par matched mantiene HOT/COLD simétricos. |
| **1** | R_LPF | **3.3 kΩ** | 1/4 W | Serie del LPF 14.6 kHz | Junto a C_LPF 3.3 nF C0G. |
| **2** | R_BAL_HOT/COLD | **470 Ω** | 1/4 W — 1 % | Build-out balanceado HOT/COLD | ECO 08-22 (antes 100 Ω). El matching protege el CMRR. |
| **2** | R_PH1/2_EXTRACT | **220 Ω** | 1/4 W — **0.1 % matched** | Extracción phantom balanceada (48 V → riel 12 V) | **El matching 0.1 % es lo que protege el CMRR, no el valor.** ECO 08-21 (antes 2.2 kΩ — presupuesto IEC 61938 corregido al 92 %). |
| **2** | R_VBIAS_TOP/BOT | **100 kΩ** | 1/4 W | Divisor del midrail V_BIAS (+6 V) | Buffered por U2B desde el ECO 08-22 — el divisor desnudo colapsaba con 3 cápsulas. |
| **1** | R_GLIFT | **100 Ω** | **1 W** | Serie del ground lift | Potencia 1 W; en serie con C_GLIFT Y-Class hacia chasis. |
| **1** | R_GATE_MUTE | **1 MΩ** | 1/4 W | Pull del gate del J111 | Con C_GATE_MUTE 1 µF → τ ≈ 1 s. |

## 7. Inductores / Supresión EMI

| Cantidad | Referencia | Valor | Función | Notas |
|:---:|:---|:---|:---|:---|
| **2** | FB_HOT, FB_COLD | **Ferrita 600 Ω @ 100 MHz** | EMI/RFI de la salida XLR (HOT y COLD) | Bead THT (equivalente Murata BLM18 en THT). Última barrera antes del conector. |

## 8. Hardware Mecánico (fuera del netlist — comprar aparte)

| Cantidad | Referencia | Componente | Función | Notas |
|:---:|:---|:---|:---|:---|
| **3** | SHOCK_MOUNT | Gomas antivibración + *felt boots* | Aislamiento mecánico de cada cápsula | **Obligatorio Touring Grade**: el ruido mecánico del fuelle es el peor enemigo del sistema. No es parte SKiDL — no aparece en `inventario_enriquecido.csv`. |

## Registro de Cambios

| Versión | Fecha | Cambio |
|:---|:---|:---|
| V1.0 | 2026-09-09 | Creación. Base: inventario regenerado 2026-09-08 (42 refs / 25 valores únicos). Refleja el diseño post-Red Team con sus ECOs ya aplicados: TVS fuera de XLR 2/3 y R_PH 220 Ω 0.1 % (08-21), mute J111 + R_BAL 470 Ω + midrail bufferizado (08-22), footprints honestos verificados contra KiCad (08-24). |
