# ESP32 LilyGO Display + Temperature Hat

A KiCad 10 hat for the **LilyGO T-Relay-8** (ESP32, 8 relays). It adds 8 thermocouple
inputs, heater current measurement, a 1-Wire port and a connector for a front panel
(1.3" SH1106 OLED with rotary encoder and buttons).

- Base board: [LilyGO T-Relay-8](https://www.amazon.pl/dp/B0B6TY79WN) —
  [vendor repo](https://github.com/Xinyuan-LilyGO/LilyGo-T-Relay) (schematic, DXF outline, pinmap)
- Front panel: [1.3" SH1106 OLED with encoder and buttons](https://allegro.pl/oferta/wyswietlacz-oled-1-3-sh1106-bialy-z-enkoderem-przyciskami-panel-sterowania-18116662587)
- Load: 24 V heaters switched by the T-Relay relays, about 18.75 A in total (assumed to be the sum of several heaters)

> **Two branches.** `master` is a **starting point for routing by hand**: the reviewed schematic,
> every original part where it was with its original tracks, the new parts placed roughly, the
> heater copper, and nothing else routed. `scripted-routing` holds a complete board routed by script
> (0 unconnected, DRC clean) on a slightly narrower outline, with J1 moved to sit flush on the T-Relay. It is kept as a reference, and
> what was learned from it is listed under "Lessons from the scripted routing".

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

- **J1 is where the original design had it, so the hat is not lined up with the T-Relay's
  edges.** It covers the T-Relay from x = 42.3 mm to past the right edge, and from 3.5 mm
  above the top edge down to y = 96.2 mm.
  - It overhangs by **3.5 mm at the top** and **5.6 mm on the right**. The T-Relay's top edge
    is at hat y = 19.99 and its right edge at hat x = 126.54, both drawn by `REF1`.
  - On the scripted branch J1 was moved 3.0 mm right and 3.5 mm up on the hat to make the top
    edges flush. That is not done here, because it takes J1 away from its original tracks.
- **Relays** are 15.7 mm tall and end at x = 37.7 mm, 4.6 mm from the hat's left edge.
- **The hat's top end covers part of the ESP32 antenna.** The module sits at T-Relay
  x = 59–77.5 mm, y = −6.4 to 25.6 mm, which is hat x = 100.5–119.0, y = 13.6–45.6. Its antenna
  end sticks out 6.4 mm past the T-Relay's top edge and the hat covers 3.5 mm of that.
- **Not rechecked for this position:** whether any hat hole lines up with a T-Relay hole, and
  what is under H1–H4 for resting spacers. The T-Relay's two upper Ø4 mm holes are at hat
  coordinates (91.5, 37.6) and (89.6, 93.5), in the J2–J9 terminal column, so screwing the
  boards together still looks ruled out. H1 and H3 at (128.3, 20.3) and (128.4, 112.4) are now
  outside the T-Relay's right edge. The checks against the STEP model on the scripted branch
  were made for the flush position and do not carry over.
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

## PCB layout: starting point for hand routing

The schematic went through a design review (items 1–11; the reasoning for each change is in
the git history). The board on `master` is prepared for routing by hand. A complete scripted
routing exists on the branch `scripted-routing`; this board deliberately does not use it.

What is on the board:

- **Every original part is where the original design had it, with its original routing.**
  91 % of the original track length and 62 of the 66 original vias are there, unmoved, also
  where a track now conflicts with a new part or a changed net. Exceptions, all forced by
  the review:
  - **J1** is on the back, mirrored, at its original place (see "J1"), so its old tracks end
    on its pads. Four signals changed pins in the review and their tracks end on the wrong
    pad: 1-Wire (now pin 21), `EXPANDER_INT` (19), `JOYSTICK_PUSH` (15), `ENCODER_B` (9). The
    old 1-Wire stub stops 0.35 mm short of pin 9, because KiCad re-nets it on save otherwise.
  - **J11, R6 and U6** have new footprints (bigger terminal block, four-terminal shunt, INA226)
    that collide at the old places, so they and **C14** sit at new positions.
  - **L1** is now 0805 instead of 1210, in the same place.
  - **Old tracks are cut back at the edge of the heater copper.** 39 segments were shortened
    or dropped and 4 vias removed where they ran through it, plus 7 segments that touched the
    heater parts. What is left of those tracks points at where they went: `ONEWIRE`,
    `TC_MOSI`, `TC_MISO`, `JOYSTICK_BACK`, `I2C_SDA`, VAA and a ground track, 14–21 mm each,
    and the old current path (`Net-(J11-Pin_1)`, `CURRENT_SHUNT`, nets that no longer exist).
- **The heater path is finished and kept as built** (see "Heater current sensing"): `24V_IN`
  and `24V_OUT` as filled zones on both outer layers between J11 and R6, 4.5 to 9 mm wide,
  stitched with fifteen 0.8 mm vias; the Kelvin pair from R6's sense pads through R7/R8 and C15
  to U6; U6's bus-voltage pin, supply, ground and C14. J11 is at (120.85, 79.38) with the wire
  entry facing right, R6 directly left of it.
- **All original tracks and vias have the project's default sizes**: tracks 0.3 mm (were 0.4
  and 0.8 mm), vias 0.6/0.3 mm (33 were 0.8/0.4). Exceptions: the heater stitching vias
  (0.8/0.4, net class `Power24V`), the 0.2 mm Kelvin and U6 tracks, and five large supply vias
  from the original (four 1.5/0.8 at J12, one 2.0/1.0 on VCC beside L1).
  - When routing, set the track width to "use netclass width". The predefined width list has
    0.2 and 0.4 mm but no 0.3 mm entry.
- **The other new parts are placed roughly and not routed:**
  - Thermocouple protection (R14–R29, D1–D4): one column at x = 96–97.6 between the terminals
    and everything else, in four groups. Each clamp array is level with the gap between its two
    connectors, each series resistor level with its terminal pin.
  - Cold-junction sensors U7 and U8 with C16 and C17: on the **back**, under the two ends of
    that column, at (95.05, 33.4) and (95.05, 101.7), about 5 mm from the terminal pins. U8
    and C17 are placed to clear J1's socket on the back.
  - R27 is at (97.56, 91.0), above J1's left-hand pins instead of level with its terminal
    pin, because J1 is in the way there.
  - Pull-ups: R9–R11 above their J10 pins, R12 at J12, R13 just below J1 pin 8.
- **The outline is the original one, 48.3 × 99.7 mm.** Whether to trim it towards the T-Relay's
  right edge (hat x = 126.54, the vertical line drawn by `REF1`) is open. The strip beyond that
  line holds C8, R3, R4, R5, H1, H3 and original tracks.
- Four layers: front and back for signals, In1 = VCC plane, In2 = GND plane (refilled).
- The channel order is the original one (J2 = channel 0 … J9 = channel 7), which is how the
  original thermocouple tracks are routed.

What DRC reports, and why (schematic parity is 0, ERC is 0):

| Count | What | Cause |
|---|---|---|
| 83 | unconnected | the new parts, the four J1 signals that changed pins, and the tracks cut at the heater copper |
| 30 | shorts | see below |
| 5 | clearance | same places as the shorts |
| 15 | dangling track ends | mostly the tracks cut at the heater copper |
| 39 | solder-mask bridges | follow from the shorts |

The shorts and clearance errors fall into three groups:

- **18: a terminal pin against its old thermocouple track.** The track belongs to the
  multiplexer-side net now; the clamp tap and the series resistor go in between.
- **3 at J1**, the tracks of signals that changed pins: `JOYSTICK_PUSH`'s track ends on pin 21
  (1-Wire), `ENCODER_B`'s on pin 15 (`JOYSTICK_PUSH`), `EXPANDER_INT`'s on pin 16 (unused).
- **14 where a new part lies on or beside an old track:** R15, R18, R20, R21, D2 and D4 in the
  column, U8 on the back, R11, R12, and the old `I2C_SDA` track against U6's ground via.

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

- [ ] **Routing by hand**, starting from the conflict list above.
- [ ] **Decide how the hat should sit on the T-Relay** (it overhangs 3.5 mm at the top and 5.6 mm on
      the right, see "How the hat sits"), then trim the outline and recheck the spacer positions.
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
