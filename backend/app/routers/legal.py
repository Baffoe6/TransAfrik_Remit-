from fastapi import APIRouter, HTTPException

from app.legal.content import DISCLAIMER, LEGAL_PAGES, OPERATOR, PLATFORM

router = APIRouter(prefix="/legal", tags=["Legal"])


@router.get("/pages")
def list_legal_pages():
    return [{"slug": k, "title": v["title"]} for k, v in LEGAL_PAGES.items()]


@router.get("/pages/{slug}")
def get_legal_page(slug: str):
    page = LEGAL_PAGES.get(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Legal page not found")
    return {"slug": slug, "title": page["title"], "sections": page["sections"], "operator": OPERATOR, "platform": PLATFORM, "disclaimer": DISCLAIMER}
