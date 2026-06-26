"""POST /api/score — 패키지 디자인 이미지 채점 엔드포인트."""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.config.constants import MAX_UPLOAD_SIZE_BYTES
from src.services.scorer import score_design

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}

VALID_CATEGORIES     = {"뷰티", "헤어바디", "옴므", "건기식", "식품", "리빙", "패션", "가전", "키즈"}
VALID_LINE_TYPES     = {"프리미엄", "스탠다드", "색조", "헤어에센스", ""}
VALID_PRODUCT_TYPES  = {"단박스", "세트박스", "카톤박스", "용기", "파우치"}


@router.post("/api/score")
async def score_design_image(
    image: UploadFile = File(...),
    category: str = Form(...),
    line_type: str = Form(""),
    product_type: str = Form(...),
    is_overseas: str = Form("false"),
) -> dict:
    """패키지 디자인 이미지를 업로드받아 채점 결과를 반환한다."""
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식: {image.content_type}")

    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 카테고리: {category}")

    if line_type not in VALID_LINE_TYPES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 라인: {line_type}")

    if product_type not in VALID_PRODUCT_TYPES:  # noqa: SIM102
        raise HTTPException(status_code=400, detail=f"유효하지 않은 용기 타입: {product_type}")

    contents = await image.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        size_mb = len(contents) / (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"파일 크기({size_mb:.1f}MB)가 20MB를 초과합니다.")

    overseas_flag = is_overseas.lower() in ("true", "1", "yes")

    try:
        result = await score_design(contents, image.content_type, category, line_type, product_type, overseas_flag)
    except Exception as e:
        err_str = str(e)
        if "503" in err_str or "UNAVAILABLE" in err_str:
            raise HTTPException(
                status_code=503,
                detail="AI 서버가 일시적으로 과부하 상태입니다. 잠시 후 다시 시도해주세요. (Gemini 503)",
            )
        raise HTTPException(status_code=500, detail=f"채점 중 오류가 발생했습니다: {err_str}")

    return result
