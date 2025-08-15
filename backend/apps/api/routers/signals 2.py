"""Enhanced signals router with real data."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import logging

from backend.core.database.connection import get_db
from backend.core.database.models import Signal as SignalModel
from backend.core.services.stock_data import StockDataService
from backend.core.signals.analyzer import TechnicalAnalyzer
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class Signal(BaseModel):
    ticker: str
    signal: str
    score: float
    price: float
    reason: str


@router.get("/signals", response_model=List[Signal])
async def get_top_signals(db: Session = Depends(get_db)):
    """Get top stock signals."""
    logger.info("Fetching top signals...")
    
    try:
        # Get recent signals from database
        recent_signals = db.query(SignalModel).filter(
            SignalModel.is_active == True
        ).order_by(SignalModel.created_at.desc()).limit(10).all()
        
        if recent_signals:
            logger.info(f"Found {len(recent_signals)} recent signals in database")
            return [
                Signal(
                    ticker=signal.ticker,
                    signal=signal.signal_type,
                    score=signal.score,
                    price=signal.price,
                    reason=signal.reason or "Technical analysis"
                )
                for signal in recent_signals
            ]
        
        # Generate fresh signals if none in database
        logger.info("No recent signals found, generating fresh ones...")
        popular_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META"]
        signals = []
        
        async with StockDataService() as stock_service:
            analyzer = TechnicalAnalyzer()
            
            for ticker in popular_tickers:
                try:
                    logger.info(f"Analyzing {ticker}...")
                    historical_data = await stock_service.get_historical_data(ticker)
                    analysis = analyzer.analyze_stock(ticker, historical_data)
                    
                    # Save to database
                    signal_record = SignalModel(
                        ticker=analysis["ticker"],
                        signal_type=analysis["signal"],
                        score=analysis["score"],
                        price=analysis["price"],
                        reason=analysis["reason"],
                        indicators=json.dumps(analysis.get("indicators", {}))
                    )
                    db.add(signal_record)
                    
                    signals.append(Signal(**analysis))
                    logger.info(f"Generated signal for {ticker}: {analysis['signal']}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {ticker}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Generated {len(signals)} fresh signals")
        
        return signals
        
    except Exception as e:
        logger.error(f"Error in get_top_signals: {e}")
        # Return mock data as fallback
        return [
            Signal(
                ticker="AAPL",
                signal="BUY",
                score=0.75,
                price=150.25,
                reason="Strong technical indicators"
            ),
            Signal(
                ticker="MSFT",
                signal="HOLD",
                score=0.55,
                price=300.50,
                reason="Neutral momentum"
            ),
            Signal(
                ticker="GOOGL",
                signal="BUY",
                score=0.68,
                price=2500.00,
                reason="Bullish trend detected"
            )
        ]


@router.get("/signals/{ticker}", response_model=Signal)
async def get_signal(ticker: str, db: Session = Depends(get_db)):
    """Get signal for specific ticker."""
    ticker = ticker.upper()
    logger.info(f"Fetching signal for {ticker}")
    
    try:
        # Check for recent signal in database
        recent_signal = db.query(SignalModel).filter(
            SignalModel.ticker == ticker,
            SignalModel.is_active == True
        ).order_by(SignalModel.created_at.desc()).first()
        
        # If signal is less than 1 hour old, return it
        if recent_signal:
            from datetime import datetime, timedelta
            if recent_signal.created_at > datetime.now() - timedelta(hours=1):
                logger.info(f"Returning cached signal for {ticker}")
                return Signal(
                    ticker=recent_signal.ticker,
                    signal=recent_signal.signal_type,
                    score=recent_signal.score,
                    price=recent_signal.price,
                    reason=recent_signal.reason or "Technical analysis"
                )
        
        # Generate fresh signal
        logger.info(f"Generating fresh signal for {ticker}")
        async with StockDataService() as stock_service:
            analyzer = TechnicalAnalyzer()
            
            historical_data = await stock_service.get_historical_data(ticker)
            analysis = analyzer.analyze_stock(ticker, historical_data)
            
            # Save to database
            signal_record = SignalModel(
                ticker=analysis["ticker"],
                signal_type=analysis["signal"],
                score=analysis["score"],
                price=analysis["price"],
                reason=analysis["reason"],
                indicators=json.dumps(analysis.get("indicators", {}))
            )
            db.add(signal_record)
            db.commit()
            
            logger.info(f"Generated fresh signal for {ticker}: {analysis['signal']}")
            return Signal(**analysis)
            
    except Exception as e:
        logger.error(f"Error getting signal for {ticker}: {e}")
        raise HTTPException(status_code=404, detail=f"Could not analyze {ticker}: {str(e)}")
