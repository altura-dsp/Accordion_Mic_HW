import builtins
from skidl import Net, Part

def _safe_pin(part, pin_id):
    """Fail-fast: asegura que el pin existe antes de intentar conectar (anti-KeyError opaco)"""
    for p in part.pins:
        if p.num == str(pin_id):
            return p
    raise ValueError(f"Pin {pin_id} no encontrado en {part.name}")

def _bias_net():
    """Obtiene o crea la red V_BIAS compartida (virtual ground single-supply +6V).
    BUG skidl: Net('V_BIAS') duplicado se renombra a V_BIAS1/V_BIAS2 -> el divisor del
    power-stage alimentaba un nodo flotante (V_BIAS2) y los op-amps quedaban sin virtual
    ground (V_BIAS=0V por rshunt) -> saturacion -> cutoff medido ~20Hz (circuito apagado).
    Net.get recupera la red existente -> 1 sola V_BIAS fisica para todo el circuito."""
    return Net.get('V_BIAS') or Net('V_BIAS')

def wire_input_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v):
    v_bias = _bias_net()
    mix_node = Net('MIX_NODE')
    
    # MIC 1, 2, 3 Ruteo
    for i in range(1, 4):
        mic = parts[f'MIC{i}']
        r_bias = parts[f'R_MIC{i}_BIAS']
        c_ac = parts[f'C_MIC{i}_AC']
        r_sum = parts[f'R_MIC{i}_SUM']
        
        _safe_pin(r_bias, '1') & v_bias
        _safe_pin(r_bias, '2') & _safe_pin(mic, '1')
        _safe_pin(mic, '2') & gnd_audio
        _safe_pin(mic, '1') & _safe_pin(c_ac, '1')
        _safe_pin(c_ac, '2') & _safe_pin(r_sum, '1')
        _safe_pin(r_sum, '2') & mix_node

    u1 = parts['U1_OPA1642']
    r_sum_fb = parts['R_SUM_FB']
    rv_vol = parts['RV_VOL']
    
    # Sumador Activo (OpA)
    _safe_pin(u1, '2') & mix_node
    _safe_pin(u1, '3') & v_bias
    _safe_pin(u1, '2') & _safe_pin(r_sum_fb, '1')
    _safe_pin(r_sum_fb, '2') & _safe_pin(u1, '1')
    
    # Control de Volumen
    _safe_pin(u1, '1') & _safe_pin(rv_vol, '3')
    _safe_pin(rv_vol, '1') & v_bias

