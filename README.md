# ESP32 LilyGO Display + Temperature Hat

A KiCad 10 hat for the **LilyGO T-Relay-8** (ESP32, 8 relays). It adds 8 thermocouple
inputs, heater current measurement, a 1-Wire port and a connector for a front panel
(1.3" SH1106 OLED with rotary encoder and buttons).

- Base board: [LilyGO T-Relay-8](https://www.amazon.pl/dp/B0B6TY79WN) —
  [vendor repo](https://github.com/Xinyuan-LilyGO/LilyGo-T-Relay) (schematic, DXF outline, pinmap)
- Front panel: [1.3" SH1106 OLED with encoder and buttons](https://allegro.pl/oferta/wyswietlacz-oled-1-3-sh1106-bialy-z-enkoderem-przyciskami-panel-sterowania-18116662587)
- Load: 24 V heaters switched by the T-Relay relays, about 18.75 A in total: several heaters, each under 10 A, one per relay

> **Branches.** `master` is the current board: routed, 0 unconnected, no DRC errors on copper.
> `hand-routed` is the first hand routing exactly as drawn. `scripted-routing` is an earlier,
> fully scripted board with a different layout. Both are kept for reference only.

## Blocks

| Block | Parts | Notes |
|---|---|---|
| Thermocouple front end | J2–J9, D1–D4, R14–R29, U1, U3 (TMUX1108), U2 (MAX31856) | Each terminal has an ESD clamp and 100 Ω in series (see "Thermocouple input protection"). U1 muxes the `+` legs, U3 the `−` legs, into one MAX31856 over SPI. Input filter: R1 100 Ω, R2 300 Ω, C1 100 nF differential, C2/C3 10 nF to GND. |
| I/O expander | U4 (PCF8574A), U5 (74LVC1G04), JP1–JP3 | Mux address and enable, MAX31856 status, two panel buttons. |
| Front panel | J10 (1x9 socket) | I²C display, encoder, buttons. |
| Heater current | J11, R6 (shunt), U6 (INA226) | High-side shunt in the +24 V feed, read over I²C. See "Heater current sensing". |
| 1-Wire | J12 (JST PH 3-pin), R12, U7, U8 | External DS18B20 probes on J12, plus two on-board DS18B20Z (U7, U8) for cold-junction sensing. Recommended; the board works without them, less accurately. |
| Supply | L1, C10–C14 | `VCC` = 3V3 from the T-Relay; `VAA` = analog rail for U2, filtered by ferrite bead L1. |

## J1: connection to the T-Relay-8

J1 is a 2x11 socket soldered on the **bottom** of the hat, facing down onto the T-Relay's pin
header P5. Its footprint is on the back side of the board, so the board file shows what is
really built: pads, silkscreen, courtyard and 3D model are all on the bottom.

**J1's pin numbers are the same as LilyGO's P5 pin numbers.** J1 pin n mates with P5 pin n.
Checked against the official T-Relay-8 schematic (`Schematic/T_Relay8_ESP32.pdf`, header P5),
the vendor pinmap image and the silkscreen labels in the vendor DXF; all three agree. The
schematic and the pinmap were downloaded and compared again on 2026-11-12. This is a check
against documents only: no real T-Relay was at hand to put a meter on. On the
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
  corner beside J10 is too narrow for it. H2 and H4 are at their original places.
  - H2 is above the T-Relay's reset button (S1), so it cannot take a resting spacer. Known
    and accepted: H2 stays where it is, without a spacer. The button is covered by the hat;
    the T-U2T programmer resets the ESP32 through the USB-C connector instead.
  - The other three, the terminal pins, the J11 pins and the parts on the back were checked
    on 2026-11-12 against the vendor STEP model, DXF and top-view photo
    (`image/T-Relay8.jpg`): all clear at an 11 mm gap, and down to about 6 mm. Under H3, H4,
    the J11 pins and the J10 pins the photo shows bare board. No real board was at hand.
  - **H1 is tight:** its pad edge is 0.4 mm from the ESP32 module in the model, and in the
    photo the spacer reaches the module's edge pads to within the 1 mm accuracy of the
    overlay. A nylon spacer there is harmless; a metal one is not.
  - Two of the T-Relay's own 4 mm mounting holes are under the hat, at (91.57, 37.57) and
    (89.64, 93.44): screw the T-Relay down before plugging the hat on.
  - Plain 4 mm holes (the T-Relay's size) were tried and do not help: the stock footprint's
    keep-out is 8.5 mm across, more than the M3 pad, and H4 would not fit between J9 and J10.
  - **Use nylon spacers.** The spacers only rest on the T-Relay's surface and the hole pads
    are GND, so a metal spacer could wear through the solder mask onto a track.
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
- **PSU− must be connected to the T-Relay's GND.** The hat has no terminal for PSU−, so the
  INA226 measures the 24 V rail against the T-Relay's ground. Powering the T-Relay from the
  same 24 V supply does this automatically. With the T-Relay on USB or on a separate isolated
  supply while the heater supply is live, the INA226 inputs float outside their −0.3 to 36 V
  range: readings are meaningless and the chip can be damaged. The T-Relay accepts 12–24 V DC,
  and the plan is to run it from the heater supply, but that is not confirmed: treat this
  as an installation rule.
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

The board controls several heaters independently, one per relay, each under 10 A; 18.75 A
(450 W at 24 V) is their **sum** (confirmed by the user, 2026-11-12). `24V_OUT` feeds the COM
terminals of all heater relays, and J11 and R6 carry the total.

- The relays are HRS4H-S-DC5V, rated 10 A at 24 V DC per contact (vendor datasheet
  `docs/HRS4-DC5V.pdf`). A single 18.75 A heater on one relay would not be acceptable.
- The INA226 measures the total only. Firmware can get a single heater's current from the
  step in the reading when that relay switches.

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

## Cold-junction sensing

A thermocouple reading is the tip temperature minus the temperature of the terminals J2–J9,
so an error in the terminal temperature goes into every reading one for one. The MAX31856
uses its own internal sensor for this, which measures the chip, not the terminals.

U7 and U8 are two DS18B20Z on the `ONEWIRE` bus (shared with J12, pulled up by R12). Firmware
can read them, interpolate along the terminal row and write the result into the MAX31856's
cold-junction register in place of the internal sensor.

- **Fit them (recommended).** U2 is about 28 mm from the terminals, and the terminals sit
  1.3 mm from the relays, which warm up when energised. U2's internal sensor does not see
  that.
- **The board still works without them.** Leave U7, U8, C16 and C17 unfitted and let the
  MAX31856 use its internal sensor; nothing else changes, and 1-Wire on J12 is unaffected.
  They are not flagged DNP in the schematic. What it costs:
  - Every channel reads wrong by the temperature difference between U2 and its terminal,
    one for one. Expect a few °C; this has not been measured.
  - The error is not a fixed offset. It depends on which relays are on and for how long,
    and it differs along the row, so it cannot be calibrated out.
  - Fine for coarse control or for watching trends; not for readings that have to be
    right to a degree.
- **Moving U2 closer was looked at and rejected** (2026-11-12). The only free spot is
  mid-row beside U3, about 12 mm from the terminal pins. It means moving eight parts and
  rerouting about 16 nets, and one sensor still cannot see the gradient along a 94 mm row.
  With U7/U8 fitted, U2's position does not matter.
- Known limit: R6 and J11 dissipate about 0.5 W level with J6/J7, mid-row, where the two
  end sensors cannot see it. Worth one measurement at full heater current on the built board.
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

## Firmware notes

- **After switching the thermocouple channel, wait 1–2 ms before starting a conversion.**
  The original review said about 100 µs. Since then each line got 100 Ω and R2 became 300 Ω,
  so C1 (100 nF) now charges through about 610 Ω plus the probe's own resistance: a time
  constant of about 65 µs. Settling a 20 mV step between two channels to 1 µV takes about
  ten time constants, 0.7 ms.

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
  The module's own schematic numbers the header the other way round (pin 1 = 3V3).

**Pin order checked against the module's silkscreen** in the seller's photos (2026-11-12),
both sides:

- Front, left to right with the header along the top edge: `CON SDA SCL PSH TRA TRB BAK GND
  VCC`. The square pad is the VCC end.
- Back, same pads: `CONFIRM OLED_SDA OLED_SCL ENCODER_PUSH ENCODER_A ENCODER_B BACK GND 3V3`.
- J10 pins 1–9 carry exactly these signals in this order, so a straight 1:1 cable from
  J10 to the panel is correct. A plain pin strip is not keyed: J10 pin 1 (the left end seen
  from above, at x = 99.6) goes to CON, pin 9 to VCC / the square pad.
- The header comes loose with the module and is soldered by the user.

**As drawn, J10 only works with a cable, not with the panel plugged straight in.** The
original intent was probably a direct plug-in; that is open, see "Remaining work". Plugged
in directly, only two positions have the right pin order, and neither is usable:

- Display facing away from the hat, panel hanging below the hat's edge: the T-Relay is
  12.6 mm below and continues past that edge, and the panel needs about 32 mm.
- Pins soldered on the display side, panel standing up and facing back over the hat: the
  display is upside down and looks at the hat.

The two positions that look natural (panel standing up and facing outwards, or hanging down
and facing inwards) have the pin order reversed, VCC on J10 pin 1.

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

State: **0 unconnected, no DRC errors on copper** (clearance, shorts, holes, edge, dangling
ends all 0), schematic parity 0, ERC 0. What DRC still lists is 34 silkscreen warnings, all of one kind: the outlines of J9 and J10
cross the board edge by a few hundredths of a millimetre, because both parts sit flush with
it. The fab clips them; nothing is lost.

Placement:

- **The original parts keep their arrangement**: multiplexers U1/U3 beside the converter U2,
  with their decoupling, as in the original design. Everything except J1 sits 3.3 mm further
  left and 3.5 mm further down on the sheet than originally; J1 did not move.
- **The protection column is at x = 91.1–92.7**, 4.7 mm from the terminal pins, in four
  groups (one clamp and four series resistors per pair of terminals). Group 4 (J8/J9) is the
  mirror image of group 1 (J2/J3).
  - The series resistors are level with their terminal pins, except R19 and R24, which sit
    0.57 mm off the pin axis: with R24 level, TC6− and TC7− only fit with 0.2 mm gaps.
- **Cold-junction sensors U7 and U8 are on the back** under the column, at (91.75, 32.06) and
  (91.75, 108.30): mirror images about the middle of the terminal row (y = 70.18). C16 and C17
  sit 4.8 mm above their sensor, at x = 90.54.
- **Heater sensing:** J11 at (117.55, 82.9) with the wire entry facing right, R6 directly
  left of it, then R7, R8, C15, U6 and C14.
- **Pull-ups:** R3–R5 with C8 at the right edge beside U4; R9–R11 above their J10 pins; R12
  at J12; R13 just above J1, on the chip-select track.
- **Mounting holes** H1–H4, see "How the hat sits".

Routing:

- Four layers: front and back for signals, In1 = VCC plane, In2 = GND plane.
  - The planes' own clearance is 0.2 mm, the same as the board's. At 0.3 mm the clearance
    holes of J1's 22 pins merged into one 27 mm slot in both planes; at 0.2 mm about 0.4 mm
    of copper stays between neighbouring pins and both planes are continuous through J1.
- **Every segment is horizontal, vertical or at 45°**, and ends on a pad or via centre.
  Tracks are 0.3 mm; only the Kelvin pair and U6's own short tracks are 0.2 mm.
- **Protection groups** are terminal → series resistor → clamp on the front. The outer line of
  a group runs straight between the pads of the inner resistor to the clamp.
- **Clamp ground vias are outside the clamps**, 1.2–1.5 mm out on the three-pin side, at
  x = 90.94. The group's inner line runs 0.37 mm further left beside the via.
  - At D1 and D4 the via comes out between the pad rows of the sensor on the back; that is
    what fixes the sensors' positions. At U8 the TC7+ track passes between the rows as well.
  - U8's ground pin goes to H4's pad, because the TC7+ track separates it from D4's via.
- **Thermocouple lines to the multiplexers:** the `−` lines run on the front between the
  column and U3; the `+` lines of channels 4–7 run on the back to vias beside U1.
  - Each pair ends on two chips 11 mm apart, so its last stretch is always split. Mean
    distance between the two lines of a pair: channels 0–2 1.0–1.8 mm, channel 3 4.8 mm,
    channels 4–6 3.4–4.2 mm, channel 7 10.6 mm.
  - **TC7+ goes round the outside of the terminal row** (x = 82). Bringing it inside needs
    the lane beside J1's left pins, which `JOYSTICK_CONFIRM` uses on the back, and a
    different order of the three vias beside U1. It was left: the heaters are switched by
    relays on DC, so the loop only sees an occasional switching edge.
- **Heater path:** `24V_IN` and `24V_OUT` zones on both outer layers between J11 and R6 with
  fifteen 0.8 mm stitching vias; Kelvin pair from R6's sense pads to U6.
- **SPI, I²C, 1-Wire and the panel lines go round the heater copper on the right.**
  - On the back, five tracks (SDA, 1-Wire, MOSI, `JOYSTICK_BACK`, MISO) at 0.6 mm pitch, with
    nested corners below the heater copper, then along J1's top row into their pins.
  - On the front, four lanes: CS 123.57, SCK 124.3, `EXPANDER_INT` 125.05, SCL 125.8, at
    least 0.6 mm from the board edge.
- **At J1:**
  - One track per gap between pin columns, centred in the gap (0.27 mm each side), so front
    and back tracks do not lie on top of each other. The exception is the leftmost gap: SDA
    (front) and SCL (back) share it for 1.8 mm, because four signals end on the four
    leftmost pins and there are only two gaps beside them.
  - The strip between the heater copper and J1's top row is 2.5 mm high and carries five
    back-side and three front-side tracks.
  - SCL from U6 changes to the back just above J1; SDA stays on the front.
- **At the pull-ups R3–R5:** `EXPANDER_INT` runs down their left side into R3, and SCL passes
  between R3's pads, because there is no room to go round R3 at the board edge. Their vias
  sit between the pad rows.
- **Tightest spots (0.2–0.25 mm), all fixed by pad geometry:** SDA/SCL at U6's pins (0.5 mm
  pin pitch) and J1's left-hand corner.
- The channel order is the original one (J2 = channel 0 … J9 = channel 7).

Silkscreen, reference designators:

- All 78 are 1.0 mm high, 0.15 mm stroke (the board's minimum text height is 1.0 mm), clear
  of pads, of other parts' bodies, of each other and of via holes.
- **Protection column:** each name directly to the right of its own part, so the names
  follow the stagger of the parts (the user's choice over one aligned column). Where a via
  sits right after the pad the name starts after the via (R16, R18, R21, R22, R28). R19 is
  above its part, R26 is 0.6 mm higher and R24 0.1 mm lower than its part, all because of
  vias; R29 is 0.15 mm higher to leave room for H4's name.
- **J3–J9:** in the gap above each terminal, at x = 84. J2 has no gap above it (board edge),
  so its name stands upright to the right of it.
- **Elsewhere:** horizontal and beside the part, on the side away from its neighbour:
  pairs C12|C10 and C13|C11 outwards, C1–C3 to the right, R3–R5 to the left, JP1–JP3 in a
  row above. Only R6 and R9–R11 are upright, for lack of width.
- **Back:** U7/U8 on the side away from the terminals, C16/C17 above.

Silkscreen, functional labels (board-level text and lines, not part of any footprint, so
"update footprints from library" leaves them alone):

- **Thermocouple channel:** `TC1`…`TC7` beside the terminal's name in the gap above J3–J9;
  `TC0` upright beside J2's name.
- **Thermocouple polarity:** there is no room for a mark at each pin, so there is one
  pictogram, at (97.3–101.9, 97.0–104.6) below J1's left end: a terminal drawn the same way
  round as the real ones, upper pin `-`, lower pin `+`, headed `TC0-7`. Pin 1 (`+`) is the
  lower pin of every terminal.
- **J11:** `OUT COM` above the block (upper terminal, to the relay COMs) and `IN +24V`
  below it (lower terminal, from the supply). J11's own name moved left to make room.
- **J12:** `3V3 GND DQ` below the pads, in pad order. The words are spread wider than the
  2 mm pad pitch, and `3V3` sits left of its pad because of the via below it.
- **J10:** `CON` above pin 1 and `VCC` above pin 9, the two ends of the panel's header.

Other things to know:

- **Footprint `REF1` is the T-Relay-8 reference, as one object.** It holds both the 2D outline
  on `Dwgs.User` (board edge, relays, ESP32 module, header pins, mounting holes, from the vendor
  DXF) and the 3D model (`3d/T-Relay8-ESP32-3D.stp`, LilyGO's own file, unchanged). It has no
  pads, is board-only, is excluded from the BOM and position files, and is locked.
  - Its anchor is the T-Relay's bottom-left corner. If J1 ever moves on the hat, unlock `REF1`
    and move it by the same amount; outline and model move together.
  - The 3D model is drawn 11 mm below the hat's underside. P5 comes unpopulated and is
    soldered by the user, so the gap is set by the parts chosen: a standard 2.54 mm pin
    header (2.5 mm plastic) plus an 8.5 mm socket for J1 gives 11 mm. With other parts,
    change the model's Z offset and the spacer length to match.
- Board coordinates in this README are sheet coordinates in the PCB editor. On 2026-11-12 the
  whole drawing was moved up by 66.04 mm (26 × 2.54) so that the hat and the T-Relay outline
  fit on the A4 sheet; coordinates in commit messages before that are 66.04 mm larger in y.
- When routing, set the track width to "use netclass width". The predefined width list has
  0.2 and 0.4 mm but no 0.3 mm entry.
- Design rules: clearance 0.2 mm, default track 0.3 mm, vias
  0.6/0.3 mm, hole clearance 0.28 mm; net class `Power24V` for the `24V_*` nets. All within
  JLCPCB's standard four-layer limits.

## Remaining work

- [ ] **BOM.** Two parts are not picked yet: R6 (1 mΩ four-terminal shunt, 2512, at least 1 W)
      and L1 (600 Ω at 100 MHz ferrite bead, 0805). Then a full list with TME order codes;
      the picks made so far are in "Chosen parts".
- [ ] **J10: how the panel connects.** The intent was probably to plug the panel straight
      into J10 (to be confirmed). As drawn that does not work: the natural position, panel
      standing up at the hat's edge and facing outwards, puts VCC on J10 pin 1 (see "Panel
      module"). If direct plug-in is wanted, J10's pin order has to be mirrored on the
      board, which means rerouting its nine nets; also check then that the 65 mm wide panel
      and its knob clear J11, H3 and the hat's edges. If a cable is fine, nothing changes.
- [ ] **A second look by the original reviewer** at the finished layout.

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
