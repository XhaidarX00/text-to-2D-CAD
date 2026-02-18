"""Shape Factory with registry pattern."""
from app.cad_engine.base import CADObject
from app.cad_engine.shapes import BoxShape, CylinderShape
from app.cad_engine.advanced_shapes import ChairShape, RoomShape
from app.core.exceptions import ShapeNotFoundError


class CADFactory:
    """
    Factory for creating CAD objects based on shape_type.
    Uses a registry dict so new shapes can be added without modifying logic.
    """

    _registry: dict[str, type[CADObject]] = {
        "box": BoxShape,
        "cylinder": CylinderShape,
        "chair": ChairShape,
        "room": RoomShape,
    }

    # Aliases for Indonesian / natural language inputs
    _aliases: dict[str, str] = {
        "kotak": "box",
        "persegi": "box",
        "meja": "box",
        "lemari": "box",
        "kabinet": "box",
        "silinder": "cylinder",
        "bundar": "cylinder",
        "bulat": "cylinder",
        "tiang": "cylinder",
        "pipa": "cylinder",
        "kursi": "chair",
        "bangku": "chair",
        "ruangan": "room",
        "ruang": "room",
        "kamar": "room",
        "l_shape": "box",        # Fallback L-shape to box for now
    }

    @classmethod
    def create_cad_object(cls, params: dict) -> CADObject:
        """
        Create a CADObject instance based on params['shape_type'].
        Supports aliases for natural language shape names.
        """
        shape_type = params.get("shape_type", "box").lower().strip()

        # Check alias first
        if shape_type in cls._aliases:
            shape_type = cls._aliases[shape_type]

        # Check registry
        if shape_type not in cls._registry:
            print(f"Warning: Unknown shape '{shape_type}', falling back to BoxShape.")
            shape_type = "box"

        shape_class = cls._registry[shape_type]
        return shape_class(params)

    @classmethod
    def register_shape(cls, name: str, shape_class: type[CADObject]):
        """Register a new shape type dynamically."""
        cls._registry[name.lower()] = shape_class

    @classmethod
    def get_available_shapes(cls) -> list[str]:
        """Return list of registered shape type names."""
        return list(cls._registry.keys())
