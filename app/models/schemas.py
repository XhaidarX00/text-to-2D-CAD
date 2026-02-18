"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional


class DoorSpec(BaseModel):
    wall: str = Field(default="south", description="Wall position: north|south|east|west")
    width: float = Field(default=80, description="Door width in cm")


class WindowSpec(BaseModel):
    wall: str = Field(default="north", description="Wall position: north|south|east|west")
    width: float = Field(default=100, description="Window width in cm")


class CADParameters(BaseModel):
    """Parameters extracted by LLM from user prompt."""
    shape_type: str = Field(default="box", description="Shape type: box|cylinder|chair|room|l_shape")
    width: float = Field(default=100, description="Width in cm")
    length: float = Field(default=100, description="Length in cm")
    height: float = Field(default=50, description="Height in cm")
    diameter: Optional[float] = Field(default=None, description="Diameter in cm (for cylinder)")
    legs: Optional[int] = Field(default=None, description="Number of legs (for chair)")
    doors: Optional[list[DoorSpec]] = Field(default=None, description="Door specifications")
    windows: Optional[list[WindowSpec]] = Field(default=None, description="Window specifications")
    description: str = Field(default="", description="Brief description of the object")


class GenerateResponse(BaseModel):
    """Response from /api/generate endpoint."""
    status: str
    data: dict
    download_url: str
    svg_preview: Optional[str] = None
    original_prompt: str


class ErrorResponse(BaseModel):
    """Error response."""
    status: str = "error"
    message: str
