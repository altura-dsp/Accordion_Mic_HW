# PLAN PoC — Acordeón Digital: 3× mic I2S alto-SPL + Pico 2 (AA + UI MVP + Salida Phantom-Híbrida)

> [!NOTE]
> **🏠 MOVIDO.** El proyecto digital del acordeón ahora vive en **`7_Acordeon_mic_DSP/`**. Este plan evolucionó a:
> **SSOT vigente:** [`../7_Acordeon_mic_DSP/docs/PLAN_PoC_Digital_Mic_I2S_V1.6.md`](../7_Acordeon_mic_DSP/docs/PLAN_PoC_Digital_Mic_I2S_V1.6.md)
> (V1.6 añade: volumen por pot-ADC; F0.1 corregida con los datos REALES de la etapa phantom V1 — zener 12 V, 220 Ω 0.1%, 10.2 mA, doctrina NO-TVS en pines 2/3; herencia: `7_Acordeon_mic_DSP/docs/Bloque_Herencia_Boutique_V1.md`)
> El `5_Acordeon_Mic` queda como proyecto de la V1 analógica.

**Versión:** 1.5 — 2026-08-30
**Estado:** 🏠 MOVIDO a 7_Acordeon_mic_DSP (V1.6)

---

## 0. Objetivo y Reglas del Juego

**Demostrar o refutar en banco, con números, la viabilidad de la cadena digital del acordeón ANTES de tocar un solo cable del instrumento.**

1. **Cero fe, todo medición.** Cada fase (F1–F8) tiene un gate numérico VERDE/ROJO. Un gate ROJO = STOP, se documenta y se decide. No se improvisa ("a ver si funciona").
2. **DRY:** este PoC reutiliza patrones ya probados del repo: PIO multi-SM sincronizado (`rules/3`), ping-pong DMA estático, Mute P1 al boot, biquads SSOT, toolchain Arduino-Pico (`rules/5`), crossfades/Equal-Power y SmoothedValue (`rules/4`), bloque phantom+protección de la V1 analógica (F0.1). Cero invención nueva donde ya hay patrón.
3. **El PoC NO es el producto.** Es el instrumento de medida que habilita (o mata) la migración completa. La librería de efectos (EQ/chorus/doubler) es **fase producto, post-GO**, portada desde `lib_DSP` de los pedales.
4. **YAGNI explícito (§7):** lista cerrada de lo que este PoC NO hace.

### F0 — Decisiones de arquitectura (✅ CERRADAS)

| Decisión | Elección | Razón |
|---|---|---|
| **MCU** | **Pico 2 (RP2350)** — STM32 descartado | Presupuesto eléctrico sobrado. STM32 = capa HAL/I2S desde cero = cero DRY |
| **Toolchain** | **Arduino-Pico (Earle Philhower) + pio_asm** | El mismo de los pedales del repo (`rules/5`) |
| **Cápsula** | **A/B en bench**: MSM261S4030H0R vs IM69D130 | Ambas I2S, ambas -26 dBFS → mismo firmware |
| **Alimentación digital** | **2× AA NiMH (Eneloop) → dido Schottky → VSYS** — Phantom descartado para el dominio digital | Decisión de usuario (2026-08-30). El buck-boost RT6150B de la Pico 2 regula 2.0–2.4 V → 3.3 V. Elimina TODO el EMI del buck-phantom. ⚠️ El **diodo SS14 en serie es obligatorio** (§2.5): sin él, programar por USB con baterías puestas = carga descontrolada de las NiMH |
| **UI** | **MVP: 1 botón + 1 NeoPixel** (mecanismo; la librería de efectos es post-GO) | Decisión de usuario. Valida el patrón completo: debounce Core 0 → dirty flag → crossfade sin pop en Core 1. Sin pantallas (ilegibles en escenario = anti-touring) |
| **Cobertura** | **3 mics, SOLO el lado de agudos**; bajos sin amplificar | Decisión de usuario. El HPF 159 Hz protege F3 ≈ 175 Hz y rechaza la fuga acústica del lado de bajos |

### F0.1 — Etapa de salida balanceada XLR (✅ CERRADA 2026-08-30): **Híbrida Baterías + Phantom con detector**

