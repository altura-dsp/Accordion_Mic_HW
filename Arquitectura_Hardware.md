# Arquitectura de Hardware: Acordeón Mic

**Versión:** 1.1 · **Fecha:** 2026-08-24 · **Estado:** Consolidación SSOT post-Red Team (PLAN_Remediacion FASE 1–5 ejecutadas)

Este documento detalla el ruteo electrónico y las topologías de conexión para el circuito "Acordeón Mic" (puramente analógico). Es la Fuente de Verdad para la generación de la Netlist (SKiDL).

## 1. Topología Analógica y Suma de Señales
El circuito mezcla pasivamente a voltaje 3 micrófonos, realiza suma activa, aplica un LPF y balancea la salida.
> **Nota de Pines Op-Amp (Diseño Híbrido):** La cadena de señal usa dos ICs distintos para respetar el budget phantom en el peor de los casos.
> - **U1 = OPA1642** (JFET dual, SMD SOIC-8 sobre adaptador a DIP-8): OpA = sumador inversor (Pines 1,2,3) y OpB = buffer/LPF HOT (Pines 5,6,7). Etapa de entrada donde importa el ruido ultra-bajo (5.1 nV/√Hz). Consumo máx 5.4 mA.
> - **U2 = TLE2072** (Excalibur dual, DIP-8): OpC = inversor COLD (Pines 1,2,3). Driver de la rama fría balanceada. OpD (Pines 5,6,7) = **BUFFER DEL MIDRAIL V_BIAS** [ECO 2026-08-22, FASE 3 Red Team: seguía del divisor 100k/100k — Thevenin 50k imposible para 3 cápsulas ~0.3mA, el midrail colapsaba a 2.4V en SPICE y el verano clipeaba contra 0V; cero partes nuevas]. Consumo máx 3.6 mA.
> - En ambos ICs: Pin 8 = V+ (`V_PHANTOM_12V`), Pin 4 = V- (`GND`).

**Ruteo de los Micrófonos (Se repite para MIC1, MIC2, MIC3):**
- `V_BIAS · Net → R_MIC1_BIAS · Pin 1`
- `R_MIC1_BIAS · Pin 2 → MIC1 · Pin 1 (Signal)`
- `MIC1 · Pin 2 (GND) → GND · Net`
- `MIC1 · Pin 1 (Signal) → C_MIC1_AC · Pin 1`
- `C_MIC1_AC · Pin 2 → R_MIC1_SUM · Pin 1`
- `R_MIC1_SUM · Pin 2 → MIX_NODE · Net`

**Sumador Activo (OpA):**
- `MIX_NODE · Net → U1_OPA1642 · Pin 2 (IN_A-)`
- `V_BIAS · Net → U1_OPA1642 · Pin 3 (IN_A+)`
- `U1_OPA1642 · Pin 2 (IN_A-) → R_SUM_FB · Pin 1`
- `R_SUM_FB · Pin 2 → U1_OPA1642 · Pin 1 (OUT_A)`

**Control de Volumen:**
- `U1_OPA1642 · Pin 1 (OUT_A) → RV_VOL · Pin 3`
- `RV_VOL · Pin 1 → V_BIAS · Net`
- `RV_VOL · Pin 2 (Wiper) → R_LPF · Pin 1`

**LPF y Driver Balanceado (OpB y OpC):**
- `R_LPF · Pin 2 → U1_OPA1642 · Pin 5 (IN_B+)`
- `U1_OPA1642 · Pin 5 (IN_B+) → C_LPF · Pin 1`
- `C_LPF · Pin 2 → GND · Net`
- `U1_OPA1642 · Pin 6 (IN_B-) → U1_OPA1642 · Pin 7 (OUT_B)`
- `U1_OPA1642 · Pin 7 (OUT_B) → R_BAL_HOT · Pin 1`
- `U1_OPA1642 · Pin 7 (OUT_B) → R_INV_IN · Pin 1`
- `R_INV_IN · Pin 2 → U2_TLE2072 · Pin 2 (IN_A-)`
- `V_BIAS · Net → U2_TLE2072 · Pin 3 (IN_A+)`
- `U2_TLE2072 · Pin 2 (IN_A-) → R_INV_FB · Pin 1`
- `R_INV_FB · Pin 2 → U2_TLE2072 · Pin 1 (OUT_A)`
- `U2_TLE2072 · Pin 1 (OUT_A) → R_BAL_COLD · Pin 1`

