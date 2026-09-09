# Manual Teórico de Audio Analógico (V1.0)

Este manual explica las decisiones de diseño del circuito bajo las restricciones del Phantom Power.

## 1. Presupuesto Phantom (Power Budget)

El Phantom Power estándar (+48V, a través de dos resistencias de 6.8 kΩ) entrega como **máximo teórico ~14 mA** al hacer un cortocircuito a tierra. Sin embargo, para mantener un voltaje operativo decente (ej. 12V), el circuito **no debe consumir más de ~10 mA**.

*   **Por eso usamos diseño Híbrido:** 
    *   **OPA1642 (Sumador):** Ultra bajo ruido, pero consume ~5.4 mA.
    *   **TLE2072 (Driver):** Menor consumo (~3.6 mA) con capacidad de drive suficiente para líneas de 600 Ω.
    *   **Total:** ~9.0 mA (Seguro, por debajo del límite, dejando margen para el Zener). Usar dos OPA1642 colapsaría el voltaje de la fuente a < 8V.

## 2. Filtros y Frecuencias de Corte (Fc)

### 2.1 Filtro Pasa Altos (HPF) de Entrada
*   **Topología:** RC Serie (Acople AC de los Mics).
*   **Valores:** C = 100 nF, R = 10 kΩ (Entrada del sumador).
*   **Fórmula:** `Fc = 1 / (2π · R · C)` = `1 / (2π · 10k · 100nF)` ≈ **159 Hz**.
*   **Motivo:** Cortar frecuencias subsónicas e impactos físicos del fuelle del acordeón para no saturar los preamplificadores de la consola (Rumble filter).

### 2.2 Filtro Pasa Bajos (LPF) Anti-Hiss
*   **Topología:** RC Serie.
*   **Valores:** R = 3.3 kΩ, C = 3.3 nF.
*   **Fórmula:** `Fc = 1 / (2π · 3.3k · 3.3nF)` ≈ **14.6 kHz**.
*   **Motivo:** Las cápsulas electret suelen tener picos de alta frecuencia. El corte a 14.6 kHz suaviza el "hiss" y siseo de las válvulas del acordeón sin afectar el tono musical.

## 3. Extracción de Señal Diferencial (Balanceo)

La señal entra asimétrica al sumador. Para convertirla a diferencial (XLR):
1.  La rama **HOT (Pin 2)** pasa por un Buffer (U1B) sin inversión de fase (0°).
2.  La rama **COLD (Pin 3)** toma la salida de la rama HOT y la pasa por un Inversor de Ganancia Unitaria (U2A, -1x, 180°). 
3.  **Crucial:** Las resistencias del Inversor (R_INV_IN, R_INV_FB) deben ser **1% o 0.1%** para asegurar que la amplitud COLD sea el espejo exacto de HOT, maximizando el Rechazo de Modo Común (CMRR) en el preamplificador receptor.
