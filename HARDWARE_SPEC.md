# Especificaciones de Hardware - Acordeón Mic (Circuito Analógico)

**Versión:** 1.1 · **Fecha:** 2026-08-24 · **Estado:** Consolidación SSOT post-Red Team (PLAN_Remediacion FASE 1–5 ejecutadas)

Este documento sirve como la **Fuente Única de Verdad (SSOT)** para la arquitectura física, ruteo analógico y restricciones de hardware del proyecto Acordeón Mic. Es el archivo que la IA leerá para generar la documentación de circuitos y diagramas en "Arquitectura_Hardware.md".

## 1. Topología Analógica (DOMINIO: Touring Grade)

La etapa analógica ha sido diseñada para microfonear internamente el lado de agudos de un acordeón, extrayendo alimentación phantom directamente del PA, sin requerir baterías, logrando una suma de alta calidad y un control total de la presión sonora del fuelle (KISS / Fire & Forget).

### 1.1 Entradas Analógicas (3 Canales)
- **Canal 1, 2 y 3 (Cápsulas Electret):** Cápsulas omnidireccionales Primo EM289 o EM189T (Alta presión sonora, 128dB SPL Máximo).
  - **Protecciones y Acondicionamiento:** Resistencias pull-up al V_BIAS (+6V) calculadas en **33 kΩ**. Esto garantiza que la cápsula nunca exceda su límite físico de 5V (6V - (110µA * 33kΩ) = ~2.4V nominal). 
  - **Pieza Maestra de Filtrado:** Acople AC individual mediante condensadores de **100nF**. Esto tiene un triple propósito innegociable: bloquea el DC del bias, genera un filtro HPF a 159Hz para descartar los graves del acordeón (que no necesitamos) y elimina el peligroso DC shift subsónico producido por los cambios de presión direccional del fuelle. **[DECISIÓN FIRMADA Jose 2026-08-22: 159 Hz DEFINITIVO]** — C_AC 100 nF inmutable (verificado SPICE: 159.2 Hz), colocación de cápsulas en el lado de agudos (treble-grille); renuncia explícita a ~72 Hz (C_AC 220 nF) para capturar la mano izquierda.
- Los tres canales convergen pasivamente en el nodo inversor de un sumador activo.

### 1.2 Salidas Analógicas (1 Zona Balanceada)
- **Mezcla Activa:** Un amplificador operacional **OPA1642** configurado como sumador activo inversor (Op-A).
- **Salida Principal (XLR Balanceada):** Diseño **Híbrido**. Utiliza el **TLE2072** para balanceo de señal (buffer HOT e inversor COLD). El TLE2072 (Excalibur) provee mejor capacidad de manejo de carga (drive) que el TL072 clásico, y su consumo máximo de 3.6 mA compensa el alto consumo del OPA1642 de entrada (5.4 mA), manteniendo el circuito total en ~9.4 mA (seguro para el Phantom Power P48 en el peor de los casos).
- **Protección Touring Grade de Salida:** Uso estricto de condensadores bipolares de 47µF a 63V para bloquear los +48V de la consola y ferritas para supresión EMI/RFI. **[ECO 2026-08-21]** Las TVS P6KE12CA fueron ELIMINADAS de los pines XLR: llevan +48V DC permanentes y una TVS de 12V avalancha en continuo (~9.7mA robados del presupuesto phantom). La ESD queda limitada por las 6.81kΩ de la consola y el zener del raíl.
- **Interruptor Ground Lift (Phantom-Safe):** Se incorpora un switch en el Pin 1 del XLR. Al activarse, interpone una resistencia de 100Ω (1W) en paralelo con un condensador Y-Class de 10nF a chasis. Esto aísla bucles de masa de 60Hz sin cortar el retorno DC crítico de los +48V del Phantom Power.

## 2. Microcontrolador y Relojes (N/A - 100% Analógico)

- **MCU:** NO APLICA (Proyecto puramente analógico sin procesamiento digital).
- **Frecuencia del Sistema:** NO APLICA.
- **I2S MCLK:** NO APLICA.
- **Sample Rate:** NO APLICA.
- **Watchdog / Thermal:** NO APLICA.