**Protección Touring Grade (Anti-Phantom y Salida XLR):**
- `R_BAL_HOT · Pin 2 → C_BLOCK_HOT · Pin 1`
- `C_BLOCK_HOT · Pin 2 → XLR_OUT · Pin 2`
- `R_BAL_COLD · Pin 2 → C_BLOCK_COLD · Pin 1`
- `C_BLOCK_COLD · Pin 2 → XLR_OUT · Pin 3`
- **[MUTE ANTI-POP JFET — ECO 2026-08-22 FASE 3]** `Q_MUTE · Pin 2 (D) → R_BAL_HOT · Pin 2` (nodo HOT) · `Q_MUTE · Pin 3 (S) → R_BAL_COLD · Pin 2` (nodo COLD) · `Q_MUTE · Pin 1 (G) → GATE_MUTE · Net`: un J111 en **SHUNT DIFERENCIAL** entre los nodos HOT/COLD (lo único que la consola ve; el modo común lo rechaza su CMRR). Banco pop_plugin: 627 mV pico diferencial al powerup (U1B OPA1642 y U2A TLE2072 despiertan a velocidades distintas, C_BLOCK cargan asimétricos, pico @9.4ms) → **92 mV** con el mute (<100 mV, criterio F5.2). La red de gate (§3) acopla la subida del riel: JFET ON durante el transitorio (diferencial clampado por Rds contra 2×470 de R_BAL), luego cortado para siempre = **fuera del camino de señal** (THD medido 0.0075%). El spread de Vto (−3..−10V) es benigno: a Vgs=−6V cualquier specimen queda en corte o sub-umbral GΩ; solo desplaza el fade de apertura (~1–3 s, inaudible). Descartado por física (medido 367 mV): JFET serie con gate-RC desde el propio riel — en uic Vgs=0=ON justo durante el pico. Limitación documentada: protege el powerup medido; el plug-in del XLR con phantom ya vivo es validación de bench F6.
- **[ECO Red Team 2026-08-21 / P0-2]** TVS P6KE12CA ELIMINADAS de los pines 2/3 del XLR: llevan +48V DC de phantom y una TVS de 12V avalancha en continuo (~9.7mA robados del presupuesto). ESD cubierta por las 6.81kΩ de la consola + zener del raíl + ferritas. Alternativa futura si se exige ESD directa: TVS VRWM ≥ 48V (SMBJ51CA) a chasis.
- `XLR_OUT · Pin 1 → SW_GROUND_LIFT · Pin 1 (Common)`
- `SW_GROUND_LIFT · Pin 2 (GND) → CHASIS_GND · Net`
- `SW_GROUND_LIFT · Pin 3 (LIFT) → R_GLIFT · Pin 1`
- `SW_GROUND_LIFT · Pin 3 (LIFT) → C_GLIFT · Pin 1`
- `R_GLIFT · Pin 2 → CHASIS_GND · Net`
- `C_GLIFT · Pin 2 → CHASIS_GND · Net`

## 2. Microcontrolador, GPIOs y Relojes
**[N/A]** - Proyecto puramente analógico (KISS). No existe RP2350, ni I2S, ni MCLK.

## 3. Fuente de Alimentación y Aislamiento (F.A.)
Extrae el Phantom Power desde las líneas de audio, lo limita a 12V y genera una tierra virtual (V_BIAS) de +6V para alimentar la cadena híbrida (OPA1642 + TLE2072) en modo asimétrico.

