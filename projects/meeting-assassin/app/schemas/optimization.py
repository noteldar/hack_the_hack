"""
Calendar optimization schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class GeneticAlgorithmParams(BaseModel):
    population_size: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    max_generations: int = 100
    fitness_threshold: Optional[float] = 0.9


class OptimizationRequest(BaseModel):
    days_ahead: int = 7
    objectives: List[str] = ["minimize_conflicts", "maximize_focus_time"]
    constraints: Optional[Dict[str, Any]] = {}
    genetic_params: Optional[GeneticAlgorithmParams] = None


class OptimizationResponse(BaseModel):
    optimization_id: str
    status: str
    message: str
    estimated_completion_time: datetime


class OptimizationResult(BaseModel):
    optimization_id: str
    status: str
    fitness_score: float
    generation: int
    best_schedule: List[Dict[str, Any]]
    improvements: Dict[str, float]
    execution_time: float
    completed_at: datetime