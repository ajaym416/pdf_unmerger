from celery import Celery
from app.core.config import settings
from app.core.utils import split_pdf
from app.core.storage import upload_to_storage
import os
from loguru import logger

celery_app = Celery("app.worker", broker=settings.broker_url, backend=settings.result_backend)

@celery_app.task(bind=True)
def process_pdf(self, pdf_path, task_id):
    logger.info(f"[{task_id}] Task received to process PDF: {pdf_path}")
    try:
        self.update_state(state="STARTED")
        logger.info(f"[{task_id}] Task state set to STARTED")
        output_dir = f"/tmp/splits/{os.path.basename(pdf_path)}"
        logger.debug(f"[{task_id}] Output directory: {output_dir}")
        results = split_pdf(pdf_path, output_dir)
        logger.success(f"[{task_id}] PDF split complete. Total parts: {len(results)}")

        # Upload to S3 using task_id as prefix
        uploaded_files = []
        for file_path in results:
            s3_key = f"{task_id}/{os.path.basename(file_path)}"
            logger.debug(f"[{task_id}] Uploading {file_path} to {s3_key}")
            upload_to_storage(file_path, s3_key)
            uploaded_files.append(s3_key)
        logger.success(f"[{task_id}] All files uploaded successfully.")
        return {"status": "success", "files": uploaded_files}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