**Extracción y Regulación (12V):**
- `XLR_OUT · Pin 2 → R_PH1_EXTRACT · Pin 1`
- `XLR_OUT · Pin 3 → R_PH2_EXTRACT · Pin 1`
- `R_PH1_EXTRACT · Pin 2 → V_PHANTOM_12V · Net`
- `R_PH2_EXTRACT · Pin 2 → V_PHANTOM_12V · Net`
- `V_PHANTOM_12V · Net → D_ZENER_12V · Pin 1 (Cathode)`
- `D_ZENER_12V · Pin 2 (Anode) → GND · Net`
- `V_PHANTOM_12V · Net → C_FILTER_12V · Pin 1`
- `C_FILTER_12V · Pin 2 → GND · Net`

**Alimentación de Op-Amps:**
- `V_PHANTOM_12V · Net → U1_OPA1642 · Pin 8 (V+)`
- `GND · Net → U1_OPA1642 · Pin 4 (V-)`
- `V_PHANTOM_12V · Net → U2_TLE2072 · Pin 8 (V+)`
- `GND · Net → U2_TLE2072 · Pin 4 (V-)`

**Generación de Virtual Ground (V_BIAS a +6V) — BUFFERED [ECO 2026-08-22 FASE 3]:**
- `V_PHANTOM_12V · Net → R_VBIAS_TOP · Pin 1`
- `R_VBIAS_TOP · Pin 2 → V_BIAS_REF · Net`
- `V_BIAS_REF · Net → R_VBIAS_BOT · Pin 1`
- `R_VBIAS_BOT · Pin 2 → GND · Net`
- `V_BIAS_REF · Net → U2_TLE2072 · Pin 5 (IN_B+)`
- `U2_TLE2072 · Pin 6 (IN_B-) → U2_TLE2072 · Pin 7 (OUT_B)`
- `U2_TLE2072 · Pin 7 (OUT_B) → V_BIAS · Net`
- `V_BIAS · Net → C_VBIAS_FILTER · Pin 1` (desacoplo en el RAIL, no sobre la referencia)
- `C_VBIAS_FILTER · Pin 2 → GND · Net`
- **Why buffer:** el divisor 100k/100k desnudo (Thevenin 50k) no puede alimentar las 3 cápsulas electret (~0.3mA): SPICE demostró V_BIAS colapsando a 2.4V y el verano clipeando contra 0V (hallazgo F3.2). U2B (canal libre del TLE2072) como seguidor = cero partes nuevas.

**Red de Gate del Mute JFET (τ = 1 s):**
- `V_PHANTOM_12V · Net → C_GATE_MUTE · Pin 1` (acopla la subida del riel al gate → JFET ON al encender)
- `C_GATE_MUTE · Pin 2 → GATE_MUTE · Net`
- `GATE_MUTE · Net → R_GATE_MUTE · Pin 1`
- `R_GATE_MUTE · Pin 2 → GND · Net` (pull-down → Vgs=−6V en régimen = corte permanente)

## 4. Interfaz de Usuario
El potenciómetro `RV_VOL` regula la salida de mezcla hacia el driver balanceado. No existen encoders digitales ni hardware debouncing ya que el circuito es analógico.

## 5. Metas de Simulación Analógica (Touring Grade Targets)
> **DOMINIO: Touring Grade (HARDWARE analógico).** 

- **Banco ENTRADA / SALIDA (Pipeline completo):** AC Sweep 20 Hz–20 kHz. Se inyecta señal por las entradas de micrófono simuladas y se mide en el XLR OUT diferencial (Pin 2 - Pin 3).
- **Metas de Filtros:** 
  - HPF de entrada a **159 Hz** para rechazar ruido de baja frecuencia del fuelle (medición: cruce descendente en bandas bajas, ej. 0.1 Hz). **[DECISIÓN FIRMADA Jose 2026-08-22: 159 Hz DEFINITIVO]** — C_AC 100 nF inmutable, colocación de cápsulas en el lado de agudos (treble-grille); se renuncia explícitamente a la alternativa ~72 Hz (C_AC 220 nF) para capturar la mano izquierda. Verificado SPICE: 159.2 Hz.
  - LPF anti-hiss a **14.6 kHz**.