**Decisión de usuario.** Arquitectura de DI activo clásica, repartida por dominios:

- **Baterías AA → TODO lo digital** (Pico 2, mics I2S, PCM5102A). El gate ≤35 mA queda intacto.
- **Phantom de la mesa (+48 V por el XLR) → SOLO la etapa analógica de salida** (TLE2072, reutilizada de la V1 analógica). Energía limpia y lineal de la mesa: cero EMI de switching, cero carga a la batería.

**Por qué gana sobre las alternativas:**

| vs Opción | Resultado |
|---|---|
| vs A (transformador) | Mismo consumo de batería (cero), pero headroom muy superior y sin 15–20 € de trafo. El aislamiento galvánico se pierde — aceptado |
| vs B (RRIO 3.3 V) | B daba +9.5 dBu máx (5.5 dB sobre nominal = margen anti-touring insuficiente). El raíl phantom da **+22.8 dBu diferenciales** |
| vs boost 12 V interno | Reintroducía switching EMI. El phantom ES la fuente limpia |

**⚠️ Trade-off aceptado y documentado:** SIN phantom en la mesa **no hay salida** (silencio total). El detector + LED amarillo (abajo) convierte el fallo silencioso en diagnóstico visible.

#### Matemática del presupuesto phantom (Thevenin en el XLR: 48 V, 6.81k∥6.81k = 3.405 kΩ)

`I_disponible = (48 V − V_raíl) / 3.405 kΩ`

| Raíl zener | I máx disponible | Consumo estimado | Veredicto |
|---|---|---|---|
| 24 V | 7.0 mA | TLE2072 dual Iq ~6.8–11 mA | ✗ colapsa si Iq real > 7 mA |
| **15 V (baseline)** | **9.7 mA** | ~7 mA (TLE2072) + 0.12 mA (detector) | ✅ margen 1.35× |
| 12 V | 10.6 mA | ídem | ✅ margen 1.5×, headroom +21 dBu (sigue sobrando) |

- Headroom con raíl 15 V: ±7.5 V por pata → **+22.8 dBu diferenciales** = 18.8 dB sobre el nominal +4 dBu.
- **Gate de banco (fase producto):** medir Iq real del TLE2072 dual < 8 mA. Si falla → zener a 12 V o swap directo a **OPA1678** (2 mA/canal, audio-grade, mismo DIP-8/SOIC-8, `rules/13`) → margen 2.4×. Cero fe.
- Topología electrónica phantom clásica: el raíl V+ cuelga de los pines 2/3 (R de alimentación), señal inyectada por acoplo desde el opamp; **portar el bloque extracción + TVS + soft-start de la V1 analógica** (DRY — ya resuelto allí).

#### Protección (P1 — lo que el plan original omitía)

- **Hot-plug:** TVS/zener + R serie en pines 2/3 — conectar el XLR con phantom activo es el zap más común del mundo real (`rules/7`).
- **Grounding:** pin 1 → GND del instrumento. Un solo cable = sin bucle de masa posible.
- ⚠️ Nota de banco: programar por USB con el XLR conectado a mesa encendida puede zumbear (GND PC ↔ GND mesa). En banco: XLR fuera o phantom off al programar.

#### Detector de phantom (corregido — el divisor 10k/3.3k original robaba 0.9 mA = 10% del presupuesto)

- Divisor de **alta impedancia 100k/27k** desde el raíl zener → **GP15**: 15 V → 3.19 V (seguro para el GPIO; la 100k serie limita la inyección a µA si el zener falla). Coste: 118 µA.
- Muestreado por Core 0 en el mismo ciclo asíncrono que el ADC de batería. Firmware con dos umbrales (histéresis) + debounce.

#### Semáforo NeoPixel (código de colores único, SSOT — `rules/8` accesibilidad)

| Patrón LED | Significado | Acción del músico |
|---|---|---|
| Color fijo (uno por preset) | Todo OK | — |
| 🔴 Rojo intermitente | Batería baja (2.1 V; mute preventivo 1.95 V) | Cambiar/recargar pilas |
| 🟡 Amarillo intermitente | **Sin phantom — salida muerta** | Pedir al técnico: "phantom en mi canal" |

