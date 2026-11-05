# Blender MCP 3D Modeling Pipeline

## 1. Blender MCP Connection
- **Blender Version**: Blender 5.2.3 LTS (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`)
- **Extension**: `bl_ext.user_default.mcp` (Official Blender Lab MCP v1.0.3)
- **Socket Bridge**: `localhost:9876` (TCP null-terminated JSON protocol)
- **Headless / Background Server Launch**:
  ```powershell
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --online-mode --command blender_mcp
  ```

## 2. Scene Collection & Naming Hierarchy
All 3D objects in `building_digital_twin.blend` and exported `public/models/building.glb` follow a strict prefix naming convention so Three.js can filter, slice, and explode floors deterministically:

| Floor Level | Collection Name | Object Prefix | Base Z (m) | Top Z (m) |
| :--- | :--- | :--- | :--- | :--- |
| **00 - Ground** | `Floor_00_Ground` | `F0_` | `0.00` | `3.50` |
| **01 - First** | `Floor_01_First` | `F1_` | `3.50` | `7.50` |
| **02 - Second** | `Floor_02_Second` | `F2_` | `7.50` | `11.50` |
| **03 - Roof** | `Floor_03_Roof` | `F3_` | `11.50` | `19.50` |

### Sub-Element Naming Convention
- `F{0..3}_Slab_*` — Floor slabs & terraces
- `F{0..3}_Wall_Ext_*` — Exterior Neo-Classical facade walls (terracotta/peach-ochre)
- `F{0..3}_Wall_Int_*` — Interior partition walls extracted from CAD layers (`A-wall`, `WALL`)
- `F{0..3}_Col_*` — Structural columns extracted from `A-col`
- `F{0..3}_Glass_*` — Window panes, arched glazing, and skylights
- `F{0..3}_Stair_*` — Straight stairs, front ceremonial stairs, and central spiral staircase
- `F{0..3}_Railing_*` — Classical balustrades and balcony railings
- `F3_SteelCage_*` — Rear-left tall arched steel truss structure (toggleable in UI)
- `F3_Canopy_*` — Right-wing rooftop steel pergola/canopy (toggleable in UI)
- `Zone_F{0..3}_{ZoneID}` — Interactive semantic zone volumes for raycasting & color-coding

## 3. Architectural Material Palette (PBR)
- `Mat_Terracotta_Main`: Base color `#D99B72`, Roughness `0.65` (Main Neo-Classical facade stucco)
- `Mat_Terracotta_Trim`: Base color `#E6B38E`, Roughness `0.55` (Pilasters, arch moldings, cornices, balustrades)
- `Mat_Interior_Wall`: Base color `#F4EFEA`, Roughness `0.75` (Clean warm-white interior partitions)
- `Mat_Floor_Slab`: Base color `#E2DCD5`, Roughness `0.50` (Interior stone/tile floor slab)
- `Mat_Parking_Asphalt`: Base color `#3A3D42`, Roughness `0.85` (Ground parking surface)
- `Mat_Glass_Facade`: Base color `#1C3144`, Metallic `0.2`, Roughness `0.1`, Alpha `0.45` (Windows & arched glazing)
- `Mat_Steel_Dark`: Base color `#26292E`, Metallic `0.8`, Roughness `0.35` (Rooftop canopy & rear steel arch cage)

## 4. Export Specification
- Save native file: `c:\Coding Projects\Digital Twin\building_digital_twin.blend`
- Export glTF 2.0 binary: `c:\Coding Projects\Digital Twin\public\models\building.glb` (`export_apply=True`, `export_yup=True`, `export_materials='EXPORT'`)

