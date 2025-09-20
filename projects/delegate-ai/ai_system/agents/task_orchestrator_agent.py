"""
Task Orchestrator Agent - Master coordinator for task delegation and project management
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum

from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

from ..core.base_agent import BaseAgent, AgentTask, TaskResult
from ..config import AgentConfig, AgentPriority

class TaskType(Enum):
    """Types of tasks that can be orchestrated"""
    DEVELOPMENT = "development"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REVIEW = "review"
    MEETING = "meeting"

class TaskDecomposition(BaseModel):
    """Structure for decomposed tasks"""
    task_id: str = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str = Field(description="Detailed task description")
    type: TaskType = Field(description="Type of task")
    priority: int = Field(description="Priority level 1-5")
    estimated_hours: float = Field(description="Estimated hours to complete")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    assigned_agent: Optional[str] = Field(default=None, description="Assigned agent")
    deadline: Optional[str] = Field(default=None, description="Task deadline")

class ProjectPlan(BaseModel):
    """Project plan structure"""
    project_id: str = Field(description="Project identifier")
    name: str = Field(description="Project name")
    objectives: List[str] = Field(description="Project objectives")
    tasks: List[TaskDecomposition] = Field(description="Decomposed tasks")
    milestones: List[Dict[str, Any]] = Field(description="Project milestones")
    timeline: Dict[str, str] = Field(description="Project timeline")
    resources: Dict[str, Any] = Field(description="Required resources")

class TaskOrchestratorAgent(BaseAgent):
    """
    Master orchestrator agent that breaks down projects into tasks,
    delegates work to other agents, and monitors progress.
    """

    def __init__(self, config: AgentConfig = None, **kwargs):
        config = config or AgentConfig(
            name="TaskOrchestratorAgent",
            description="Master task orchestrator and project manager",
            temperature=0.5,
            max_tokens=4000
        )

        super().__init__(config, **kwargs)

        self.logger = logging.getLogger("delegate.orchestrator_agent")

        # Project and task tracking
        self.active_projects: Dict[str, ProjectPlan] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id
        self.task_status: Dict[str, str] = {}  # task_id -> status

        # Agent capabilities mapping
        self.agent_capabilities = {
            "MeetingPrepAgent": [TaskType.MEETING, TaskType.PLANNING],
            "ResearchAgent": [TaskType.RESEARCH, TaskType.ANALYSIS],
            "CommunicationAgent": [TaskType.COMMUNICATION],
            "ScheduleOptimizer": [TaskType.PLANNING, TaskType.MEETING]
        }

        # Task templates
        self.task_templates = self._load_task_templates()

    def _get_system_prompt(self) -> str:
        """System prompt for task orchestrator"""
        return """You are a master task orchestrator and project manager. Your responsibilities include:

1. Breaking down complex projects into executable subtasks
2. Analyzing task dependencies and creating optimal execution plans
3. Delegating tasks to appropriate specialized agents
4. Monitoring task progress and adjusting plans as needed
5. Coordinating multi-agent collaboration
6. Ensuring project deadlines are met
7. Optimizing resource allocation across tasks

You work autonomously to manage projects end-to-end, making intelligent decisions
about task prioritization, delegation, and resource management.