---

## 1. BOM (comprar UNA vez)

| # | Componente | Qty | Notas |
|---|---|---|---|
| 1 | **Módulo MSM261S4030H0R** (I2S, AliExpress/LCSC) | **3** | Candidata producción: AOP 135–140 dB. ⚠️ Verificar pin **L/R** expuesto (si no: fallback §2.1) |
| 2 | **S2GO-MEMSMIC-IM69D** (breakout Infineon) | **3** | Referencia de verdad (AOP 130 documentado). El ganador del A/B = kit de producto |
| 3 | Raspberry Pi **Pico 2** (RP2350) | 1 | |
| 4 | Módulo **PCM5102A** I2S DAC | 1 | Patrón 4_Pico-Scarlett |
| 5 | **Portapilas 2× AA CON interruptor** + 2 Eneloop | 1 | Interruptor = mute mecánico de gala. Calidad de contactos = asunto touring (R6) |
| 6 | **Diodo Schottky SS14/1N5819** | 1 | Serie batería→VSYS. P1: evita carga descontrolada por USB + protege pilas invertidas |
| 7 | **Electrolítico 220 µF/10 V** en VSYS | 1 | Sobrevive glitches de contacto por vibración del fuelle |
| 8 | **Pulsador táctil** | 1 | UI MVP (el PoC valida el mecanismo con UNO) |
| 9 | **WS2812B** (NeoPixel individual) | 1 | Con cap de brillo §5 (≤8 mA) |
| 10 | Protoboard + jumpers | 1 | |

**BOM de producto (post-GO, etapa F0.1):** TLE2072, zener 15 V, TVS pines 2/3, caps de acoplo 10 µF, divisor 100k/27k, conector XLR — bloque mayormente heredado de la V1 analógica.

**Nota de sourcing:** MSM261S4030H0R = mismo die que **CUI CMM-4030D-261-I2S-TR** (Mouser/DigiKey, datasheet de primer mundo) para el PCB de producto.

---

## 2. Arquitectura PoC

### 2.1 Topología de 3 mics (truco L/R slotting + línea extra)

```
   SCK (GP10) ──┬──► mic A (L/R→GND) ──┐
   WS  (GP11) ──┼──► mic B (L/R→3V3) ──┴──► SD1 (GP12) → SM1 (frame estéreo)
              └──► mic C (L/R→GND) ──────► SD2 (GP13) → SM2 (data-only, slot L)
```

- Un frame I2S tiene solo 2 slots → el 3er mic va en SD propia con SM data-only en lockstep (patrón `bschwind/rp2040-i2s`: SM maestro genera relojes; SMs esclavos `.with().sync().start()`).
- 5 pines GPIO para 3 micrófonos. SCK/WS compartidos (fan-out 3, sin buffer).
- **Fallback** si el módulo MSM261 no expone L/R: 3 líneas SD (3 SM data-only), mismo patrón.

### 2.2 Firmware — doble núcleo

| Bloque | Implementación |
|---|---|
| **Toolchain** | Arduino-Pico (Philhower), sketch `.ino` + `i2s_mic.pio` via pio_asm — igual que los pedales |
| **PIO0 SM0** (maestro) | Genera BCLK + WS. Reloj: tabla §2.3 |
| **PIO0 SM1** (captura SD1) | Frame estéreo 32-bit (mics A+B) |
| **PIO0 SM2** (captura SD2) | Data-only, slot L (mic C), lockstep con SM0 |
| **DMA** | 2 cadenas ping-pong sobre buffers `static` (2×48 muestras estéreo c/u). Cero `malloc` (P2) |
| **Core 1** (audio) | DSP ininterrumpido: DC-block ×3 → HPF ×3 → **(A+B+C)/4** → LPF → ganancia con crossfade. Lee presets vía dirty-flag atómico |
| **Core 0** (control) | Housekeeping, watchdog, telemetría, **XSMT/mute, debounce botón, NeoPixel, monitoreo batería ADC3 (GP29), detector phantom GP15** |
| **Salida bench (PoC)** | PCM5102A: `BCK→GP6`, `LRCLK→GP7`, `DIN→GP8`, **`SCK→GND`** (PLL interna), **`XSMT→GP22`** con pull-down = mute hardware P1 |
| **Salida producto (F0.1)** | La línea del DAC → acoplo → TLE2072 (hot/cold) → XLR, etapa alimentada por phantom. Gates W1–W3 en §4 |

