# Mantenimiento y Troubleshooting (V1.0)

**Peligro de Voltaje:** Este equipo opera conectado a Phantom Power (+48V DC). No cortocircuitar las líneas HOT y COLD a tierra mientras la consola esté encendida.

## 1. Verificación Rápida de Voltajes (Rails)

Si el equipo no enciende o el sonido distorsiona, usar un multímetro (modo DC) con la punta negra en el CHASIS:

1.  **Entrada Phantom:** Medir pines 2 y 3 del XLR. Deben marcar aproximadamente **+48V**. Si marcan 0V, la consola no está enviando Phantom.
2.  **Riel Principal (V+):** Medir el cátodo del diodo Zener (D1). Debe marcar **+12V (± 0.5V)**. Si marca +48V, el Zener se quemó y los OpAmps probablemente estén destruidos. Si marca < 8V, hay un cortocircuito en los OpAmps consumiendo exceso de corriente.
3.  **Tierra Virtual (V_BIAS):** Medir el nodo central del divisor resistivo. Debe marcar exactamente la mitad del riel principal (ej. **+6.0V**). Si es inestable, revisar el condensador electrolítico de filtro de V_BIAS.

## 2. Guía de Fallos Comunes

| Síntoma | Posible Causa | Acción (Solución) |
| :--- | :--- | :--- |
| **Pops/Clicks fuertes al mover el acordeón** | Falla de conexión a tierra de cápsulas. | Revisar que la malla exterior del cable de los micrófonos esté firmemente soldada al chasis. |
| **Sonido ahogado o extremadamente bajo** | Una cápsula en corto, tirando V_BIAS a GND. | Desoldar las cápsulas una por una hasta recuperar +6V en la línea V_BIAS. |
| **Zumbido 60Hz persistente (Hum)** | Bucle de masa (Ground Loop). | Activar el switch de **Ground Lift** en el panel lateral. |
| **Distorsión temprana (Clipping)** | Zener dañado o Phantom débil de consola. | Verificar que los OpAmps reciban sus +12V íntegros. Consolas baratas pueden entregar solo +24V, lo que limita el headroom. |