Key principles:
- Always decompose complex tasks into manageable subtasks
- Consider dependencies when scheduling tasks
- Match tasks to agents based on their capabilities
- Monitor progress and adapt plans dynamically
- Ensure efficient resource utilization
- Maintain clear communication about project status"""

    def _get_specialized_tools(self) -> List:
        """Get specialized tools for task orchestration"""
        tools = []

        # Task decomposition tool
        tools.append(StructuredTool(
            name="decompose_project",
            func=self._decompose_project,
            description="Break down a project into executable tasks",
            args_schema=ProjectPlan
        ))

        # Task delegation tool
        tools.append(Tool(
            name="delegate_task",
            func=self._delegate_task,
            description="Delegate a task to an appropriate agent"
        ))

        # Progress monitoring tool
        tools.append(Tool(
            name="monitor_progress",
            func=self._monitor_progress,
            description="Monitor the progress of active tasks"
        ))

        # Task prioritization tool
        tools.append(Tool(
            name="prioritize_tasks",
            func=self._prioritize_tasks,
            description="Prioritize tasks based on dependencies and deadlines"
        ))

        # Resource optimization tool
        tools.append(Tool(
            name="optimize_resources",
            func=self._optimize_resources,
            description="Optimize resource allocation across tasks"
        ))

        return tools

    async def execute_task(self, task: AgentTask) -> TaskResult:
        """Execute a task orchestration request"""
        start_time = datetime.now()

        try:
            task_type = task.parameters.get("orchestration_type", "project_management")

            if task_type == "project_decomposition":
                result = await self._handle_project_decomposition(task.parameters)
            elif task_type == "task_delegation":
                result = await self._handle_task_delegation(task.parameters)
            elif task_type == "progress_monitoring":
                result = await self._handle_progress_monitoring(task.parameters)
            elif task_type == "resource_optimization":
                result = await self._handle_resource_optimization(task.parameters)
            elif task_type == "project_management":
                result = await self._handle_full_project_management(task.parameters)
            else:
                raise ValueError(f"Unknown orchestration type: {task_type}")

            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="success",
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    "orchestration_type": task_type,
                    "parameters": task.parameters
                }
            )

        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                agent_name=self.config.name,
                status="error",
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

    async def _handle_project_decomposition(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project decomposition into tasks"""
        project_info = parameters.get("project", {})

        self.logger.info(f"Decomposing project: {project_info.get('name', 'Unnamed')}")

        # Analyze project requirements
        requirements = self._analyze_requirements(project_info)

        # Generate task breakdown
        tasks = await self._generate_task_breakdown(project_info, requirements)

        # Identify dependencies
        dependencies = self._identify_dependencies(tasks)

        # Create execution plan
        execution_plan = self._create_execution_plan(tasks, dependencies)

        # Estimate timeline
        timeline = self._estimate_timeline(execution_plan)

        # Create project plan
        project_plan = ProjectPlan(
            project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=project_info.get("name", "Unnamed Project"),
            objectives=project_info.get("objectives", []),
            tasks=tasks,
            milestones=self._identify_milestones(tasks, timeline),
            timeline=timeline,
            resources=self._identify_required_resources(tasks)
        )

        # Store project plan
        self.active_projects[project_plan.project_id] = project_plan

        return {
            "project_plan": project_plan.dict(),
            "total_tasks": len(tasks),
            "estimated_duration": timeline.get("total_duration"),
            "critical_path": execution_plan.get("critical_path", []),
            "resource_requirements": project_plan.resources
        }

    async def _handle_task_delegation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task delegation to agents"""
        tasks_to_delegate = parameters.get("tasks", [])
        delegation_results = []

        for task_info in tasks_to_delegate:
            # Find suitable agent
            suitable_agent = await self._find_suitable_agent(task_info)

            if suitable_agent:
                # Delegate task
                delegation_result = await self._delegate_to_agent(
                    task_info,
                    suitable_agent
                )

                delegation_results.append({
                    "task_id": task_info.get("task_id"),
                    "delegated_to": suitable_agent,
                    "status": "delegated",
                    "estimated_completion": delegation_result.get("estimated_completion")
                })

                # Update tracking
                self.task_assignments[task_info.get("task_id")] = suitable_agent
                self.task_status[task_info.get("task_id")] = "in_progress"
            else:
                delegation_results.append({
                    "task_id": task_info.get("task_id"),
                    "status": "no_suitable_agent",
                    "queued": True
                })

        return {
            "delegations": delegation_results,
            "successful_delegations": len([d for d in delegation_results if d["status"] == "delegated"]),
            "queued_tasks": len([d for d in delegation_results if d.get("queued")])
        }

    async def _handle_progress_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor progress of active tasks and projects"""
        project_id = parameters.get("project_id")

        if project_id and project_id in self.active_projects:
            project = self.active_projects[project_id]
            progress_report = await self._generate_project_progress_report(project)
        else:
            # Monitor all active tasks
            progress_report = await self._generate_overall_progress_report()

        # Identify issues
        issues = self._identify_progress_issues(progress_report)

        # Generate recommendations
        recommendations = self._generate_progress_recommendations(issues)

        return {
            "progress_report": progress_report,
            "identified_issues": issues,
            "recommendations": recommendations,
            "overall_health": self._calculate_project_health(progress_report)
        }

    async def _handle_resource_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation across tasks"""
        self.logger.info("Optimizing resource allocation")

        # Analyze current resource utilization
        current_utilization = await self._analyze_resource_utilization()

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(current_utilization)

        # Generate optimization plan
        optimization_plan = self._generate_optimization_plan(
            current_utilization,
            bottlenecks
        )

        # Apply optimizations
        optimization_results = await self._apply_optimizations(optimization_plan)

        return {
            "current_utilization": current_utilization,
            "bottlenecks": bottlenecks,
            "optimization_plan": optimization_plan,
            "results": optimization_results,
            "efficiency_gain": self._calculate_efficiency_gain(
                current_utilization,
                optimization_results
            )
        }

    async def _handle_full_project_management(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end-to-end project management"""
        project_info = parameters.get("project", {})

        # Step 1: Decompose project
        decomposition = await self._handle_project_decomposition({"project": project_info})

        # Step 2: Prioritize tasks
        prioritized_tasks = await self._prioritize_project_tasks(
            decomposition["project_plan"]["tasks"]
        )

        # Step 3: Begin delegation
        initial_delegations = await self._handle_task_delegation({
            "tasks": prioritized_tasks[:5]  # Start with first 5 tasks
        })

        # Step 4: Set up monitoring
        monitoring_schedule = self._create_monitoring_schedule(
            decomposition["project_plan"]
        )

        return {
            "project_id": decomposition["project_plan"]["project_id"],
            "decomposition": decomposition,
            "initial_delegations": initial_delegations,
            "monitoring_schedule": monitoring_schedule,
            "status": "project_initiated",
            "next_review": monitoring_schedule.get("next_review")
        }

    # Helper methods

    def _decompose_project(self, project: ProjectPlan) -> Dict[str, Any]:
        """Tool function for project decomposition"""
        return {
            "project_id": project.project_id,
            "tasks": len(project.tasks),
            "status": "decomposed"
        }

    def _delegate_task(self, task_info: str) -> str:
        """Tool function for task delegation"""
        return f"Task delegated: {task_info}"

    def _monitor_progress(self, context: str) -> str:
        """Tool function for progress monitoring"""
        return f"Progress monitored: {context}"

    def _prioritize_tasks(self, context: str) -> str:
        """Tool function for task prioritization"""
        return f"Tasks prioritized: {context}"

    def _optimize_resources(self, context: str) -> str:
        """Tool function for resource optimization"""
        return f"Resources optimized: {context}"

    def _analyze_requirements(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project requirements"""
        return {
            "functional_requirements": project_info.get("requirements", []),
            "constraints": project_info.get("constraints", []),
            "success_criteria": project_info.get("success_criteria", [])
        }

    async def _generate_task_breakdown(
        self,
        project_info: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[TaskDecomposition]:
        """Generate task breakdown for a project"""
        tasks = []
        task_counter = 1

        # Create tasks based on project type
        project_type = project_info.get("type", "general")

        if project_type == "software":
            tasks.extend(self._generate_software_tasks(project_info, task_counter))
        elif project_type == "research":
            tasks.extend(self._generate_research_tasks(project_info, task_counter))
        else:
            tasks.extend(self._generate_general_tasks(project_info, task_counter))

        return tasks

    def _generate_software_tasks(
        self,
        project_info: Dict[str, Any],
        counter: int
    ) -> List[TaskDecomposition]:
        """Generate tasks for software projects"""
        tasks = []
        base_id = project_info.get("name", "project").lower().replace(" ", "_")

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter}",
            title="Requirements Analysis",
            description="Analyze and document detailed requirements",
            type=TaskType.ANALYSIS,
            priority=1,
            estimated_hours=8.0
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+1}",
            title="System Design",
            description="Create system architecture and design documents",
            type=TaskType.PLANNING,
            priority=1,
            estimated_hours=16.0,
            dependencies=[f"{base_id}_task_{counter}"]
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+2}",
            title="Implementation",
            description="Develop the solution",
            type=TaskType.DEVELOPMENT,
            priority=2,
            estimated_hours=40.0,
            dependencies=[f"{base_id}_task_{counter+1}"]
        ))

        return tasks

    def _generate_research_tasks(
        self,
        project_info: Dict[str, Any],
        counter: int
    ) -> List[TaskDecomposition]:
        """Generate tasks for research projects"""
        tasks = []
        base_id = project_info.get("name", "project").lower().replace(" ", "_")

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter}",
            title="Literature Review",
            description="Review relevant literature and prior work",
            type=TaskType.RESEARCH,
            priority=1,
            estimated_hours=12.0
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+1}",
            title="Data Collection",
            description="Gather required data and information",
            type=TaskType.RESEARCH,
            priority=2,
            estimated_hours=16.0
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+2}",
            title="Analysis",
            description="Analyze collected data",
            type=TaskType.ANALYSIS,
            priority=2,
            estimated_hours=20.0,
            dependencies=[f"{base_id}_task_{counter+1}"]
        ))

        return tasks

    def _generate_general_tasks(
        self,
        project_info: Dict[str, Any],
        counter: int
    ) -> List[TaskDecomposition]:
        """Generate general project tasks"""
        tasks = []
        base_id = project_info.get("name", "project").lower().replace(" ", "_")

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter}",
            title="Project Planning",
            description="Create detailed project plan",
            type=TaskType.PLANNING,
            priority=1,
            estimated_hours=4.0
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+1}",
            title="Execution",
            description="Execute project tasks",
            type=TaskType.DEVELOPMENT,
            priority=2,
            estimated_hours=24.0,
            dependencies=[f"{base_id}_task_{counter}"]
        ))

        tasks.append(TaskDecomposition(
            task_id=f"{base_id}_task_{counter+2}",
            title="Review and Validation",
            description="Review results and validate outcomes",
            type=TaskType.REVIEW,
            priority=3,
            estimated_hours=8.0,
            dependencies=[f"{base_id}_task_{counter+1}"]
        ))

        return tasks

    def _identify_dependencies(self, tasks: List[TaskDecomposition]) -> Dict[str, List[str]]:
        """Identify task dependencies"""
        dependencies = {}
        for task in tasks:
            if task.dependencies:
                dependencies[task.task_id] = task.dependencies
        return dependencies

    def _create_execution_plan(
        self,
        tasks: List[TaskDecomposition],
        dependencies: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Create optimal execution plan"""
        # Simple topological sort for task ordering
        ordered_tasks = self._topological_sort(tasks, dependencies)

        # Identify critical path
        critical_path = self._find_critical_path(ordered_tasks, dependencies)

        return {
            "execution_order": [t.task_id for t in ordered_tasks],
            "critical_path": critical_path,
            "parallel_opportunities": self._identify_parallel_tasks(ordered_tasks, dependencies)
        }

    def _topological_sort(
        self,
        tasks: List[TaskDecomposition],
        dependencies: Dict[str, List[str]]
    ) -> List[TaskDecomposition]:
        """Perform topological sort on tasks"""
        # Simple implementation - in production would be more sophisticated
        sorted_tasks = []
        task_dict = {t.task_id: t for t in tasks}
        visited = set()

        def visit(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            if task_id in dependencies:
                for dep in dependencies[task_id]:
                    if dep in task_dict:
                        visit(dep)
            sorted_tasks.append(task_dict[task_id])

        for task in tasks:
            visit(task.task_id)

        return sorted_tasks

    def _find_critical_path(
        self,
        tasks: List[TaskDecomposition],
        dependencies: Dict[str, List[str]]
    ) -> List[str]:
        """Find the critical path through the project"""
        # Simplified critical path - would use CPM algorithm in production
        path = []
        for task in tasks:
            if not task.dependencies:  # Start nodes
                path.append(task.task_id)
                break

        # Follow longest path
        current = path[0] if path else None
        while current:
            next_tasks = [t for t in tasks if current in t.dependencies]
            if next_tasks:
                # Choose task with highest priority/longest duration
                next_task = max(next_tasks, key=lambda t: t.estimated_hours)
                path.append(next_task.task_id)
                current = next_task.task_id
            else:
                current = None

        return path

    def _identify_parallel_tasks(
        self,
        tasks: List[TaskDecomposition],
        dependencies: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Identify tasks that can be executed in parallel"""
        parallel_groups = []
        processed = set()

        for task in tasks:
            if task.task_id in processed:
                continue

            # Find tasks with same dependencies (can run in parallel)
            group = [task.task_id]
            task_deps = set(task.dependencies)

            for other in tasks:
                if other.task_id != task.task_id and other.task_id not in processed:
                    other_deps = set(other.dependencies)
                    if task_deps == other_deps:
                        group.append(other.task_id)
                        processed.add(other.task_id)

            if len(group) > 1:
                parallel_groups.append(group)
            processed.add(task.task_id)

        return parallel_groups

    def _estimate_timeline(self, execution_plan: Dict[str, Any]) -> Dict[str, str]:
        """Estimate project timeline"""
        # Simplified timeline estimation
        total_hours = sum(self.active_projects.values().__iter__().__next__().tasks[0].estimated_hours
                         if self.active_projects else [0])

        start_date = datetime.now()
        end_date = start_date + timedelta(hours=total_hours)

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_duration": f"{total_hours} hours",
            "buffer": "20%"  # Add buffer for uncertainty
        }

    def _identify_milestones(
        self,
        tasks: List[TaskDecomposition],
        timeline: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Identify project milestones"""
        milestones = []

        # Group tasks by type for milestone identification
        planning_tasks = [t for t in tasks if t.type == TaskType.PLANNING]
        dev_tasks = [t for t in tasks if t.type == TaskType.DEVELOPMENT]
        review_tasks = [t for t in tasks if t.type == TaskType.REVIEW]

        if planning_tasks:
            milestones.append({
                "name": "Planning Complete",
                "tasks": [t.task_id for t in planning_tasks],
                "target_date": (datetime.now() + timedelta(days=2)).isoformat()
            })

        if dev_tasks:
            milestones.append({
                "name": "Development Complete",
                "tasks": [t.task_id for t in dev_tasks],
                "target_date": (datetime.now() + timedelta(days=7)).isoformat()
            })

        if review_tasks:
            milestones.append({
                "name": "Project Complete",
                "tasks": [t.task_id for t in review_tasks],
                "target_date": timeline.get("end_date")
            })

        return milestones

    def _identify_required_resources(self, tasks: List[TaskDecomposition]) -> Dict[str, Any]:
        """Identify resources required for tasks"""
        resources = {
            "agents": {},
            "total_hours": 0,
            "skills_required": set()
        }

        for task in tasks:
            # Count agent requirements
            agent_type = self._get_agent_for_task_type(task.type)
            resources["agents"][agent_type] = resources["agents"].get(agent_type, 0) + 1

            # Sum total hours
            resources["total_hours"] += task.estimated_hours

            # Collect required skills
            resources["skills_required"].add(task.type.value)

        resources["skills_required"] = list(resources["skills_required"])
        return resources

    def _get_agent_for_task_type(self, task_type: TaskType) -> str:
        """Get appropriate agent for a task type"""
        mapping = {
            TaskType.MEETING: "MeetingPrepAgent",
            TaskType.RESEARCH: "ResearchAgent",
            TaskType.COMMUNICATION: "CommunicationAgent",
            TaskType.PLANNING: "ScheduleOptimizer",
            TaskType.DEVELOPMENT: "TaskOrchestratorAgent",
            TaskType.ANALYSIS: "ResearchAgent",
            TaskType.REVIEW: "TaskOrchestratorAgent"
        }
        return mapping.get(task_type, "TaskOrchestratorAgent")

    async def _find_suitable_agent(self, task_info: Dict[str, Any]) -> Optional[str]:
        """Find suitable agent for a task"""
        task_type = TaskType(task_info.get("type", "development"))

        for agent_name, capabilities in self.agent_capabilities.items():
            if task_type in capabilities:
                # Check if agent is available (simplified)
                return agent_name

        return None

    async def _delegate_to_agent(
        self,
        task_info: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """Delegate task to specific agent"""
        # In production, would actually communicate with agent
        return {
            "delegation_id": f"del_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_id": task_info.get("task_id"),
            "agent_id": agent_id,
            "estimated_completion": (datetime.now() + timedelta(
                hours=task_info.get("estimated_hours", 1)
            )).isoformat()
        }

    async def _generate_project_progress_report(self, project: ProjectPlan) -> Dict[str, Any]:
        """Generate progress report for a project"""
        completed_tasks = [t for t in project.tasks if self.task_status.get(t.task_id) == "completed"]
        in_progress_tasks = [t for t in project.tasks if self.task_status.get(t.task_id) == "in_progress"]
        pending_tasks = [t for t in project.tasks if t.task_id not in self.task_status]

        return {
            "project_id": project.project_id,
            "project_name": project.name,
            "total_tasks": len(project.tasks),
            "completed": len(completed_tasks),
            "in_progress": len(in_progress_tasks),
            "pending": len(pending_tasks),
            "completion_percentage": (len(completed_tasks) / len(project.tasks) * 100) if project.tasks else 0,
            "on_track": True,  # Simplified
            "estimated_completion": project.timeline.get("end_date")
        }

    async def _generate_overall_progress_report(self) -> Dict[str, Any]:
        """Generate overall progress report"""
        return {
            "active_projects": len(self.active_projects),
            "total_tasks": len(self.task_status),
            "completed_tasks": len([s for s in self.task_status.values() if s == "completed"]),
            "in_progress_tasks": len([s for s in self.task_status.values() if s == "in_progress"]),
            "agent_assignments": len(self.task_assignments)
        }

    def _identify_progress_issues(self, progress_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify issues in progress"""
        issues = []

        if progress_report.get("completion_percentage", 0) < 25:
            issues.append({
                "type": "slow_progress",
                "description": "Project progress is below expected rate",
                "severity": "medium"
            })

        return issues

    def _generate_progress_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []

        for issue in issues:
            if issue["type"] == "slow_progress":
                recommendations.append("Consider allocating additional resources")
                recommendations.append("Review task dependencies for optimization")

        return recommendations

    def _calculate_project_health(self, progress_report: Dict[str, Any]) -> str:
        """Calculate overall project health"""
        completion = progress_report.get("completion_percentage", 0)
        on_track = progress_report.get("on_track", True)

        if completion > 75 and on_track:
            return "excellent"
        elif completion > 50 and on_track:
            return "good"
        elif completion > 25:
            return "fair"
        else:
            return "needs_attention"

    async def _analyze_resource_utilization(self) -> Dict[str, Any]:
        """Analyze current resource utilization"""
        return {
            "agent_utilization": {
                agent: len([a for a in self.task_assignments.values() if a == agent])
                for agent in self.agent_capabilities.keys()
            },
            "task_distribution": {
                "by_type": {},  # Would calculate distribution
                "by_priority": {}  # Would calculate distribution
            }
        }

    def _identify_bottlenecks(self, utilization: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify resource bottlenecks"""
        bottlenecks = []

        for agent, tasks in utilization.get("agent_utilization", {}).items():
            if tasks > 3:  # Threshold for bottleneck
                bottlenecks.append({
                    "resource": agent,
                    "load": tasks,
                    "impact": "high"
                })

        return bottlenecks

    def _generate_optimization_plan(
        self,
        utilization: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate resource optimization plan"""
        return {
            "reallocations": [],  # Would generate reallocation suggestions
            "priority_adjustments": [],  # Would suggest priority changes
            "parallel_opportunities": []  # Would identify parallelization options
        }

    async def _apply_optimizations(self, optimization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource optimizations"""
        return {
            "applied": True,
            "reallocations_made": 0,
            "estimated_improvement": "15%"
        }

    def _calculate_efficiency_gain(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> float:
        """Calculate efficiency gain from optimization"""
        return 15.0  # Simplified - would calculate actual gain

    async def _prioritize_project_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tasks for execution"""
        # Sort by priority and dependencies
        return sorted(tasks, key=lambda t: (t.get("priority", 5), len(t.get("dependencies", []))))

    def _create_monitoring_schedule(self, project_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring schedule for project"""
        return {
            "frequency": "daily",
            "next_review": (datetime.now() + timedelta(days=1)).isoformat(),
            "checkpoints": [
                {"date": (datetime.now() + timedelta(days=3)).isoformat(), "type": "milestone_review"},
                {"date": (datetime.now() + timedelta(days=7)).isoformat(), "type": "comprehensive_review"}
            ]
        }

    def _load_task_templates(self) -> Dict[str, Any]:
        """Load task templates"""
        return {
            "software_development": {
                "phases": ["requirements", "design", "implementation", "testing", "deployment"]
            },
            "research": {
                "phases": ["literature_review", "data_collection", "analysis", "reporting"]
            },
            "general": {
                "phases": ["planning", "execution", "review"]
            }
        }