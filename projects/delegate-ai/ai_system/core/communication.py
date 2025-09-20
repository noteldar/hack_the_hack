"""
Inter-Agent Communication System
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import uuid

@dataclass
class Message:
    """Message structure for inter-agent communication"""
    message_id: str
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    correlation_id: Optional[str] = None
    priority: int = 5  # 1-10, 1 being highest

@dataclass
class Broadcast:
    """Broadcast message for multi-agent communication"""
    broadcast_id: str
    sender: str
    message_type: str
    content: Dict[str, Any]
    recipients: List[str] = field(default_factory=list)  # Empty = all agents
    timestamp: datetime = field(default_factory=datetime.now)

class InterAgentCommunicator:
    """
    Manages communication between agents, enabling collaboration
    and information sharing.
    """

    def __init__(self):
        self.logger = logging.getLogger("delegate.communicator")

        # Agent registry
        self.agents: Dict[str, Any] = {}  # agent_id -> agent instance

        # Message queues
        self.message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

        # Message handlers
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Communication channels
        self.channels: Dict[str, List[str]] = defaultdict(list)

        # Message history
        self.message_history: List[Message] = []
        self.broadcast_history: List[Broadcast] = []

        # Response tracking
        self.pending_responses: Dict[str, asyncio.Future] = {}

        # Communication protocols
        self.protocols = {
            "request": self._handle_request,
            "response": self._handle_response,
            "broadcast": self._handle_broadcast,
            "collaboration": self._handle_collaboration,
            "delegation": self._handle_delegation,
            "notification": self._handle_notification
        }

        # Running state
        self.running = False
        self.message_processor_task: Optional[asyncio.Task] = None

    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent with the communication system"""
        self.agents[agent_id] = agent_instance
        self.message_queues[agent_id] = asyncio.Queue()
        self.logger.info(f"Registered agent for communication: {agent_id}")

    def subscribe_to_channel(self, agent_id: str, channel: str):
        """Subscribe an agent to a communication channel"""
        if agent_id in self.agents:
            self.channels[channel].append(agent_id)
            self.logger.info(f"Agent {agent_id} subscribed to channel: {channel}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type].append(handler)

    async def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Dict[str, Any],
        requires_response: bool = False,
        priority: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Send a message from one agent to another"""
        message_id = f"msg_{uuid.uuid4().hex[:8]}"

        message = Message(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            requires_response=requires_response,
            priority=priority
        )

        # Store in history
        self.message_history.append(message)

        # Queue the message
        await self.message_queues[recipient].put(message)

        self.logger.debug(f"Message sent: {sender} -> {recipient} [{message_type}]")

        # Wait for response if required
        if requires_response:
            future = asyncio.Future()
            self.pending_responses[message_id] = future

            try:
                response = await asyncio.wait_for(future, timeout=30)
                return response
            except asyncio.TimeoutError:
                self.logger.warning(f"Response timeout for message {message_id}")
                del self.pending_responses[message_id]
                return None

        return None

    async def broadcast(
        self,
        sender: str,
        message_type: str,
        content: Dict[str, Any],
        recipients: List[str] = None
    ):
        """Broadcast a message to multiple agents"""
        broadcast_id = f"broadcast_{uuid.uuid4().hex[:8]}"

        broadcast = Broadcast(
            broadcast_id=broadcast_id,
            sender=sender,
            message_type=message_type,
            content=content,
            recipients=recipients or []
        )

        # Store in history
        self.broadcast_history.append(broadcast)

        # Determine recipients
        target_agents = recipients if recipients else list(self.agents.keys())
        target_agents = [a for a in target_agents if a != sender]

        # Send to all recipients
        for agent_id in target_agents:
            if agent_id in self.agents:
                message = Message(
                    message_id=f"{broadcast_id}_{agent_id}",
                    sender=sender,
                    recipient=agent_id,
                    message_type="broadcast",
                    content={
                        "broadcast_type": message_type,
                        "data": content
                    },
                    priority=7  # Broadcasts have higher priority
                )

                await self.message_queues[agent_id].put(message)

        self.logger.info(f"Broadcast sent from {sender} to {len(target_agents)} agents")

    async def request_collaboration(
        self,
        requester: str,
        collaborator: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request collaboration between agents"""
        return await self.send_message(
            sender=requester,
            recipient=collaborator,
            message_type="collaboration",
            content={
                "action": "request",
                "task": task
            },
            requires_response=True,
            priority=3
        )

    async def delegate_task(
        self,
        delegator: str,
        delegate: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate a task from one agent to another"""
        return await self.send_message(
            sender=delegator,
            recipient=delegate,
            message_type="delegation",
            content={
                "task": task,
                "delegation_type": "full"
            },
            requires_response=True,
            priority=2
        )

    async def share_knowledge(
        self,
        sender: str,
        knowledge_type: str,
        knowledge_data: Dict[str, Any],
        recipients: List[str] = None
    ):
        """Share knowledge between agents"""
        await self.broadcast(
            sender=sender,
            message_type="knowledge_sharing",
            content={
                "knowledge_type": knowledge_type,
                "data": knowledge_data
            },
            recipients=recipients
        )

    async def _process_messages(self):
        """Process messages for all agents"""
        while self.running:
            try:
                # Process messages for each agent
                for agent_id, queue in self.message_queues.items():
                    if not queue.empty():
                        message = await queue.get()
                        await self._handle_message(agent_id, message)

                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error processing messages: {e}")
                await asyncio.sleep(1)

    async def _handle_message(self, agent_id: str, message: Message):
        """Handle an incoming message for an agent"""
        try:
            # Get the protocol handler
            if message.message_type in self.protocols:
                await self.protocols[message.message_type](agent_id, message)
            else:
                # Use custom handlers
                for handler in self.message_handlers.get(message.message_type, []):
                    await handler(agent_id, message)

            # Notify the agent
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                if hasattr(agent, 'handle_message'):
                    await agent.handle_message(message)

        except Exception as e:
            self.logger.error(f"Error handling message for {agent_id}: {e}")

    async def _handle_request(self, agent_id: str, message: Message):
        """Handle a request message"""
        self.logger.debug(f"Handling request for {agent_id}: {message.content}")

        # Agent should process and respond
        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # Process the request
            response_content = await self._process_agent_request(agent, message)

            # Send response if required
            if message.requires_response:
                await self._send_response(
                    message.message_id,
                    agent_id,
                    message.sender,
                    response_content
                )

    async def _handle_response(self, agent_id: str, message: Message):
        """Handle a response message"""
        correlation_id = message.correlation_id

        if correlation_id and correlation_id in self.pending_responses:
            # Complete the pending future
            self.pending_responses[correlation_id].set_result(message.content)
            del self.pending_responses[correlation_id]

    async def _handle_broadcast(self, agent_id: str, message: Message):
        """Handle a broadcast message"""
        self.logger.debug(f"Agent {agent_id} received broadcast: {message.content}")

        # Process broadcast based on type
        broadcast_type = message.content.get("broadcast_type")
        broadcast_data = message.content.get("data")

        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if hasattr(agent, 'handle_broadcast'):
                await agent.handle_broadcast(broadcast_type, broadcast_data)

    async def _handle_collaboration(self, agent_id: str, message: Message):
        """Handle collaboration requests"""
        action = message.content.get("action")
        task = message.content.get("task")

        if action == "request" and agent_id in self.agents:
            agent = self.agents[agent_id]

            # Check if agent can collaborate
            can_collaborate = True  # This would be more sophisticated in production

            response = {
                "action": "response",
                "accepted": can_collaborate,
                "agent_status": agent.status.value if hasattr(agent, 'status') else "unknown"
            }

            if message.requires_response:
                await self._send_response(
                    message.message_id,
                    agent_id,
                    message.sender,
                    response
                )

    async def _handle_delegation(self, agent_id: str, message: Message):
        """Handle task delegation"""
        task = message.content.get("task")
        delegation_type = message.content.get("delegation_type")

        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # Accept or reject delegation based on agent capacity
            can_accept = True  # This would check agent workload in production

            response = {
                "accepted": can_accept,
                "estimated_completion": "30 minutes" if can_accept else None,
                "reason": None if can_accept else "Agent at capacity"
            }

            if message.requires_response:
                await self._send_response(
                    message.message_id,
                    agent_id,
                    message.sender,
                    response
                )

            if can_accept and hasattr(agent, 'accept_delegation'):
                await agent.accept_delegation(task)

    async def _handle_notification(self, agent_id: str, message: Message):
        """Handle notification messages"""
        self.logger.info(f"Notification for {agent_id}: {message.content}")

        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if hasattr(agent, 'handle_notification'):
                await agent.handle_notification(message.content)

    async def _send_response(
        self,
        original_message_id: str,
        sender: str,
        recipient: str,
        content: Dict[str, Any]
    ):
        """Send a response to a message"""
        response_message = Message(
            message_id=f"resp_{uuid.uuid4().hex[:8]}",
            sender=sender,
            recipient=recipient,
            message_type="response",
            content=content,
            correlation_id=original_message_id,
            priority=2  # Responses have high priority
        )

        await self.message_queues[recipient].put(response_message)

    async def _process_agent_request(self, agent: Any, message: Message) -> Dict[str, Any]:
        """Process a request for an agent"""
        # This would be implemented based on agent capabilities
        return {
            "status": "processed",
            "result": f"Request processed by {agent.config.name if hasattr(agent, 'config') else 'agent'}"
        }

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        stats = {
            "total_messages": len(self.message_history),
            "total_broadcasts": len(self.broadcast_history),
            "pending_responses": len(self.pending_responses),
            "message_distribution": defaultdict(int),
            "active_channels": list(self.channels.keys())
        }

        # Calculate message distribution
        for message in self.message_history:
            stats["message_distribution"][message.message_type] += 1

        return stats

    def get_agent_communication_history(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Message]:
        """Get communication history for a specific agent"""
        agent_messages = [
            msg for msg in self.message_history
            if msg.sender == agent_id or msg.recipient == agent_id
        ]

        return agent_messages[-limit:]

    async def start(self):
        """Start the communication system"""
        self.running = True
        self.message_processor_task = asyncio.create_task(self._process_messages())
        self.logger.info("Inter-agent communication system started")

    async def stop(self):
        """Stop the communication system"""
        self.running = False

        if self.message_processor_task:
            self.message_processor_task.cancel()

        # Clear pending responses
        for future in self.pending_responses.values():
            future.cancel()

        self.pending_responses.clear()

        self.logger.info("Inter-agent communication system stopped")