# ESP32 LilyGO Display + Temperature Hat

A KiCad 10 hat for the **LilyGO T-Relay-8** (ESP32, 8 relays). It adds 8 thermocouple
inputs, heater current measurement, a 1-Wire port and a connector for a front panel
(1.3" SH1106 OLED with rotary encoder and buttons).

- Base board: [LilyGO T-Relay-8](https://www.amazon.pl/dp/B0B6TY79WN) —
  [vendor repo](https://github.com/Xinyuan-LilyGO/LilyGo-T-Relay) (schematic, DXF outline, pinmap)
- Front panel: [1.3" SH1106 OLED with encoder and buttons](https://allegro.pl/oferta/wyswietlacz-oled-1-3-sh1106-bialy-z-enkoderem-przyciskami-panel-sterowania-18116662587)
- Load: 24 V heater, about 18.75 A, switched by the T-Relay relays

## Blocks

| Block | Parts | Notes |
|---|---|---|
| Thermocouple front end | J2–J9, U1, U3 (TMUX1108), U2 (MAX31856) | U1 muxes the `+` legs, U3 the `−` legs, into one MAX31856 over SPI. Input filter: R1/R2 100 Ω, C1 100 nF differential, C2/C3 10 nF to GND. |
| I/O expander | U4 (PCF8574A), U5 (74LVC1G04), JP1–JP3 | Mux address and enable, MAX31856 status, two panel buttons. |
| Front panel | J10 (1x9 socket) | I²C display, encoder, buttons. |
| Heater current | J11, R6 (shunt), U6 (INA226) | High-side shunt in the +24 V feed, read over I²C. See "Heater current sensing". |
| 1-Wire | J12 (JST PH 3-pin) | External DS18B20 probes. |
| Supply | L1, C10–C14 | `VCC` = 3V3 from the T-Relay; `VAA` = analog rail for U2, filtered by ferrite bead L1. |

## J1: connection to the T-Relay-8

Checked against the official T-Relay-8 schematic (`Schematic/T_Relay8_ESP32.pdf` in the vendor
repo, header P5) and the vendor pinmap image; both agree.

**The two rows are numbered the other way round on the two boards.** Hat J1 pin 1 (3V3) mates
with T-Relay P5 pin 2. In general hat odd pin n ↔ P5 pin n+1, hat even pin n ↔ P5 pin n−1.
This is what you get from a socket mounted on the underside of the hat, facing down onto the
T-Relay's pins, so it is intended and the schematic needs no change for it.

For layout (review item 15): J1 is a socket soldered on the **bottom** of the hat. Put the
footprint on the back side so silkscreen, courtyard and 3D model are on the correct side, and
check that pad 1 sits over the T-Relay's 3V3 pin (P5 pin 2). If the rows end up swapped, 3V3
lands on GND. In the board as of 2026-11-12 the J1 footprint is still on the front side.

| J1 (hat) | P5 (T-Relay) | ESP32 | Signal | Notes |
|---|---|---|---|---|
| 1, 3 | 2, 4 | 3V3 | VCC | |
| 2, 4 | 1, 3 | GND | GND | |
| 5 | 6 | IO2 | TC_MISO | Boot strap. LilyGO names this net `GPIO2/MISO`. |
| 6 | 5 | IO14 | TC_SCK | LilyGO: `GPIO14/CLK` |
| 7 | 8 | IO4 | TC_CS | |
| 8 | 7 | IO15 | TC_MOSI | Boot strap. LilyGO: `GPIO15/MOSI` |
| 9, 11, 12, 13, 14 | 10, 12, 11, 14, 13 | NC | — | Not connected on the T-Relay |
| 10 | 9 | IO35 | ENCODER_B | Input-only |
| 15 | 16 | IO36 | free | Input-only, ADC1. See note below. |
| 16 | 15 | IO39 | JOYSTICK_PUSH | Input-only. See note below. |
| 17 | 18 | GND | GND | |
| 18 | 17 | IO34 | ENCODER_A | Input-only |
| 19 | 20 | IO27 | I2C_SDA | |
| 20 | 19 | IO26 | EXPANDER_INT | Pulled up by R3 |
| 21 | 22 | IO23 | I2C_SCL | |
| 22 | 21 | IO22 | ONEWIRE | The only free bidirectional pin; 1-Wire needs one |

- IO34, IO35, IO36 and IO39 are input-only and have no internal pull-ups or pull-downs.
  The front panel provides 10 kΩ pull-ups for the encoder and push button.
- IO36 and IO39 can see very short spurious low pulses when the ESP32's ADC is used or Wi-Fi
  runs with modem sleep (documented by Espressif). Do not use an edge interrupt on
  JOYSTICK_PUSH without debouncing; polling or a debounce of a millisecond or more is enough.
  This is why the push button, not an encoder phase or the expander interrupt, sits on IO39.
- On the T-Relay-8 none of the header GPIOs connect to anything else on the board.
  Relays use IO21, IO19, IO18, IO5, IO12, IO13, IO32, IO33; IO25 is the red LED.

## Heater current sensing

```
PSU+ → J11.1 (24V_IN) → R6 → J11.2 (24V_OUT) → relay COMs → heater → PSU−
```

- The hat sits in the positive feed. No heater current flows in the hat's GND.
- R6 is a 1 mΩ 4-terminal (Kelvin) shunt, Vishay WSK2512 footprint. Pads 1/4 carry the current,
  pads 2/3 go only to the INA226 inputs. At 18.75 A: 18.75 mV, 0.35 W.
- U6 is an INA226AIDGS at I²C address `0x40` (A0 = A1 = GND), powered from `VCC`, decoupled by C14.
  `Vbus` is on `24V_OUT`, so firmware can also read the supply voltage after the shunt.
  The `Alert` pin is not connected: firmware polls over I²C, and the relays are driven by the
  ESP32 anyway, so a hardware alert would not switch anything off faster.
- R7/R8 (10 Ω) and C15 (100 nF) filter the sense inputs (TI's recommended input filter, corner
  about 80 kHz). They keep relay switching spikes and RF out of the converter and limit current
  into the inputs during transients. 10 Ω is TI's upper limit; the gain error it adds is negligible.
- The review asked for 2 mΩ / 3 W. 1 mΩ was chosen because the WSK2512 is a 1 W part and
  2 mΩ would run it at 0.7 W; resolution is still about 2.5 mA per LSB.

Open point for the system owner: the T-Relay-8 relays are believed to be rated about 10 A per
contact, so 18.75 A must not go through a single relay. How the heater is split across relays
is not known here.

## U4 (PCF8574A) port map

Address `0x38` with JP1–JP3 in their default position (A0–A2 to GND).

| Port | Signal | Direction |
|---|---|---|
| P0–P2 | TC_A0–TC_A2 (mux channel; channel n = TCn) | out |
| P3 | mux enable, inverted by U5: P3 low = muxes on. High at power-up, so muxes start disabled. | out |
| P4 | JOYSTICK_CONFIRM | in |
| P5 | JOYSTICK_BACK | in |
| P6 | TC_DRDY | in |
| P7 | TC_FAULT | in |

## J10: front panel

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | JOYSTICK_CONFIRM | 6 | ENCODER_B |
| 2 | I2C_SDA | 7 | JOYSTICK_BACK |
| 3 | I2C_SCL | 8 | GND |
| 4 | JOYSTICK_PUSH | 9 | VCC |
| 5 | ENCODER_A | | |

### Panel module

Generic "1.3 inch OLED + EC11 encoder" module, 9-pin header, about 65 × 35 mm, four M3 holes.
Details below are read from the seller manual's schematic (a low-resolution image of the
generic module, not measured on our unit):

- Display: SH1106, I²C address 0x3C, 3.3 V supply only (no regulator shown).
- I²C: 10 kΩ pull-ups to 3V3 on SDA and SCL on the module.
- Encoder A/B (TRA/TRB) and push (PSH): each has a 10 kΩ pull-up to 3V3, 100 nF to GND
  and a 100 Ω series resistor. Switches close to GND (active-low).
- CON (KEY1) and BAK (KEY0) buttons: 10 kΩ pull-up, 100 nF to GND, switch to GND.
- Header order is CON, SDA, SCL, PSH, TRA, TRB, BAK, GND, VCC, which matches J10 pin 1–9.
  The module's own schematic numbers the header the other way round (pin 1 = 3V3), so
  check the physical orientation of J10 in layout.

Consequences: the hat's pull-ups for the encoder and push button (review item 6) are
back-ups and can stay unfitted. With the panel connected, the I²C bus already has the
panel's 10 kΩ in parallel with R4/R5.

## Chosen parts

Parts picked so far, as input for a BOM at the end. Prices are TME gross, single unit, checked 2026-11-12.

| Ref | Part | Footprint | Notes |
|---|---|---|---|
| J11 | Degson [`DG638-9.52-02P`](https://www.tme.eu/pl/details/DG638-9.52-02P/), 4.49 zł | `TerminalBlock_Ningbo-Kagnex_HB9500_1x02_P9.5mm` | 32 A, 4 mm² wire, 9.52 mm pitch, 0.9 mm square pins. The footprint is deliberately generic: 9.5 mm pitch, 2 mm holes, 3.3 × 6.6 mm pads, so any 9.5 mm 30 A block (screw or barrier type) or a soldered wire fits. The pin is loose in the hole; hold the block square and fill the joint fully. |
| U6 | TI `INA226AIDGSR` | `TSSOP-10_3x3mm_P0.5mm` | In stock at TME (confirmed by the user, price not looked up). |
| R6 | 1 mΩ 4-terminal 2512, Vishay WSK2512 type | `R_Shunt_Vishay_WSK2512_6332Metric_T2.21mm` | Exact part not picked yet. Needs ≥ 1 W. |
| L1 | Ferrite bead, 600 Ω at 100 MHz, 0805 | `L_0805_2012Metric` | Exact part not picked yet. |

Considered for J11 and not used: Phoenix `MKDS5/2-6.35` (32 A, 8.04 zł, exact fit on KiCad's Metz
RT11L 6.35 mm footprint, 1.3 mm holes) and Phoenix `MKDS3/2-5.08` (only 24 A).

## Review fixes in progress

A design review found the items below. Only the schematic is being changed by Claude;
the PCB layout is done by hand afterwards. Items 12–14 of the review are deliberately
out of scope. The review text for items 5, 7, 8 and 10 arrived truncated, so missing
values are chosen during the work and recorded here.

Must fix:

- [x] 1. Remap J1. ONEWIRE was on an input-only pin (IO35); it is now on IO22, with the other
      signals shuffled onto input-only pins (table in "J1").
- [ ] 2. 4.7 kΩ pull-up from ONEWIRE to VCC.
- [x] 3. Replace J11 (was rated about 8 A, heater draws about 18.75 A). Now a generic 9.5 mm pitch
      footprint with 2 mm holes; default part Degson `DG638-9.52-02P` (32 A). See "Chosen parts".
- [x] 4. Current sensing: INA226 on the 24 V side with a 4-terminal shunt (details below).
- [ ] 5. Protect the 16 thermocouple lines: series resistor on each line and low-leakage ESD/TVS clamps
      at the terminals. Use insulated (ungrounded-junction) probes only.

Should fix:

- [ ] 6. 10 kΩ pull-ups on ENCODER_A, ENCODER_B, JOYSTICK_PUSH (leave unfitted if the panel has them).
- [ ] 7. 10 kΩ pull-up on TC_CS, so the MAX31856 stays off MISO (IO2, boot strap) during boot.
- [ ] 8. Cold-junction sensing: 2× DS18B20Z (SO-8) on the hat, one at each end of the J2–J9 row.
- [x] 9. I²C pull-ups R4/R5 from 10 kΩ to 4.7 kΩ.
- [x] 10. L1 value was entered as "100uF". Now a ferrite bead, 600 Ω at 100 MHz, 0805 (footprint changed from 1210).
- [x] 11. C10–C13 from 20 µF to 22 µF.

Layout only (not done by Claude):

- Keep the shunt, J11, L1 and 24 V copper away from J2–J9 and U2; group the terminals close to U2.
- Wide copper (ideally 2 oz) on both layers for the heater path.
- 15. Check J1 position and mounting holes against the T-Relay outline (`dxf/` in the vendor repo).

## Working on the schematic

- Close the KiCad schematic editor (or use File → Revert afterwards) when the `.kicad_sch`
  file is edited outside KiCad, otherwise a save from KiCad overwrites the change.
- Check each change with:

  ```sh
  kicad-cli sch erc ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  kicad-cli sch export netlist --format orcadpcb2 -o net.txt ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  ```

  and diff the netlist against the one from before the change.
- Baseline ERC: 3 `power_pin_not_driven` violations, 0 others.
