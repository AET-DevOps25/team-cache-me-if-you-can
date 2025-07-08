import logging
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from app.services.summarization_service import (
    SummarizationService,
    get_summarization_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class SummaryResponse(BaseModel):
    filename: str
    summary: str


@router.post("/{source_filename}/summarize", response_model=SummaryResponse)
async def summarize_document_endpoint(
    source_filename: str = Path(..., description="The filename of the document to summarize, e.g., 'my_document.pdf'"),
    summary_service: SummarizationService = Depends(get_summarization_service),
):
    """
    Generates and returns a summary of a previously uploaded document.
    """
    logger.info(f"Received request to summarize document: {source_filename}")
    try:
        summary = await summary_service.summarize_document(source_filename)

        if summary.startswith("Could not find the document"):
            raise HTTPException(status_code=404, detail=summary)
        if summary.startswith("An error occurred"):
            raise HTTPException(status_code=500, detail=summary)

        return SummaryResponse(filename=source_filename, summary=summary)
    except HTTPException as http_exc:
        # Re-raise HTTPException to ensure FastAPI handles it correctly
        raise http_exc
    except Exception as e:
        logger.error(
            f"Unexpected error in summarization endpoint for {source_filename}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected server error occurred while summarizing {source_filename}.",
        )
