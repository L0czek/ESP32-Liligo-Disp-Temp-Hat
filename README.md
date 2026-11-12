# ESP32 LilyGO Display + Temperature Hat

A KiCad 10 hat for the **LilyGO T-Relay-8** (ESP32, 8 relays). It adds 8 thermocouple
inputs, heater current measurement, a 1-Wire port and a connector for a front panel
(1.3" SH1106 OLED with rotary encoder and buttons).

- Base board: [LilyGO T-Relay-8](https://www.amazon.pl/dp/B0B6TY79WN) —
  [vendor repo](https://github.com/Xinyuan-LilyGO/LilyGo-T-Relay) (schematic, DXF outline, pinmap)
- Front panel: [1.3" SH1106 OLED with encoder and buttons](https://allegro.pl/oferta/wyswietlacz-oled-1-3-sh1106-bialy-z-enkoderem-przyciskami-panel-sterowania-18116662587)
- Load: 24 V heaters switched by the T-Relay relays, about 18.75 A in total (assumed to be the sum of several heaters)

> **Branches.** `master` holds the board **routed by hand and then cleaned up by script**
> (0 unconnected, DRC clean). `hand-routed` is the hand routing exactly as drawn, kept as the
> reference for the clean-up. `scripted-routing` is an earlier, fully scripted board with a
> different layout; what was learned from it is under "Lessons from the scripted routing".

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
board, pad 2 (3V3) is at (121.54, 95.89) and pad 1 (GND) at (121.54, 93.35), which is the
right-hand end of the header seen from above with the relays on the left.

(Before 2026-11-12 the footprint sat on the front layer with the two rows numbered the other
way round, pin 1 = 3V3. That was electrically the same but drew the socket on the wrong side.)

### How the hat sits on the T-Relay-8

From the vendor DXF and STEP model (T-Relay board is 85 × 170 mm). With J1 mated, a point on
the hat at (x, y) is above the T-Relay point (x − 41.54, y − 19.99) mm, measured from the
T-Relay's top-left corner with the relays on the left.

- **The hat's top and right edges are flush with the T-Relay's.** The outline is 46.0 × 99.7 mm
  (it was 48.3 mm wide; 2.3 mm were cut off on the right). It covers the T-Relay from
  x = 39.0 mm to the right edge and from the top edge down to y = 99.7 mm.
  - Relative to the original design, everything except J1 sits 3.3 mm further left and
    3.5 mm further down on the sheet; J1 and `REF1` did not move.
  - The T-Relay's top edge is at hat y = 19.99 and its right edge at hat x = 126.54.
- **Relays** are 15.7 mm tall and end at x = 37.7 mm, 1.3 mm from the hat's left edge.
- **The ESP32 antenna is not under the hat.** The module sits at T-Relay x = 59–77.5 mm,
  y = −6.4 to 25.6 mm; its antenna end sticks out past the T-Relay's top edge, where the hat
  stops.
- **Mounting holes** are M3 with a 6.4 mm pad, as in the original. H1 is at (122.7, 23.8) and
  H3 at (122.9, 104.1): both had to move in from the cut edge, and H3 also up, because the
  corner beside J10 is too narrow for it. These two spots were checked against the STEP
  model on the scripted branch to be over bare T-Relay board. H2 and H4 are at their original
  places and not rechecked.
  - Plain 4 mm holes (the T-Relay's size) were tried and do not help: the stock footprint's
    keep-out is 8.5 mm across, more than the M3 pad, and H4 would not fit between J9 and J10.
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
- J11 is a Phoenix MKDS5/2-6.35 screw terminal block (fixed, not pluggable).
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
| P0–P2 | TC_A0–TC_A2 (mux channel n = `TCn` = terminal J(n+2): J2 is channel 0, J9 is channel 7) | out |
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
| J11 | Phoenix [`MKDS5/2-6.35`](https://www.tme.eu/pl/details/MKDS5_2-6.35/), 8.04 zł | `TerminalBlock_MetzConnect_Type701_RT11L02HGLU_1x02_P6.35mm_Horizontal` | 32 A, 4 mm² wire, 6.35 mm pitch, 1 × 1 mm pins in 1.3 mm holes (hole size confirmed on the Phoenix drawing by the user). Exact fit on the stock KiCad footprint, 12.7 × 12.5 mm body. 80 in stock at TME on 2026-11-12. |
| U6 | TI `INA226AIDGSR` | `TSSOP-10_3x3mm_P0.5mm` | In stock at TME (confirmed by the user, price not looked up). |
| D1–D4 | Nexperia [`PESD5V0L4UG.115`](https://www.tme.eu/pl/details/PESD5V0L4UG.115/), 1.23 zł | `SOT-353_SC-70-5` | 4-channel ESD clamp, 5 V, common anode. 5900 in stock. |
| R6 | 1 mΩ 4-terminal 2512, Vishay WSK2512 type | `R_Shunt_Vishay_WSK2512_6332Metric_T2.21mm` | Exact part not picked yet. Needs ≥ 1 W. |
| L1 | Ferrite bead, 600 Ω at 100 MHz, 0805 | `L_0805_2012Metric` | Exact part not picked yet. |

J11 was first given a generic 9.5 mm footprint with 2 mm holes for the Degson `DG638-9.52-02P`
(32 A, 4.49 zł), to fit whatever 30 A block was on hand. It took 21.6 × 18.9 mm of board and
was the main reason the layout was tight, so it was replaced by the smaller Phoenix part.
Phoenix `MKDS3/2-5.08` (24 A) was rejected as too small for a continuous 19 A load.

## PCB layout

The schematic went through a design review (items 1–11; the reasoning for each change is in
the git history). The board was then routed by hand on top of the original layout (branch
`hand-routed`), and `master` is that routing after a scripted clean-up.

State: **0 unconnected, no DRC errors on copper** (clearance, shorts, holes, edge, dangling
ends all 0), schematic parity 0, ERC 0. What DRC still lists is silkscreen only (104 warnings).

After the clean-up the board was moved 3.5 mm down relative to J1 and cut to the T-Relay's
right edge (script `tools/move_board.py`, decisions in `tools/move_overrides.py`). That put
J1 3.5 mm closer to the heater copper and its left pins onto three tracks, so these parts
were redrawn:

- **Right-hand bundle on the back** (SDA, 1-Wire, MOSI, `JOYSTICK_BACK`, MISO): nested corners
  below the heater copper, then along J1's top row at 0.55–0.6 mm pitch into their pins.
- **Chip select and R13:** R13 sits on the track between J1 pins 7 and 5; the line leaves it
  to the right under the heater copper and turns up outside it.
- **I²C from U6:** SCL changes to the back just above J1; SDA stays on the front.
- **TC6−, TC7− and `JOYSTICK_CONFIRM`** turn 3.3–3.5 mm earlier to pass above J1's left pins;
  TC5+'s via moved 0.9 mm to make room. R19 and R24 are back 0.57 mm off their pin axis, as
  in the hand routing, because R24 level with its pin leaves only 0.2 mm gaps there.
- **Pull-ups R3–R5 and C8** are 0.7 mm further left. Their vias sit between the pad rows
  instead of at the edge; `EXPANDER_INT` runs down their left side into R3, SCL passes
  between R3's pads.
- **Lanes on the front right:** CS 123.57, SCK 124.3, `EXPANDER_INT` 125.05, SCL 125.8, at
  least 0.6 mm from the new edge.

What the hand routing did:

- **Everything except J1 and `REF1` sits 3.3 mm further left** than in the original design.
- **The protection column is at x = 91.1–92.7**, 4.7 mm from the terminal pins. Each group is
  terminal → series resistor → clamp on the front layer. The outer line of a group runs
  straight down between the pads of the inner resistor to the clamp.
- **Thermocouple lines to the multiplexers** run as one bundle on the front between the column
  and U1/U3, with the lower channels crossing on the back.
- **Cold-junction sensors U7 and U8 are on the back** under the column, at (91.75, 32.06) and
  (91.75, 108.30): mirror images about the middle of the terminal row (y = 70.18). C16 and C17
  sit 4.8 mm above their sensor, at x = 90.54.
- **Clamp ground vias are outside the clamps**, 1.2–1.5 mm out on the three-pin side, at
  x = 90.94. The group's inner line runs 0.37 mm further left beside the via, so the via has
  0.38 mm to both neighbours.
  - At D1 and D4 the via comes out between the pad rows of the sensor on the back; that is
    what fixes the sensors' positions. At U8 the TC7+ track passes between the rows as well.
  - U8's ground pin goes to H4's pad, because the TC7+ track separates it from D4's via.
- **Heater path** as before: `24V_IN` and `24V_OUT` zones on both outer layers between J11 and
  R6 with fifteen 0.8 mm stitching vias, Kelvin pair to U6.
- **SPI, I²C, 1-Wire and the panel lines** go round the heater copper on the right: five
  tracks on the back between the heater zones and J11's far side, four on the front further
  right.
- Four layers: front and back for signals, In1 = VCC plane, In2 = GND plane.
- The channel order is the original one (J2 = channel 0 … J9 = channel 7).

What the clean-up changed relative to `hand-routed` (script in `tools/`, see below):

- **The hand move is exact.** It was (−3.32, +0.045) mm; it is now (−3.30, 0).
- **Parts that belong on a pin's axis are exactly on it**: the series resistors level with
  their terminal pins, the clamps centred between the two inner pins, R9–R11 above their J10
  pins. Shifts of 0.001–0.1 mm, except:
  - **R19 and R24 moved 0.57 mm** to be level with their pins like the other outer resistors.
  - **R27 moved 4.9 mm down** to be level with J8 pin 2. It had been parked above J1 when J1
    was in the way; it no longer is. Group 4 (J8/J9) is now the mirror image of group 1.
  - **U7 moved 0.15 mm up** so that D1's ground via sits in the middle of the clamp.
- **Tracks**: every segment is exactly horizontal, vertical or 45°; all ends are on pad or
  via centres; 24 stub segments shorter than 0.15 mm and 4 dangling ends are gone
  (581 → 514 segments, still 100 vias).
- **Widths**: the hand-drawn 0.2 mm pieces are 0.3 mm like the rest. Only the Kelvin pair and
  U6's own short tracks stay 0.2 mm.
- **Spacing was opened up where there was room:**
  - Tracks between two J1 pins are centred in the gap (0.27 mm each side instead of 0.2).
  - The four-track bundle left of U1/U3 has 0.25 mm gaps (was 0.15–0.2).
  - The fan-out of the `−` lines at U3 is staggered: 0.26–0.3 mm between the diagonals.
  - The five-track bundle on the back right of the heater copper has a 0.6 mm pitch (was 0.5).
- **Still at 0.2–0.25 mm**, because pads fix the geometry: SDA/SCL at U6's pins (0.5 mm pin
  pitch), and four spots in J1's left-hand corner where I²C, 1-Wire and `EXPANDER_INT` share
  two pin gaps.

Other things to know:

- **Footprint `REF1` is the T-Relay-8 reference, as one object.** It holds both the 2D outline
  on `Dwgs.User` (board edge, relays, ESP32 module, header pins, mounting holes, from the vendor
  DXF) and the 3D model (`3d/T-Relay8-ESP32-3D.stp`, LilyGO's own file, unchanged). It has no
  pads, is board-only, is excluded from the BOM and position files, and is locked.
  - Its anchor is the T-Relay's bottom-left corner. If J1 ever moves on the hat, unlock `REF1`
    and move it by the same amount; outline and model move together.
  - The 3D model is drawn 11 mm below the hat's underside, an assumed stack height for the
    header and socket. Correct the model's Z offset once the real gap is measured.
- Board coordinates in this README are sheet coordinates in the PCB editor. On 2026-11-12 the
  whole drawing was moved up by 66.04 mm (26 × 2.54) so that the hat and the T-Relay outline
  fit on the A4 sheet; coordinates in commit messages before that are 66.04 mm larger in y.
- When routing, set the track width to "use netclass width". The predefined width list has
  0.2 and 0.4 mm but no 0.3 mm entry.
- Design rules: clearance 0.2 mm, default track 0.3 mm, vias
  0.6/0.3 mm, hole clearance 0.28 mm; net class `Power24V` for the `24V_*` nets. All within
  JLCPCB's standard four-layer limits.

## Lessons from the scripted routing

The branch `scripted-routing` got to a complete, DRC-clean board, but by redrawing about 92 %
of the original routing. These are the things worth knowing before routing this one by hand.

Placement:

- **Leave the multiplexers beside U2.** They were moved to the middle of the terminal row once
  to make the thermocouple lines short and straight. That stretched U1's output to the ADC
  from 9 mm to 35 mm and pushed the decoupling 15–21 mm away, and it was undone.
- **The protection column works as placed.** Terminal → clamp tap → resistor fits on the front
  layer with no crossings if the two inner lines of a group tap straight to the clamp and the
  two outer lines tap through the gap between the inner resistor's pads. J2 pin 2 and J9
  pin 1 sit beside H2 and H4 and have to go round the neighbouring pin.
- **The back layer under the column is the one free north–south channel on the left**, as long
  as the vias of the thermocouple lines stay east of the resistors. That is why the sensors
  sit there. A via under the column hits the front-side parts, so supply vias for the sensors
  need spots that are clear on both layers; D1's and D4's ground vias can be shared.
- **Put the back-side sensors at least 1 mm from the terminal pads.** At 0.3 mm they were legal
  but cramped.

Heater path:

- **18.75 A needs filled copper, not tracks.** Zones about 9 mm wide on both outer layers
  between J11 and R6, stitched with 0.8 mm vias and connected solidly to the pads, worked.
  R6's two small pads are sense pads and go only to R7 and R8.
- **That copper closes the middle of the board.** The original ran SPI, I²C, 1-Wire and two
  joystick lines through it. Two ways round were found: the strip between the heater copper
  and the right-hand edge (both layers, under J11's body; it carried four SPI and two I²C
  lines), and a narrower strip just west of the heater copper, under U6.

J1 and the lines to it:

- **A J1 pin between two gaps that are both used on both layers cannot be reached at all.**
  This happened to `ENCODER_A` on pin 17 when two thermocouple pairs took the gaps either
  side of it.
- **J1's four left-hand pins are crowded** since the pin fix: 1-Wire, SCL, SDA and
  `EXPANDER_INT` all end there, behind whatever runs from the lower terminals to the
  multiplexers.
- **The panel signals are in a different left-to-right order at J1 and at J10**, so
  `ENCODER_A` and `JOYSTICK_PUSH` must cross the I²C pair. Doing that by layer worked;
  `ENCODER_A` also had to pass between two J10 pins and enter its own pin from the far side.
- **I²C from U6 straight through J1 to J10 on the front needed no vias** (two gaps between J1
  pin columns, then diagonals to J10 pins 2 and 3).

Routing practice:

- **Keep the two lines of a thermocouple pair together.** Length and via count do not matter
  electrically (0.3 mm track is 1.6 mΩ/mm against 100 Ω series resistors; a via is copper to
  copper). The open loop between a `+` and a `−` that run millimetres apart is what picks up
  the heater current stepping.
- **0.3 mm tracks were needed in places**; 0.4 mm did not fit everywhere between the column and
  the multiplexers.
- **Do not let a via sit partly on a pad**, and prefer 45° corners; both had to be cleaned up
  afterwards.
- **Count what a change throws away.** Each step of the scripted work looked reasonable alone;
  together they replaced a reviewed layout with a new, unproven one.

## Remaining work

- [x] **Routing** (by hand, then cleaned up).
- [x] **Fit to the T-Relay**: top and right edges flush.
- [ ] **Silkscreen** once the parts are final.
- [ ] **BOM.** Two parts are not picked yet: R6 (1 mΩ four-terminal shunt, 2512, at least 1 W)
      and L1 (600 Ω at 100 MHz ferrite bead, 0805). Then a full list with TME order codes;
      the picks made so far are in "Chosen parts".
- [ ] **A second look by the original reviewer** when the routing is done.
- [ ] **Check against the hardware:**
  - J10's pin order against the real panel module (its header is numbered the other way
    round, see "J10").
  - The board-to-board gap, assumed 11 mm. It sets the length of the resting spacers and the
    Z offset of the T-Relay 3D model.
  - That each heater stays within one relay contact's rating (see "Heater current sensing").
- [ ] **Firmware notes to carry over:** a settling delay after changing the multiplexer
      address before a conversion starts, and the INA226 is polled (its Alert pin is not
      connected).

## The clean-up script

`tools/clean_hand_routing.py draft.kicad_pcb base.kicad_pcb out.kicad_pcb` turns the board on
`hand-routed` into the one on `master` (`base` is the board of commit a5f51c9, used to tell
the original 0.2 mm tracks from hand-drawn ones). `tools/overrides.py` holds every correction
that was decided by hand, with a comment each. Run `kicad-cli pcb drc --refill-zones
--save-board` on the result to refill the zones.

## Working on the schematic and board files

- Close the KiCad schematic editor (or use File → Revert afterwards) when the `.kicad_sch`
  file is edited outside KiCad, otherwise a save from KiCad overwrites the change.
- Check each change with:

  ```sh
  kicad-cli sch erc ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  kicad-cli sch export netlist --format orcadpcb2 -o net.txt ESP32-Liligo-Disp-Temp-Hat.kicad_sch
  ```

  and diff the netlist against the one from before the change.
- When the `.kicad_pcb` is edited by script, compare every track's net before and after KiCad
  saves it: KiCad silently re-nets a track that touches copper of another net. Remove old
  tracks before moving the parts they end on.
- ERC is clean (0 violations). VCC, VAA and GND each carry a `PWR_FLAG` because power comes in through J1.
