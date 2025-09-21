"""
Genetic Algorithm for Calendar Optimization
"""

import random
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    """Represents a time slot in the calendar"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_available: bool = True
    priority: float = 1.0
    meeting_id: Optional[int] = None

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another"""
        return (self.start_time < other.end_time and
                self.end_time > other.start_time)

    def get_overlap_minutes(self, other: 'TimeSlot') -> int:
        """Get overlap duration in minutes"""
        if not self.overlaps_with(other):
            return 0

        overlap_start = max(self.start_time, other.start_time)
        overlap_end = min(self.end_time, other.end_time)
        return int((overlap_end - overlap_start).total_seconds() / 60)


@dataclass
class MeetingGene:
    """Represents a meeting in the genetic algorithm chromosome"""
    meeting_id: int
    title: str
    duration_minutes: int
    required_attendees: List[str]
    optional_attendees: List[str]
    priority: float
    flexibility: float  # How flexible the meeting time is (0.0 to 1.0)
    preferred_time_slots: List[TimeSlot]
    constraints: Dict[str, Any]

    def __post_init__(self):
        """Validate the gene after initialization"""
        if not 0 <= self.priority <= 1.0:
            raise ValueError("Priority must be between 0.0 and 1.0")
        if not 0 <= self.flexibility <= 1.0:
            raise ValueError("Flexibility must be between 0.0 and 1.0")


class Chromosome:
    """Represents a complete calendar schedule solution"""

    def __init__(self, genes: List[MeetingGene], time_slots: List[TimeSlot]):
        self.genes = genes
        self.time_slots = time_slots
        self.fitness_score: Optional[float] = None
        self.schedule_conflicts = 0
        self.focus_time_blocks = 0
        self.optimization_metrics = {}

    def assign_meeting_to_slot(self, gene: MeetingGene, slot: TimeSlot) -> bool:
        """Assign a meeting to a specific time slot"""
        if not slot.is_available or slot.duration_minutes < gene.duration_minutes:
            return False

        slot.meeting_id = gene.meeting_id
        slot.is_available = False
        return True

    def get_conflicts(self) -> List[Tuple[TimeSlot, TimeSlot]]:
        """Get all scheduling conflicts"""
        conflicts = []
        occupied_slots = [slot for slot in self.time_slots if not slot.is_available]

        for i, slot1 in enumerate(occupied_slots):
            for slot2 in occupied_slots[i+1:]:
                if slot1.overlaps_with(slot2):
                    conflicts.append((slot1, slot2))

        return conflicts

    def get_focus_time_blocks(self, min_duration_minutes: int = 60) -> List[TimeSlot]:
        """Get available focus time blocks"""
        available_slots = [slot for slot in self.time_slots if slot.is_available]
        focus_blocks = []

        for slot in available_slots:
            if slot.duration_minutes >= min_duration_minutes:
                focus_blocks.append(slot)

        return focus_blocks

    def clone(self) -> 'Chromosome':
        """Create a deep copy of the chromosome"""
        new_slots = [TimeSlot(
            start_time=slot.start_time,
            end_time=slot.end_time,
            duration_minutes=slot.duration_minutes,
            is_available=slot.is_available,
            priority=slot.priority,
            meeting_id=slot.meeting_id
        ) for slot in self.time_slots]

        return Chromosome(self.genes.copy(), new_slots)


class FitnessFunction(ABC):
    """Abstract base class for fitness functions"""

    @abstractmethod
    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """Calculate fitness score for a chromosome"""
        pass


