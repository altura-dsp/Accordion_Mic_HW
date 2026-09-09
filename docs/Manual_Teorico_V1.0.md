# Manual Teórico de Audio Analógico (V1.0)

**Versión:** 1.0 · **Fecha:** 2026-09-08 · **Base:** `Arquitectura_Hardware.md` V1.1 (consolidación post-Red Team)

Este manual explica las decisiones de diseño del circuito bajo las restricciones del Phantom Power.

## 1. Presupuesto Phantom (Power Budget)

El Phantom Power estándar (IEC 61938: +48V a través de dos resistencias de 6.81 kΩ en la consola) entrega como **máximo teórico ~14 mA** en cortocircuito. El circuito extrae esa alimentación por los pines 2/3 del XLR mediante **R_PH1/R_PH2_EXTRACT = 220 Ω al 0.1%** (ECO 2026-08-21: el valor anterior 2.2 kΩ estrangulaba el presupuesto; lo que protege el CMRR es el matching 0.1%, no el valor).

*   **Presupuesto validado (peor caso, Red Team):** disponible = (48−12)/(6810+220)×2 ≈ **10.2 mA** contra un consumo máximo de **9.39 mA** (92 % de uso). Nota de rodilla: a consumo máximo simultáneo el zener queda a ~0.85 mA (IZK ≈ 1 mA) y el riel puede caer a ~11.4 V, aún por encima del mínimo del TLE2072 (±4.5 V).
*   **Por eso usamos diseño Híbrido:** 
    *   **OPA1642 (Sumador U1A + Buffer/LPF U1B):** Ultra bajo ruido (5.1 nV/√Hz), consume ~5.4 mA máx.
    *   **TLE2072 (Inversor COLD U2A + Buffer de V_BIAS U2B):** Menor consumo (~3.6 mA máx) con capacidad de drive suficiente para líneas de 600 Ω.
    *   **Total op-amps:** ~9.0 mA (88 % del budget P48). Usar dos OPA1642 colapsaría el voltaje de la fuente a < 8V.

### 1.1 Tierra Virtual Bufferizada (V_BIAS = +6V)

El divisor 100k/100k desnudo presenta un Thevenin de 50 kΩ y **no puede** alimentar las 3 cápsulas electret (~0.3 mA totales): SPICE demostró el midrail colapsando a 2.4 V y el sumador clipeando contra 0 V (hallazgo F3.2, ECO 2026-08-22). Solución con **cero partes nuevas**: el canal U2B del TLE2072 (antes libre) queda como seguidor del divisor.

*   **Ruta:** `V_PHANTOM_12V → R_VBIAS_TOP 100k → V_BIAS_REF → R_VBIAS_BOT 100k → GND` · `V_BIAS_REF → U2B (IN+)` · `U2B (OUT) → V_BIAS` (lazo cerrado pin 6→7).
*   El desacoplo C_VBIAS_FILTER 10 µF va **en el rail V_BIAS** (salida del buffer), no sobre la referencia del divisor.

## 2. Filtros y Frecuencias de Corte (Fc)

### 2.1 Filtro Pasa Altos (HPF) de Entrada
*   **Topología:** RC Serie (Acople AC de los Mics).
*   **Valores:** C = 100 nF (C_MICx_AC), R = 10 kΩ (R_MICx_SUM).
*   **Fórmula:** `Fc = 1 / (2π · R · C)` = `1 / (2π · 10k · 100nF)` ≈ **159 Hz** (verificado SPICE: 159.2 Hz). **[DECISIÓN FIRMADA 2026-08-22: 159 Hz DEFINITIVO]** — cápsulas en el lado de agudos (treble-grille); renuncia explícita a la alternativa ~72 Hz.
*   **Motivo:** Cortar frecuencias subsónicas e impactos físicos del fuelle del acordeón para no saturar los preamplificadores de la consola (Rumble filter).