### 2.3 Relojes matemáticos (anti-jitter, `rules/3`)

| Fase | sysclk | ÷ N | BCLK | WS |
|---|---|---|---|---|
| **PoC (USB)** | 196.608 MHz | 64 | 3.072 MHz | 48 kHz |
| **Producto (batería)** | **49.152 MHz** | 16 | 3.072 MHz | 48 kHz |

⚠️ NO usar 48 MHz (48/3.072 = 15.625 → divider fraccional → jitter). 49.152 = 196.608/4, misma PLL. El underclock es lo que compra las ~35 h de batería.

### 2.4 Estructura de archivos (KISS)

```
5_Acordeon_Mic/src/PoC_Digital/
├── PoC_Digital.ino   # boot, mute P1, watchdog, bucle core 0 (UI, batería, phantom, telemetría)
├── i2s_mic.pio       # SM maestro + 2 SM captura
├── dsp_chain.cpp/.h  # DC-block + biquads + suma + ganancia crossfadeada (SSOT coeficientes)
└── config.h          # PUNTO ÚNICO DE VERDAD: fs, pines, fc, ganancias, umbrales, brillo LED
```

### 2.5 Alimentación del dominio digital (P1 — el detalle que rompe todo si se ignora)

```
2×AA NiMH (2.4 V) ──[interruptor]──[SS14 ▼]──► VSYS ──► RT6150B (buck-boost onboard) ──► 3V3
                              │                    │
                        220 µF a GND          ADC3 (GP29) lee VSYS/3 (divisor onboard, gratis)
```

- **El dido es no-negociable:** USB puesto + baterías directas a VSYS = VBUS (~4.7 V post-diodo del Pico) empuja corriente INTO las NiMH sin control. Con SS14: USB y baterías pueden coexistir (programar en vivo sin desmontar).
- Caída del dido ~0.2 V → VSYS ≈ 2.2 V cargado, 1.9 V al final de vida → dentro del rango del RT6150B para 3.3 V.
- **Monitoreo batería (Core 0, asíncrono):** umbral **2.1 V** (1.05 V/celda) → NeoPixel rojo intermitente; **1.95 V → mute P1 + shutdown limpio** (el mute va ANTES del brownout, o el acordeón hace pop en el escenario).

---

## 3. Gain Staging y SPL — el corazón del PoC

### 3.1 Los números (datasheets verificados)

| Parámetro | MSM261S4030H0R | IM69D130 |
|---|---|---|
| Sensibilidad | **-26 dBFS** @ 94 dB SPL | **-26 dBFS ±1 dB** @ 94 dB SPL |
| ⇒ 0 dBFS eléctrico ≈ | **120 dB SPL** | **120 dB SPL** |
| AOP reclamado | 135 (CUI) – 140 (MEMSensing) dB SPL | 130 dB SPL |
| SNR | ~65 dB(A) | 69 dB(A) |

### 3.2 ⚠️ R1 — La discrepancia de techo (resolver en bench, no ignorar)

La matemática de sensibilidad pone el techo **eléctrico** en ~120 dB SPL; los AOP reclamados son 10–20 dB mayores. La diferencia reside en la linealidad mecánica de la cápsula más allá del FS eléctrico, pero **no se supone: se mide**.

**Diseño conservador (Fire & Forget):**
- **CERO ganancia antes de la suma.**
- **Clip detector a -1 dBFS** con latch + telemetría.
- Peaks de fuelle: **110–125 dB SPL** → convivir con niveles cercanos a FS. Techo limpio < 118 dB SPL medido → **NO-GO** (el EM289 analógico gana).
- Suma de 3 mics = +4.8 dB → **escala ¼ (shift 2 bits Q31)** tras sumar (-1.2 dB SNR, irrelevante con señal de fuelle).
- **El A/B decide:** si ambas clipean al mismo SPL → techo eléctrico (120) → empatan → gana la barata. Si la MSM261 aguanta más → su AOP de cápsula es real → gana por margen.

