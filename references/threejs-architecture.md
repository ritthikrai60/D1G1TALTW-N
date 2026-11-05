# Vite + Three.js Digital Twin Architecture

## 1. Application Structure
```text
c:\Coding Projects\Digital Twin\
├── index.html                  # Main entry page & HUD overlay structure
├── package.json                # Vite + Three.js dependencies
├── public/
│   ├── models/
│   │   └── building.glb        # 4-story 3D model generated via Blender MCP
│   └── plans/
│       ├── floor_00.png        # High-res transparent CAD vector overlay (Ground)
│       ├── floor_01.png        # High-res transparent CAD vector overlay (First)
│       ├── floor_02.png        # High-res transparent CAD vector overlay (Second)
│       └── floor_03.png        # High-res transparent CAD vector overlay (Roof)
└── src/
    ├── main.js                 # Three.js Renderer, Scene, Camera, Controls, Interaction
    ├── data/
    │   └── twinData.js         # Zone metadata, telemetry simulation, and IoT device coordinates
    └── style.css               # Glassmorphism dark UI theme & responsive layout
```

## 2. Core Interactive Capabilities

### 2.1 Floor Selector & Vertical Exploded View
- **Floor Isolation (`All`, `00`, `01`, `02`, `03`)**:
  - Filtering by floor hides upper floors so the user can inspect the interior layout and room partitions of the selected level clearly.
  - Camera smoothly animates (`lerp`) to focus on the selected floor's elevation.
- **Explode Slider (`0%` to `100%`)**:
  - Offsets each floor group (`F0`, `F1`, `F2`, `F3`) vertically along the Y-axis in Three.js (`+0m`, `+6m`, `+12m`, `+18m` at max explode) for multi-floor architectural inspection.
- **Structure Toggles**:
  - Independent switches to show/hide the **Rear-Left Steel Arch Cage** (`F3_SteelCage_*`) and **Rooftop Canopy** (`F3_Canopy_*`).

### 2.2 Dual Overlay System (CAD Plan & Zone Color Coding)
- **2D CAD Floor Plan Overlay**:
  - Planes mapped with `floor_00.png` .. `floor_03.png` placed `0.03 m` above each floor slab (`x_span = [-44.8m, +54.5m]`, `z_span = [-36.0m, +36.8m]`), aligned 1:1 with the 3D walls.
- **Zone Color-Coding Overlay**:
  - Semi-transparent colored meshes (`Zone_F*`) colored by function (Lobby = Gold, Lounge/Dining = Amber/Coral, Banquet/Commercial = Cyan/Blue, Restroom/Service = Emerald, Parking = Slate/Purple).

### 2.3 Camera & Lighting Modes
- **Camera Perspective Toggle**: Smooth switching between **3D Perspective Orbit** and **2D Top-Down Plan View**.
- **Sun / Time-of-Day Slider**: Adjusts directional sunlight azimuth/elevation and ambient hemisphere intensity from Morning (`06:00`) → Noon (`12:00`) → Sunset (`18:00`) → Night (`21:00` with warm interior & facade architectural lighting).

### 2.4 Raycasting Inspector & 3D IoT Pins
- Clicking any room/zone highlights its 3D volume and opens the **Zone Telemetry Drawer** showing real-time occupancy, area (`m²`), temperature (`°C`), audio zone status (`dB`), and active devices.
- Interactive 3D HTML/CSS2D or sprite markers for **Audio**, **HVAC**, **CCTV**, and **Parking** filterable from the top toolbar.

