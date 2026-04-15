"""
agents/__init__.py
------------------
Public surface of the multi-agent trading intelligence framework.

Import pattern for callers:
    from agents import Orchestrator, AgentSignal, TradeDecision
    from agents import TechnicalAnalyst, SentimentAnalyst, RiskAgent
"""

from agents.base_agent import AgentSignal, Direction, BaseAnalystAgent
from agents.technical_analyst import TechnicalAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.fundamentals_analyst import FundamentalsAnalyst
from agents.news_analyst import NewsAnalyst
from agents.risk_agent import RiskAgent, VetoReason
from agents.debate import DebateEngine, DebateVerdict
from agents.portfolio_manager import PortfolioManager, PositionSizing
from agents.darwinian import DarwinianEvolutionEngine
from agents.orchestrator import Orchestrator, TradeDecision

__all__ = [
    # Data structures
    "AgentSignal",
    "Direction",
    "TradeDecision",
    "PositionSizing",
    "DebateVerdict",
    "VetoReason",
    # Base class
    "BaseAnalystAgent",
    # Specialist agents
    "TechnicalAnalyst",
    "SentimentAnalyst",
    "FundamentalsAnalyst",
    "NewsAnalyst",
    "RiskAgent",
    # Engines
    "DebateEngine",
    "PortfolioManager",
    "DarwinianEvolutionEngine",
    "Orchestrator",
]
