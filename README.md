# ESP32 LilyGO Display + Temperature Hat

A KiCad 10 hat for the **LilyGO T-Relay-8** (ESP32, 8 relays). It adds 8 thermocouple
inputs, heater current measurement, a 1-Wire port and a connector for a front panel
(1.3" SH1106 OLED with rotary encoder and buttons).

- Base board: [LilyGO T-Relay-8](https://www.amazon.pl/dp/B0B6TY79WN) —
  [vendor repo](https://github.com/Xinyuan-LilyGO/LilyGo-T-Relay) (schematic, DXF outline, pinmap)
- Front panel: [1.3" SH1106 OLED with encoder and buttons](https://allegro.pl/oferta/wyswietlacz-oled-1-3-sh1106-bialy-z-enkoderem-przyciskami-panel-sterowania-18116662587)
- Load: 24 V heaters switched by the T-Relay relays, about 18.75 A in total (assumed to be the sum of several heaters)

## Blocks

| Block | Parts | Notes |
|---|---|---|
| Thermocouple front end | J2–J9, D1–D4, R14–R29, U1, U3 (TMUX1108), U2 (MAX31856) | Each terminal has an ESD clamp and 100 Ω in series (see "Thermocouple input protection"). U1 muxes the `+` legs, U3 the `−` legs, into one MAX31856 over SPI. Input filter: R1 100 Ω, R2 300 Ω, C1 100 nF differential, C2/C3 10 nF to GND. |
| I/O expander | U4 (PCF8574A), U5 (74LVC1G04), JP1–JP3 | Mux address and enable, MAX31856 status, two panel buttons. |
| Front panel | J10 (1x9 socket) | I²C display, encoder, buttons. |
| Heater current | J11, R6 (shunt), U6 (INA226) | High-side shunt in the +24 V feed, read over I²C. See "Heater current sensing". |
| 1-Wire | J12 (JST PH 3-pin), R12, U7, U8 | External DS18B20 probes on J12, plus two optional on-board DS18B20Z (U7, U8) for cold-junction sensing. |
| Supply | L1, C10–C14 | `VCC` = 3V3 from the T-Relay; `VAA` = analog rail for U2, filtered by ferrite bead L1. |

## J1: connection to the T-Relay-8

J1 is a 2x11 socket soldered on the **bottom** of the hat, facing down onto the T-Relay's pin
header P5. Its footprint is on the back side of the board, so the board file shows what is
really built: pads, silkscreen, courtyard and 3D model are all on the bottom.

**J1's pin numbers are the same as LilyGO's P5 pin numbers.** J1 pin n mates with P5 pin n.
Checked against the official T-Relay-8 schematic (`Schematic/T_Relay8_ESP32.pdf`, header P5),
the vendor pinmap image and the silkscreen labels in the vendor DXF; all three agree. On the
board, pad 2 (3V3) is at (124.54, 92.39) and pad 1 (GND) at (124.54, 89.85), which is the
right-hand end of the header seen from above with the relays on the left.

(Before 2026-11-12 the footprint sat on the front layer with the two rows numbered the other
way round, pin 1 = 3V3. That was electrically the same but drew the socket on the wrong side.)

### How the hat sits on the T-Relay-8

From the vendor DXF and STEP model (T-Relay board is 85 × 170 mm). With J1 mated, a point on
the hat at (x, y) is above the T-Relay point (x − 44.54, y − 16.49) mm, measured from the
T-Relay's top-left corner with the relays on the left.

- **The hat is flush with the T-Relay's top and right edges** and covers it from x = 39.3 to
  85.0 mm and y = 0 to 99.7 mm: the upper half, to the right of the relays. The hat is
  45.7 × 99.7 mm (it was 48.3 mm wide and overhung by 5.6 mm on the right and 3.5 mm at the top).
- **Relays** are 15.7 mm tall and end at x = 37.7 mm, 1.6 mm from the hat's left edge. The hat's
  underside is assumed to be about 11 mm up, so the hat cannot go further left.
- **The ESP32 antenna is no longer under the hat.** The module sits at T-Relay x = 59–77.5 mm,
  y = −6.4 to 25.6 mm; its antenna end sticks out past the T-Relay's top edge, where the hat
  now stops.
- **No hat hole can be screwed to the T-Relay.** The T-Relay has three Ø4 mm holes in one
  column, at (50.0, 17.6), (48.1, 73.5) and (48.1, 158.6). The first two are under the hat, at
  hat coordinates (94.6, 34.1) and (92.6, 89.9): right against the J2–J9 terminal column, with
  no room for a screw head beside the terminal bodies.
- **Three hat holes sit over bare T-Relay board** (checked against the STEP model) and can take
  resting spacers of the board-to-board height: H1 in the top-right corner at (125.7, 20.3),
  H3 at (125.9, 100.6) and H4 at (97.3, 112.4). H2 at (97.8, 20.3) is above the T-Relay's reset
  button, so it gets none. The hat also covers that reset button.
- **J12 sits above the ESP32 module's top end**, so the 1-Wire cable leaves across the antenna.
  This was looked at and accepted; moving J12 to the top-left corner was tried and rejected.

| J1 = P5 pin | ESP32 | Signal | Notes |
|---|---|---|---|
| 1, 3 | GND | GND | |
| 2, 4 | 3V3 | VCC | |
| 5 | IO14 | TC_SCK | LilyGO names this net `GPIO14/CLK` |
| 6 | IO2 | TC_MISO | Boot strap. LilyGO: `GPIO2/MISO` |
| 7 | IO15 | TC_MOSI | Boot strap. LilyGO: `GPIO15/MOSI` |
| 8 | IO4 | TC_CS | Pulled up by R13 (4.7 kΩ) so the MAX31856 stays deselected, and off IO2, during boot |
| 9 | IO35 | ENCODER_B | Input-only |
| 10–14 | NC | — | Not connected on the T-Relay |
| 15 | IO39 | JOYSTICK_PUSH | Input-only. See note below. |
| 16 | IO36 | free | Input-only, ADC1. See note below. |
| 17 | IO34 | ENCODER_A | Input-only |
| 18 | GND | GND | |
| 19 | IO26 | EXPANDER_INT | Pulled up by R3 |
| 20 | IO27 | I2C_SDA | |
| 21 | IO22 | ONEWIRE | The only free bidirectional pin; 1-Wire needs one |
| 22 | IO23 | I2C_SCL | |

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

Working assumption (not confirmed by the system owner): the board controls several heaters
independently, one per relay, and 18.75 A (450 W at 24 V) is their **sum**. That fits the
review's wording "J11.2 → relay COMs" (plural), the 8 relays and the 8 thermocouple inputs.
`24V_OUT` then feeds the COM terminals of all heater relays, and J11 and R6 carry the total.

- The INA226 measures the total only. Firmware can get a single heater's current from the
  step in the reading when that relay switches.
- Still to confirm with the owner: each heater must stay within one relay contact's rating
  (believed to be about 10 A on the T-Relay-8). A single 18.75 A heater on one relay would
  not be acceptable.

## Thermocouple input protection

**Use insulated (ungrounded-junction) thermocouple probes only.** The protection below covers
static discharge and switching spikes. It does not cover a thermocouple line held on 24 V:
that would destroy the clamp and probably the multiplexer.

```
terminal J2–J9 ──────┬── 100 Ω ── TCn± ── TMUX1108 ── ... ── MAX31856
                     │
              ESD clamp to GND
```

- The MAX31856 inputs withstand ±45 V, but the TMUX1108 in front of it only allows −0.5 V to
  VDD + 0.5 V on its signal pins and is rated for 2 kV ESD, so the multiplexers are the weak point.
- D1–D4: Nexperia PESD5V0L4UG, four clamps per package, one package per pair of terminals
  (D1: J2/J3, D2: J4/J5, D3: J6/J7, D4: J8/J9). Place each one right at its terminals.
  The schematic symbol is KiCad's generic 4-diode array (`SP0504BAJT`: same pinout, same
  SOT-353 footprint) with the value set to PESD5V0L4UG, because the library's own PESD symbol
  is split into four separate diode units and reads badly.
- R14–R29: 100 Ω in each line, between the clamp and the multiplexer.
- R2 is 300 Ω, not 100 Ω. The bias point is at the multiplexer output, so both added 100 Ω
  resistors of a channel end up in the T+ path (R1 + 2 × 100 Ω). The MAX31856 datasheet
  ("Effect of Series Resistance") says to match the two paths: offset = I_B × ΔR_S + ΔI_B × R_S,
  with I_B up to 65 nA. Unmatched, 200 Ω would add up to 13 µV; matched, about 2 µV (0.05 °C, type K).
- Series resistance per input stays far below 5 kΩ, so the fast open-circuit detection mode
  (`OCFAULT = 01`) still applies.
- Clamp leakage (25 nA per TME's listing, at 5 V; lower at the 0.7 V the lines sit at) flows
  through 100 Ω at most: under 3 µV.

Considered and not used: 2.2 kΩ + BAV199 rail clamps + 100 Ω per line, which would survive a
continuous 24 V on any line. It needs 48 parts, R2 of about 4.75 kΩ, the slower open-circuit
mode, and costs up to about 20 µV (0.5 °C) worst case.

## Cold-junction sensing (optional)

A thermocouple reading is the tip temperature minus the temperature of the terminals J2–J9,
so an error in the terminal temperature goes into every reading one for one. The MAX31856
uses its own internal sensor for this, which measures the chip, not the terminals.

U7 and U8 are two DS18B20Z on the `ONEWIRE` bus (shared with J12, pulled up by R12). Firmware
can read them, interpolate along the terminal row and write the result into the MAX31856's
cold-junction register in place of the internal sensor.

- Optional: if this accuracy is not needed, leave U7, U8, C16 and C17 unfitted and let the
  MAX31856 use its internal sensor. They are not flagged DNP in the schematic.
- Layout: one sensor at each end of the J2–J9 row, close to the terminals, each with its
  capacitor (C16, C17) next to it. Keep the shunt, J11, L1 and the 24 V copper away from the
  terminals and from U2, and group the terminals close to U2 if possible.

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

Consequences: the hat's pull-ups for the encoder and push button (R9–R11, 10 kΩ) are
back-ups, marked do-not-populate. Fit them only if a panel without pull-ups is used. With the panel connected, the I²C bus already has the
panel's 10 kΩ in parallel with R4/R5.

## Chosen parts

Parts picked so far, as input for a BOM at the end. Prices are TME gross, single unit, checked 2026-11-12.

| Ref | Part | Footprint | Notes |
|---|---|---|---|
| J11 | Degson [`DG638-9.52-02P`](https://www.tme.eu/pl/details/DG638-9.52-02P/), 4.49 zł | `TerminalBlock_Ningbo-Kagnex_HB9500_1x02_P9.5mm` | 32 A, 4 mm² wire, 9.52 mm pitch, 0.9 mm square pins. The footprint is deliberately generic: 9.5 mm pitch, 2 mm holes, 3.3 × 6.6 mm pads, so any 9.5 mm 30 A block (screw or barrier type) or a soldered wire fits. The pin is loose in the hole; hold the block square and fill the joint fully. |
| U6 | TI `INA226AIDGSR` | `TSSOP-10_3x3mm_P0.5mm` | In stock at TME (confirmed by the user, price not looked up). |
| D1–D4 | Nexperia [`PESD5V0L4UG.115`](https://www.tme.eu/pl/details/PESD5V0L4UG.115/), 1.23 zł | `SOT-353_SC-70-5` | 4-channel ESD clamp, 5 V, common anode. 5900 in stock. |
| R6 | 1 mΩ 4-terminal 2512, Vishay WSK2512 type | `R_Shunt_Vishay_WSK2512_6332Metric_T2.21mm` | Exact part not picked yet. Needs ≥ 1 W. |
| L1 | Ferrite bead, 600 Ω at 100 MHz, 0805 | `L_0805_2012Metric` | Exact part not picked yet. |

Considered for J11 and not used: Phoenix `MKDS5/2-6.35` (32 A, 8.04 zł, exact fit on KiCad's Metz
RT11L 6.35 mm footprint, 1.3 mm holes) and Phoenix `MKDS3/2-5.08` (only 24 A).

## PCB layout tasks

The schematic went through a design review (items 1–11; the reasoning for each change is in
the git history) and the board has been brought in line with it.

State of the board:

- All parts are placed, on the top side. The outline is 45.7 × 99.7 mm, cut back on the right
  so that the hat is flush with the T-Relay (see "How the hat sits on the T-Relay-8").
- **Routing is partly restored.** All tracks were first removed, because the new parts sit where
  many of them ran and several pads changed net. Then 137 original track segments and vias (of 495) were
  put back by script: only those whose pads are all still on the same net and have not moved
  by more than 2 mm (ends on slightly moved pads were stretched to fit), and only if DRC stayed
  clean with them. That covers the core around U1, U3, U4, U2 and the jumpers: the multiplexer
  outputs and input filter (U1/U3 → R1/R2/C1–C3 → U2), `TC_A2`, `TC_DRDY`, `TC_FAULT`, the
  U4–U5 enable line, the JP1/JP2 address lines, and the local VCC/GND stubs and plane vias.
  Everything that touches J1, J11, the terminals, the I²C pull-ups or the supply filter still
  has to be routed. The VCC and GND planes (In1, In2) are kept and refilled.
- DRC shows no clearance, short or courtyard errors, 139 unconnected items (the routing to do),
  and silkscreen warnings.
- **Footprint `REF1` is the T-Relay-8 reference, as one object.** It holds both the 2D outline
  on `Dwgs.User` (board edge, relays, ESP32 module, header pins, mounting holes, from the vendor
  DXF) and the 3D model (`3d/T-Relay8-ESP32-3D.stp`, LilyGO's own file, unchanged, from
  `dxf/T-Relay8-ESP32-3D.7z` in the vendor repo). It has no pads, is board-only, and is excluded
  from the BOM and position files. It is locked so it is not dragged by accident.
  - Its anchor is the T-Relay's bottom-left corner. If J1 ever moves on the hat, unlock `REF1`
    and move it by the same amount; outline and model move together.
  - The 3D model is drawn 11 mm below the hat's underside, an assumed stack height for the
    header and socket. Correct the model's Z offset once the real gap is measured.
- Board coordinates in this README are sheet coordinates in the PCB editor. On 2026-11-12 the
  whole drawing was moved up by 66.04 mm (26 × 2.54) so that the hat and the T-Relay outline
  fit on the A4 sheet; coordinates in commit messages before that are 66.04 mm larger in y.
- There is no antenna keep-out. One was added when the hat covered half the antenna and removed
  once the hat became flush with the T-Relay's top edge, where it only cut a corner out of the
  VCC plane and kept the planes away from J12's ground mounting pads.

Where things are:

- **Terminals J2–J9** are where the original design had them, on the left edge, at an exactly
  uniform 12.70 mm pitch.
- **Thermocouple protection** is one column (x = 96.9) between the terminals and the
  multiplexers, mirror-symmetric about the centre of the terminal row (y = 66.7). Each clamp
  array is next to the connectors it serves (D1: J2/J3, D2: J4/J5, D3: J6/J7, D4: J8/J9).
- **Cold-junction sensors** are in that column, in the same orientation, each centred in a gap
  between two terminals and 12.7 mm either side of the row's centre: U7 between J4 and J5
  (y = 54.0), U8 between J6 and J7 (y = 79.4). Terminal pins run from y = 19.7 to 113.7.
  C16 and C17 sit at mirrored positions beside them.
- **Heater path** at the right edge above J1: J11 with its wire entry facing outward, R6 directly
  behind it (pad 1 towards J11 pin 1), then a column with R7, R8, C15, U6 and C14.
- **Supply filter** (L1, C10–C13) is below U3, moved from the right to make room for J11.
- **Pull-ups:** R12 by J12, R13 by U2, R9–R11 (not fitted) in a row above J10.

Routing tasks:

- [ ] **Heater path** (`24V_IN`, `24V_OUT` between J11 and R6): short, wide copper on both outer
      layers, ideally 2 oz, sized for about 19 A. The inner planes are VCC and GND, so cut them
      back under this copper. Keep clearance between 24 V and the 3.3 V circuitry.
- [ ] **Kelvin routing at the shunt.** R6 pads 2 and 3 as a tight pair to R7/R8, then C15,
      then U6 pins 10/9. Nothing else connects to those two tracks. `Vbus` (U6 pin 8) gets a
      thin track from `24V_OUT`.
- [ ] **Thermocouple inputs.** Terminal pad → clamp pin → series resistor → multiplexer, with the
      `+` and `−` of each channel routed together and no vias if possible.
- [ ] **Keep heat and noise away from the terminals and U2**: no 24 V copper near J2–J9 or U2.
- [ ] **J1 is on the back side.** It is a through-hole part, so its pads are reachable from both
      copper layers as before. Do not move it: its position fixes how the hat sits on the T-Relay.
- [ ] **J11 footprint check.** The footprint is generic (9.5 mm pitch, 2 mm holes). The default
      part, Degson DG638-9.52-02P, has a 19.04 × 16 mm body with the pin row 4.9 mm from its
      back face.
- [ ] **J10 orientation** against the physical panel module (its header is numbered the other
      way round, see "J10").
- [ ] **Mechanical support: resting spacers** in H1, H3 and H4 (see "How the hat sits on the
      T-Relay-8"). Their length is the board-to-board gap, about 11 mm, to be measured on the
      real header and socket. H1's spacer is 0.6 mm from the ESP32 module if it is 6 mm wide;
      a 5 mm one gives more room.
- [ ] **DRC clean**, with a net class for the 24 V nets.

## Working on the schematic

- Close the KiCad schematic editor (or use File → Revert afterwards) when the `.kicad_sch`
  file is edited outside KiCad, otherwise a save from KiCad overwrites the change.
- Check each change with:

  ```sh
  kicad-cli sch erc ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  kicad-cli sch export netlist --format orcadpcb2 -o net.txt ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  ```

  and diff the netlist against the one from before the change.
- ERC is clean (0 violations). VCC, VAA and GND each carry a `PWR_FLAG` because power comes in through J1.
