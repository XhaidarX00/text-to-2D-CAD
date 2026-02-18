"""Unit tests for CAD Engine — shapes, factory, and export."""
import os
import tempfile
import pytest
import ezdxf

from app.cad_engine.shapes import BoxShape, CylinderShape
from app.cad_engine.advanced_shapes import ChairShape, RoomShape
from app.cad_engine.factory import CADFactory
from app.cad_engine.svg_exporter import dxf_to_svg


class TestBoxShape:
    """Tests for BoxShape."""

    def test_creates_valid_dxf(self):
        params = {"width": 120, "length": 60, "height": 75}
        shape = BoxShape(params)
        shape.draw_top_view()
        shape.draw_front_view()

        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            shape.save(f.name)
            # Verify file can be read back
            doc = ezdxf.readfile(f.name)
            msp = doc.modelspace()
            entities = list(msp)
            assert len(entities) > 0, "DXF should contain entities"
            os.unlink(f.name)

    def test_has_correct_layers(self):
        params = {"width": 100, "length": 100, "height": 50}
        shape = BoxShape(params)
        shape.draw_top_view()
        shape.draw_front_view()

        layers = [layer.dxf.name for layer in shape.doc.layers]
        assert "TOP_VIEW" in layers
        assert "FRONT_VIEW" in layers
        assert "DIMENSIONS" in layers

    def test_uses_provided_dimensions(self):
        params = {"width": 200, "length": 150, "height": 80}
        shape = BoxShape(params)
        shape.draw_top_view()

        # Check polyline points
        polylines = [e for e in shape.msp if e.dxftype() == "LWPOLYLINE"]
        assert len(polylines) >= 1, "Should have at least 1 polyline for top view"


class TestCylinderShape:
    """Tests for CylinderShape."""

    def test_creates_circle_top_view(self):
        params = {"diameter": 60, "height": 100}
        shape = CylinderShape(params)
        shape.draw_top_view()

        circles = [e for e in shape.msp if e.dxftype() == "CIRCLE"]
        assert len(circles) >= 1, "Top view should have a circle"
        assert circles[0].dxf.radius == 30, "Radius should be diameter/2"

    def test_creates_valid_dxf(self):
        params = {"diameter": 50, "height": 80}
        shape = CylinderShape(params)
        shape.draw_top_view()
        shape.draw_front_view()

        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            shape.save(f.name)
            doc = ezdxf.readfile(f.name)
            assert doc is not None
            os.unlink(f.name)


class TestChairShape:
    """Tests for ChairShape."""

    def test_has_leg_circles(self):
        params = {"width": 40, "length": 40, "height": 45, "legs": 4}
        shape = ChairShape(params)
        shape.draw_top_view()

        circles = [e for e in shape.msp if e.dxftype() == "CIRCLE"]
        assert len(circles) == 4, "Chair should have 4 leg circles in top view"

    def test_front_view_has_polylines(self):
        params = {"width": 40, "length": 40, "height": 45, "legs": 4}
        shape = ChairShape(params)
        shape.draw_front_view()

        polylines = [e for e in shape.msp if e.dxftype() == "LWPOLYLINE"]
        assert len(polylines) >= 3, "Front view should have backrest + seat + legs"


class TestRoomShape:
    """Tests for RoomShape."""

    def test_basic_room(self):
        params = {"width": 400, "length": 500, "height": 300}
        shape = RoomShape(params)
        shape.draw_top_view()
        shape.draw_front_view()

        polylines = [e for e in shape.msp if e.dxftype() == "LWPOLYLINE"]
        assert len(polylines) >= 2, "Should have wall outlines in both views"

    def test_room_with_door(self):
        params = {
            "width": 400, "length": 500, "height": 300,
            "doors": [{"wall": "south", "width": 80}]
        }
        shape = RoomShape(params)
        shape.draw_top_view()

        arcs = [e for e in shape.msp if e.dxftype() == "ARC"]
        assert len(arcs) >= 1, "Door should produce an arc symbol"

    def test_room_with_window(self):
        params = {
            "width": 400, "length": 500, "height": 300,
            "windows": [{"wall": "north", "width": 100}]
        }
        shape = RoomShape(params)
        shape.draw_top_view()

        lines = [e for e in shape.msp if e.dxftype() == "LINE"]
        assert len(lines) >= 3, "Window should produce parallel lines"


class TestCADFactory:
    """Tests for CADFactory."""

    def test_creates_box(self):
        obj = CADFactory.create_cad_object({"shape_type": "box"})
        assert isinstance(obj, BoxShape)

    def test_creates_cylinder(self):
        obj = CADFactory.create_cad_object({"shape_type": "cylinder"})
        assert isinstance(obj, CylinderShape)

    def test_creates_chair(self):
        obj = CADFactory.create_cad_object({"shape_type": "chair"})
        assert isinstance(obj, ChairShape)

    def test_creates_room(self):
        obj = CADFactory.create_cad_object({"shape_type": "room"})
        assert isinstance(obj, RoomShape)

    def test_alias_kursi(self):
        obj = CADFactory.create_cad_object({"shape_type": "kursi"})
        assert isinstance(obj, ChairShape)

    def test_alias_ruangan(self):
        obj = CADFactory.create_cad_object({"shape_type": "ruangan"})
        assert isinstance(obj, RoomShape)

    def test_unknown_falls_back_to_box(self):
        obj = CADFactory.create_cad_object({"shape_type": "spaceship"})
        assert isinstance(obj, BoxShape)

    def test_available_shapes(self):
        shapes = CADFactory.get_available_shapes()
        assert "box" in shapes
        assert "cylinder" in shapes
        assert "chair" in shapes
        assert "room" in shapes


class TestSVGExporter:
    """Tests for DXF to SVG conversion."""

    def test_converts_box_to_svg(self):
        params = {"width": 100, "length": 100, "height": 50}
        shape = BoxShape(params)
        shape.draw_top_view()
        shape.draw_front_view()

        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            shape.save(f.name)
            svg = dxf_to_svg(f.name)
            assert svg.startswith("<svg"), "Should produce valid SVG"
            assert "viewBox" in svg, "Should have viewBox"
            os.unlink(f.name)
