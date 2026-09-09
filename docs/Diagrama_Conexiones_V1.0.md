# Diagrama de Conexiones (V1.0)

Este documento muestra el ruteo físico de la señal a través del circuito analógico, usando diagramas ASCII Touring-Grade.

## 1. Ruteo de Señal Principal (Mix & Driver)

```ascii
             +6V (V_BIAS)
                 |
[MIC 1] --(33k)--+--(100nF)----(10k)--+
                                      |
             +6V (V_BIAS)             |
                 |                    |
[MIC 2] --(33k)--+--(100nF)----(10k)--+---- [ U1A OPA1642 ] --- (VOL 10k) ---+
                                      |      (Sumador Inversor)              |
             +6V (V_BIAS)             |                                      |
                 |                    |                                      |
[MIC 3] --(33k)--+--(100nF)----(10k)--+                                      |
                                                                             |
                                     +---------------------------------------+
                                     |
                                     +--> [ LPF 3.3k/3.3nF ] --> [ U1B OPA1642 ] -------> (47uF) ----> [XLR PIN 2] (HOT)
                                                                  (Buffer)          |
                                                                                    |
                                                                                    +---> [ U2A TLE2072 ] -> (47uF) ----> [XLR PIN 3] (COLD)
                                                                                         (Inversor -1x)
```

## 2. Extracción de Phantom Power (+48V)

```ascii
[XLR PIN 2] (HOT)  ---- (220R 0.1%) ---+
                                       |
                                       +---> [ ZENER 12V ] ---> GND
                                       |
[XLR PIN 3] (COLD) ---- (220R 0.1%) ---+
                                       |
                                       +---> (12V) Riel principal OpAmps (V+)
                                       |
                                       +---> (Divisor 100k/100k) ---> (+6V V_BIAS)
```

## 3. Ground Lift

```ascii
[XLR PIN 1] (GND) --- [ SPDT Switch ] 
                          |-- (Pos 1: GND) -----> [ CHASIS GND ]
                          |
                          +-- (Pos 2: LIFT) ----> (100 ohm) // (10nF) ----> [ CHASIS GND ]
```
