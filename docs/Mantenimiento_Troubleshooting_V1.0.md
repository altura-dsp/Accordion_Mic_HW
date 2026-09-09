# Mantenimiento y Troubleshooting (V1.0)

**Versión:** 1.0 · **Fecha:** 2026-09-08 · **Refs:** según `Arquitectura_Hardware.md` V1.1 (post-Red Team)

**Peligro de Voltaje:** Este equipo opera conectado a Phantom Power (+48V DC). No cortocircuitar las líneas HOT y COLD a tierra mientras la consola esté encendida.

## 1. Verificación Rápida de Voltajes (Rails)

Si el equipo no enciende o el sonido distorsiona, usar un multímetro (modo DC) con la punta negra en el CHASIS:

1.  **Entrada Phantom:** Medir pines 2 y 3 del XLR. Deben marcar aproximadamente **+48V**. Si marcan 0V, la consola no está enviando Phantom o el cable está defectuoso en líneas 2/3.
2.  **Riel Principal (V_PHANTOM_12V):** Medir el cátodo (pin 1) de **D_ZENER_12V (1N4742A)**. Ventana sana: **11.5 – 12.5 V** (criterio Red Team; SPICE: 12.3 V en régimen, 12.06 V al encender). Nota: a consumo máximo simultáneo puede caer legítimamente a ~11.4 V. Si marca +48V, el Zener se quemó y los OpAmps probablemente estén destruidos. Si cae por debajo de ~11 V sostenido, hay exceso de consumo (OpAmp en corto).
3.  **Tierra Virtual (V_BIAS):** Medir el **rail V_BIAS** (pin 7 de U2_TLE2072, salida del buffer U2B, o el común de las R_MIC_BIAS): debe marcar exactamente la mitad del riel principal (**+6.0V**). El nodo del divisor **V_BIAS_REF** (pin 5 de U2) también debe dar ~6V; si V_BIAS_REF está sano pero V_BIAS no, el buffer U2B está dañado → reemplazar U2. Si es inestable, revisar C_VBIAS_FILTER 10 µF.
4.  **Gate del mute (GATE_MUTE):** En régimen debe estar a **0V** (Vgs = −6V, JFET Q_MUTE J111 cortado = fuera de la señal). Un gate atascado positivo → revisar C_GATE_MUTE 1 µF y R_GATE_MUTE 1 MΩ.

## 2. Guía de Fallos Comunes

| Síntoma | Posible Causa | Acción (Solución) |
| :--- | :--- | :--- |
| **Pops/Clicks fuertes al mover el acordeón** | Falla de conexión a tierra de cápsulas. | Revisar que la malla exterior del cable de los micrófonos esté firmemente soldada al chasis. |
| **Sonido ahogado o extremadamente bajo** | Una cápsula en corto, tirando V_BIAS a GND; o Q_MUTE (J111) atascado ON (shunt permanente de HOT-COLD). | Desoldar las cápsulas una por una hasta recuperar +6V. Si el riel y V_BIAS están sanos y el nivel no retorna, revisar Q_MUTE y su red de gate (C_GATE_MUTE / R_GATE_MUTE). |
| **Fade de apertura mayor a ~5 s (audio tarda en abrir tras encender)** | Red de gate del mute desviada (C_GATE_MUTE con fuga o R_GATE_MUTE fuera de valor, τ ≠ 1 s). | Reemplazar C_GATE_MUTE 1 µF y R_GATE_MUTE 1 MΩ. |
| **Zumbido 60Hz persistente (Hum)** | Bucle de masa (Ground Loop). | Activar el switch de **Ground Lift** en el panel lateral. |
| **Zumbido o inducción eléctrica grave (Falta CMRR)** | R_PH1/R_PH2_EXTRACT (220 Ω) sin matching 0.1% o con daño térmico. | Reemplazar el par por 220 Ω 0.1% matched. |
| **Distorsión temprana (Clipping)** | Zener dañado o Phantom débil de consola. | Verificar ventana 11.5–12.5 V en V_PHANTOM_12V. Consolas baratas pueden entregar solo +24V, lo que limita el headroom. |
| **Pops/golpes masivos de aire que colapsan el preamp** | Se montaron capacitores de acople de entrada de 1 µF o mayores (HPF de 159 Hz perdido). | Reemplazar C_MICx_AC por 100 nF film. |
| **Sonido "hueco", pérdida de graves al mezclar** | Inversión de fase (el sumador interno invierte). | Presionar el botón de Inversión de Fase (Ø) en el canal de la consola si se usa microfonía externa paralela. |
| **Sonido "ahogado" o pérdida total del brillo** | C_LPF erróneo o de valor muy superior a 3.3 nF (LPF anti-hiss desplazado). | Reemplazar por 3.3 nF C0G/NP0. |
