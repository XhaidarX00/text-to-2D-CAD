"""Custom exception classes for structured error handling."""


class CADError(Exception):
    """Base exception for CAD engine errors."""
    pass


class ShapeNotFoundError(CADError):
    """Raised when the requested shape type is not registered."""
    def __init__(self, shape_type: str):
        self.shape_type = shape_type
        super().__init__(f"Shape type '{shape_type}' is not registered in the factory.")


class CADGenerationError(CADError):
    """Raised when DXF/SVG generation fails."""
    pass


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class LLMError(AIServiceError):
    """Raised when LLM reasoning fails."""
    pass


class VisionError(AIServiceError):
    """Raised when vision analysis fails."""
    pass


class TranscriptionError(AIServiceError):
    """Raised when audio transcription fails."""
    pass


class EmptyInputError(Exception):
    """Raised when no input is provided."""
    pass
