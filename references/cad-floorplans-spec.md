# CAD Floor Plans Specification (4 Floors)

## 1. File Format & Embedded Vector Data
All four PDF files (`00-Ground_Floor-Clean.pdf`, `01-First_Floor-Clean.pdf`, `02-Second_Floor-Clean.pdf`, `03-Roof_Floor-Clean.pdf`) contain:
1. **PDF Content Stream (Stream 0)**: Standard PDF vector operators (`m`, `l`, `S`, `RG`) transformed by `1 0 0 -1 0 2384 cm` (top-left origin `[0..3370, 0..2384]`).
2. **VectorCraft JSON Stream (Stream 1)**: Zlib-compressed UTF-8 JSON (`{"format":"vectorcraft","version":4,"generator":"VectorCraft 0.18.0", ...}`) containing the full hierarchical CAD layer tree (`document.layers[]`).

## 2. Scale & Coordinate Transformation
- **Paper Size**: `3370 × 2384 pt` (ISO A0 Landscape at 72 points/inch = `1188.86 mm × 841.02 mm`)
- **Scale**: **1:100** (`1 cm on paper = 1.00 m in real world = 28.3464567 pt`)
- **Reference Origin `(X_0, Y_0)`**: `(1570.0, 1180.0)` pt
- **Conversion to 3D Meters (Blender X, Y)**:
  ```python
  PT_PER_METER = 28.3464567
  ORIGIN_X_PT = 1570.0
  ORIGIN_Y_PT = 1180.0

  def pdf_to_blender(x_pt, y_pt):
      x_m = (x_pt - ORIGIN_X_PT) / PT_PER_METER
      y_m = -(y_pt - ORIGIN_Y_PT) / PT_PER_METER
      return x_m, y_m
  ```

## 3. CAD Layer Mapping Across Floors

| Layer Name | Description | Target 3D Element / Usage |
| :--- | :--- | :--- |
| `A-col` | Structural columns (`0.30m` to `0.60m` square/rectangular) | 3D Extruded Columns per floor |
| `A-wall`, `WALL`, `P-2 (0.15)`, `P-4 (0.10)` | Exterior & interior partition walls (`10–20 cm` thick) | 3D Extruded Wall Meshes |
| `D&W` | Doors, windows, curtain wall mullions, and arched bays | Window/door openings & glass panels |
| `A-stair` | Straight staircases & central spiral staircase | 3D Staircase Geometry |
| `SANITARY`, `WC-OUTL`, `WC-DET1`, `WC-DET2`, `SANI-DETL` | Restroom partitions, toilets, sinks | Interior restroom walls & 2D Floor Plan Overlay |
| `P-1`, `P-1 (0.50)`, `H-1`, `SN-RL` | Slab outlines, balconies, balustrades, parking stalls | Floor Slabs, Balustrades, Parking Overlay |
| `GRID`, `DIMENSION` | Structural grid lines (`5.0m`, `8.0m` bays) & stall numbers (`1–30`) | Structural alignment & 2D Overlay |

## 4. Floor-by-Floor Spatial Breakdown

### 00 - Ground Floor (`00-Ground_Floor-Clean.pdf`)
- **West / Left Under-croft & Outdoor Parking**: 30 angled parking stalls (`#1–#12` north row, `#13–#20` middle row, `#21–#30` south row) in `X: 380..1285 pt, Y: 900..1980 pt`.
- **Rear-Left Structural Grid**: Foundation & column grid (`X: 438..1870 pt, Y: 278..945 pt`) supporting the rear steel frame.
- **Central Core**: Main ceremonial entrance stair base (`X: 1100..1265 pt, Y: 1900..2035 pt`), ground restrooms (`X: 997..1341 pt, Y: 1280..1575 pt`), and service stairs.
- **East / Right Wing**: Structural foundation column grid along the swept curve (`X: 1475..2823 pt, Y: 927..1815 pt`).

### 01 - First Floor (`01-First_Floor-Clean.pdf`)
- **West Wing Front**: Circular event/lounge room (`center ≈ (630, 1680) pt, radius ≈ 5.2 m`), adjacent private rooms, front balustrade terrace with **8 window bays**.
- **West Wing Mid**: Locker rooms, showers, changing facilities, and recreation lounge (`X: 350..1150 pt, Y: 940..1520 pt`).
- **Rear-Left Zone**: Steel structure base (`X: 315..1870 pt, Y: 254..940 pt`).
- **Central Grand Portal**: Grand entrance terrace & portico (`X: 1090..1270 pt, Y: 1870..2037 pt`), Main Reception Lobby, **Central Spiral Staircase** (`center ≈ (1345, 1485) pt`), and central restrooms.
- **East Curved Wing**: 13 structural bays sweeping from `(1475, 1815) pt` to `(2815, 1276) pt`, front arcaded terrace, diagonal front parking stalls (`#31–#37`), and far-right elevator/stair core (`X: 2460..2815 pt`).

### 02 - Second Floor (`02-Second_Floor-Clean.pdf`)
- **West Wing**: Club lounge & dining hall (`X: 298..1280 pt, Y: 900..1930 pt`) with **8 tall arched windows** along the south facade.
- **Central Portal**: Monumental double-height **Grand Arch Pediment** + glass balcony (`X: 1090..1280 pt, Y: 1875..1935 pt`), upper landing of the spiral staircase, and central restrooms (`X: 1214..1693 pt, Y: 1359..1661 pt`).
- **East Curved Wing**: Large open-span banquet / multi-purpose hall (`X: 1500..2819 pt`) fronted by **13 tall arched windows**, terminating at the far-right stair/elevator core.

### 03 - Roof Floor (`03-Roof_Floor-Clean.pdf`)
- **Rear-Left Steel Arch Cage**: Tall arched steel truss frame (`X: 315..1295 pt, Y: 900..1910 pt` / rear-left volume) rising above the left wing.
- **Central Roof**: Semicircular glass skylight dome over the spiral staircase, central rooftop restroom core (`X: 1500..1700 pt`), and main pediment roof.
- **East Curved Rooftop Terrace**: Open-air sky deck with a **Steel Pergola Canopy** (`X: 1650..2480 pt`) and the far-right enclosed rooftop pavilion & stair/elevator core (`X: 2450..2820 pt`).