def wire_output_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v):
    v_bias = _bias_net()
    u1 = parts['U1_OPA1642']
    u2 = parts['U2_TLE2072']
    rv_vol = parts['RV_VOL']
    r_lpf = parts['R_LPF']
    c_lpf = parts['C_LPF']
    
    # LPF (OpB)
    _safe_pin(rv_vol, '2') & _safe_pin(r_lpf, '1')
    _safe_pin(r_lpf, '2') & _safe_pin(u1, '5')
    _safe_pin(u1, '5') & _safe_pin(c_lpf, '1')
    _safe_pin(c_lpf, '2') & gnd_audio
    _safe_pin(u1, '6') & _safe_pin(u1, '7')
    
    r_bal_hot = parts['R_BAL_HOT']
    r_inv_in = parts['R_INV_IN']
    r_inv_fb = parts['R_INV_FB']
    
    # Buffer HOT e Inversor COLD
    _safe_pin(u1, '7') & _safe_pin(r_bal_hot, '1')
    _safe_pin(u1, '7') & _safe_pin(r_inv_in, '1')
    _safe_pin(r_inv_in, '2') & _safe_pin(u2, '2')
    _safe_pin(u2, '3') & v_bias
    _safe_pin(u2, '2') & _safe_pin(r_inv_fb, '1')
    _safe_pin(r_inv_fb, '2') & _safe_pin(u2, '1')
    
    r_bal_cold = parts['R_BAL_COLD']
    _safe_pin(u2, '1') & _safe_pin(r_bal_cold, '1')

    # NOTA: U2B (TLE2072 pines 5,6,7) NO se termina aquí — es el BUFFER DEL
    # MIDRAIL (ver wire_power_stage). Red Team FASE 3 (2026-08-22): el divisor
    # 100k/100k de V_BIAS (Thevenin 50k) no puede alimentar las 3 cápsulas
    # electret (~0.3 mA en total): el midrail colapsaría igual que en el
    # testbench SPICE (V_BIAS→2.4 V, verano clipeando contra 0 V — hallazgo
    # del banco thd_1khz). El canal libre U2B queda como seguidor duro.

    # Protección Touring, XLR y Ground Lift
    c_block_hot = parts['C_BLOCK_HOT']
    c_block_cold = parts['C_BLOCK_COLD']
    fb_hot = parts['FB_HOT']
    fb_cold = parts['FB_COLD']
    xlr_out = parts['XLR_OUT']

    # MUTE ANTI-POP JFET SHUNT DIFERENCIAL (Red Team F3.2/F5.2, 2026-08-22):
    # el banco pop_plugin midió 627 mV pico DIFERENCIAL HOT−COLD al energizar
    # phantom (uic): U1B (OPA1642, buffer HOT) y U2A (TLE2072, inversor COLD)
    # despiertan a velocidades distintas y los C_BLOCK cargan asimétricos
    # (pico @ 9.4 ms, asentado ~100 ms). Topología: UN solo J111 ENTRE los
    # nodos HOT y COLD (tras R_BAL_x, antes de C_BLOCK_x) — corta el
    # DIFERENCIAL, lo único que la consola ve (el modo común lo rechaza su
    # CMRR). Red de gate en wire_power_stage: C_GATE_MUTE 1uF desde el riel
    # ACOPLA la subida al gate (Vgs ~ +1..+7 V durante 2-3 s -> JFET ON ->
    # pico clampado por Rds 30 ohm contra 2x100 de R_BAL, ~13 %) mientras todo
    # se asienta; luego R_GATE_MUTE 1Meg a masa baja el gate a 0 V -> Vgs=−6 V
    # (nodos al midrail) -> CORTADO para siempre: el JFET queda FUERA del
    # camino de señal (invisible en gain/THD). El spread de Vto del J111
    # (−3..−10 V) aquí es benigno: a Vgs=−6 V cualquier specimen está en
    # corte o sub-umbral de gigaohm; solo desplaza el instante del unmute,
    # que es un fade lento (~1-3 s) inaudible. Limitación documentada: protege
    # el POWERUP medido; el plug-in del XLR con phantom ya vivo es bench F6.
    # (Descartado por física, medido 367 mV: el JFET SERIE con gate-RC desde
    # el propio riel — en uic Vgs arranca en 0 V = ON justo durante el pico.)
    q_mute = parts['Q_MUTE']
    gate_mute = Net('GATE_MUTE')   # red RC del gate en wire_power_stage (tiene el riel)

    _safe_pin(q_mute, '1') & gate_mute

    _safe_pin(r_bal_hot, '2') & _safe_pin(c_block_hot, '1')
    _safe_pin(r_bal_hot, '2') & _safe_pin(q_mute, '2')      # D -> nodo HOT
    _safe_pin(r_bal_cold, '2') & _safe_pin(c_block_cold, '1')
    _safe_pin(r_bal_cold, '2') & _safe_pin(q_mute, '3')     # S -> nodo COLD

    _safe_pin(c_block_hot, '2') & _safe_pin(fb_hot, '1')
    _safe_pin(fb_hot, '2') & _safe_pin(xlr_out, '2')

    _safe_pin(c_block_cold, '2') & _safe_pin(fb_cold, '1')
    _safe_pin(fb_cold, '2') & _safe_pin(xlr_out, '3')
    
    # ECO Red Team 2026-08-21 (P0-2): TVS P6KE12CA ELIMINADAS de los pines XLR.
    # Estos pines llevan +48V DC permanentes (phantom): con V_BR≈13.3-14.7V la TVS
    # avalancha en CONTINUO y roba (48-14)/6810 ≈ 4.85mA por línea (~9.7mA de los
    # 10.6mA del presupuesto IEC 61938). La ESD ya está limitada por las 6.81k de
    # la consola y el zener del rail clampa sobretensiones. Renuncia documentada
    # en Arquitectura_Hardware.md §Protección Touring Grade. Alternativa futura si
    # se exige ESD directa en conector: TVS con VRWM >= 48V (ej. SMBJ51CA) a chasis.
    
    # Ground Lift
    sw_glift = parts['SW_GROUND_LIFT']
    r_glift = parts['R_GLIFT']
    c_glift = parts['C_GLIFT']
    
    _safe_pin(xlr_out, '1') & _safe_pin(sw_glift, '1')
    _safe_pin(sw_glift, '2') & gnd_chasis
    _safe_pin(sw_glift, '3') & _safe_pin(r_glift, '1')
    _safe_pin(sw_glift, '3') & _safe_pin(c_glift, '1')
    _safe_pin(r_glift, '2') & gnd_chasis
    _safe_pin(c_glift, '2') & gnd_chasis