- **Umbrales Touring Grade:** THD+N **< 0.1 % @ 1 kHz**, Respuesta de Frecuencia Plana en la banda de paso (300 Hz - 10 kHz). Riel phantom regulado en ventana 11.5–12.5 V (ripple zener y powerup transitorio); residuo de modo-común (CMRR) ≤ −18 dB @ 1 kHz.

## 6. BOM (SKiDL-ready) — alimenta inventario_bruto.csv

| Ref | Valor | Package (THT/SMD) | Montaje | Veredicto ROI/YAGNI |
|---|---|---|---|---|
| MIC1, MIC2, MIC3 | Primo EM289 / EM189T (128dB) | THT/Wire | Manual | Alto SPL (128dB) requerido por fuelle. ROI Excelente (~2$). |
| R_MIC1_BIAS, R_MIC2_BIAS, R_MIC3_BIAS | 33 kΩ | THT | Soldado | Bias de cápsulas. Garantiza ~2.4V cayendo desde el riel de +6V. |
| C_MIC1_AC, C_MIC2_AC, C_MIC3_AC | 100 nF | THT (Film) | Soldado | Bloqueo DC y HPF 159Hz crítico. |
| R_MIC1_SUM, R_MIC2_SUM, R_MIC3_SUM | 10 kΩ | THT | Soldado | Suma resistiva. |
| U1_OPA1642 | OPA1642 | SMD (SOIC-8) a DIP-8 | Adaptador/Zócalo | Sumador de entrada. Ruido nulo (5.1 nV/√Hz), consumo max 5.4mA. |
| U2_TLE2072 | TLE2072 | DIP-8 | Zócalo | Driver de salida. Mejor drive que TL072, consumo max 3.6mA. |
| R_SUM_FB | 30 kΩ | THT (1%) | Soldado | Feedback del sumador. Ganancia -3× (compensa la división de sumar 3 señales). |
| R_INV_IN, R_INV_FB | 10 kΩ | THT (1%) | Soldado | Inversor COLD, ganancia -1× (matched para preservar CMRR). |
| RV_VOL | 10 kΩ Audio | Panel (THT) | Manual | Control maestro. |
| R_LPF | 3.3 kΩ | THT | Soldado | Parte del LPF 14.6kHz. |
| C_LPF | 3.3 nF C0G/NP0 | THT (Cerámico) | Soldado | Dieléctrico estable para LPF. |
| R_BAL_HOT, R_BAL_COLD | 470 Ω | THT (1%) | Soldado | Equilibrio de impedancia de salida. ECO 2026-08-22 (FASE 3): 100→470Ω — cabeza resistiva contra la que el J111 del mute clampa el diferencial de encendido (627→92 mV); además aísla al opamp del cable capacitivo. Pérdida plana ~0.5 dB, dentro del margen de planicie ±1 dB. |
| C_BLOCK_HOT, C_BLOCK_COLD | 47 µF 63V Bipolar | THT (Electrolítico) | Soldado | Bloqueo Anti-Phantom imperativo. |
| Q_MUTE | J111 (JFET n-ch) | THT (TO-92) | Soldado | Mute anti-pop shunt diferencial (ECO 2026-08-22 FASE 3). En régimen cortado (Vgs=−6V): invisible en la señal. Pinout TO-92 por fabricante — verificar datasheet en KiCad (Ley 15). |
| R_GATE_MUTE | 1 MΩ | THT | Soldado | Pull-down del gate del mute (τ=1s con C_GATE). |
| C_GATE_MUTE | 1 µF | THT (Film) | Soldado | Acopla la subida del riel al gate → JFET ON durante el transitorio de encendido. |
| XLR_OUT | Neutrik NC3MAH | Panel/THT | Manual | Conector principal. |
| R_PH1_EXTRACT, R_PH2_EXTRACT | 220 Ω | THT (0.1%) | Soldado | Preservación estricta de CMRR. ECO 2026-08-21: 2.2k→220Ω corrige el presupuesto phantom (10.2mA disp. vs 9.39mA consumo máx); el matching 0.1% es lo que protege el CMRR, no el valor. |
| D_ZENER_12V | 1N4742A | THT | Soldado | Regulación pasiva desde +48V. |
| C_FILTER_12V | 100 µF 25V | THT (Electrolítico) | Soldado | Filtro principal del Zener (ripple 50/60Hz y transitorios de consumo). |
| C_VBIAS_FILTER | 10 µF | THT (Electrolítico) | Soldado | Desacoplo de la referencia V_BIAS. |
| R_VBIAS_TOP, R_VBIAS_BOT | 100 kΩ | THT | Soldado | Divisor resistivo V_BIAS. |
| SW_GROUND_LIFT | SPDT Switch | Panel/THT | Manual | Ground Lift (Phantom-Safe). |
| R_GLIFT | 100 Ω 1W | THT | Soldado | Retorno DC para Phantom en modo LIFT. |
| C_GLIFT | 10 nF 250V | THT (Y-Class) | Soldado | Filtro RF en modo LIFT. |
| C_DEC_HF1, C_DEC_HF2 | 100 nF X7R | THT (Cerámico) | Soldado | Desacoplo HF de los ICs (uno por V+ de U1 y U2). Estabilidad. |
| FB_HOT, FB_COLD | Ferrita 600Ω @100MHz | THT (Murata BLM18 equiv) | Soldado | Bloqueo RF en salida XLR, invisible en banda de audio. |
| SHOCK_MOUNT | Gomas antivibración + Felt boots | Hardware | Manual | Aislamiento mecánico Touring Grade obligatorio. |