class CalendarFitnessFunction(FitnessFunction):
    """Fitness function for calendar optimization"""

    def __init__(self, user_preferences: Dict[str, Any]):
        self.user_preferences = user_preferences
        self.weights = {
            'conflict_penalty': 0.4,
            'focus_time_bonus': 0.3,
            'priority_bonus': 0.2,
            'work_hours_bonus': 0.1
        }

    def calculate_fitness(self, chromosome: Chromosome) -> float:
        """Calculate comprehensive fitness score"""
        score = 1.0  # Start with perfect score

        # Penalty for conflicts
        conflicts = chromosome.get_conflicts()
        conflict_penalty = len(conflicts) * self.weights['conflict_penalty']
        score -= conflict_penalty

        # Bonus for focus time
        focus_blocks = chromosome.get_focus_time_blocks(
            self.user_preferences.get('min_focus_duration', 60)
        )
        total_focus_time = sum(block.duration_minutes for block in focus_blocks)
        target_focus_time = self.user_preferences.get('target_focus_hours', 4) * 60

        focus_ratio = min(total_focus_time / target_focus_time, 1.0) if target_focus_time > 0 else 0
        focus_bonus = focus_ratio * self.weights['focus_time_bonus']
        score += focus_bonus

        # Bonus for high-priority meetings in optimal slots
        priority_score = self._calculate_priority_score(chromosome)
        score += priority_score * self.weights['priority_bonus']

        # Bonus for meetings within work hours
        work_hours_score = self._calculate_work_hours_score(chromosome)
        score += work_hours_score * self.weights['work_hours_bonus']

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def _calculate_priority_score(self, chromosome: Chromosome) -> float:
        """Calculate score based on priority meeting placement"""
        total_priority = sum(gene.priority for gene in chromosome.genes)
        if total_priority == 0:
            return 0

        achieved_priority = 0
        for slot in chromosome.time_slots:
            if not slot.is_available and slot.meeting_id:
                gene = next((g for g in chromosome.genes if g.meeting_id == slot.meeting_id), None)
                if gene:
                    # Higher priority meetings in preferred slots get higher scores
                    achieved_priority += gene.priority * slot.priority

        return achieved_priority / total_priority

    def _calculate_work_hours_score(self, chromosome: Chromosome) -> float:
        """Calculate score for meetings within work hours"""
        work_start = self.user_preferences.get('work_hours_start', 9)
        work_end = self.user_preferences.get('work_hours_end', 17)

        total_meetings = len([s for s in chromosome.time_slots if not s.is_available])
        if total_meetings == 0:
            return 1.0

        work_hours_meetings = 0
        for slot in chromosome.time_slots:
            if not slot.is_available:
                hour = slot.start_time.hour
                if work_start <= hour <= work_end:
                    work_hours_meetings += 1

        return work_hours_meetings / total_meetings


