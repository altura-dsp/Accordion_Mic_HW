# Manual de Usuario: Acordeón Mic (V1.0)

**Versión:** 1.0 · **Fecha:** 2026-09-08

El sistema de microfonía interna analógica para acordeón está diseñado para ser conectado y funcionar (Fire & Forget), sin baterías, operando exclusivamente con Phantom Power (+48V) de la mesa de mezclas.

## 1. Conexión Inicial (Puesta en Marcha)

1.  Asegúrate de que el canal de la mesa de mezclas esté **muteado** antes de conectar.
2.  Conecta un cable XLR estándar desde el panel del acordeón hasta la entrada de micrófono de la mesa **antes** de activar el Phantom (el mute interno protege el encendido desde cero; conectar con el phantom ya vivo depende del mute del canal de la consola).
3.  Activa el botón de **Phantom Power (+48V)** en la mesa de mezclas. 
4.  Espera **~3 segundos**: el mute anti-pop interno (JFET J111) mantiene la salida silenciada mientras los condensadores se cargan y luego abre con un fade lento de 1–3 s, inaudible. Ese fade de apertura al encender es **comportamiento normal**, no una falla.
5.  Desmutea el canal y comienza a tocar.

## 2. Controles Físicos

*   **Perilla MASTER (Volumen):** Controla el nivel general de los 3 micrófonos internos. 
    *   *Sugerencia:* Inicia con la perilla al 50% (a las 12 en punto) para dejar margen al ingeniero de sonido (Headroom).
*   **Switch GROUND LIFT:** Ubicado junto al conector XLR.
    *   **Posición GND (Por defecto):** El chasis del acordeón y las cápsulas están conectadas a la tierra de la mesa de mezclas. Es la posición más silenciosa.
    *   **Posición LIFT:** Úsalo **SOLO** si escuchas un zumbido de fondo de 60Hz (Hum de masa) cuando tocas en escenarios con cableado eléctrico deficiente. Esto levanta la conexión directa de tierra mientras mantiene la ruta segura para el Phantom Power (resistencia de 100Ω 1W + condensador Y-Class de 10nF a chasis).
