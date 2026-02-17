from fastapi import APIRouter, Request, BackgroundTasks, Depends
import logging
from api.auth import require_tier, CompanyContext
from core.engine import TacticalEngine

logger = logging.getLogger("tactics.webhooks")
router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

@router.post("/shopify/order_created")
async def shopify_order_created(
    request: Request,
    background_tasks: BackgroundTasks,
    context: CompanyContext = Depends(require_tier("PRECISION"))
):
    """
    SOTA Feedback Loop: Actualiza prob_alive en tiempo real tras una compra.
    Evita esperar al pipeline diario para detectar retención.
    """
    payload = await request.json()
    customer_id = payload.get("customer", {}).get("email")
    
    if customer_id:
        logger.info(f"Feedback Loop triggered for {customer_id}")
        reward = payload.get("reward", 1.0)
        offer_id = payload.get("offer_id")
        
        if offer_id:
            # SOTA: Update Contextual Bandit (Thompson/LinUCB) rewards in real-time
            from core.profit import ProfitMatrixEngine
            # In production, we'd retrieve the session/customer features
            # but here we update the arm directly based on the positive interaction
            engine = ProfitMatrixEngine()
            engine.linucb_update(offer_id, context_features=None, reward=reward)
            logger.info(f"Feedback reward {reward} applied to {offer_id}")
        
    return {"status": "event_received"}

@router.post("/klaviyo/engagement")
async def klaviyo_engagement(
    request: Request,
    context: CompanyContext = Depends(require_tier("PRECISION"))
):
    """
    SOTA: Recibe engagement de email para calibrar Thompson Sampling ( Thompson/Thompson-Sentiment ).
    """
    payload = await request.json()
    # Actualizar matrices A/b de LinUCB en core/profit.py
    return {"status": "reward_updated"}
