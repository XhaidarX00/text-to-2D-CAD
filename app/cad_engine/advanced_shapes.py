"""Advanced CAD shapes: Chair and Room with architectural symbols."""
import math
from app.cad_engine.base import CADObject


class ChairShape(CADObject):
    """
    Chair with seat + legs + optional backrest.
    Top view: rectangle (seat) + 4 dots (legs)
    Front view: backrest + seat plate + 4 legs
    """

    def draw_top_view(self):
        width = self.params.get("width", 40)
        length = self.params.get("length", 40)
        legs = self.params.get("legs", 4)
        leg_radius = 2  # visual radius for leg dots

        # Title
        self.add_title("TAMPAK ATAS", (0, length + 20))

        # Seat (rectangle)
        seat_points = [
            (0, 0), (width, 0), (width, length), (0, length)
        ]
        self.msp.add_lwpolyline(seat_points, close=True, dxfattribs={"layer": "TOP_VIEW"})

        # Leg positions (corners, inset by margin)
        margin = 3
        leg_positions = []
        if legs >= 4:
            leg_positions = [
                (margin, margin),
                (width - margin, margin),
                (width - margin, length - margin),
                (margin, length - margin),
            ]
        elif legs == 3:
            leg_positions = [
                (width / 2, margin),
                (width - margin, length - margin),
                (margin, length - margin),
            ]

        for pos in leg_positions[:legs]:
            self.msp.add_circle(pos, leg_radius, dxfattribs={"layer": "TOP_VIEW"})

        # Backrest indicator (thick line at the back)
        self.msp.add_lwpolyline(
            [(0, length), (width, length)],
            dxfattribs={"layer": "TOP_VIEW", "const_width": 2}
        )

        # Dimensions
        self.add_dimension_line((0, 0), (width, 0), offset=15)
        self.add_dimension_line((width, 0), (width, length), offset=-15)

    def draw_front_view(self):
        width = self.params.get("width", 40)
        height = self.params.get("height", 45)
        seat_thickness = 3
        backrest_height = 20
        leg_width = 3
        offset_y = self.VIEW_GAP

        # Title
        total_h = height + backrest_height
        self.add_title("TAMPAK DEPAN", (0, offset_y + total_h + 15))

        seat_top = offset_y + height
        backrest_top = seat_top + backrest_height

        # Backrest
        self.msp.add_lwpolyline([
            (0, seat_top), (width, seat_top),
            (width, backrest_top), (0, backrest_top)
        ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Seat plate
        self.msp.add_lwpolyline([
            (0, seat_top - seat_thickness), (width, seat_top - seat_thickness),
            (width, seat_top), (0, seat_top)
        ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Left front leg
        lx = leg_width
        self.msp.add_lwpolyline([
            (lx, offset_y), (lx + leg_width, offset_y),
            (lx + leg_width, seat_top - seat_thickness), (lx, seat_top - seat_thickness)
        ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Right front leg
        rx = width - leg_width * 2
        self.msp.add_lwpolyline([
            (rx, offset_y), (rx + leg_width, offset_y),
            (rx + leg_width, seat_top - seat_thickness), (rx, seat_top - seat_thickness)
        ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

    def draw_side_view(self):
        length = self.params.get("length", 40)
        height = self.params.get("height", 45)
        seat_thickness = 3
        backrest_height = 20
        leg_width = 3
        offset_x = self.SIDE_GAP
        offset_y = self.VIEW_GAP

        total_h = height + backrest_height
        # Title
        self.add_title("TAMPAK SAMPING", (offset_x, offset_y + total_h + 15))

        seat_top = offset_y + height
        backrest_top = seat_top + backrest_height

        # Backrest (thin rectangle at the back edge)
        self.msp.add_lwpolyline([
            (offset_x + length - leg_width, seat_top),
            (offset_x + length, seat_top),
            (offset_x + length, backrest_top),
            (offset_x + length - leg_width, backrest_top)
        ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Seat plate
        self.msp.add_lwpolyline([
            (offset_x, seat_top - seat_thickness),
            (offset_x + length, seat_top - seat_thickness),
            (offset_x + length, seat_top),
            (offset_x, seat_top)
        ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Front leg (left in side view)
        self.msp.add_lwpolyline([
            (offset_x + leg_width, offset_y),
            (offset_x + leg_width * 2, offset_y),
            (offset_x + leg_width * 2, seat_top - seat_thickness),
            (offset_x + leg_width, seat_top - seat_thickness)
        ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Back leg (right in side view)
        rx = length - leg_width * 2
        self.msp.add_lwpolyline([
            (offset_x + rx, offset_y),
            (offset_x + rx + leg_width, offset_y),
            (offset_x + rx + leg_width, seat_top - seat_thickness),
            (offset_x + rx, seat_top - seat_thickness)
        ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Dimensions
        self.add_dimension_line(
            (offset_x, offset_y), (offset_x, seat_top), offset=15
        )
        self.add_dimension_line(
            (offset_x, offset_y), (offset_x + length, offset_y), offset=15
        )


class RoomShape(CADObject):
    """
    Architectural room/floor plan with doors and windows.
    Top view: rectangle + door arcs + window dashed lines
    Front view: wall elevation with door/window openings
    Side view: side wall elevation with openings
    """

    def draw_top_view(self):
        width = self.params.get("width", 400)   # in cm
        length = self.params.get("length", 500)  # in cm

        # Title
        self.add_title("DENAH RUANGAN (TAMPAK ATAS)", (0, length + 30))

        # Room walls
        wall_points = [
            (0, 0), (width, 0), (width, length), (0, length)
        ]
        self.msp.add_lwpolyline(wall_points, close=True, dxfattribs={"layer": "TOP_VIEW"})

        # Draw doors
        doors = self.params.get("doors") or []
        for door in doors:
            if isinstance(door, dict):
                wall = door.get("wall", "south")
                door_w = door.get("width", 80)
                self._draw_door_symbol(wall, door_w, width, length)

        # Draw windows
        windows = self.params.get("windows") or []
        for window in windows:
            if isinstance(window, dict):
                wall = window.get("wall", "north")
                win_w = window.get("width", 100)
                self._draw_window_symbol(wall, win_w, width, length)

        # Dimensions
        self.add_dimension_line((0, 0), (width, 0), offset=25)
        self.add_dimension_line((width, 0), (width, length), offset=-25)

    def _draw_door_symbol(self, wall: str, door_width: float, room_w: float, room_l: float):
        """Draw a door symbol (arc + line) on the specified wall."""
        if wall == "south":
            # Door centered on south wall
            cx = room_w / 2 - door_width / 2
            # Gap in wall
            self.msp.add_line(
                (cx, 0), (cx + door_width, 0),
                dxfattribs={"layer": "TOP_VIEW", "color": 0}  # background to "erase"
            )
            # Door leaf (line)
            self.msp.add_line(
                (cx, 0), (cx, door_width),
                dxfattribs={"layer": "TOP_VIEW"}
            )
            # Door arc (90 degree swing)
            self.msp.add_arc(
                center=(cx, 0), radius=door_width,
                start_angle=0, end_angle=90,
                dxfattribs={"layer": "TOP_VIEW"}
            )
        elif wall == "north":
            cx = room_w / 2 - door_width / 2
            self.msp.add_line(
                (cx, room_l), (cx, room_l - door_width),
                dxfattribs={"layer": "TOP_VIEW"}
            )
            self.msp.add_arc(
                center=(cx, room_l), radius=door_width,
                start_angle=270, end_angle=360,
                dxfattribs={"layer": "TOP_VIEW"}
            )
        elif wall == "west":
            cy = room_l / 2 - door_width / 2
            self.msp.add_line(
                (0, cy), (door_width, cy),
                dxfattribs={"layer": "TOP_VIEW"}
            )
            self.msp.add_arc(
                center=(0, cy), radius=door_width,
                start_angle=0, end_angle=90,
                dxfattribs={"layer": "TOP_VIEW"}
            )
        elif wall == "east":
            cy = room_l / 2 - door_width / 2
            self.msp.add_line(
                (room_w, cy), (room_w - door_width, cy),
                dxfattribs={"layer": "TOP_VIEW"}
            )
            self.msp.add_arc(
                center=(room_w, cy), radius=door_width,
                start_angle=90, end_angle=180,
                dxfattribs={"layer": "TOP_VIEW"}
            )

    def _draw_window_symbol(self, wall: str, win_width: float, room_w: float, room_l: float):
        """Draw window symbol (3 parallel lines) on the specified wall."""
        wall_thickness = 3

        if wall == "north":
            cx = room_w / 2 - win_width / 2
            for offset in [-wall_thickness, 0, wall_thickness]:
                self.msp.add_line(
                    (cx, room_l + offset), (cx + win_width, room_l + offset),
                    dxfattribs={"layer": "TOP_VIEW"}
                )
        elif wall == "south":
            cx = room_w / 2 - win_width / 2
            for offset in [-wall_thickness, 0, wall_thickness]:
                self.msp.add_line(
                    (cx, offset), (cx + win_width, offset),
                    dxfattribs={"layer": "TOP_VIEW"}
                )
        elif wall == "east":
            cy = room_l / 2 - win_width / 2
            for offset in [-wall_thickness, 0, wall_thickness]:
                self.msp.add_line(
                    (room_w + offset, cy), (room_w + offset, cy + win_width),
                    dxfattribs={"layer": "TOP_VIEW"}
                )
        elif wall == "west":
            cy = room_l / 2 - win_width / 2
            for offset in [-wall_thickness, 0, wall_thickness]:
                self.msp.add_line(
                    (offset, cy), (offset, cy + win_width),
                    dxfattribs={"layer": "TOP_VIEW"}
                )

    def draw_front_view(self):
        width = self.params.get("width", 400)
        height = self.params.get("height", 300)
        offset_y = self.VIEW_GAP - 100  # Extra gap for room

        # Title
        self.add_title("TAMPAK DEPAN", (0, offset_y + height + 15))

        # Wall outline
        wall_points = [
            (0, offset_y), (width, offset_y),
            (width, offset_y + height), (0, offset_y + height)
        ]
        self.msp.add_lwpolyline(wall_points, close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Door opening (south wall, front view)
        doors = self.params.get("doors") or []
        for door in doors:
            if isinstance(door, dict):
                door_w = door.get("width", 80)
                door_h = min(200, height * 0.7)
                cx = width / 2 - door_w / 2
                # Door opening rectangle
                self.msp.add_lwpolyline([
                    (cx, offset_y), (cx + door_w, offset_y),
                    (cx + door_w, offset_y + door_h), (cx, offset_y + door_h)
                ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Window opening
        windows = self.params.get("windows") or []
        for window in windows:
            if isinstance(window, dict):
                win_w = window.get("width", 100)
                win_h = min(100, height * 0.3)
                sill_h = height * 0.35  # window sill height
                cx = width / 2 - win_w / 2
                self.msp.add_lwpolyline([
                    (cx, offset_y + sill_h),
                    (cx + win_w, offset_y + sill_h),
                    (cx + win_w, offset_y + sill_h + win_h),
                    (cx, offset_y + sill_h + win_h)
                ], close=True, dxfattribs={"layer": "FRONT_VIEW"})

        # Dimensions
        self.add_dimension_line((0, offset_y), (width, offset_y), offset=25)
        self.add_dimension_line((0, offset_y), (0, offset_y + height), offset=25)

    def draw_side_view(self):
        length = self.params.get("length", 500)
        height = self.params.get("height", 300)
        offset_x = self.SIDE_GAP + 200  # Extra offset for large rooms
        offset_y = self.VIEW_GAP - 100

        # Title
        self.add_title("TAMPAK SAMPING", (offset_x, offset_y + height + 15))

        # Side wall outline
        wall_points = [
            (offset_x, offset_y),
            (offset_x + length, offset_y),
            (offset_x + length, offset_y + height),
            (offset_x, offset_y + height)
        ]
        self.msp.add_lwpolyline(wall_points, close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Check for doors/windows on east or west walls (visible from side)
        doors = self.params.get("doors") or []
        for door in doors:
            if isinstance(door, dict):
                wall = door.get("wall", "south")
                if wall in ("east", "west"):
                    door_w = door.get("width", 80)
                    door_h = min(200, height * 0.7)
                    cx = offset_x + length / 2 - door_w / 2
                    self.msp.add_lwpolyline([
                        (cx, offset_y), (cx + door_w, offset_y),
                        (cx + door_w, offset_y + door_h), (cx, offset_y + door_h)
                    ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        windows = self.params.get("windows") or []
        for window in windows:
            if isinstance(window, dict):
                wall = window.get("wall", "north")
                if wall in ("east", "west"):
                    win_w = window.get("width", 100)
                    win_h = min(100, height * 0.3)
                    sill_h = height * 0.35
                    cx = offset_x + length / 2 - win_w / 2
                    self.msp.add_lwpolyline([
                        (cx, offset_y + sill_h),
                        (cx + win_w, offset_y + sill_h),
                        (cx + win_w, offset_y + sill_h + win_h),
                        (cx, offset_y + sill_h + win_h)
                    ], close=True, dxfattribs={"layer": "SIDE_VIEW"})

        # Dimensions
        self.add_dimension_line(
            (offset_x, offset_y), (offset_x + length, offset_y), offset=25
        )
        self.add_dimension_line(
            (offset_x + length, offset_y),
            (offset_x + length, offset_y + height), offset=-25
        )
