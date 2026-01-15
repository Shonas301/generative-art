# Comprehensive Algorithm & Math Reference

## Table of Contents
1. [Perlin Noise Wind Field](#1-perlin-noise-wind-field)
2. [Obstacle Deflection (Potential Field)](#2-obstacle-deflection-potential-field)
3. [Point Distribution (Jittered Grid)](#3-point-distribution-jittered-grid)
4. [Gaussian Clustering](#4-gaussian-clustering-around-obstacles)
5. [Blob Detection (Flood Fill)](#5-blob-detection-from-bump-maps)
6. [Obstacle Merging (Weighted Centroid)](#6-obstacle-merging)
7. [Coordinate Transformations](#7-coordinate-transformations)
8. [Animation Math](#8-animation-math)

---

## 1. Perlin Noise Wind Field

**Location:** `src/generative_art/flow_field.py:95-122`

### Algorithm
Uses 3D Perlin noise where the third dimension is time, creating smoothly evolving wind patterns.

### Math

```
noise_value = pnoise3(x · scale, y · scale, t · time_scale)
```

Where:
- `scale` = 0.003 (default) — controls spatial frequency
- `time_scale` = 0.01 — controls animation speed

**Convert noise to direction:**
```
θ = noise_value · 4π
```

The noise function returns values in [-1, 1], so multiplying by 4π maps to [-4π, 4π] radians, allowing full rotational coverage with smooth transitions.

**Convert angle to velocity vector:**
```
vx = cos(θ) · strength
vy = sin(θ) · strength
```

### Fractal Brownian Motion (fBm)
The `pnoise3` function uses octaves for detail:

```
noise = Σᵢ (persistenceⁱ · pnoise(2ⁱ · x, 2ⁱ · y, 2ⁱ · t))
```

With default `octaves=3` and `persistence=0.5`:
- Octave 0: weight 1.0, frequency 1x
- Octave 1: weight 0.5, frequency 2x
- Octave 2: weight 0.25, frequency 4x

---

## 2. Obstacle Deflection (Potential Field)

**Location:** `src/generative_art/flow_field.py:124-181`

### Algorithm
Tangential deflection creates smooth flow around obstacles, similar to fluid dynamics around cylinders.

### Math

**Given:**
- Point position: `(x, y)`
- Obstacle center: `(ox, oy)`
- Obstacle radius: `r`
- Influence radius: `R` (default: 2.5r)

**Step 1: Vector to point**
```
dx = x - ox
dy = y - oy
d = √(dx² + dy²)
```

**Step 2: Handle zones**

| Zone | Condition | Behavior |
|------|-----------|----------|
| Inside | d < r | Strong outward push: `(dx/d · 2s, dy/d · 2s)` |
| Influence | r ≤ d ≤ R | Tangential deflection |
| Outside | d > R | No effect: `(0, 0)` |

**Step 3: Tangential deflection (for influence zone)**

Normalized radial vector:
```
n̂ = (dx/d, dy/d)
```

Tangent vector (90° rotation):
```
t̂ = (-ny, nx) = (-dy/d, dx/d)
```

**Step 4: Quadratic falloff**
```
                    d - r
falloff = (1 - ─────────)²
                  R - r
```

This gives:
- falloff = 1.0 at obstacle edge (d = r)
- falloff = 0.0 at influence edge (d = R)
- Quadratic curve provides smooth transition

**Step 5: Final deflection**
```
deflection = t̂ · falloff · strength · flow_strength
```

### Visualization

```
        Influence zone
       ╭─────────────╮
      ╱               ╲
     ╱   ╭─────────╮   ╲
    │   ╱  Obstacle ╲   │
    │  │   (push    │  │
    │   ╲  outward) ╱   │
     ╲   ╰─────────╯   ╱
      ╲    ←──────    ╱   ← Tangential flow
       ╰─────────────╯
```

---

## 3. Point Distribution (Jittered Grid)

**Location:** `src/generative_art/flow_field.py:397-442`

### Algorithm
Stratified sampling using a jittered grid ensures even coverage while avoiding regularity artifacts.

### Math

**Step 1: Calculate grid dimensions**
```
aspect = width / height
rows = √(n / aspect)
cols = n / rows
```

This ensures approximately square cells regardless of canvas aspect ratio.

**Step 2: Cell dimensions**
```
cell_width = width / cols
cell_height = height / rows
```

**Step 3: For each cell (row, col), calculate center:**
```
cx = (col + 0.5) · cell_width
cy = (row + 0.5) · cell_height
```

**Step 4: Add random jitter (±40% of cell size):**
```
jx = uniform(-0.4, 0.4) · cell_width
jy = uniform(-0.4, 0.4) · cell_height

px = clamp(cx + jx, 0, width-1)
py = clamp(cy + jy, 0, height-1)
```

### Why 40% jitter?
- **< 40%**: Points still look grid-like
- **= 50%**: Points can overlap cell boundaries (clustering)
- **40%**: Sweet spot — random appearance, guaranteed coverage

---

## 4. Gaussian Clustering Around Obstacles

**Location:** `src/generative_art/flow_field.py:444-477`

### Algorithm
Phase 2 adds extra points around obstacle edges using polar coordinates with Gaussian radial distribution.

### Math

**Extra points per obstacle:**
```
extra_ratio = multiplier - 1.0
points_per_obstacle = (n · extra_ratio) / (num_obstacles · 3)
```

The division by 3 is a tuning factor to prevent over-clustering.

**For each extra point:**

**Step 1: Random angle (uniform around circle)**
```
θ = uniform(0, 2π)
```

**Step 2: Radial distance (Gaussian distribution)**
```
target = r + edge_offset
spread = (outer - inner) / 2
d = normal(target, spread)
d = clamp(d, inner, outer)
```

Where:
- `inner = r + edge_offset · 0.5`
- `outer = r + influence · 0.4`

**Step 3: Convert polar to Cartesian:**
```
px = obstacle_x + cos(θ) · d
py = obstacle_y + sin(θ) · d
```

### Gaussian Distribution

The normal distribution `N(μ, σ)` has PDF:
```
           1              (x - μ)²
f(x) = ─────────── · exp(- ────────)
       σ · √(2π)            2σ²
```

This creates a bell curve of point density centered at `edge_offset` distance from the obstacle.

---

## 5. Blob Detection from Bump Maps

**Location:** `src/maya_grass/terrain.py:236-345`

### Algorithm
Flood-fill based connected component analysis to find contiguous regions above threshold.

### Math

**Step 1: Binary thresholding**
```
mask[y,x] = 1 if bump_map[y,x] > threshold else 0
```

**Step 2: Flood fill (4-connected)**

Starting from unvisited pixel where `mask=1`, recursively visit neighbors:
```
neighbors(y,x) = {(y-1,x), (y+1,x), (y,x-1), (y,x+1)}
```

**Step 3: Centroid calculation**

For blob with pixel coordinates `{(x₁,y₁), (x₂,y₂), ...}`:
```
cx = (Σ xᵢ) / n
cy = (Σ yᵢ) / n
```

**Step 4: Radius estimation**

Assuming circular blob, area = πr²:
```
area = n pixels
r_pixels = √(area / π)
```

**Step 5: Convert to world coordinates**
```
u = cx / (width - 1)
v = 1 - cy / (height - 1)    ← flip Y (image coords are top-down)

world_x = bounds.min_x + u · bounds.width
world_z = bounds.min_z + v · bounds.depth
world_r = r_pixels / width · bounds.width
```

---

## 6. Obstacle Merging

**Location:** `src/maya_grass/terrain.py:347-410`

### Algorithm
Weighted centroid merging combines nearby obstacles using radius² as weight (larger obstacles have more influence).

### Math

**Step 1: Find obstacles within merge distance**
```
d = √((x₁-x₂)² + (z₁-z₂)²)
merge if d < merge_distance
```

**Step 2: Weighted centroid**
```
W = Σ rᵢ²

cx = (Σ xᵢ · rᵢ²) / W
cz = (Σ zᵢ · rᵢ²) / W
```

Using r² as weight means area-proportional influence.

**Step 3: Combined radius**

The new radius encompasses all original obstacles:
```
r_new = max(dist(cx,cz → obstacleᵢ) + rᵢ)
```

---

## 7. Coordinate Transformations

### Maya World ↔ Flow Field 2D

Maya uses (X, Y, Z) where Y is up.
Flow field uses (x, y) for the ground plane.

```
Flow Field          Maya World
    x        →         X
    y        →         Z
    -        →         Y (height)
```

**Location:** `src/maya_grass/generator.py:350-369`

### World ↔ Clusterer Space

The PointClusterer operates in normalized space [0, width] × [0, height].

**World to Clusterer:**
```
clusterer_x = world_x - bounds.min_x
clusterer_y = world_z - bounds.min_z
```

**Clusterer to World:**
```
world_x = clusterer_x + bounds.min_x
world_z = clusterer_y + bounds.min_z
```

### World ↔ UV (Bump Map)

**World to UV:**
```
u = (x - min_x) / width
v = (z - min_z) / depth
```

**UV to Pixel:**
```
px = u · (img_width - 1)
py = (1 - v) · (img_height - 1)    ← flip for image coords
```

---

## 8. Animation Math

**Location:** `src/maya_grass/generator.py:648-679`

### Wind Vector at Frame

```python
angle = sin(x · noise_scale + frame · time_scale) 
      · cos(z · noise_scale + frame · time_scale) · π

vx = cos(angle) · strength
vz = sin(angle) · strength

# add obstacle deflection
for each obstacle:
    vx += deflection_x
    vz += deflection_z
```

### Grass Rotation

**Wind direction (Y-axis rotation):**
```
rotation_y = atan2(vz, vx)
```

**Lean angle (tilt toward wind):**
```
magnitude = √(vx² + vz²)
lean = min(30°, magnitude · 10)
```

### Final MASH Rotation Tuple
```
(rx, ry, rz) = (0, base_rotation + wind_angle · 0.3, lean_angle)
```

The `0.3` factor blends wind influence with the base random rotation, preventing all grass from pointing the same direction.

---

## Summary Table

| Algorithm | Complexity | Key Parameters |
|-----------|------------|----------------|
| Perlin Noise | O(octaves) per sample | scale, time_scale, octaves |
| Obstacle Deflection | O(obstacles) per point | influence_radius, strength |
| Jittered Grid | O(n) | jitter factor (0.4) |
| Gaussian Clustering | O(obstacles · extra_points) | edge_offset, multiplier |
| Flood Fill | O(pixels) | threshold |
| Obstacle Merge | O(n²) | merge_distance |

---

## Visual Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     GRASS GENERATION PIPELINE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Bump Map    │────▶│  Flood Fill  │────▶│  Obstacles   │ │
│  │  (grayscale) │     │  Detection   │     │  (x,z,r)     │ │
│  └──────────────┘     └──────────────┘     └──────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Jittered    │────▶│   Gaussian   │────▶│  Point       │ │
│  │  Grid        │     │   Clustering │     │  Positions   │ │
│  │  (phase 1)   │     │   (phase 2)  │     │  (x,z)       │ │
│  └──────────────┘     └──────────────┘     └──────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Perlin      │────▶│  Tangential  │────▶│  Wind        │ │
│  │  Noise       │     │  Deflection  │     │  Vectors     │ │
│  │  (x,z,frame) │     │  (obstacles) │     │  (vx,vz)     │ │
│  └──────────────┘     └──────────────┘     └──────┬───────┘ │
│                                                   │         │
│                                                   ▼         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MASH Python Node: rotation = (0, atan2(vz,vx), lean) │  │
│  │  Evaluated every frame for animation                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