---

## Changelog / ECOs

### ECO 2026-08-24 — Red Team FASE 4+5: footprints reales, BOM comprable, consolidación SSOT V1.1
- **Footprints físicos (F4.1):** 19 entradas del proyecto + 2 defaults por categoría (R/C THT) en `tools/footprint_map.json`, verificados contra la librería KiCad 10 instalada (Ley 15): XLR Neutrik NC3MAH real (antes footprint de **resistencia**), cápsula EM289 THT/Wire (antes 0402/MLF-24, absurdo), OPA1642 SOIC-8, TLE2072 PDIP-8, 1N4742A DO-41, electrolíticos radiales por voltaje, ferrita THT, SW_SPDT.
- **Refs lógicas en el netlist (motor):** skidl ya no auto-numera (R1, C1, U1…); el netlist KiCad usa las Referencia_Local de este documento → paridad 1:1 wiring ↔ BOM ↔ PCB (42 refs).
- **BOM comprable (F4.2):** `BOM_Arquitectura.md` = 27 líneas / 42 piezas, agrupadas por (Categoría, Valor, Footprint); LCSC es atributo, no clave de agrupación. Eliminada la mentira "33 kΩ ×21" (LCSC C78546 reciclado como placeholder).
- **Recategoría:** `SW_GROUND_LIFT` pasa de XLR a **SWITCH** (símbolo `Switch:SW_SPDT`, pines 1=A 2=B 3=C verificados en KiCad 10).
- **Esqueleto purgado (F5.3):** cero DUMMY_ENCODER/DUMMY_HC14 (encoders ahora OPT-IN vía `ITERATOR_BASE_ENCODER`), netlist con 27/27 nets con nodos (cero huérfanas), y el deck SPICE ya no emite la fuente `V_VEE` fantasma en proyectos single-supply (el motor emite cada fuente de riel solo si su net tiene pines).
- **Decisiones firmadas por Jose (F5.5, 2026-08-22):** ① HPF **159 Hz DEFINITIVO** (C_AC 100 nF, colocación treble-grille; renuncia documentada a ~72 Hz / mano izquierda). ② ESD directa en conector = **renuncia documentada** (default del PLAN; la ESD queda cubierta por 6.81 kΩ de consola + zener de raíl + ferritas).
- **Mute anti-pop (F5.2) — CERRADO:** resuelto en FASE 3 (ver ECO 2026-08-22): J111 shunt diferencial + red de gate τ=1 s, pop medido 92 mV < 100 mV. Excepción/limitación documentada: el plug-in del XLR con phantom ya vivo queda como validación de bench F6.
- Motor (agnóstico): caché `_sklib.py` de skidl neutralizada (`backup_parts` no-op) — el netlist ya no puede "recordar" el estado físico de una corrida anterior (reproducibilidad, DIRECTIVA CERO).

