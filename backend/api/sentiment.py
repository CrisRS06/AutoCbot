"""
Sentiment Analysis API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.schemas import (
    FearGreedIndex,
    SentimentAnalysis,
    SocialSentiment
)
from services.sentiment import SentimentService

router = APIRouter()
sentiment_service = SentimentService()


@router.get("/fear-greed", response_model=FearGreedIndex)
async def get_fear_greed_index():
    """Get current Fear & Greed Index"""
    try:
        index = await sentiment_service.get_fear_greed_index()
        return index
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/social/{symbol}", response_model=SocialSentiment)
async def get_social_sentiment(symbol: str):
    """Get social sentiment for a specific symbol"""
    try:
        sentiment = await sentiment_service.get_social_sentiment(symbol)
        if not sentiment:
            raise HTTPException(status_code=404, detail=f"Sentiment data not available for {symbol}")
        return sentiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis", response_model=SentimentAnalysis)
async def get_sentiment_analysis(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols")
):
    """Get comprehensive sentiment analysis"""
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]

        analysis = await sentiment_service.get_comprehensive_analysis(symbol_list)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending-topics")
async def get_trending_topics(limit: int = Query(10, ge=1, le=50)):
    """Get trending topics in crypto social media"""
    try:
        topics = await sentiment_service.get_trending_topics(limit)
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
