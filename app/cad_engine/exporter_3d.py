"""3D Exporter — Create 3D mesh from CAD parameters and export as STL."""
import numpy as np

try:
    import trimesh
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False


def export_3d_stl(params: dict, output_path: str) -> bool:
    """
    Create a simple 3D mesh from CAD parameters and save as STL.
    Uses trimesh.creation primitives (no triangulation engine needed).
    Returns True on success, False on failure.
    """
    if not HAS_TRIMESH:
        print("trimesh not installed, skipping 3D export")
        return False

    shape_type = params.get("shape_type", "box").lower()

    try:
        if shape_type in ("cylinder", "bundar", "bulat", "silinder"):
            mesh = _create_cylinder_mesh(params)
        elif shape_type == "chair":
            mesh = _create_chair_mesh(params)
        elif shape_type in ("room", "ruangan", "kamar"):
            mesh = _create_room_mesh(params)
        else:
            mesh = _create_box_mesh(params)

        mesh.export(output_path, file_type="stl")
        return True

    except Exception as e:
        print(f"3D Export Error: {e}")
        return False


def _create_box_mesh(params: dict) -> "trimesh.Trimesh":
    """Create a box mesh using trimesh.creation.box (no triangulation needed)."""
    width = params.get("width", 100) / 100   # cm → m
    length = params.get("length", 100) / 100
    height = params.get("height", 50) / 100

    mesh = trimesh.creation.box(extents=[width, length, height])
    # Move so bottom sits at Z=0
    mesh.apply_translation([width / 2, length / 2, height / 2])
    return mesh


def _create_cylinder_mesh(params: dict) -> "trimesh.Trimesh":
    """Create a cylinder mesh using trimesh.creation.cylinder."""
    diameter = params.get("diameter", 100) / 100  # cm → m
    height = params.get("height", 100) / 100
    radius = diameter / 2

    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    # Move so bottom sits at Z=0
    mesh.apply_translation([0, 0, height / 2])
    return mesh


def _create_chair_mesh(params: dict) -> "trimesh.Trimesh":
    """Create a simplified chair mesh (seat + 4 legs) from box primitives."""
    width = params.get("width", 40) / 100
    length = params.get("length", 40) / 100
    height = params.get("height", 45) / 100
    seat_t = 0.03  # 3cm seat thickness
    leg_w = 0.03   # 3cm leg width

    parts = []

    # Seat plate
    seat = trimesh.creation.box(extents=[width, length, seat_t])
    seat.apply_translation([width / 2, length / 2, height + seat_t / 2])
    parts.append(seat)

    # 4 Legs at corners
    margin = 0.03
    leg_positions = [
        (margin + leg_w / 2, margin + leg_w / 2),
        (width - margin - leg_w / 2, margin + leg_w / 2),
        (width - margin - leg_w / 2, length - margin - leg_w / 2),
        (margin + leg_w / 2, length - margin - leg_w / 2),
    ]
    for lx, ly in leg_positions:
        leg = trimesh.creation.box(extents=[leg_w, leg_w, height])
        leg.apply_translation([lx, ly, height / 2])
        parts.append(leg)

    # Backrest
    backrest_h = 0.20
    backrest = trimesh.creation.box(extents=[width, seat_t, backrest_h])
    backrest.apply_translation([width / 2, length, height + seat_t + backrest_h / 2])
    parts.append(backrest)

    # Combine all parts
    combined = trimesh.util.concatenate(parts)
    return combined


