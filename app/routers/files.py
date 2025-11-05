from fastapi import APIRouter, File, UploadFile


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", summary="Upload a file", responses={200: {"description": "Upload ok"}})
async def upload(file: UploadFile = File(..., description="Any file")):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

