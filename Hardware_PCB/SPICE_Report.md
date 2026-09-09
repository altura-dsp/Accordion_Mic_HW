# 📋 SPICE Report — 5_Acordeon_Mic

- **Fecha:** 2026-09-08 21:18:01
- **Dominio:** Touring Grade (hardware analógico)
- **Veredicto global:** ✅ **PASS** (8/8 targets OK)

## Resumen ejecutivo

| # | Banco | Tipo | Mediciones (medido vs límite) | Estado |
|:--|:------|:-----|:-------------------------------|:------:|
| 1 | `input_hpf_cutoff` | ac | cutoff: medido 159.2 Hz vs esperado 159.0 Hz (err 0.12%, tol 10.0%) | ✅ **PASS** |
| 2 | `output_lpf_cutoff` | ac | cutoff: medido 14891.3 Hz vs esperado 14600.0 Hz (err 2.00%, tol 10.0%) | ✅ **PASS** |
| 3 | `power_ripple_zener` | transient | Vout pico: 12.297 V vs max 12.5 V · Vout pico: 12.297 V vs min 11.5 V | ✅ **PASS** |
| 4 | `powerup_transient` | transient | Vdc nodo generado: 12.063 V vs ventana [11.5, 12.5] V | ✅ **PASS** |
| 5 | `gain_band` | ac | band_flatness: 0.80 dB (limite <= 1.00 dB) desv. vs media de banda [300 Hz -> -1.56 dB, 1e+03 Hz -> -0.70 dB, 1e+04 Hz -> -2.24 dB] | ✅ **PASS** |
| 6 | `thd_1khz` | transient | THD: medido 0.0075% vs limite 0.1% | ✅ **PASS** |
| 7 | `cmrr_common_mode` | ac | atenuacion @ 1e+03 Hz: -300.00 dB (limite <= -18.0 dB) | ✅ **PASS** |
| 8 | `pop_plugin` | transient | Vout pico: 0.092 V vs max 0.1 V | ✅ **PASS** |

---

### ✅ input_hpf_cutoff (ac) -> `PASS`
- cutoff: medido 159.2 Hz vs esperado 159.0 Hz (err 0.12%, tol 10.0%) -> OK

---

### ✅ output_lpf_cutoff (ac) -> `PASS`
- cutoff: medido 14891.3 Hz vs esperado 14600.0 Hz (err 2.00%, tol 10.0%) -> OK

---

### ✅ power_ripple_zener (transient) -> `PASS`
- Vout pico: 12.297 V vs max 12.5 V -> OK
- Vout pico: 12.297 V vs min 11.5 V -> OK

---

### ✅ powerup_transient (transient) -> `PASS`
- Vdc nodo generado: 12.063 V vs ventana [11.5, 12.5] V -> OK

---

### ✅ gain_band (ac) -> `PASS`
- band_flatness: 0.80 dB (limite <= 1.00 dB) desv. vs media de banda [300 Hz -> -1.56 dB, 1e+03 Hz -> -0.70 dB, 1e+04 Hz -> -2.24 dB] -> OK

---

### ✅ thd_1khz (transient) -> `PASS`
- THD: medido 0.0075% vs limite 0.1% -> OK

---

### ✅ cmrr_common_mode (ac) -> `PASS`
- atenuacion @ 1e+03 Hz: -300.00 dB (limite <= -18.0 dB) -> OK

---

### ✅ pop_plugin (transient) -> `PASS`
- Vout pico: 0.092 V vs max 0.1 V -> OK