def _create_room_mesh(params: dict) -> "trimesh.Trimesh":
    """
    Create a room mesh with hollow walls, floor, and door/window openings.
    Walls are built as thin slabs, split into segments around openings.
    """
    width = params.get("width", 400) / 100   # cm → m
    length = params.get("length", 500) / 100
    height = params.get("height", 300) / 100
    wall_t = 0.15  # 15cm wall thickness

    parts = []

    # ── Floor slab ──
    floor = trimesh.creation.box(extents=[width, length, wall_t])
    floor.apply_translation([width / 2, length / 2, -wall_t / 2])
    parts.append(floor)

    # ── Collect openings per wall ──
    wall_openings: dict[str, list] = {
        "south": [], "north": [], "west": [], "east": []
    }

    for door in (params.get("doors") or []):
        if isinstance(door, dict):
            wall = door.get("wall", "south")
            door_w = door.get("width", 80) / 100
            door_h = min(2.0, height * 0.7)  # max 2m or 70% of wall
            if wall in wall_openings:
                wall_openings[wall].append({
                    "type": "door", "w": door_w, "h": door_h, "sill": 0
                })

    for window in (params.get("windows") or []):
        if isinstance(window, dict):
            wall = window.get("wall", "north")
            win_w = window.get("width", 100) / 100
            win_h = min(1.0, height * 0.3)
            sill_h = height * 0.35
            if wall in wall_openings:
                wall_openings[wall].append({
                    "type": "window", "w": win_w, "h": win_h, "sill": sill_h
                })

    # ── Build each wall ──
    # South wall: along X axis at Y=0
    parts.extend(_build_wall_segments(
        wall_len=width, wall_h=height, wall_t=wall_t,
        openings=wall_openings["south"],
        origin=(0, 0, 0), axis="x"
    ))

    # North wall: along X axis at Y=length
    parts.extend(_build_wall_segments(
        wall_len=width, wall_h=height, wall_t=wall_t,
        openings=wall_openings["north"],
        origin=(0, length - wall_t, 0), axis="x"
    ))

    # West wall: along Y axis at X=0
    parts.extend(_build_wall_segments(
        wall_len=length, wall_h=height, wall_t=wall_t,
        openings=wall_openings["west"],
        origin=(0, 0, 0), axis="y"
    ))

    # East wall: along Y axis at X=width
    parts.extend(_build_wall_segments(
        wall_len=length, wall_h=height, wall_t=wall_t,
        openings=wall_openings["east"],
        origin=(width - wall_t, 0, 0), axis="y"
    ))

    combined = trimesh.util.concatenate(parts)
    return combined


def _build_wall_segments(
    wall_len: float, wall_h: float, wall_t: float,
    openings: list, origin: tuple, axis: str
) -> list:
    """
    Build a wall as box segments, leaving gaps for openings.
    axis='x' means wall runs along X; axis='y' means along Y.
    Returns a list of trimesh box meshes.
    """
    ox, oy, oz = origin
    segments = []

    if not openings:
        # Solid wall, no openings
        if axis == "x":
            wall = trimesh.creation.box(extents=[wall_len, wall_t, wall_h])
            wall.apply_translation([ox + wall_len / 2, oy + wall_t / 2, wall_h / 2])
        else:
            wall = trimesh.creation.box(extents=[wall_t, wall_len, wall_h])
            wall.apply_translation([ox + wall_t / 2, oy + wall_len / 2, wall_h / 2])
        return [wall]

    # Center each opening along the wall
    for opening in openings:
        op_w = opening["w"]
        op_h = opening["h"]
        sill = opening["sill"]  # bottom of opening (0 for doors)
        op_center = wall_len / 2  # centered on wall
        op_left = op_center - op_w / 2
        op_right = op_center + op_w / 2
        op_top = sill + op_h

        # Left segment (full height)
        if op_left > 0.01:
            seg_w = op_left
            if axis == "x":
                seg = trimesh.creation.box(extents=[seg_w, wall_t, wall_h])
                seg.apply_translation([ox + seg_w / 2, oy + wall_t / 2, wall_h / 2])
            else:
                seg = trimesh.creation.box(extents=[wall_t, seg_w, wall_h])
                seg.apply_translation([ox + wall_t / 2, oy + seg_w / 2, wall_h / 2])
            segments.append(seg)

        # Right segment (full height)
        if op_right < wall_len - 0.01:
            seg_w = wall_len - op_right
            if axis == "x":
                seg = trimesh.creation.box(extents=[seg_w, wall_t, wall_h])
                seg.apply_translation([ox + op_right + seg_w / 2, oy + wall_t / 2, wall_h / 2])
            else:
                seg = trimesh.creation.box(extents=[wall_t, seg_w, wall_h])
                seg.apply_translation([ox + wall_t / 2, oy + op_right + seg_w / 2, wall_h / 2])
            segments.append(seg)

        # Above opening (lintel)
        if op_top < wall_h - 0.01:
            lintel_h = wall_h - op_top
            if axis == "x":
                seg = trimesh.creation.box(extents=[op_w, wall_t, lintel_h])
                seg.apply_translation([ox + op_center, oy + wall_t / 2, op_top + lintel_h / 2])
            else:
                seg = trimesh.creation.box(extents=[wall_t, op_w, lintel_h])
                seg.apply_translation([ox + wall_t / 2, oy + op_center, op_top + lintel_h / 2])
            segments.append(seg)

        # Below opening (sill wall — for windows)
        if sill > 0.01:
            if axis == "x":
                seg = trimesh.creation.box(extents=[op_w, wall_t, sill])
                seg.apply_translation([ox + op_center, oy + wall_t / 2, sill / 2])
            else:
                seg = trimesh.creation.box(extents=[wall_t, op_w, sill])
                seg.apply_translation([ox + wall_t / 2, oy + op_center, sill / 2])
            segments.append(seg)

    return segments