### ECO 2026-08-22 — Red Team FASE 3: SPICE hardening, gate 8/8 PASS
Testbench con chasis realista + 5 bancos nuevos (`powerup_transient`, `gain_band`, `thd_1khz`, `cmrr_common_mode`, `pop_plugin`). Resultado final 8/8: HPF 159.2 Hz · LPF 14.9 kHz · zener 12.3 V · powerup 12.06 V · planicie 0.80 dB · THD 0.0075 % @1 kHz (nivel cápsula 10 mVpk) · CMRR −300 dB · pop 92 mV.
- **Buffer del midrail (hallazgo real):** U2B (TLE2072 canal B, antes libre) ahora sigue el divisor 100k/100k → V_BIAS de baja impedancia. Sin él, las 3 cápsulas (~0.3mA) colapsaban el Thevenin 50k a 2.4V y el verano clipeaba contra 0V (demostrado en SPICE). Cero partes nuevas.
- **Mute anti-pop J111 (hallazgo real):** pop de encendido diferencial de 627 mV (chips HOT/COLD despiertan distinto, pico @9.4ms) → 92 mV con un J111 en shunt diferencial + red de gate τ=1s + R_BAL 100→470Ω. Topología serie descartada por física (367 mV: en uic Vgs=0=ON durante el pico).
- **RV_VOL:** value de testbench `POT_10K` (modelo RK27 del motor); físico = pot de panel 10k (TS-1902A). Con value "10k" el exportador lo trataba como R de 2 terminales y el pin de señal quedaba al aire (cadena muerta a −60dB) — fix de pinmap del motor.
- Motor (agnóstico): extensiones `powerup/uic`, `settle_time_s`, `band_points_hz/band_tolerance_db`, `input_nodes` (modo común), `output_node_cold` (diferencial); pinmap `POT_10K` y `J111` (primitiva J nativa); modelos `J111.lib` (β recalculada a Idss 20mA real) y reuso de `RK27_10kB_dual.lib`.

### ECO 2026-08-21 — Red Team (PLAN_Remediacion_RedTeam_V1.0, FASE 1+2 ejecutadas)
- **P0-1 (Zener):** el cableado `D_ZENER_12V pin1→riel / pin2→GND` de esta doc siempre fue el físicamente correcto (pin1=K en el símbolo Device:D). El `wiring_logic.py` se revirtió a esta orientación tras corregir el exportador de diodos del motor (`tools/main_build.py` ahora resuelve pines por nombre A/K, no por número). Evidencia: con el motor honesto, el wiring anterior colapsaba el raíl a 1.37V en sim (zener FORWARD); con el revert, SPICE 3/3 PASS y el hardware físico correcto.
- **P0-2 (TVS):** ELIMINADAS `TVS_HOT`/`TVS_COLD` (P6KE12CA) de los pines 2/3 del XLR (avalancha continua sobre +48V DC, ~9.7mA robados). Renuncia documentada en §Protección; inventario/alias/BOM actualizados.
- **P0-3 (R_PH):** `R_PH1/PH2_EXTRACT` 2.2kΩ → **220Ω 0.1%**. Presupuesto corregido: disponible = (48−12)/(6810+220)×2 ≈ **10.2mA** vs consumo máx 9.39mA (92%). Nota de rodilla: a consumo máximo simultáneo el zener queda a ~0.85mA (IZK≈1mA) → raíl puede caer a ~11.4V, aún > mínimo del TLE2072. Cierre final: medición real de cápsula (FASE 5.4 del PLAN).
- **P1-4 (RL_12V):** carga ligera del raíl (100k) movida del DUT físico al testbench SPICE (`build_spice_stage`); NO es parte del BOM. Cierra el error "No footprint for R/R6x" del netlist KiCad.
- `docs/temp/` NO tocado: histórico con valores pre-ECO; destino se decide en FASE 5.1 del PLAN.