def wire_power_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v):
    v_phantom_12v = Net('V_PHANTOM_12V')
    v_bias = _bias_net()
    
    r_ph1 = parts['R_PH1_EXTRACT']
    r_ph2 = parts['R_PH2_EXTRACT']
    xlr_out = parts['XLR_OUT']
    
    _safe_pin(xlr_out, '2') & _safe_pin(r_ph1, '1')
    _safe_pin(xlr_out, '3') & _safe_pin(r_ph2, '1')
    _safe_pin(r_ph1, '2') & v_phantom_12v
    _safe_pin(r_ph2, '2') & v_phantom_12v
    
    d_zener = parts['D_ZENER_12V']
    c_filter = parts['C_FILTER_12V']
    
    # Zener 1N4742A en REVERSE-breakdown para regular +12V: cátodo (pin 1) al riel,
    # ánodo (pin 2) a GND. El símbolo Device:D declara pin1=K(cátodo) / pin2=A(ánodo)
    # (coinciden KiCad y main_build_sklib). ECO Red Team 2026-08-21 (P0-1): el cableado
    # pin2->riel anterior era un "fix" que compensaba el exportador de diodos invertido
    # del motor (emitía net(pin1) net(pin2) como anodo-catodo): SPICE veía REVERSE y
    # pasaba 12V, pero el hardware físico quedaba en FORWARD = dispositivo muerto
    # (rail ~1.4V, demostrado en sim con el exportador corregido). Orientación física
    # Y de simulación correctas a la vez.
    _safe_pin(d_zener, '1') & v_phantom_12v
    _safe_pin(d_zener, '2') & gnd_audio
    _safe_pin(c_filter, '1') & v_phantom_12v
    _safe_pin(c_filter, '2') & gnd_audio
    
    # Generación de V_BIAS (midrail) — Red Team FASE 3 (2026-08-22):
    # divisor 100k/100k -> V_BIAS_REF (nodo aislado, cero carga) -> seguidor
    # U2B (TLE2072 canal B, antes terminado sin usar) -> V_BIAS de baja
    # impedancia. Sin buffer, las 3 cápsulas (~0.3 mA) sobre el Thevenin de
    # 50k del divisor arrastran el midrail varios voltios (demostrado en
    # SPICE: V_BIAS 2.4 V, N_7 clipea contra 0 V). El U2B ya estaba en el
    # BOM: cero partes nuevas (Fire&Forget / ROI puro).
    r_top = parts['R_VBIAS_TOP']
    r_bot = parts['R_VBIAS_BOT']
    c_vbias = parts['C_VBIAS_FILTER']

    v_bias_ref = Net('V_BIAS_REF')
    v_phantom_12v & _safe_pin(r_top, '1')
    _safe_pin(r_top, '2') & v_bias_ref
    v_bias_ref & _safe_pin(r_bot, '1')
    _safe_pin(r_bot, '2') & gnd_audio

    u2 = parts['U2_TLE2072']
    _safe_pin(u2, '5') & v_bias_ref        # IN+B <- referencia del divisor
    _safe_pin(u2, '6') & v_bias            # IN-B <- lazo cerrado a la salida
    _safe_pin(u2, '7') & v_bias            # OUT_B -> V_BIAS (rail del midrail)

    # Desacoplo del midrail en el RAIL (no en la ref): C_VBIAS sobre la
    # salida del buffer, no sobre el divisor.
    v_bias & _safe_pin(c_vbias, '1')
    _safe_pin(c_vbias, '2') & gnd_audio

    # Red de gate del mute JFET (Red Team F3.2/F5.2): C_GATE_MUTE 1uF ACOPLA la
    # subida del riel al gate (JFET ON durante el transitorio de encendido) y
    # R_GATE_MUTE 1Meg a masa lo baja a 0 V después (tau = 1 s) -> Vgs = −6 V
    # en régimen (corte permanente). El JFET shunt diferencial vive en
    # wire_output_stage; diseño completo allá.
    gate_mute = Net.get('GATE_MUTE') or Net('GATE_MUTE')
    v_phantom_12v & _safe_pin(parts['C_GATE_MUTE'], '1')
    _safe_pin(parts['C_GATE_MUTE'], '2') & gate_mute
    gate_mute & _safe_pin(parts['R_GATE_MUTE'], '1')
    _safe_pin(parts['R_GATE_MUTE'], '2') & gnd_audio
    
    # Alimentación OpAmps
    u1 = parts['U1_OPA1642']
    u2 = parts['U2_TLE2072']
    
    v_phantom_12v & _safe_pin(u1, '8')
    gnd_audio & _safe_pin(u1, '4')
    v_phantom_12v & _safe_pin(u2, '8')
    gnd_audio & _safe_pin(u2, '4')
    
    c_dec1 = parts['C_DEC_HF1']
    c_dec2 = parts['C_DEC_HF2']
    v_phantom_12v & _safe_pin(c_dec1, '1')
    gnd_audio & _safe_pin(c_dec1, '2')
    v_phantom_12v & _safe_pin(c_dec2, '1')
    gnd_audio & _safe_pin(c_dec2, '2')

