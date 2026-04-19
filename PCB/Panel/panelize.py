#!/usr/bin/env python3
"""
Multi-board KiKit panelization script
======================================
Creates a panel with:
  - 5x Board 1 (23mm x 31mm) in a row
  - 1x Board 2 (14mm x 35mm) on the far left
  - 1x Board 3 (125.25mm x 18mm) across the bottom
  - Mousebite tabs for depanelization
  - Top/bottom rails with tooling holes

Panel layout (approximate):
  ┌─────────────────────────────────────────────────┐  ← top rail
  │  ┌──────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │
  │  │Board2│ │Brd1a│ │Brd1b│ │Brd1c│ │Brd1d│ │Brd1e│ │
  │  │14x35 │ │23x31│ │23x31│ │23x31│ │23x31│ │23x31│ │
  │  │      │ │     │ │     │ │     │ │     │ │     │ │
  │  └──────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ │
  │  ┌───────────────────────────────────────────────┐  │
  │  │            Board 3  (125.25 x 18)             │  │
  │  └───────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘  ← bottom rail

Tested with KiCAD 7/8 and KiKit >= 1.4
Usage: Open KiCAD command prompt, then run:
       python panelize_multi.py

Author: Adapted from maxanier's multi-board example gist
License: MIT (derived from KiKit)
"""

from kikit import panelize_ui_impl as ki
from kikit.units import mm
from kikit.panelize import Panel, BasicGridPosition, Origin
from pcbnewTransition.pcbnew import LoadBoard, VECTOR2I
from pcbnewTransition import pcbnew
from itertools import chain

# =============================================================================
# USER CONFIG — Edit these paths and parameters
# =============================================================================

# Board file paths (adjust to your actual project paths)
BOARD1_PATH = "../Falconia-Beacon/Falconia-Beacon.kicad_pcb"  # 23mm x 31mm — 5 copies
BOARD2_PATH = "../Programmer/programmer.kicad_pcb"  # 14mm x 35mm — 1 copy (far left)
BOARD3_PATH = "../Charger/charger.kicad_pcb"  # 125.25mm x 18mm — 1 copy (bottom)

OUTPUT_PATH = "./Panel2.kicad_pcb"

# Board dimensions (for reference / manual offset calculation)
B1_W, B1_H = 23.0, 31.0    # Board 1
B2_W, B2_H = 14.0, 35.0    # Board 2
B3_W, B3_H = 125.25, 18.0  # Board 3

# Spacing between boards (routed slot gap — 2mm is typical for mousebites)
BOARD_GAP = 2.0  # mm

# Rail / frame config
RAIL_WIDTH = 5.0   # mm — width of top and bottom rails
RAIL_VSPACE = 3.0  # mm — gap between boards and rail edge

# Tab config for mousebites
TAB_WIDTH = 3.0    # mm — width of each breakaway tab
TAB_SPACING = 15.0 # mm — distance between tab centers along an edge

# Mousebite drill parameters (these work well for JLCPCB)
MBITE_DRILL = 0.5    # mm — drill hole diameter
MBITE_SPACING = 0.8  # mm — center-to-center hole spacing along the cut line
MBITE_OFFSET = 0.0   # mm — offset from board edge (0 = centered on edge)

# Tooling holes
TOOLING_HOFFSET = 5.0  # mm from panel edge
TOOLING_VOFFSET = 3.0  # mm from panel edge
TOOLING_SIZE = 1.152   # mm — JLCPCB standard tooling hole diameter

# =============================================================================
# LAYOUT GEOMETRY CALCULATION
# =============================================================================

# All positions are relative to an origin point.
# We place Board 2 on the far left, then 5x Board 1 to its right.
# Board 3 goes below, spanning the full width.

# Starting X offset (some margin from absolute origin)
ORIGIN_X = 30.0
ORIGIN_Y = 30.0

