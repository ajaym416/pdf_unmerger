from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.worker.tasks import process_pdf
from app.core.config import settings
import uuid, os
import boto3
from loguru import logger

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    filename = f"{task_id}_{file.filename}"
    file_path = f"/tmp/uploads/{filename}"
    os.makedirs("/tmp/uploads", exist_ok=True)
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.success(f"[{task_id}] File saved to {file_path}")

        task = process_pdf.apply_async(args=[file_path, task_id], task_id=task_id)
        logger.info(f"[{task_id}] Celery task dispatched: {task.id}")
        return {"task_id": task.id}

    except Exception as e:
        logger.error(f"[{task_id}] Failed to handle upload: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@router.get("/status/{task_id}")
def get_status(task_id: str):
    task = process_pdf.AsyncResult(task_id)
    return {"status": task.status}


@router.get("/results/{task_id}")
def list_files_for_task(task_id: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )

    try:
        response = s3.list_objects_v2(
            Bucket=settings.s3_bucket,
            Prefix=f"{task_id}/"
        )
        contents = response.get("Contents", [])
        if not contents:
            logger.warning(f"[{task_id}] No files found in S3")
            return {"status": "empty", "files": []}
        return {"status": "success", "files": [obj["Key"] for obj in contents]}
    except Exception as e:
        logger.error(f"[{task_id}] Failed to list files: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@router.get("/download/{filename:path}")  # `:path` allows slashes in filename
def download_file(filename: str):
    logger.info(f"Downloading file: {filename}")
    file_path = f"/tmp/downloads/{filename.replace('/', '_')}"  # Local save
    os.makedirs("/tmp/downloads", exist_ok=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )

    try:
        s3.download_file(settings.s3_bucket, filename, file_path)
        logger.success(f"File downloaded locally as {file_path}")
        return FileResponse(path=file_path, filename=os.path.basename(filename))
    except Exception as e:
        logger.error(f"Download failed for {filename}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}