class GeneticAlgorithm:
    """Genetic Algorithm implementation for calendar optimization"""

    def __init__(self,
                 population_size: int = 50,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 max_generations: int = 100,
                 fitness_threshold: float = 0.95):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_generations = max_generations
        self.fitness_threshold = fitness_threshold
        self.population: List[Chromosome] = []
        self.best_chromosome: Optional[Chromosome] = None
        self.fitness_history: List[float] = []

    def initialize_population(self, genes: List[MeetingGene], available_slots: List[TimeSlot]):
        """Initialize random population"""
        self.population = []

        for _ in range(self.population_size):
            chromosome = self._create_random_chromosome(genes, available_slots)
            self.population.append(chromosome)

        logger.info(f"Initialized population with {len(self.population)} chromosomes")

    def _create_random_chromosome(self, genes: List[MeetingGene], available_slots: List[TimeSlot]) -> Chromosome:
        """Create a random chromosome by randomly assigning meetings to slots"""
        # Create fresh copy of slots
        slots = [TimeSlot(
            start_time=slot.start_time,
            end_time=slot.end_time,
            duration_minutes=slot.duration_minutes,
            is_available=True,
            priority=slot.priority
        ) for slot in available_slots]

        chromosome = Chromosome(genes, slots)

        # Randomly assign meetings to available slots
        shuffled_genes = genes.copy()
        random.shuffle(shuffled_genes)

        for gene in shuffled_genes:
            suitable_slots = [
                slot for slot in chromosome.time_slots
                if slot.is_available and slot.duration_minutes >= gene.duration_minutes
            ]

            if suitable_slots:
                # Prefer preferred time slots if available
                preferred_slots = [
                    slot for slot in suitable_slots
                    if any(pref.overlaps_with(slot) for pref in gene.preferred_time_slots)
                ]

                chosen_slot = random.choice(preferred_slots if preferred_slots else suitable_slots)
                chromosome.assign_meeting_to_slot(gene, chosen_slot)

        return chromosome

    def evolve(self, fitness_function: FitnessFunction) -> Chromosome:
        """Run the genetic algorithm"""
        logger.info(f"Starting evolution with {self.max_generations} generations")

        for generation in range(self.max_generations):
            # Calculate fitness for all chromosomes
            for chromosome in self.population:
                chromosome.fitness_score = fitness_function.calculate_fitness(chromosome)

            # Sort population by fitness (descending)
            self.population.sort(key=lambda x: x.fitness_score or 0, reverse=True)

            # Track best chromosome
            current_best = self.population[0]
            if not self.best_chromosome or current_best.fitness_score > self.best_chromosome.fitness_score:
                self.best_chromosome = current_best.clone()

            self.fitness_history.append(current_best.fitness_score)

            logger.info(f"Generation {generation + 1}: Best fitness = {current_best.fitness_score:.4f}")

            # Check if we've reached the fitness threshold
            if current_best.fitness_score >= self.fitness_threshold:
                logger.info(f"Fitness threshold reached at generation {generation + 1}")
                break

            # Create new population
            new_population = []

            # Keep elite (top 10%)
            elite_size = max(1, int(self.population_size * 0.1))
            new_population.extend(self.population[:elite_size])

            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()

                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.clone(), parent2.clone()

                if random.random() < self.mutation_rate:
                    self._mutate(child1)
                if random.random() < self.mutation_rate:
                    self._mutate(child2)

                new_population.extend([child1, child2])

            # Trim to population size
            self.population = new_population[:self.population_size]

        logger.info(f"Evolution completed. Best fitness: {self.best_chromosome.fitness_score:.4f}")
        return self.best_chromosome

    def _tournament_selection(self, tournament_size: int = 3) -> Chromosome:
        """Tournament selection for parent selection"""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness_score or 0)

    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """Single-point crossover for chromosomes"""
        child1 = parent1.clone()
        child2 = parent2.clone()

        if len(parent1.time_slots) <= 1:
            return child1, child2

        # Choose crossover point
        crossover_point = random.randint(1, len(parent1.time_slots) - 1)

        # Swap meeting assignments after crossover point
        for i in range(crossover_point, len(parent1.time_slots)):
            child1.time_slots[i].meeting_id = parent2.time_slots[i].meeting_id
            child1.time_slots[i].is_available = parent2.time_slots[i].is_available

            child2.time_slots[i].meeting_id = parent1.time_slots[i].meeting_id
            child2.time_slots[i].is_available = parent1.time_slots[i].is_available

        return child1, child2

    def _mutate(self, chromosome: Chromosome):
        """Mutate a chromosome by randomly reassigning meetings"""
        occupied_slots = [slot for slot in chromosome.time_slots if not slot.is_available]

        if not occupied_slots:
            return

        # Choose random occupied slot to modify
        slot_to_mutate = random.choice(occupied_slots)
        original_meeting_id = slot_to_mutate.meeting_id

        # Free the slot
        slot_to_mutate.is_available = True
        slot_to_mutate.meeting_id = None

        # Find a new slot for the meeting
        gene = next((g for g in chromosome.genes if g.meeting_id == original_meeting_id), None)
        if gene:
            available_slots = [
                slot for slot in chromosome.time_slots
                if slot.is_available and slot.duration_minutes >= gene.duration_minutes
            ]

            if available_slots:
                new_slot = random.choice(available_slots)
                chromosome.assign_meeting_to_slot(gene, new_slot)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            'generations_completed': len(self.fitness_history),
            'best_fitness': self.best_chromosome.fitness_score if self.best_chromosome else 0,
            'fitness_improvement': (
                self.fitness_history[-1] - self.fitness_history[0]
                if len(self.fitness_history) > 1 else 0
            ),
            'convergence_generation': (
                next((i for i, f in enumerate(self.fitness_history)
                     if f >= self.fitness_threshold), len(self.fitness_history))
            )
        }