### 3.3 Cadena DSP (Core 1) — plana durante TODO el PoC

```
mic A ─► DC-block ─► HPF biquad 159 Hz (Q=0.707) ─┐
mic B ─► DC-block ─► HPF biquad 159 Hz (Q=0.707) ─┼──► (A+B+C)/4 ──► LPF biquad 14.6 kHz ──► ganancia (crossfade) ──► DAC
mic C ─► DC-block ─► HPF biquad 159 Hz (Q=0.707) ─┘    (shift 2 bits)
```

- DC-blocker primero SIEMPRE (los MEMS tienen offset DC; si no, el HPF lo integra y derivationa el headroom).
- Coeficientes en compilación, no runtime (P2). `typedef float sample_t`, FTZ activo (`rules/3`).
- El HPF 159 Hz hace doble trabajo: protege F3 ≈ 175 Hz (nota más grave del manual derecho) y rechaza la fuga del lado de bajos.
- **Sin efectos en el PoC** (§0.3): un doubler introduciría 15–30 ms de delay y rompería el gate de latencia; contaminaría además la F5. La ganancia crossfadeada de F6 valida EL mecanismo que los efectos usarán después.

---

## 4. Fases y Gates numéricos

### F1 — Captura de 1 mic (bench, telemetría serie)
**Hacer:** SM maestro + captura, streaming USB-serie a PC (plot mínimo). Primero IM69D130, luego MSM261 (mismo firmware).
**Gate VERDE:** 48 kHz/24-bit **10 min sin overrun DMA** en AMBAS cápsulas; DC offset de cada una documentado en `config.h`; **consumo total medido** (baseline §6 R2 — alimentar por USB con amperímetro, NO con baterías todavía).

### F2 — Multi-mic escalonado: 2 mics (L/R slotting) → 3er mic (SD2)
**Gate VERDE (2 mics):** canales independientes (tapar mic A → canal L cae >20 dB); fase coherente; cero glitch de lockstep.
**Gate VERDE (3 mics):** tres canales activos (tapar uno a uno); fase coherente ×3; cero glitch; buffers de ambas cadenas DMA sin skew (mismo índice de bloque).

### F3 — DSP suma + filtros (cadena plana)
**Gate VERDE:** HPF/LPF con sweep (fc ±10% de 159 Hz / 14.6 kHz); noise floor silencio < **-95 dBFS** RMS; **latencia mic→DAC < 3 ms** (impulso + osciloscopio).

### F4 — Salida PCM5102A + Mute P1
**Gate VERDE:** **cero pops en 20 ciclos de encendido/apagado**; XSMT con pull-down verificado (mute activo sin firmware); watchdog 4 s armado; MSPLIM (`rules/10`).

### F5 — Tortura acústica A/B (el día del juicio)
**Hacer:** fuelle real o fuente fuerte, fortissimo sostenido, ambas cápsulas en la misma posición (intercambio repetido).
**Gate VERDE:** 30 min por cápsula, **cero clips latcheados por debajo de fortissimo**; techo comparado (dato §3.2); cero underruns; consistencia entre repeticiones.

### F6 — UI MVP (mecanismo, no librería)
**Hacer:** 1 botón → alterna 2 presets de ganancia (p.ej. 0 dB / -6 dB) en Core 1 vía dirty-flag atómico + crossfade ~10 ms (patrón SmoothedValue/Equal-Power, `rules/4`); NeoPixel indica preset; **monitoreo batería ADC3 + detector phantom GP15 activos** (semáforo F0.1).
**Gate VERDE:** cambio de preset **sin pop medible** (osciloscopio en la salida, chasquido no audible); debounce sin rebotes en 100 pulsaciones; **batería baja**: rojo intermitente al bajar VSYS con fuente variable + **mute preventivo a 1.95 V demostrado** (P1); **detector phantom**: amarillo intermitente al quitar el raíl simulado (P1).

