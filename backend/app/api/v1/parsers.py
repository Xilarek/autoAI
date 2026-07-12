"""API endpoints для парсеров"""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.parsers.drom_apify import DromApifyParser
from app.parsers.avito_apify import AvitoApifyParser
from app.services.listing_service import ListingService
from app.schemas.search import SearchParams
from app.core.rate_limit import limiter
from app.core.exceptions import (
    ParserError, ParserTimeoutError, ParserUnavailableError,
    ParserBlockedError, ParserEmptyResultError, ApifyAPIError
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/drom/search")
@limiter.limit("10/minute")
async def search_drom(
    request: Request,
    params: SearchParams,
    db: AsyncSession = Depends(get_db)
):
    """Поиск на Дроме через Apify"""
    try:
        parser = DromApifyParser()
        listings = await parser.parse_search(params.dict())
        
        service = ListingService()
        saved = await service.save_listings(db, listings)
        
        logger.info(f"Дром: найдено {len(saved)} объявлений")
        
        return {
            "count": len(saved),
            "listings": [
                {
                    "id": listing.id,
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "price": int(listing.price_rub) if listing.price_rub else 0,
                    "url": listing.url
                }
                for listing in saved
            ]
        }
    except ParserTimeoutError as e:
        logger.error(f"⏱️ Таймаут парсера: {e.message}")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "parser_timeout",
                "message": e.message,
                "details": e.details,
                "retry_after": 60
            }
        )
    except ParserUnavailableError as e:
        logger.error(f"🔌 Парсер недоступен: {e.message}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "parser_unavailable",
                "message": e.message,
                "details": e.details
            }
        )
    except ParserBlockedError as e:
        logger.error(f"🚫 Парсер заблокирован: {e.message}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "parser_blocked",
                "message": e.message,
                "details": e.details,
                "retry_after": 300
            }
        )
    except ParserEmptyResultError as e:
        logger.warning(f"📭 Пустой результат: {e.message}")
        return {
            "count": 0,
            "listings": [],
            "message": e.message,
            "details": e.details
        }
    except ApifyAPIError as e:
        logger.error(f"❌ Ошибка Apify API: {e.message}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "apify_api_error",
                "message": e.message,
                "details": e.details
            }
        )
    except ParserError as e:
        logger.error(f"❌ Ошибка парсера: {e.message}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "parser_error",
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Unexpected error occurred",
                "details": str(e)
            }
        )

@router.post("/avito/search")
@limiter.limit("10/minute")
async def search_avito(
    request: Request,
    params: SearchParams,
    db: AsyncSession = Depends(get_db)
):
    """Поиск на Авито через Apify"""
    try:
        parser = AvitoApifyParser()
        listings = await parser.parse_search(params.dict())
        
        service = ListingService()
        saved = await service.save_listings(db, listings)
        
        logger.info(f"Авито: найдено {len(saved)} объявлений")
        
        return {
            "count": len(saved),
            "listings": [
                {
                    "id": listing.id,
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "price": int(listing.price_rub) if listing.price_rub else 0,
                    "url": listing.url
                }
                for listing in saved
            ]
        }
    except ParserTimeoutError as e:
        raise HTTPException(status_code=504, detail={"error": "parser_timeout", "message": e.message})
    except ParserUnavailableError as e:
        raise HTTPException(status_code=503, detail={"error": "parser_unavailable", "message": e.message})
    except ParserBlockedError as e:
        raise HTTPException(status_code=429, detail={"error": "parser_blocked", "message": e.message})
    except ParserEmptyResultError as e:
        return {"count": 0, "listings": [], "message": e.message}
    except ParserError as e:
        raise HTTPException(status_code=500, detail={"error": "parser_error", "message": e.message})
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})

@router.post("/drom/parse-task")
@limiter.limit("5/minute")
async def start_drom_parsing(request: Request, params: SearchParams, background_tasks: BackgroundTasks):
    """Запустить парсинг Дрома в фоне"""
    from app.tasks.parse_tasks import parse_drom_apify
    task = parse_drom_apify.delay(params.dict())
    return {"status": "queued", "task_id": task.id}

@router.post("/avito/parse-task")
@limiter.limit("5/minute")
async def start_avito_parsing(request: Request, params: SearchParams, background_tasks: BackgroundTasks):
    """Запустить парсинг Авито в фоне"""
    from app.tasks.parse_tasks import parse_avito_apify
    task = parse_avito_apify.delay(params.dict())
    return {"status": "queued", "task_id": task.id}