## 3. Seguridad Física y Protecciones

- **Mute Anti-Pop (JFET, ECO 2026-08-22 FASE 3):** un J111 en **shunt diferencial** entre los nodos HOT/COLD de salida + red de gate RC (τ=1 s) silencia el transitorio de encendido: pop diferencial medido en SPICE **627 mV → 92 mV** (< 100 mV, criterio F5.2 del PLAN). Un relé es físicamente imposible con 10 mA de presupuesto — el JFET consume µA y queda cortado para siempre tras el encendido (invisible en señal: THD 0.0075%). En régimen el gate queda a −6 V (corte); el spread de Vto (−3…−10 V) solo desplaza el fade de apertura (~1–3 s, inaudible). **Limitación documentada:** protege el powerup medido; el plug-in del XLR con phantom ya vivo se valida en bench F6. Un **relé de mute NO aplica** (depende además del mute del canal en la consola FOH).
- **Aislamiento Mecánico (Shock-Mount):** Para mitigar el masivo *DC-bias shift* por la presión transitoria del fuelle y el ruido de manipulación, es obligatorio el uso de fieltros (*felt boots*) en cada cápsula y separadores de goma (*shock-mounts*) para la PCB.
- **Brown-Out Detector (BOD):** NO APLICA.
- **Modo Standalone / Redundancia:** El circuito en sí mismo opera de manera standalone continua al recibir energía de la consola.

## 4. Interfaz de Usuario (UX)

- **Control de Volumen Principal:** Un potenciómetro logarítmico (Audio Taper) de 10kΩ ubicado entre la salida del preamplificador sumador y el driver balanceado. **Restricción de ruteo estricta:** El extremo inferior del potenciómetro debe referenciarse a **V_BIAS (+6V)** y NO a Tierra (GND), para preservar el nivel de offset DC de la señal y evitar clipeo asimétrico masivo al bajar el volumen.

## 5. Fuente de Alimentación (F.A.) y Gestión de Energía

- **Entrada Principal:** Phantom Power (+48V) extraído de las líneas HOT y COLD de la consola mediante resistencias de precisión **220Ω al 0.1%** para mantener intacto el CMRR (ECO 2026-08-21: el valor anterior 2.2k estrangulaba el presupuesto — ver F.A.).
- **Filtrado y Protección:** Regulación con diodo Zener 1N4742A de 12V.
- **Reguladores (LDOs / DC-DC):** Se implementa un Virtual Ground (V_BIAS) de **+6V** usando un divisor resistivo simple y un condensador de filtrado desde el raíl de +12V. Esto permite operar la cadena híbrida en modo single-supply (KISS), ahorrando los miliamperios que hubiese consumido un inversor de carga negativo (ej. ICL7660S). **Budget validado (peor caso, híbrido, ECO Red Team 2026-08-21):** ~9.39mA consumidos de **~10.2mA disponibles** — fórmula correcta IEC 61938 con R_PH en serie: (48−12)/(6810+220)×2. El cálculo anterior (10.6mA) ignoraba las propias R_PH de extracción. Uso del 92%, margen 0.85mA. Nota de rodilla: a consumo máximo simultáneo el zener queda a ~0.85mA (IZK≈1mA del 1N4742A) → el raíl puede caer a ~11.4V en el peor caso absoluto, aún por encima del mínimo del TLE2072 (±4.5V). Pendiente de cierre con la medición real de consumo de la cápsula (FASE 5.4 del PLAN de Remediación).
- **Esquema de Tierras:** Plano de tierra sólido en el PCB, con una estricta partición geométrica de las trazas para aislar la zona de inyección ruidosa de la extracción phantom respecto a la ruta delicada de suma de micrófonos.

## 6. Auditoría Anti-Colisión GPIO y Deudas Técnicas
- **Conflictos de pines:** N/A (Sin MCU).
- **Dependencias ocultas:** N/A.
- **Canales ADC internos vs GPIO:** N/A.
- **Deudas técnicas detectadas:** Ninguna detectada. El plan inicial cubre sobradamente los requerimientos energéticos y acústicos.

