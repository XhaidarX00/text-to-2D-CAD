"""Abstract Base Class for all CAD objects."""
from abc import ABC, abstractmethod
import ezdxf


class CADObject(ABC):
    """
    Base class for all drawable CAD shapes.
    Each shape must implement draw_top_view(), draw_front_view(), and draw_side_view().
    """

    # Vertical offset between top view and front view
    VIEW_GAP = -150
    # Horizontal offset for side view (placed to the right of front view)
    SIDE_GAP = 250

    def __init__(self, params: dict):
        self.params = params
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._setup_layers()

    def _setup_layers(self):
        """Create standard CAD layers for organization."""
        self.doc.layers.add("TOP_VIEW", color=7)       # White
        self.doc.layers.add("FRONT_VIEW", color=5)      # Blue
        self.doc.layers.add("SIDE_VIEW", color=4)        # Cyan
        self.doc.layers.add("DIMENSIONS", color=1)       # Red
        self.doc.layers.add("ANNOTATIONS", color=3)      # Green
        self.doc.layers.add("CENTER_LINES", color=2)     # Yellow

    @abstractmethod
    def draw_top_view(self):
        """Draw the top view (plan view) of the object."""
        pass

    @abstractmethod
    def draw_front_view(self):
        """Draw the front view (elevation) of the object, offset below top view."""
        pass

    @abstractmethod
    def draw_side_view(self):
        """Draw the side view (right elevation), offset to the right."""
        pass

    def add_title(self, text: str, position: tuple, height: float = 5):
        """Add a text annotation."""
        self.msp.add_text(
            text,
            dxfattribs={
                "insert": position,
                "height": height,
                "layer": "ANNOTATIONS",
            }
        )

    def add_dimension_line(self, start: tuple, end: tuple, offset: float = 10):
        """Add a simple dimension indicator using lines and text."""
        import math
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)

        # Perpendicular direction for offset
        if abs(dx) > abs(dy):
            # Horizontal dimension
            y_off = start[1] - offset
            self.msp.add_line(
                (start[0], y_off), (end[0], y_off),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            # Extension lines
            self.msp.add_line(
                (start[0], start[1]), (start[0], y_off),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            self.msp.add_line(
                (end[0], end[1]), (end[0], y_off),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            # Text
            mid_x = (start[0] + end[0]) / 2
            self.msp.add_text(
                f"{length:.0f}",
                dxfattribs={
                    "insert": (mid_x, y_off - 5),
                    "height": 3,
                    "layer": "DIMENSIONS",
                }
            )
        else:
            # Vertical dimension
            x_off = start[0] - offset
            self.msp.add_line(
                (x_off, start[1]), (x_off, end[1]),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            self.msp.add_line(
                (start[0], start[1]), (x_off, start[1]),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            self.msp.add_line(
                (end[0], end[1]), (x_off, end[1]),
                dxfattribs={"layer": "DIMENSIONS"}
            )
            mid_y = (start[1] + end[1]) / 2
            self.msp.add_text(
                f"{length:.0f}",
                dxfattribs={
                    "insert": (x_off - 8, mid_y),
                    "height": 3,
                    "layer": "DIMENSIONS",
                }
            )

    def save(self, filepath: str):
        """Save the DXF document to disk."""
        self.doc.saveas(filepath)

    def get_params_summary(self) -> dict:
        """Return a clean summary of parameters for API response."""
        summary = {}
        skip_keys = {"description"}
        for key, value in self.params.items():
            if key not in skip_keys and value is not None:
                summary[key] = value
        return summary