def wire_circuit(parts, gnd_audio, gnd_chasis, gnd_digital, vcc_12v, vcc_5v, vcc_3v3):
    vee_minus_12v = Net('-12V_CLEAN')
    
    wire_input_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    wire_output_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    wire_power_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    
    # Autolimpieza de huérfanos (recopilar primero, remover después)
    to_remove = [p for p in builtins.default_circuit.parts if not any(pin.nets for pin in p.pins)]
    for p in to_remove:
        builtins.default_circuit.parts.remove(p)

def build_spice_stage(stage_name, parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v):
    """DUT Completo (100% Real). Todos los tests usan el mismo circuito físico bajo diferentes estímulos."""
    from skidl import Part, Net
    
    # 1. Llamamos a las funciones de cableado reales para ensamblar todo el circuito
    wire_input_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    wire_output_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    wire_power_stage(parts, gnd_audio, gnd_chasis, vcc_12v, vee_minus_12v)
    
    # 2. Nombrar las redes críticas para que ngspice las encuentre según spice_targets.yaml
    # SKiDL permite buscar los pines y nombrar sus redes asociadas.
    parts['C_MIC1_AC']['1'].net.name = 'MIC1'
    parts['R_MIC1_SUM']['1'].net.name = 'MIX_NODE'
    parts['C_FILTER_12V']['1'].net.name = 'V_PHANTOM_12V'

    # Nodos del LPF anti-hiss (R_LPF 3.3k + C_LPF 3.3nF en Op-B del OPA1642):
    # para que spice_targets.yaml mida el cutoff REAL de 14.6 kHz y no la tierra
    # virtual del sumador (MIX_NODE) ni el nodo inexistente XLR_OUT. LPF_IN = wiper
    # del potenciometro (antes de R_LPF); LPF_OUT = OUT_B (U1 pin 7, buffer seguidor).
    # Fc teorica = 1/(2*pi*3300*3.3nF) = 14.6 kHz.
    parts['RV_VOL']['2'].net.name = 'LPF_IN'
    parts['U1_OPA1642']['7'].net.name = 'LPF_OUT'
    
    # El nodo XLR_OUT en spice_targets.yaml se usa para inyectar/medir en la salida.
    # Vamos a asignarlo al pin 2 (HOT) del conector XLR.
    parts['XLR_OUT']['2'].net.name = 'XLR_OUT'
    # Pin 3 (COLD) nombrado para los bancos DIFERENCIALES del F3.2 (Red Team):
    # CMRR mide el residuo V(XLR_OUT)-V(XLR_COLD) bajo estimulo modo comun, y
    # pop_plugin mide el pico diferencial de encendido. Sin nombre canonico el
    # motor no puede referenciarlo desde spice_targets.yaml.
    parts['XLR_OUT']['3'].net.name = 'XLR_COLD'
    
    # En el mundo real, inyectamos Phantom Power (+48V) a través de resistencias de 6.81k 
    # hacia los pines 2 (HOT) y 3 (COLD) del XLR.
    
    phantom_dc_node = Net('PHANTOM_DC_NODE')
    r_phantom_hot = Part('Device', 'R', value='6.81k')
    r_phantom_cold = Part('Device', 'R', value='6.81k')
    
    _safe_pin(r_phantom_hot, '1') & phantom_dc_node
    _safe_pin(r_phantom_hot, '2') & parts['XLR_OUT']['2']
    
    _safe_pin(r_phantom_cold, '1') & phantom_dc_node
    _safe_pin(r_phantom_cold, '2') & parts['XLR_OUT']['3']
    
    # Para la simulación AC, ngspice inyectará automáticamente 'vstim' en el nodo de entrada
    # definido en spice_targets.yaml (ej. MIC1 o MIX_NODE o XLR_OUT).

    # Autolimpieza de huérfanos para SPICE
    import builtins
    to_remove = [p for p in builtins.default_circuit.parts if not any(pin.nets for pin in p.pins)]
    for p in to_remove:
        builtins.default_circuit.parts.remove(p)

    # Fuentes SPICE extra declaradas por el PROYECTO (tools/ las concatena sin interpretar).
    # Phantom +48V DC (IEC 61938): polariza el riel interno vía las 2x 6.81k (r_phantom_hot/
    # cold) -> Zener 1N4742A regula V_PHANTOM_12V~12V -> divisor 100k/100k -> V_BIAS +6V.
    # Sin esto, V_BIAS=0V y los op-amps saturan (cutoff medido ~20Hz = circuito apagado).
    #
    # F3.1 (Red Team, chasis aterrizado): RESUELTO POR DISEÑO DEL MAPEO MOTOR —
    # main_build.py mapea toda net GND*/CHASIS* al nodo 0, es decir GND_CHASIS
    # YA está aterrizado en sim (= switch de ground lift CERRADO, posición por
    # defecto en gira). Sumar "R_TIE_CHASIS GND_CHASIS 0 1m" aquí crearía un
    # nodo colgante inexistente en el .cir (todo pin CHASIS colapsa a 0). El
    # caso lift ABIERTO (aislamiento de loop de tierra) es validación de bench
    # F6, no simulable con el mapeo unificado.
    return [
        "V_PHANTOM_DC PHANTOM_DC_NODE 0 48",
        # Carga ligera del riel regulado (anti timestep-too-small), TESTBENCH-ONLY:
        # NO es una parte física del BOM. ECO Red Team 2026-08-21 (P1-4): antes era un
        # Part('Device','R') inline en wire_power_stage que ensuciaba el netlist KiCad
        # ("No footprint for R/R6x"). 100k = 0.12mA, despreciable, mantiene el nodo
        # estable sin ahogar el Zener.
        "RL_12V V_PHANTOM_12V 0 100k",
    ]