## 7. BOM con ROI Máximo (matriz rules/7 §7.0.3)

| Función | Componente | Justificación ROI/YAGNI |
|---|---|---|
| Cápsulas | **Primo EM289 / EM189T** | Soporta 128dB SPL. Resiste el entorno extremo interior del fuelle sin clipear físicamente. Reemplaza a las costosas DPA cumpliendo el ROI Máximo (Costo ~2 USD). |
| Op-Amp Entrada (U1) | **OPA1642** | Sumador + buffer HOT. Ruido ultra-bajo (5.1 nV/√Hz). Consumo máx **5.4 mA**. Requiere adaptador SOIC→DIP para prototipo. |
| Op-Amp Salida (U2) | **TLE2072** | Inversor COLD. Mejor drive que TL072. Consumo máx **3.6 mA**. Junto al OPA1642 totaliza 9.0 mA de op-amps (88% del budget P48 en peor caso). |
| Regulación Phantom | **1N4742A** (Zener 12V) | Regulador pasivo robusto para bajar y estabilizar los 48V de la consola. |
| Extracción Phantom | R 220Ω **0.1%** | Precisión militar crítica para no destruir el CMRR (rechazo al modo común) de la señal. El valor bajo maximiza la corriente disponible del phantom. |
| Filtro Fuelle (HPF) | Condensador **100nF** | Pieza clave (triple acción): bloquea DC bias, rechaza graves inútiles, y filtra el temblor de bajas frecuencias del fuelle (Fc = 159Hz). |
| Volumen General | **Pot 10kΩ Audio** | Control manual indispensable antes del LPF anti-hiss. |
| Driver LPF Anti-Hiss| C **3.3nF C0G/NP0** | Condensador dieléctrico estable para filtro paso bajo (Fc = 14.6kHz) antes del buffer balanceado. |
| Protección Touring | C Bipolar **47µF 63V** | Bloqueo imperativo de los 48V de consola en los pines de salida. |
| Supresión Transitorios| Zener de raíl 1N4742A + ferritas 600Ω | ECO 2026-08-21: TVS en pines XLR eliminadas (avalancha continua sobre +48V DC); el zener del raíl clampa y las 6.81kΩ de la consola limitan la ESD. |
| Mute Anti-Pop | **J111** (JFET shunt) + R 1MΩ + C 1µF | ECO 2026-08-22 FASE 3: pop de encendido 627→92 mV. Consumo µA (un relé es imposible con 10 mA). Cortado en régimen = invisible (THD 0.0075%). |

## 8. Troubleshooting Shield (tabla Síntoma → Causa Raíz)

| Síntoma | Causa Raíz |
|---|---|
| **Ausencia total de audio** | Consola FOH no tiene encendido el Phantom Power (+48V) en el canal, o cable XLR defectuoso en líneas 2/3. |
| **Clipeo o distorsión asimétrica al bajar el volumen** | El pin inferior del potenciómetro de volumen fue ruteado a GND (0V) en lugar del plano V_BIAS (+6V). |
| **Pops/golpes masivos de aire que colapsan el ampli** | Se usaron capacitores de acople de entrada de 1µF o mayores. El HPF de 159Hz se ha perdido. Reemplazar por 100nF. |
| **Sonido "ahogado" o pérdida total del brillo** | El condensador C0G/NP0 del LPF anti-hiss fue calculado erróneamente o se montó un valor muy superior a 3.3nF. |
| **Sonido "hueco", pérdida de graves al mezclar** | **Inversión de Fase (Phase Cancellation):** El sumador interno invierte la fase. Presionar el botón de Inversión de Fase (Ø) en el canal de la consola FOH si se usa microfonía externa paralela. |
| **Zumbido o inducción eléctrica grave (Falta CMRR)** | Las resistencias de extracción Phantom (220Ω) no son del 0.1% o sufrieron daño térmico. |
