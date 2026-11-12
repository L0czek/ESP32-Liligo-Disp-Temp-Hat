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
| Heater current | J11, R6 (shunt), U6 (INA215) | Low-side shunt, analog output to the ESP32 ADC. Under rework, see review item 4. |
| 1-Wire | J12 (JST PH 3-pin) | External DS18B20 probes. |
| Supply | L1, C10–C14 | `VCC` = 3V3 from the T-Relay; `VAA` = filtered analog rail through L1. |

## J1: connection to the T-Relay-8

J1 pin 1 is the 3V3 corner of the T-Relay header. GPIOs are read from the vendor
T-Relay-8 pinmap. IO34, IO35, IO36 and IO39 are **input-only and have no internal
pull-ups**. IO26 is on ADC2, which does not work while WiFi is on.

| J1 | ESP32 | Signal now | After review item 1 |
|---|---|---|---|
| 1, 3 | 3V3 | VCC | |
| 2, 4, 17 | GND | GND | |
| 5 | IO2 (boot strap) | TC_MISO | |
| 6 | IO14 | TC_SCK | |
| 7 | IO4 | TC_CS | |
| 8 | IO15 (boot strap) | TC_MOSI | |
| 9, 11, 12, 13, 14 | NC | — | |
| 10 | IO35 (input-only) | ONEWIRE | ENCODER_B |
| 15 | IO36 (input-only, ADC1) | EXPANDER_INT | CURRENT_SHUNT |
| 16 | IO39 (input-only) | ENCODER_B | JOYSTICK_PUSH |
| 18 | IO34 (input-only) | ENCODER_A | |
| 19 | IO27 | I2C_SDA | |
| 20 | IO26 (ADC2) | CURRENT_SHUNT | EXPANDER_INT |
| 21 | IO23 | I2C_SCL | |
| 22 | IO22 | JOYSTICK_PUSH | ONEWIRE |

Relays on the T-Relay-8 use IO33, IO32, IO13, IO12, IO21, IO19, IO18, IO5; IO25 is the
red LED. None of these reach the hat.

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

## Review fixes in progress

A design review found the items below. Only the schematic is being changed by Claude;
the PCB layout is done by hand afterwards. Items 12–14 of the review are deliberately
out of scope. The review text for items 5, 7, 8 and 10 arrived truncated, so missing
values are chosen during the work and recorded here.

Must fix:

- [ ] 1. Remap J1 (table above). ONEWIRE is on an input-only pin and CURRENT_SHUNT on ADC2.
- [ ] 2. 4.7 kΩ pull-up from ONEWIRE to VCC.
- [ ] 3. Replace J11 (rated about 8 A, heater draws about 18.75 A) with a 30 A terminal block or M4 lugs.
- [ ] 4. Current sensing. Recommended: INA226 on the 24 V side over I²C with a 2 mΩ 4-terminal 2512 shunt
      (PSU+ → J11.1 → shunt → J11.2 → relay COMs). Alternative: keep INA215 with a 1 mΩ Kelvin shunt,
      separate HEATER_RTN net tied to GND at one point, 1 kΩ/100 nF on OUT. **Option not chosen yet.**
- [ ] 5. Protect the 16 thermocouple lines: series resistor on each line and low-leakage ESD/TVS clamps
      at the terminals. Use insulated (ungrounded-junction) probes only.

Should fix:

- [ ] 6. 10 kΩ pull-ups on ENCODER_A, ENCODER_B, JOYSTICK_PUSH (leave unfitted if the panel has them).
- [ ] 7. 10 kΩ pull-up on TC_CS, so the MAX31856 stays off MISO (IO2, boot strap) during boot.
- [ ] 8. Cold-junction sensing: 2× DS18B20Z (SO-8) on the hat, one at each end of the J2–J9 row.
- [ ] 9. I²C pull-ups R4/R5 from 10 kΩ to 4.7 kΩ.
- [ ] 10. L1 value is entered as "100uF". Replace with a ferrite bead (about 600 Ω) or a correct inductor value.
- [ ] 11. C10–C13 from 20 µF to 22 µF.

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