### 2.2 Filtro Pasa Bajos (LPF) Anti-Hiss
*   **Topología:** RC Serie sobre el buffer U1B (nodos **LPF_IN → LPF_OUT**).
*   **Valores:** R = 3.3 kΩ (R_LPF), C = 3.3 nF C0G/NP0 (C_LPF).
*   **Fórmula:** `Fc = 1 / (2π · 3.3k · 3.3nF)` ≈ **14.6 kHz** (SPICE: 14.9 kHz).
*   **Motivo:** Las cápsulas electret suelen tener picos de alta frecuencia. El corte suaviza el "hiss" y siseo de las válvulas del acordeón sin afectar el tono musical. La banda de paso (300 Hz–10 kHz) se valida con planicie ±1 dB (caída acumulada ~1.1 dB en los extremos por los corners firmados).

## 3. Extracción de Señal Diferencial (Balanceo)

La señal entra asimétrica al sumador (ganancia −3× con R_SUM_FB 30 kΩ). Para convertirla a diferencial (XLR):
1.  La rama **HOT (Pin 2)** sale del buffer U1B (LPF_OUT) sin inversión de fase (0°) a través de R_BAL_HOT 470 Ω.
2.  La rama **COLD (Pin 3)** toma LPF_OUT y pasa por el Inversor de Ganancia Unitaria U2A (R_INV_IN / R_INV_FB = 10 kΩ **1% matched**, 180°) a través de R_BAL_COLD 470 Ω.
3.  **Crucial:** el matching 1 % del inversor y el 0.1 % de R_PH aseguran que la amplitud COLD sea el espejo exacto de HOT, maximizando el Rechazo de Modo Común (CMRR). Criterio Red Team: residuo en modo común a 1 kHz ≥ 34 dB bajo la ganancia diferencial nominal (+15.6 dB = ×6) → **límite −18 dB @ 1 kHz** (banco `cmrr_common_mode`; la sim topológica mide −300 dB, el matching físico es constraint de BOM).
4.  **R_BAL 470 Ω** (ECO 2026-08-22: 100→470 Ω): cabeza resistiva contra la que el J111 del mute clampa el transitorio de encendido, y aísla al opamp del cable capacitivo. Pérdida plana ~0.5 dB, dentro del margen ±1 dB.
5.  Bloqueo anti-phantom imperativo: C_BLOCK_HOT / C_BLOCK_COLD **47 µF 63V bipolares** + ferritas FB_HOT / FB_COLD 600 Ω @ 100 MHz antes del conector.

## 4. Mute Anti-Pop (J111) y Protección de Salida

### 4.1 Shunt diferencial J111 (ECO 2026-08-22, FASE 3)
Al energizar el phantom, U1B y U2A despiertan a velocidades distintas y los C_BLOCK cargan asimétricos: pico diferencial medido de **627 mV** (@ 9.4 ms). El JFET **Q_MUTE J111 en shunt entre los nodos HOT y COLD** (D→HOT, S→COLD) lo reduce a **92 mV** (< 100 mV, criterio F5.2): corta el diferencial —lo único que la consola ve— mientras el modo común lo rechaza su CMRR.
*   **Red de gate (τ = 1 s):** C_GATE_MUTE 1 µF desde el riel *acopla* la subida al gate (JFET ON durante el transitorio; el pico clampa por Rds contra 2×470 Ω de R_BAL) y R_GATE_MUTE 1 MΩ a masa lo baja después → Vgs = −6 V = **cortado para siempre, fuera del camino de señal** (THD medido 0.0075 %).
*   El spread de Vto del J111 (−3…−10 V) es benigno a Vgs = −6 V: solo desplaza el fade de apertura (~1–3 s, inaudible).
*   Topología serie descartada por física: 367 mV medidos (en uic Vgs = 0 = ON justo durante el pico).
*   Un relé de mute es físicamente imposible con 10 mA de presupuesto; el JFET consume µA. Limitación documentada: protege el encendido medido; el plug-in del XLR con phantom ya vivo es validación de bench.

### 4.2 Protección ESD de la salida (diseño SIN TVS en XLR 2/3)
Los pines 2/3 del XLR llevan +48V DC permanentes de phantom: una TVS de 12 V avalancha en continuo y robaría ~9.7 mA del presupuesto (ECO 2026-08-21, renuncia documentada). La ESD queda cubierta por las 6.81 kΩ de la consola + el zener del raíl + las ferritas. Alternativa futura si se exige ESD directa en conector: TVS con VRWM ≥ 48 V (SMBJ51CA) a chasis.