### F7 — Prueba real de batería (2×AA NiMH)
**Hacer:** montar §2.5 completo (diodo + electro + interruptor); sistema entero a baterías; programar por USB CON baterías puestas (verificar que el dido hace su trabajo — las celdas no se calientan).
**Gate VERDE:** consumo medio ≤ **35 mA @3.3 V** (LED capped incluido; la etapa phantom NO cuenta — se alimenta de la mesa); arranque confiable con celdas recién cargadas Y al 30% de descarga; **2 h de estrés sin un solo reset** (sacudir el portapilas encima de la mesa — emulación de fuelle); duración proyectada ≥ **30 h** (medida × capacidad).

### F8 — GO/NO-GO (gate de producto)

| Métrica | GO si | NO-GO si |
|---|---|---|
| Techo limpio medido | ≥ 118 dB SPL sin clip audible | < 118 (EM289 analógico gana) |
| Latencia mic→DAC (cadena plana) | < 3 ms | ≥ 5 ms |
| Noise floor | < -95 dBFS | ≥ -90 dBFS |
| Robustez (F5+F7) | sin watchdog reset ni reboot por vibración | cualquier reset |
| Consumo @49.152 MHz | ≤ 35 mA @3.3 V | > 45 mA (reduce a <20 h de batería) |
| Batería baja + mute preventivo | demostrado en F6 | no funciona |

**GO habilita:** PLAN de producto — cápsula ganadora ×3; UI completa (librería de efectos portada de `lib_DSP`, DRY); **etapa salida phantom-híbrida F0.1 con sus gates W**:

- **W1 — Raíl phantom bajo carga:** zener 15 V estable, ripple <10 mVpp, I_total < 8 mA medidos (gate del presupuesto F0.1; si falla → zener 12 V u OPA1678).
- **W2 — Hot-plug ×20:** phantom on/off con XLR conectado/desconectado, **cero thump** (TVS + soft-start de la V1 analógica).
- **W3 — Audio etapa:** THD <0.01% @ +4 dBu, headroom hasta clip ≥ +18 dBu diferenciales.

---

## 5. Reglas de firmware aplicadas (checklist P1/P2/P3)

- [ ] **P1:** XSMT con **pull-down** (mute activo sin alimentación/firmware); subida solo con stream estable + 500 ms
- [ ] **P1:** dido SS14 en serie batería→VSYS; 220 µF en VSYS
- [ ] **P1:** monitoreo batería ADC3: alerta 2.1 V, **mute preventivo 1.95 V antes del brownout**
- [ ] **P1:** detector phantom GP15 con histéresis + LED amarillo (salida muerta nunca silenciosa)
- [ ] **P1:** Watchdog 4 s; MSPLIM stack guard (`rules/10`)
- [ ] **P2:** buffers `static`, ping-pong DMA, cero `new/malloc`; `config.h` = punto único de verdad
- [ ] **P2:** NeoPixel con cap de brillo (≤8 mA) en `config.h`
- [ ] **P3:** DC-block primero; ganancia con semántica segura; NaN imposible (FTZ, sin divisiones en hot-path); `typedef float sample_t`
- [ ] **UI:** dirty-flag atómico Core 0 → Core 1 (`std::atomic`, `rules/10`); crossfade obligatorio en todo cambio de parámetro audible

---

## 6. Riesgos (vivos, con dueño de fase)

