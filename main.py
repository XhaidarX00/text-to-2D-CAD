"""AI CAD Architect — FastAPI Entry Point + API Routes."""
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid

from app.core.config import settings
from app.services.reasoning_service import ReasoningService
from app.services.audio_service import AudioService
from app.services.vision_service import VisionService
from app.cad_engine.factory import CADFactory
from app.cad_engine.svg_exporter import dxf_to_svg
from app.cad_engine.exporter_3d import export_3d_stl
from app.services.history_service import create_entry as history_create, get_all_entries as history_list, get_entry as history_get, update_entry as history_update, delete_entry as history_delete, clear_all as history_clear

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
reasoning_service = ReasoningService()
audio_service = AudioService()
vision_service = VisionService()

# In-memory cache for params (keyed by DXF filename)
_params_cache: dict[str, dict] = {}


@app.get("/")
async def index(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate_cad(
    text_prompt: str = Form(None),
    audio_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
):
    """
    Multi-modal CAD generation endpoint.
    Accepts text, audio, and/or image input.
    Returns CAD parameters + DXF download URL + SVG preview.
    """
    final_prompt = ""

    # 1. Process Audio → Text (Whisper-large-v3-turbo)
    if audio_file:
        audio_content = await audio_file.read()
        if audio_content:
            result = await audio_service.transcribe_audio(audio_content, audio_file.filename)
            if result["text"]:
                final_prompt += f" {result['text']}"

    # 2. Process Image → Text (Llama 4 Scout Vision)
    if image_file:
        image_content = await image_file.read()
        if image_content:
            description = vision_service.analyze_sketch(
                image_content,
                mime_type=image_file.content_type or "image/jpeg"
            )
            if description:
                final_prompt += f" {description}"

    # 3. Process Text (direct append)
    if text_prompt:
        final_prompt += f" {text_prompt}"

    if not final_prompt.strip():
        return JSONResponse(
            {"status": "error", "message": "Input kosong. Berikan teks, suara, atau gambar."},
            status_code=400
        )

    # 4. Reasoning → JSON Parameters (Llama 3.3 streaming)
    params = reasoning_service.extract_cad_parameters(final_prompt.strip())

    # 5. CAD Generation (Factory Pattern)
    try:
        cad_object = CADFactory.create_cad_object(params)
        cad_object.draw_top_view()
        cad_object.draw_front_view()
        cad_object.draw_side_view()

        filename = f"{uuid.uuid4()}.dxf"
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        cad_object.save(filepath)

        # Cache params for 3D export
        _params_cache[filename] = params

        # 6. Generate SVG Preview
        svg_preview = ""
        try:
            svg_preview = dxf_to_svg(filepath)
        except Exception as e:
            print(f"SVG Preview Error: {e}")

        # 7. Save to history
        history_entry = history_create(
            prompt=final_prompt.strip(),
            params=params,
            dxf_filename=filename,
            svg_preview=svg_preview,
        )

        return {
            "status": "success",
            "data": params,
            "download_url": f"/download/{filename}",
            "svg_preview": svg_preview,
            "original_prompt": final_prompt.strip(),
            "history_id": history_entry["id"],
        }

    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"CAD generation failed: {str(e)}"},
            status_code=500
        )


@app.get("/download/{filename}")
async def download_dxf(filename: str):
    """Download generated DXF file."""
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return JSONResponse({"status": "error", "message": "File not found"}, status_code=404)
    return FileResponse(filepath, filename=filename, media_type="application/dxf")


@app.post("/api/export-3d/{filename}")
async def export_3d(filename: str):
    """Export a generated DXF to 3D STL format."""
    dxf_path = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(dxf_path):
        return JSONResponse({"status": "error", "message": "DXF file not found"}, status_code=404)

    stl_filename = filename.replace(".dxf", ".stl")
    stl_path = os.path.join(settings.OUTPUT_DIR, stl_filename)

    # Retrieve cached params from generation
    params = _params_cache.get(filename, {"shape_type": "box", "width": 100, "length": 100, "height": 50})
    success = export_3d_stl(params, stl_path)

    if success:
        # Update history with STL filename
        history_update(
            _params_cache.get(f"{filename}_history_id", ""),
            {"stl_filename": stl_filename}
        )
        return {
            "status": "success",
            "download_url": f"/download-3d/{stl_filename}"
        }
    else:
        return JSONResponse(
            {"status": "error", "message": "3D export failed. trimesh/shapely may not be installed."},
            status_code=500
        )


@app.get("/download-3d/{filename}")
async def download_stl(filename: str):
    """Download generated STL file."""
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return JSONResponse({"status": "error", "message": "File not found"}, status_code=404)
    return FileResponse(filepath, filename=filename, media_type="application/sla")


# ==================== History CRUD API ====================

@app.get("/api/history")
async def list_history():
    """Get all CAD generation history entries."""
    entries = history_list()
    return {"status": "success", "data": entries, "count": len(entries)}


@app.get("/api/history/{entry_id}")
async def get_history_entry(entry_id: str):
    """Get a single history entry by ID."""
    entry = history_get(entry_id)
    if entry is None:
        return JSONResponse({"status": "error", "message": "Entry not found"}, status_code=404)
    return {"status": "success", "data": entry}


@app.put("/api/history/{entry_id}")
async def update_history_entry(entry_id: str, request: Request):
    """Update a history entry (prompt or params)."""
    body = await request.json()
    updated = history_update(entry_id, body)
    if updated is None:
        return JSONResponse({"status": "error", "message": "Entry not found"}, status_code=404)
    return {"status": "success", "data": updated}


@app.delete("/api/history/{entry_id}")
async def delete_history_entry(entry_id: str):
    """Delete a single history entry."""
    deleted = history_delete(entry_id)
    if not deleted:
        return JSONResponse({"status": "error", "message": "Entry not found"}, status_code=404)
    return {"status": "success", "message": "Entry deleted"}


@app.delete("/api/history")
async def clear_history():
    """Delete all history entries."""
    count = history_clear()
    return {"status": "success", "message": f"{count} entries deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
