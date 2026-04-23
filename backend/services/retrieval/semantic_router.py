from semantic_router import Route, SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
import structlog

logger = structlog.get_logger(__name__)

finance_route = Route(
    name="finance",
    utterances=[
        "budget", "revenue", "P&L", "forecast", "headcount cost", 
        "expenses", "financial reports", "CAPEX", "OPEX", "EBITDA margin expected"
    ],
)

engineering_route = Route(
    name="engineering",
    utterances=[
        "architecture", "API", "deployment", "bug", "sprint", 
        "tech debt", "system latency", "database schema", "code formatting", "pull request review"
    ],
)

marketing_route = Route(
    name="marketing",
    utterances=[
        "campaign", "brand", "leads", "conversion", "social media", 
        "SEO", "click-through rate", "ad spend", "content strategy", "product launch"
    ],
)

employee_route = Route(
    name="employee",
    utterances=[
        "leave policy", "onboarding", "benefits", "HR", "payroll", 
        "PTO", "sick days", "holiday calendar", "insurance claim", "workfromhome policy"
    ],
)

c_level_route = Route(
    name="c_level",
    utterances=[
        "board", "strategy", "M&A", "investor", "OKR", "roadmap", 
        "board meeting", "acquisitions", "market expansion", "competitor analysis"
    ],
)

try:
    logger.info("Loading Semantic Router encoder...")
    encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")
    router_layer = SemanticRouter(
        encoder=encoder,
        routes=[finance_route, engineering_route, marketing_route, employee_route, c_level_route]
    )
except Exception as e:
    logger.error("Failed to load Semantic Router encoder", error=str(e))
    router_layer = None

def get_routing_collection(query: str) -> str | None:
    if not router_layer:
        return None
        
    route_choice = router_layer(query)
    if route_choice.name:
        return f"rag_{route_choice.name}"
    return None