| ID | Riesgo | Mitigación | Fase |
|---|---|---|---|
| R1 | Techo SPL real < 128 dB (discrepancia §3.2) | A/B + clip-latch; gate F8 | F1/F5 |
| R2 | Consumo real > estimado (35 h teóricas) | Medir en F1 (USB+amperímetro) y F7; gate 35 mA | F1/F7 |
| R3 | Pop al cambiar presets | Crossfade ~10 ms + dirty-flag; gate F6 | F6 |
| R4 | Módulo MSM261 sin L/R expuesto | Fallback 3 líneas SD (patrón bschwind) | F2 |
| R5 | **Presupuesto phantom justo** (Iq TLE2072 ~7 mA vs 9.7 mA disponibles) | Gate W1: medir Iq real < 8 mA; fallback zener 12 V o OPA1678 (2 mA/canal, mismo footprint) | Producto/W1 |
| R6 | Contactos de portapilas vibrando (el acordeón se mueve) | Portapilas de calidad + 220 µF; prueba de sacudida en F7 | F7 |
| R7 | Módulos AliExpress con die falso/clon | El A/B contra IM69D130 (documentado) lo destapa en F1 | F1/F5 |
| R8 | Carga descontrolada NiMH por USB | Diodo SS14 serie (§2.5); verificar en F7 que las celdas no se calientan con USB puesto | F7 |
| R9 | **Mesa sin phantom = silencio total** (trade-off F0.1 aceptado) | Detector GP15 + LED amarillo con instrucción clara al músico; semáforo F0.1 | F6/producto |
| R10 | Zap por hot-plug XLR con phantom activo | TVS/zener + R serie pines 2/3 (bloque V1 analógica); gate W2 ×20 ciclos sin thump | Producto/W2 |

---

## 7. Lo que este PoC NO hace (YAGNI explícito)

- ❌ No librería de efectos (EQ/chorus/doubler) — post-GO, portada DRY desde `lib_DSP` de los pedales; el doubler rompería el gate de latencia de validación
- ❌ No pantallas OLED/TFT/LCD (ilegibles en escenario = anti-touring); no encoders con menús
- ❌ No más de 1 botón + 1 LED (el mecanismo se valida con uno; la matriz completa es producto)
- ❌ No Phantom para el dominio digital (migrado permanente a AA — decisión de usuario); el phantom SOLO alimenta la etapa de salida (F0.1)
- ❌ No 4º micrófono ni cobertura de bajos (decisión de producto: 3 mics solo agudos)
- ❌ No etapa phantom-híbrida en banco (gates W1–W3 son fase producto; la salida de banco es la línea del PCM5102A)
- ❌ No STM32, no ESP32, no WiFi, no Bluetooth, no USB-audio-device

---

## Historial

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0–1.2 | 2026-08-30 | Evolución 2→3 mics (solo agudos); F0 cerrado (Pico2+Philhower, STM32 descartado); A/B cápsulas; relojes duales; buck-phantom F7. |
| 1.3 | 2026-08-30 | (Gemini, sobre V1.2) Decisiones de usuario: baterías AA + UI MVP. ⚠️ Perdió el gate GO/NO-GO, la tabla de relojes y la disciplina R1; añadió efectos al PoC; sin dido USB↔NiMH; sin batería-baja ni mute fail-safe; BOM/TLE2072 inconsistentes. |
| 1.4 | 2026-08-30 | Reconstrucción senior: restaura GO/NO-GO (F8) + relojes + R1 completa; efectos → post-GO (DRY desde lib_DSP); **P1: dido SS14 batería→VSYS** (carga descontrolada USB), electro 220 µF anti-vibración, batería-baja por ADC3 con **mute preventivo 1.95 V**, XSMT con pull-down fail-safe; NeoPixel capped ≤8 mA; matemática de batería coherente (≤35 mA → ≥30 h); F0.1 abierta: etapa balanceada XLR (transformador vs RRIO 3.3 V, TLE2072 inviable a 3.3 V); F6 = UI-mecanismo con gate anti-pop medible. |
| 1.5 | 2026-08-30 | **F0.1 CERRADA** (decisión de usuario, sesión Gemini): etapa salida = **híbrida baterías+phantom** (phantom alimenta SOLO el TLE2072 por el XLR; baterías quedan íntegras para lo digital → gate ≤35 mA intacto) + **detector de phantom**. Integrada con fixes: matemática de presupuesto (Thevenin 48 V/3.405 kΩ → zener 15 V baseline, 9.7 mA, margen 1.35×, headroom +22.8 dBu); divisor detector corregido 100k/27k a GP15 (el 10k/3.3k de la propuesta robaba 0.9 mA = 10% del presupuesto); protección hot-plug TVS + grounding pin 1 (omitidos en la propuesta); gates W1–W3 para la etapa en fase producto; semáforo NeoPixel unificado (fijo/rojo/amarillo); riesgos R5/R9/R10. |
