"""Basic CAD shapes: Box and Cylinder."""
from app.cad_engine.base import CADObject


class BoxShape(CADObject):
    """
    Rectangular box shape — handles tables, cabinets, rooms (basic).
    Top view: rectangle (width x length)
    Front view: rectangle (width x height)
    Side view: rectangle (length x height)
    """

    def draw_top_view(self):
        width = self.params.get("width", 100)
        length = self.params.get("length", 100)

        # Title
        self.add_title("TAMPAK ATAS", (0, length + 15))

        # Draw rectangle
        points = [
            (0, 0), (width, 0), (width, length), (0, length)
        ]
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "TOP_VIEW"})

        # Dimensions
        self.add_dimension_line((0, 0), (width, 0), offset=15)
        self.add_dimension_line((width, 0), (width, length), offset=-15)

    def draw_front_view(self):
        width = self.params.get("width", 100)
        height = self.params.get("height", 50)
        offset_y = self.VIEW_GAP

        # Title
        self.add_title("TAMPAK DEPAN", (0, offset_y + height + 15))

        # Draw rectangle
        points = [
            (0, offset_y),
            (width, offset_y),
            (width, offset_y + height),
            (0, offset_y + height)
        ]
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Dimensions
        self.add_dimension_line((0, offset_y), (width, offset_y), offset=15)
        self.add_dimension_line((0, offset_y), (0, offset_y + height), offset=15)

    def draw_side_view(self):
        length = self.params.get("length", 100)
        height = self.params.get("height", 50)
        offset_x = self.SIDE_GAP
        offset_y = self.VIEW_GAP

        # Title
        self.add_title("TAMPAK SAMPING", (offset_x, offset_y + height + 15))

        # Side view = length x height
        points = [
            (offset_x, offset_y),
            (offset_x + length, offset_y),
            (offset_x + length, offset_y + height),
            (offset_x, offset_y + height)
        ]
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Dimensions
        self.add_dimension_line((offset_x, offset_y), (offset_x + length, offset_y), offset=15)
        self.add_dimension_line((offset_x + length, offset_y), (offset_x + length, offset_y + height), offset=-15)


class CylinderShape(CADObject):
    """
    Cylindrical shape — handles pillars, round tables, pipes.
    Top view: circle
    Front view: rectangle (diameter x height)
    Side view: rectangle (diameter x height) — symmetric
    """

    def draw_top_view(self):
        diameter = self.params.get("diameter", 100)
        radius = diameter / 2

        # Title
        self.add_title("TAMPAK ATAS", (0, diameter + 15))

        # Circle centered in bounding box
        self.msp.add_circle(
            (radius, radius), radius,
            dxfattribs={"layer": "TOP_VIEW"}
        )

        # Center crosshair
        self.msp.add_line(
            (radius - radius * 0.3, radius), (radius + radius * 0.3, radius),
            dxfattribs={"layer": "CENTER_LINES"}
        )
        self.msp.add_line(
            (radius, radius - radius * 0.3), (radius, radius + radius * 0.3),
            dxfattribs={"layer": "CENTER_LINES"}
        )

    def draw_front_view(self):
        diameter = self.params.get("diameter", 100)
        height = self.params.get("height", 100)
        offset_y = self.VIEW_GAP

        # Title
        self.add_title("TAMPAK DEPAN", (0, offset_y + height + 15))

        # Front view of cylinder is a rectangle
        points = [
            (0, offset_y),
            (diameter, offset_y),
            (diameter, offset_y + height),
            (0, offset_y + height)
        ]
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Dimensions
        self.add_dimension_line((0, offset_y), (diameter, offset_y), offset=15)
        self.add_dimension_line((0, offset_y), (0, offset_y + height), offset=15)

    def draw_side_view(self):
        diameter = self.params.get("diameter", 100)
        height = self.params.get("height", 100)
        offset_x = self.SIDE_GAP
        offset_y = self.VIEW_GAP

        # Title
        self.add_title("TAMPAK SAMPING", (offset_x, offset_y + height + 15))

        # Side view of cylinder is identical to front (symmetric)
        points = [
            (offset_x, offset_y),
            (offset_x + diameter, offset_y),
            (offset_x + diameter, offset_y + height),
            (offset_x, offset_y + height)
        ]
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Center line (dashed vertical)
        center_x = offset_x + diameter / 2
        self.msp.add_line(
            (center_x, offset_y - 5), (center_x, offset_y + height + 5),
            dxfattribs={"layer": "CENTER_LINES"}
        )

        # Dimensions
        self.add_dimension_line((offset_x, offset_y), (offset_x + diameter, offset_y), offset=15)
        self.add_dimension_line((offset_x + diameter, offset_y), (offset_x + diameter, offset_y + height), offset=-15)

