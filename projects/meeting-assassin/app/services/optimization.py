"""
Calendar optimization service using genetic algorithms
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.genetic import (
    GeneticAlgorithm, CalendarFitnessFunction, MeetingGene, TimeSlot, Chromosome
)
from app.schemas.optimization import OptimizationRequest, GeneticAlgorithmParams
from app.core.websocket import WebSocketManager


class OptimizationService:
    """Service for calendar optimization using genetic algorithms"""

    def __init__(self):
        self.active_optimizations: Dict[str, Dict[str, Any]] = {}
        self.websocket_manager = WebSocketManager()

    async def optimize_calendar(self, user_id: int, request: OptimizationRequest, optimization_id: str):
        """Run calendar optimization using genetic algorithm"""
        try:
            # Store optimization status
            self.active_optimizations[optimization_id] = {
                "status": "running",
                "user_id": user_id,
                "start_time": datetime.utcnow(),
                "progress": 0
            }

            # Create genetic algorithm instance
            ga_params = request.genetic_params or GeneticAlgorithmParams()
            ga = GeneticAlgorithm(
                population_size=ga_params.population_size,
                mutation_rate=ga_params.mutation_rate,
                crossover_rate=ga_params.crossover_rate,
                max_generations=ga_params.max_generations,
                fitness_threshold=ga_params.fitness_threshold or 0.9
            )

            # Generate mock meeting genes and time slots for demo
            genes = self._generate_mock_meeting_genes()
            time_slots = self._generate_mock_time_slots(request.days_ahead)

            # Initialize population
            ga.initialize_population(genes, time_slots)

            # Create fitness function with user preferences
            user_preferences = {
                "target_focus_hours": 4,
                "work_hours_start": 9,
                "work_hours_end": 17,
                "min_focus_duration": 60
            }
            fitness_function = CalendarFitnessFunction(user_preferences)

            # Run optimization with progress updates
            best_chromosome = await self._run_optimization_with_progress(
                ga, fitness_function, optimization_id, user_id
            )

            # Store results
            result = {
                "optimization_id": optimization_id,
                "status": "completed",
                "fitness_score": best_chromosome.fitness_score,
                "generation": len(ga.fitness_history),
                "best_schedule": self._chromosome_to_schedule(best_chromosome),
                "improvements": self._calculate_improvements(ga),
                "execution_time": (datetime.utcnow() - self.active_optimizations[optimization_id]["start_time"]).total_seconds(),
                "completed_at": datetime.utcnow()
            }

            self.active_optimizations[optimization_id] = result

            # Send WebSocket completion notification
            await self.websocket_manager.send_calendar_optimization(
                str(user_id),
                result
            )

        except Exception as e:
            self.active_optimizations[optimization_id] = {
                "status": "failed",
                "error": str(e),
                "user_id": user_id
            }

    async def _run_optimization_with_progress(self, ga: GeneticAlgorithm, fitness_function, optimization_id: str, user_id: int):
        """Run optimization with progress updates"""
        # Mock progress updates
        for generation in range(ga.max_generations):
            # Simulate generation processing
            await asyncio.sleep(0.1)  # Small delay for demo

            # Update progress
            progress = (generation + 1) / ga.max_generations
            self.active_optimizations[optimization_id]["progress"] = progress

            # Send progress update via WebSocket
            if generation % 10 == 0:  # Update every 10 generations
                await self.websocket_manager.send_calendar_optimization(
                    str(user_id),
                    {
                        "optimization_id": optimization_id,
                        "status": "running",
                        "progress": progress,
                        "generation": generation + 1
                    }
                )

        # For demo, return a mock best chromosome
        return self._create_mock_best_chromosome()

    def _generate_mock_meeting_genes(self) -> List[MeetingGene]:
        """Generate mock meeting genes for demo"""
        now = datetime.utcnow()
        return [
            MeetingGene(
                meeting_id=1,
                title="Team Standup",
                duration_minutes=30,
                required_attendees=["team@company.com"],
                optional_attendees=[],
                priority=0.7,
                flexibility=0.6,
                preferred_time_slots=[],
                constraints={}
            ),
            MeetingGene(
                meeting_id=2,
                title="Project Review",
                duration_minutes=60,
                required_attendees=["manager@company.com"],
                optional_attendees=["stakeholder@company.com"],
                priority=0.8,
                flexibility=0.4,
                preferred_time_slots=[],
                constraints={}
            ),
            MeetingGene(
                meeting_id=3,
                title="Client Call",
                duration_minutes=45,
                required_attendees=["client@external.com"],
                optional_attendees=[],
                priority=0.9,
                flexibility=0.2,
                preferred_time_slots=[],
                constraints={}
            )
        ]

    def _generate_mock_time_slots(self, days_ahead: int) -> List[TimeSlot]:
        """Generate mock time slots for demo"""
        slots = []
        start_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)

        for day in range(days_ahead):
            day_start = start_date + timedelta(days=day)

            # Create hourly slots during work hours
            for hour in range(9, 17):
                slot_start = day_start.replace(hour=hour)
                slot_end = slot_start + timedelta(hours=1)

                slots.append(TimeSlot(
                    start_time=slot_start,
                    end_time=slot_end,
                    duration_minutes=60,
                    is_available=True,
                    priority=0.8 if 10 <= hour <= 15 else 0.6  # Higher priority for mid-day slots
                ))

        return slots

    def _create_mock_best_chromosome(self) -> Chromosome:
        """Create a mock best chromosome for demo"""
        genes = self._generate_mock_meeting_genes()
        slots = self._generate_mock_time_slots(7)

        chromosome = Chromosome(genes, slots)
        chromosome.fitness_score = 0.85

        return chromosome

    def _chromosome_to_schedule(self, chromosome: Chromosome) -> List[Dict[str, Any]]:
        """Convert chromosome to schedule format"""
        schedule = []

        for slot in chromosome.time_slots:
            if not slot.is_available and slot.meeting_id:
                gene = next((g for g in chromosome.genes if g.meeting_id == slot.meeting_id), None)
                if gene:
                    schedule.append({
                        "meeting_id": gene.meeting_id,
                        "title": gene.title,
                        "start_time": slot.start_time.isoformat(),
                        "end_time": slot.end_time.isoformat(),
                        "duration_minutes": gene.duration_minutes,
                        "priority": gene.priority
                    })

        return sorted(schedule, key=lambda x: x["start_time"])

    def _calculate_improvements(self, ga: GeneticAlgorithm) -> Dict[str, float]:
        """Calculate optimization improvements"""
        if len(ga.fitness_history) < 2:
            return {"fitness_improvement": 0.0}

        initial_fitness = ga.fitness_history[0]
        final_fitness = ga.fitness_history[-1]

        return {
            "fitness_improvement": final_fitness - initial_fitness,
            "conflict_reduction": 0.25,  # Mock value
            "focus_time_increase": 1.5   # Mock value in hours
        }

    async def get_optimization_result(self, optimization_id: str) -> Optional[Dict[str, Any]]:
        """Get optimization result by ID"""
        return self.active_optimizations.get(optimization_id)

    async def get_reschedule_suggestions(self, user_id: int, days_ahead: int, max_suggestions: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get AI-powered reschedule suggestions"""
        # Mock suggestions for demo
        suggestions = [
            {
                "meeting_id": 1,
                "current_time": "2024-01-15T10:00:00",
                "suggested_time": "2024-01-15T14:00:00",
                "reason": "Reduced conflict with focus time block",
                "confidence": 0.8,
                "improvement_score": 0.15
            },
            {
                "meeting_id": 2,
                "current_time": "2024-01-15T15:00:00",
                "suggested_time": "2024-01-16T10:00:00",
                "reason": "Better attendee availability",
                "confidence": 0.7,
                "improvement_score": 0.12
            }
        ]

        return suggestions[:max_suggestions]

    async def optimize_focus_time(self, user_id: int, target_hours: float, optimization_id: str):
        """Optimize calendar for maximum focus time"""
        # Mock implementation for demo
        self.active_optimizations[optimization_id] = {
            "status": "completed",
            "user_id": user_id,
            "focus_time_achieved": target_hours * 0.9,
            "meetings_rescheduled": 3,
            "completion_time": datetime.utcnow()
        }

    async def resolve_conflicts(self, user_id: int, auto_apply: bool, resolution_id: str):
        """Resolve scheduling conflicts automatically"""
        # Mock implementation for demo
        self.active_optimizations[resolution_id] = {
            "status": "completed",
            "user_id": user_id,
            "conflicts_resolved": 2,
            "auto_applied": auto_apply,
            "completion_time": datetime.utcnow()
        }

    async def get_fitness_analytics(self, user_id: int, days: int, db: AsyncSession) -> Dict[str, Any]:
        """Get calendar fitness analytics"""
        # Mock analytics for demo
        return {
            "current_fitness_score": 0.75,
            "average_fitness": 0.68,
            "trend": "improving",
            "conflict_count": 3,
            "focus_time_hours": 25.5,
            "meeting_efficiency": 0.82,
            "optimization_suggestions": 5
        }

    async def update_user_ga_params(self, user_id: int, params: GeneticAlgorithmParams):
        """Update genetic algorithm parameters for user"""
        # Store user-specific GA parameters
        pass

    async def get_user_optimization_status(self, user_id: int) -> Dict[str, Any]:
        """Get status of all running optimizations for user"""
        user_optimizations = {
            k: v for k, v in self.active_optimizations.items()
            if v.get("user_id") == user_id
        }

        return {
            "active_optimizations": len([o for o in user_optimizations.values() if o.get("status") == "running"]),
            "completed_optimizations": len([o for o in user_optimizations.values() if o.get("status") == "completed"]),
            "optimizations": user_optimizations
        }

    async def test_algorithm(self, user_id: int, test_params: Dict[str, Any]) -> Dict[str, Any]:
        """Test genetic algorithm with sample data"""
        # Quick algorithm test for demo
        return {
            "test_duration_ms": 156,
            "generations_completed": 50,
            "best_fitness": 0.89,
            "convergence_achieved": True,
            "algorithm_health": "good"
        }