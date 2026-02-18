"""SVG Exporter — Convert DXF entities to SVG for browser preview."""
import ezdxf
import math


def dxf_to_svg(filepath: str, width: int = 800, height: int = 600) -> str:
    """
    Read a DXF file and convert its entities to an SVG string
    suitable for embedding in HTML. Auto-scales to fit viewport.
    """
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    # Collect all coordinate points to determine bounds
    all_points = []
    entities_data = []

    for entity in msp:
        if entity.dxftype() == "LWPOLYLINE":
            points = list(entity.get_points(format="xy"))
            all_points.extend(points)
            is_closed = entity.close
            entities_data.append(("polyline", points, is_closed, entity.dxf.layer))

        elif entity.dxftype() == "LINE":
            start = (entity.dxf.start.x, entity.dxf.start.y)
            end = (entity.dxf.end.x, entity.dxf.end.y)
            all_points.extend([start, end])
            entities_data.append(("line", [start, end], False, entity.dxf.layer))

        elif entity.dxftype() == "CIRCLE":
            cx, cy = entity.dxf.center.x, entity.dxf.center.y
            r = entity.dxf.radius
            all_points.extend([(cx - r, cy - r), (cx + r, cy + r)])
            entities_data.append(("circle", (cx, cy, r), False, entity.dxf.layer))

        elif entity.dxftype() == "ARC":
            cx, cy = entity.dxf.center.x, entity.dxf.center.y
            r = entity.dxf.radius
            all_points.extend([(cx - r, cy - r), (cx + r, cy + r)])
            start_angle = math.radians(entity.dxf.start_angle)
            end_angle = math.radians(entity.dxf.end_angle)
            entities_data.append(("arc", (cx, cy, r, start_angle, end_angle), False, entity.dxf.layer))

        elif entity.dxftype() == "TEXT":
            ix, iy = entity.dxf.insert.x, entity.dxf.insert.y
            all_points.append((ix, iy))
            entities_data.append(("text", (ix, iy, entity.dxf.text, entity.dxf.height), False, entity.dxf.layer))

    if not all_points:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="10" y="50" fill="#999">No preview</text></svg>'

    # Calculate bounds
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    data_w = max_x - min_x or 1
    data_h = max_y - min_y or 1
    padding = max(data_w, data_h) * 0.1

    vb_x = min_x - padding
    vb_y = min_y - padding
    vb_w = data_w + padding * 2
    vb_h = data_h + padding * 2

    # Layer colors
    layer_colors = {
        "TOP_VIEW": "#e2e8f0",
        "FRONT_VIEW": "#93c5fd",
        "SIDE_VIEW": "#22d3ee",
        "DIMENSIONS": "#f87171",
        "ANNOTATIONS": "#4ade80",
        "CENTER_LINES": "#fbbf24",
    }
    default_color = "#cbd5e1"

    # Build SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}" ',
        f'width="{width}" height="{height}" style="background:#0f172a;border-radius:12px;">',
    ]

    # Flip Y axis (DXF Y goes up, SVG Y goes down)
    svg_parts.append(f'<g transform="translate(0, {min_y + max_y}) scale(1, -1)">')

    for etype, data, closed, layer in entities_data:
        color = layer_colors.get(layer, default_color)
        stroke_w = 0.5 if layer == "DIMENSIONS" else 1

        if etype == "polyline":
            pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in data)
            tag = "polygon" if closed else "polyline"
            fill = "none"
            svg_parts.append(
                f'<{tag} points="{pts_str}" fill="{fill}" stroke="{color}" stroke-width="{stroke_w}"/>'
            )

        elif etype == "line":
            (x1, y1), (x2, y2) = data
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="{stroke_w}"/>'
            )

        elif etype == "circle":
            cx, cy, r = data
            svg_parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                f'fill="none" stroke="{color}" stroke-width="{stroke_w}"/>'
            )

        elif etype == "arc":
            cx, cy, r, sa, ea = data
            x1 = cx + r * math.cos(sa)
            y1 = cy + r * math.sin(sa)
            x2 = cx + r * math.cos(ea)
            y2 = cy + r * math.sin(ea)
            sweep = 1 if ea > sa else 0
            large = 1 if abs(ea - sa) > math.pi else 0
            svg_parts.append(
                f'<path d="M {x1:.1f} {y1:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {x2:.1f} {y2:.1f}" '
                f'fill="none" stroke="{color}" stroke-width="{stroke_w}"/>'
            )

        elif etype == "text":
            tx, ty, text_content, text_h = data
            font_size = max(text_h * 0.8, 3)
            # Text needs inverse flip to be readable
            svg_parts.append(
                f'<g transform="translate({tx:.1f},{ty:.1f}) scale(1,-1)">'
                f'<text font-size="{font_size:.1f}" fill="{color}" font-family="monospace">{text_content}</text>'
                f'</g>'
            )

    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    return "\n".join(svg_parts)
