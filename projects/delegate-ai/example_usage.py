"""
Delegate.ai - Example Usage

This example demonstrates how to set up and use the autonomous AI agent system
for managing productivity workflows.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Set up environment variables (in production, use .env file)
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["SERPER_API_KEY"] = "your-serper-api-key"  # For web search

# Import the AI system components
from ai_system import (
    AgentOrchestrator,
    MeetingPrepAgent,
    TaskOrchestratorAgent,
    CommunicationAgent,
    ResearchAgent,
    ScheduleOptimizer
)
from ai_system.config import SystemConfig, AGENT_CONFIGS, AgentPriority

async def setup_delegate_ai():
    """Set up the complete Delegate.ai system"""

    print("🚀 Initializing Delegate.ai Autonomous System...")

    # Create system configuration
    config = SystemConfig(
        proactive_mode=True,  # Enable autonomous operation
        background_execution_interval=300,  # Check every 5 minutes
        max_concurrent_agents=5,
        enable_failure_recovery=True,
        user_preference_learning=True
    )

    # Initialize the orchestrator
    orchestrator = AgentOrchestrator(config)

    # Register specialized agents
    print("📋 Registering specialized AI agents...")

    # 1. Meeting Prep Agent
    orchestrator.register_agent(
        MeetingPrepAgent,
        "meeting_prep_agent",
        config=AGENT_CONFIGS["meeting_prep"]
    )

    # 2. Task Orchestrator Agent
    orchestrator.register_agent(
        TaskOrchestratorAgent,
        "task_orchestrator",
        config=AGENT_CONFIGS["task_orchestrator"]
    )

    # 3. Communication Agent
    orchestrator.register_agent(
        CommunicationAgent,
        "communication_agent",
        config=AGENT_CONFIGS["communication"]
    )

    # 4. Research Agent
    orchestrator.register_agent(
        ResearchAgent,
        "research_agent",
        config=AGENT_CONFIGS["research"]
    )

    # 5. Schedule Optimizer
    orchestrator.register_agent(
        ScheduleOptimizer,
        "schedule_optimizer",
        config=AGENT_CONFIGS["schedule_optimizer"]
    )

    # Start the orchestrator
    await orchestrator.start()

    print("✅ Delegate.ai system is now running autonomously!")

    return orchestrator

async def example_meeting_preparation():
    """Example: Autonomous meeting preparation"""

    print("\n📅 Example 1: Preparing for tomorrow's board meeting...")

    orchestrator = await setup_delegate_ai()

    # Submit meeting preparation task
    meeting_task_id = await orchestrator.submit_task(
        task_type="meeting_prep",
        description="Prepare for board meeting with key stakeholders",
        parameters={
            "meeting_info": {
                "title": "Q4 Strategy Review",
                "attendees": ["John Smith (CEO)", "Sarah Johnson (CFO)", "Mike Chen (CTO)"],
                "date": (datetime.now() + timedelta(days=1)).isoformat(),
                "time": "14:00",
                "duration": 60,
                "topic": "Q4 performance review and 2025 strategic planning"
            },
            "task_type": "full_prep"
        },
        priority=AgentPriority.HIGH,
        agent_id="meeting_prep_agent"
    )

    print(f"📝 Meeting prep task submitted: {meeting_task_id}")

    # The agent will autonomously:
    # 1. Research each attendee's background
    # 2. Generate a comprehensive agenda
    # 3. Prepare talking points
    # 4. Create a briefing document
    # 5. Identify potential outcomes

    # Wait for completion (in production, this happens asynchronously)
    await asyncio.sleep(5)

    # Check status
    status = orchestrator.get_system_status()
    print(f"📊 System status: {status['agents']['meeting_prep_agent']['status']}")

async def example_project_orchestration():
    """Example: Breaking down and managing a complex project"""

    print("\n🎯 Example 2: Orchestrating a product launch project...")

    orchestrator = await setup_delegate_ai()

    # Submit complex project for decomposition and management
    project_task_id = await orchestrator.submit_task(
        task_type="task_management",
        description="Manage product launch project end-to-end",
        parameters={
            "orchestration_type": "project_management",
            "project": {
                "name": "Mobile App Launch",
                "type": "software",
                "objectives": [
                    "Launch mobile app to 100k users",
                    "Achieve 4.5+ app store rating",
                    "Generate $1M ARR in first quarter"
                ],
                "constraints": ["6-week timeline", "Limited to 5 team members"],
                "requirements": [
                    "iOS and Android support",
                    "Payment integration",
                    "User onboarding flow"
                ]
            }
        },
        priority=AgentPriority.CRITICAL,
        agent_id="task_orchestrator"
    )

    print(f"🚀 Project orchestration started: {project_task_id}")

    # The orchestrator will:
    # 1. Break down the project into subtasks
    # 2. Identify dependencies
    # 3. Delegate tasks to appropriate agents
    # 4. Monitor progress continuously
    # 5. Adjust plans as needed

    await asyncio.sleep(5)

async def example_proactive_communication():
    """Example: Autonomous email drafting and follow-ups"""

    print("\n✉️ Example 3: Managing communications autonomously...")

    orchestrator = await setup_delegate_ai()

    # Set up proactive status updates
    comm_task_id = await orchestrator.submit_task(
        task_type="communication",
        description="Send weekly status update to stakeholders",
        parameters={
            "communication_type": "status_update",
            "project": {
                "name": "Q4 Initiatives",
                "id": "proj_q4_2024"
            },
            "stakeholders": [
                "board@company.com",
                "investors@company.com",
                "team-leads@company.com"
            ]
        },
        priority=AgentPriority.HIGH,
        agent_id="communication_agent"
    )

    print(f"📧 Communication task initiated: {comm_task_id}")

    # The agent will:
    # 1. Gather project status automatically
    # 2. Draft personalized updates for each stakeholder
    # 3. Send at optimal times
    # 4. Track engagement
    # 5. Send follow-ups as needed

async def example_continuous_research():
    """Example: Continuous market research and intelligence"""

    print("\n🔍 Example 4: Continuous market intelligence...")

    orchestrator = await setup_delegate_ai()

    # Set up continuous research monitoring
    research_task_id = await orchestrator.submit_task(
        task_type="research",
        description="Monitor industry trends and competitor activities",
        parameters={
            "research_type": "industry_monitoring",
            "industry": "AI/ML SaaS",
            "competitors": ["OpenAI", "Anthropic", "Google AI"],
            "timeframe": "real-time",
            "areas": ["product_launches", "partnerships", "funding", "technology"]
        },
        priority=AgentPriority.MEDIUM,
        agent_id="research_agent"
    )

    print(f"🔬 Research monitoring activated: {research_task_id}")

    # The agent will continuously:
    # 1. Monitor news and developments
    # 2. Analyze competitor moves
    # 3. Identify trends
    # 4. Generate insights
    # 5. Alert on critical developments

async def example_schedule_optimization():
    """Example: Continuous calendar optimization"""

    print("\n📆 Example 5: Optimizing calendar for productivity...")

    orchestrator = await setup_delegate_ai()

    # Optimize next week's schedule
    optimization_task_id = await orchestrator.submit_task(
        task_type="scheduling",
        description="Optimize calendar for maximum productivity",
        parameters={
            "optimization_type": "full_optimization",
            "date_range": "next_week",
            "preferences": {
                "focus_time_needed": 12,  # hours
                "preferred_meeting_days": ["Tuesday", "Thursday"],
                "no_meeting_blocks": ["09:00-10:00", "16:00-17:00"]
            }
        },
        priority=AgentPriority.MEDIUM,
        agent_id="schedule_optimizer"
    )

    print(f"⏰ Schedule optimization started: {optimization_task_id}")

    # The optimizer will:
    # 1. Analyze current calendar
    # 2. Identify inefficiencies
    # 3. Suggest meeting consolidations
    # 4. Block focus time
    # 5. Resolve conflicts automatically

async def example_multi_agent_collaboration():
    """Example: Multiple agents working together"""

    print("\n🤝 Example 6: Multi-agent collaboration for complex task...")

    orchestrator = await setup_delegate_ai()

    # Submit a task that requires multiple agents
    complex_task_id = await orchestrator.submit_task(
        task_type="complex_project",
        description="Prepare for investor pitch next week",
        parameters={
            "project": {
                "name": "Series B Investor Pitch",
                "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                "requirements": [
                    "Research investor backgrounds",
                    "Prepare pitch deck",
                    "Schedule rehearsals",
                    "Draft follow-up emails",
                    "Analyze competitor funding rounds"
                ]
            }
        },
        priority=AgentPriority.CRITICAL
    )

    print(f"🎭 Complex collaborative task initiated: {complex_task_id}")

    # The orchestrator will coordinate:
    # 1. Research Agent: Investor research and competitive analysis
    # 2. Communication Agent: Draft emails and pitch narrative
    # 3. Schedule Optimizer: Book rehearsal times
    # 4. Meeting Prep Agent: Prepare for investor meetings
    # 5. Task Orchestrator: Coordinate all activities

    await asyncio.sleep(5)

    # Monitor collaboration
    status = orchestrator.get_system_status()
    print(f"📊 Active agents: {len([a for a in status['agents'].values() if a['status'] != 'idle'])}")

async def monitor_system_performance():
    """Monitor the AI system's autonomous operation"""

    orchestrator = await setup_delegate_ai()

    print("\n📈 Monitoring autonomous system performance...")

    # Continuous monitoring loop
    for i in range(3):
        await asyncio.sleep(10)

        # Get system status
        status = orchestrator.get_system_status()

        print(f"\n⏱️ System Check {i+1}:")
        print(f"  • Running: {status['running']}")
        print(f"  • Active Agents: {sum(1 for a in status['agents'].values() if a['status'] != 'idle')}")
        print(f"  • Queue Size: {status['queue_size']}")
        print(f"  • Tasks Completed: {status['metrics']['total_tasks_completed']}")
        print(f"  • Tasks Failed: {status['metrics']['total_tasks_failed']}")

        # Check individual agent performance
        for agent_id, agent_info in status['agents'].items():
            if agent_info['workload'] > 0:
                print(f"  • {agent_id}: {agent_info['status']} (workload: {agent_info['workload']})")

