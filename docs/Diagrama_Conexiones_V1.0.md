# Diagrama de Conexiones (V1.0)

**Versión:** 1.0 · **Fecha:** 2026-09-08 · **Base:** netlist SKiDL `5_Acordeon_Mic.net` + `Arquitectura_Hardware.md` V1.1 (post-Red Team)

Este documento muestra el ruteo físico de la señal a través del circuito analógico, usando diagramas ASCII Touring-Grade.

## 1. Ruteo de Señal Principal (Mix & Driver)

### 1.1 Entradas, Sumador y LPF (U1 OPA1642)

```ascii
             +6V (V_BIAS)
                 |
[MIC 1] --(33k)--+--(100nF)----(10k)--+
                                      |            [ U1A OPA1642 ]
             +6V (V_BIAS)             +----------> (Sumador Inversor -3x)
                 |                    |             R_SUM_FB 30k · IN+ (pin 3) a V_BIAS
[MIC 2] --(33k)--+--(100nF)----(10k)--+
                                      |                    |
             +6V (V_BIAS)             |                    v
                 |                    |            [ RV_VOL 10k Audio ]
[MIC 3] --(33k)--+--(100nF)----(10k)--+             (pin 1 a V_BIAS, NUNCA a GND)
                                                           |
                                                 wiper (pin 2) = LPF_IN
                                                           |
                                (R_LPF 3.3k) --> [ U1B OPA1642 (Buffer) ] --> LPF_OUT
                                                      |
                                                 (C_LPF 3.3nF)
                                                      |
                                                   GND_AUDIO
```

### 1.2 Driver Balanceado, Mute Anti-Pop y Salida XLR

```ascii
              LPF_OUT
                 |-->(R_BAL_HOT 470R 1%)--> nodo HOT --(C_BLOCK_HOT 47uF 63V bipolar)--(FB_HOT ferrita 600R)--> [XLR PIN 2] (net XLR_OUT)
                 |
                 +-->(R_INV_IN 10k)--> [ U2A TLE2072 ] --(R_BAL_COLD 470R 1%)--> nodo COLD --(C_BLOCK_COLD 47uF)--(FB_COLD ferrita 600R)--> [XLR PIN 3] (net XLR_COLD)
                                       (Inversor -1x · R_INV_FB 10k · IN+ a V_BIAS)

              Q_MUTE = J111 en SHUNT DIFERENCIAL entre nodos HOT/COLD (mute anti-pop, ECO 2026-08-22):
                  D (pin 2) --> nodo HOT
                  S (pin 3) --> nodo COLD
                  G (pin 1) --> GATE_MUTE   (red RC en §2; en régimen Vgs = -6V = cortado, fuera de señal)
```

## 2. Extracción de Phantom Power (+48V) y Midrail Bufferizado

```ascii
[XLR PIN 2] (XLR_OUT)  ---- (R_PH1_EXTRACT 220R 0.1%) ---+
                                                          +---> V_PHANTOM_12V ---+--> [D_ZENER_12V 1N4742A] --> GND_AUDIO
[XLR PIN 3] (XLR_COLD) ---- (R_PH2_EXTRACT 220R 0.1%) ---+                      |      (pin 1 = K cátodo al riel, pin 2 = A ánodo a GND)
                                                                                 +--> (C_FILTER_12V 100uF 25V) --> GND_AUDIO
                                                                                 +--> (C_DEC_HF1 / C_DEC_HF2 100nF, uno por IC) --> GND_AUDIO
                                                                                 |
                                                                                 +-->(R_VBIAS_TOP 100k)-- V_BIAS_REF --(R_VBIAS_BOT 100k)--> GND_AUDIO
                                                                                                           |
                                                                                                    [ U2B TLE2072 (seguidor) ]
                                                                                                     buffer del midrail (ECO 2026-08-22)
                                                                                                           |
                                                                                                        V_BIAS (+6V) --(C_VBIAS_FILTER 10uF, en el rail)--> GND_AUDIO
                                                                                 |
                                                                                 +--(C_GATE_MUTE 1uF)-- GATE_MUTE --(R_GATE_MUTE 1Meg)--> GND_AUDIO
                                                                                                        (tau = 1 s: acopla la subida del riel -> JFET ON
                                                                                                         al encender; pull-down -> Vgs = -6V = corte en régimen)
```

## 3. Ground Lift

```ascii
[XLR PIN 1] (GND) --- [ SW_GROUND_LIFT (SPDT) ] 
                          |-- (Pos GND) -----> [ CHASIS_GND ]
                          |
                          +-- (Pos LIFT) ----> (R_GLIFT 100R 1W) // (C_GLIFT 10nF Y-Class 250V) ----> [ CHASIS_GND ]
```