# --- Top row: Board2 (left) + 5x Board1 (right) ---
# Board 2 position (top-left corner reference)
b2_x = ORIGIN_X
b2_y = ORIGIN_Y

# Board 1 positions start after Board 2 + gap
b1_start_x = b2_x + B2_W + BOARD_GAP
b1_y = ORIGIN_Y  # Same Y as Board 2 (top-aligned)

# Note: Board 2 is 35mm tall, Board 1 is 31mm tall.
# You may want to vertically center Board 1 relative to Board 2:
b1_y_centered = b2_y + (B2_H - B1_H) / 2.0  # Centers Board1 with Board2

# Positions for each of the 5x Board 1 copies
b1_positions = []
for i in range(5):
    x = b1_start_x + i * (B1_W + BOARD_GAP)
    b1_positions.append((x, b1_y_centered))

# --- Bottom row: Board 3 ---
# Board 3 goes below the top row, with a gap
top_row_bottom = b2_y + B2_H  # Bottom edge of Board 2 (tallest in top row)
b3_x = ORIGIN_X
b3_y = top_row_bottom + BOARD_GAP

# Verify Board 3 fits under everything
# Total top row width: Board2 + gap + 5*(Board1 + gap) - last gap
top_row_width = B2_W + BOARD_GAP + 5 * B1_W + 4 * BOARD_GAP
# Board 3 width: 125.25mm
# Top row width: 14 + 2 + 5*23 + 4*2 = 14 + 2 + 115 + 8 = 139mm
# Board 3 is 125.25mm, so it fits. You could center it:
b3_x_centered = ORIGIN_X + (top_row_width - B3_W) / 2.0

print(f"Top row width: {top_row_width:.2f} mm")
print(f"Board 3 width: {B3_W:.2f} mm")
print(f"Board 3 centered X offset: {b3_x_centered:.2f} mm")
print(f"Panel approx size: {top_row_width:.1f} x {top_row_bottom - ORIGIN_Y + BOARD_GAP + B3_H:.1f} mm (boards only)")

# =============================================================================
# KIKIT PANEL CONSTRUCTION
# =============================================================================

# KiKit preset config — controls tabs, cuts, framing, tooling
#framing = {
#    "type": "railstb",              # Rails on top and bottom only
#    "vspace": f"{RAIL_VSPACE}mm",   # Vertical space between boards and rail
#    "width": f"{RAIL_WIDTH}mm",     # Rail width
#}

framing = {
    "type": "frame",
    "hspace": f"{RAIL_VSPACE}mm",
    "vspace": f"{RAIL_VSPACE}mm",
    "width": f"{RAIL_WIDTH}mm",
}

cuts = {
    "type": "mousebites",
    "drill": f"{MBITE_DRILL}mm",
    "spacing": f"{MBITE_SPACING}mm",
    "offset": f"{MBITE_OFFSET}mm",
    "prolong": "0.5mm",            # Extend cuts slightly past board edge
}

tabs = {
    "type": "spacing",
    "width": f"{TAB_WIDTH}mm",
    "spacing": f"{TAB_SPACING}mm",
}

tooling = {
    "type": "3hole",
    "hoffset": f"{TOOLING_HOFFSET}mm",
    "voffset": f"{TOOLING_VOFFSET}mm",
    "size": f"{TOOLING_SIZE}mm",
}

# Merge with KiKit defaults
preset = ki.obtainPreset([], tabs=tabs, cuts=cuts, framing=framing, tooling=tooling)

# --- Create the panel ---
board1 = LoadBoard(BOARD1_PATH)
board2 = LoadBoard(BOARD2_PATH)
board3 = LoadBoard(BOARD3_PATH)

panel = Panel(OUTPUT_PATH)
panel.inheritDesignSettings(board1)
panel.inheritProperties(board1)
panel.inheritTitleBlock(board1)