async def main():
    """Main execution function"""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║           Delegate.ai - Autonomous AI System            ║
    ║                                                          ║
    ║   True AI Operators Working 24/7 Without Human Input    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    try:
        # Run examples sequentially
        await example_meeting_preparation()
        await example_project_orchestration()
        await example_proactive_communication()
        await example_continuous_research()
        await example_schedule_optimization()
        await example_multi_agent_collaboration()

        # Monitor the system
        await monitor_system_performance()

        print("\n✨ All examples completed successfully!")
        print("🤖 The AI agents continue working autonomously in the background...")

    except KeyboardInterrupt:
        print("\n👋 Shutting down Delegate.ai system...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())

"""
Key Features Demonstrated:

1. **Autonomous Operation**: Agents work continuously without prompts
2. **Multi-Agent Collaboration**: Agents communicate and delegate tasks
3. **Proactive Execution**: System anticipates needs and acts accordingly
4. **Learning & Adaptation**: Agents learn from user preferences
5. **Intelligent Orchestration**: Tasks are intelligently routed and managed
6. **Failure Recovery**: System handles errors and retries automatically
7. **Real-time Monitoring**: Continuous system health and performance tracking

The system truly operates as "AI Operators" not "AI Assistants" - making
decisions and taking actions autonomously to manage productivity workflows.
"""