# Source areas (auto-detect from board outline)
sourceArea1 = ki.readSourceArea(preset["source"], board1)
sourceArea2 = ki.readSourceArea(preset["source"], board2)
sourceArea3 = ki.readSourceArea(preset["source"], board3)

# Net/ref renamer to avoid collisions between different boards
netRenamer = lambda x, y: f"Board_{x}-{y}"
refRenamer = lambda x, y: f"Board_{x}-{y}"

substrateCount = len(panel.substrates)

# --- Place Board 2 (far left) ---
print("Placing Board 2 (far left)...")
area_b2 = panel.appendBoard(
    BOARD2_PATH,
    destination=VECTOR2I(int(b2_x * mm), int(b2_y * mm)),
    origin=Origin.TopLeft,
    sourceArea=sourceArea2,
    netRenamer=netRenamer,
    refRenamer=refRenamer,
)

# --- Place 5x Board 1 ---
for i, (bx, by) in enumerate(b1_positions):
    print(f"Placing Board 1 copy {i+1}/5 at ({bx:.1f}, {by:.1f})...")
    area_b1 = panel.appendBoard(
        BOARD1_PATH,
        destination=VECTOR2I(int(bx * mm), int(by * mm)),
        origin=Origin.TopLeft,
        sourceArea=sourceArea1,
        netRenamer=netRenamer,
        refRenamer=refRenamer,
        inheritDrc=False,
    )

# --- Place Board 3 (bottom, centered) ---
print(f"Placing Board 3 (bottom) at ({b3_x_centered:.1f}, {b3_y:.1f})...")
area_b3 = panel.appendBoard(
    BOARD3_PATH,
    destination=VECTOR2I(int(b3_x_centered * mm), int(b3_y * mm)),
    origin=Origin.TopLeft,
    sourceArea=sourceArea3,
    netRenamer=netRenamer,
    refRenamer=refRenamer,
    inheritDrc=False,
)

# Collect all newly placed substrates
substrates = panel.substrates[substrateCount:]
print(f"Total substrates placed: {len(substrates)}")

# --- Build partition lines (needed for tab generation) ---
framingSubstrates = ki.dummyFramingSubstrate(substrates, preset)
panel.buildPartitionLineFromBB(framingSubstrates)
backboneCuts = ki.buildBackBone(preset["layout"], panel, substrates, preset)

# --- Build tabs, frame, tooling ---
tabCuts = ki.buildTabs(preset, panel, substrates, framingSubstrates)
frameCuts = ki.buildFraming(preset, panel)

ki.buildTooling(preset, panel)
ki.buildFiducials(preset, panel)

for textSection in ["text", "text2", "text3", "text4"]:
    ki.buildText(preset[textSection], panel)

ki.buildPostprocessing(preset["post"], panel)

# --- Clean up silkscreen text: strip "Board_N-" prefix from visible references ---
import re
for footprint in panel.board.GetFootprints():
    ref_field = footprint.Reference()
    ref_text = ref_field.GetText()
    # Strip the "Board_N-" prefix for display only
    cleaned = re.sub(r'^Board_\d+-', '', ref_text)
    ref_field.SetText(cleaned)

# --- Apply mousebite cuts ---
ki.makeTabCuts(preset, panel, tabCuts)
ki.makeOtherCuts(preset, panel, chain(backboneCuts, frameCuts))

# --- Copper fill and final steps ---
ki.buildCopperfill(preset["copperfill"], panel)
ki.setStackup(preset["source"], panel)
ki.setPageSize(preset["page"], panel, board1)
ki.positionPanel(preset["page"], panel)
ki.runUserScript(preset["post"], panel)
ki.buildDebugAnnotation(preset["debug"], panel)

# --- Save ---
panel.save(
    reconstructArcs=preset["post"]["reconstructarcs"],
    refillAllZones=preset["post"]["refillzones"],
)

print(f"\nPanel saved to: {OUTPUT_PATH}")
print("Open in KiCAD PCB editor to verify before generating gerbers.")
