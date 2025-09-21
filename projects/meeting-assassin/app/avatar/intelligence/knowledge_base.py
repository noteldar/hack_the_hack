"""
Knowledge Base System - Vector database for avatar's knowledge
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import logging
from datetime import datetime
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeEntry:
    """A single knowledge entry"""
    id: str
    content: str
    source: str
    category: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    relevance_score: float = 1.0


@dataclass
class SearchResult:
    """Search result from knowledge base"""
    entry: KnowledgeEntry
    score: float
    context: str = ""


class KnowledgeBase:
    """
    Vector-based knowledge management system for meeting context
    """

    def __init__(
        self,
        collection_name: str = "meeting_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize knowledge base"""
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./avatar_knowledge"
        ))

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

        # Initialize embedding model
        self.embedder = SentenceTransformer(embedding_model)

        # Knowledge categories
        self.categories = {
            "company": "Company information and policies",
            "project": "Project details and requirements",
            "personal": "Personal preferences and history",
            "technical": "Technical documentation and specs",
            "meeting": "Previous meeting notes and decisions",
            "contact": "Contact information and relationships"
        }

        # Cache for frequently accessed knowledge
        self.cache: Dict[str, KnowledgeEntry] = {}

    async def add_knowledge(
        self,
        content: str,
        source: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add new knowledge to the base"""
        try:
            # Generate ID
            entry_id = self._generate_id(content)

            # Check if already exists
            if self._exists(entry_id):
                logger.info(f"Knowledge already exists: {entry_id}")
                return entry_id

            # Create embedding
            embedding = self.embedder.encode(content).tolist()

            # Add to ChromaDB
            self.collection.add(
                documents=[content],
                embeddings=[embedding],
                ids=[entry_id],
                metadatas=[{
                    "source": source,
                    "category": category,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }]
            )

            # Create entry
            entry = KnowledgeEntry(
                id=entry_id,
                content=content,
                source=source,
                category=category,
                timestamp=datetime.now(),
                metadata=metadata or {},
                embedding=np.array(embedding)
            )

            # Cache if frequently used category
            if category in ["personal", "company"]:
                self.cache[entry_id] = entry

            logger.info(f"Added knowledge: {entry_id} in category {category}")
            return entry_id

        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            return ""

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search knowledge base"""
        try:
            # Create query embedding
            query_embedding = self.embedder.encode(query).tolist()

            # Prepare filter
            where = {"category": category} if category else None

            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where
            )

            # Process results
            search_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    score = 1.0 - results["distances"][0][i]  # Convert distance to similarity

                    if score >= threshold:
                        metadata = results["metadatas"][0][i]
                        entry = KnowledgeEntry(
                            id=results["ids"][0][i],
                            content=doc,
                            source=metadata.get("source", ""),
                            category=metadata.get("category", ""),
                            timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                            metadata=metadata,
                            relevance_score=score
                        )

                        search_results.append(SearchResult(
                            entry=entry,
                            score=score,
                            context=self._extract_context(doc, query)
                        ))

            return sorted(search_results, key=lambda x: x.score, reverse=True)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def load_context(self, meeting_context: Any) -> None:
        """Load relevant knowledge for meeting context"""
        try:
            # Load company knowledge
            await self._load_category_knowledge("company")

            # Load project knowledge if relevant
            if hasattr(meeting_context, 'title'):
                project_results = await self.search(
                    meeting_context.title,
                    category="project",
                    limit=10
                )
                for result in project_results:
                    self.cache[result.entry.id] = result.entry

            # Load meeting history
            if hasattr(meeting_context, 'previous_meeting_ref'):
                meeting_results = await self.search(
                    f"meeting {meeting_context.previous_meeting_ref}",
                    category="meeting",
                    limit=5
                )
                for result in meeting_results:
                    self.cache[result.entry.id] = result.entry

            logger.info(f"Loaded {len(self.cache)} knowledge entries for meeting")

        except Exception as e:
            logger.error(f"Failed to load meeting context: {e}")

    async def _load_category_knowledge(self, category: str) -> None:
        """Load all knowledge from a category"""
        try:
            results = self.collection.get(
                where={"category": category}
            )

            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i]
                    entry = KnowledgeEntry(
                        id=results["ids"][i],
                        content=doc,
                        source=metadata.get("source", ""),
                        category=category,
                        timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                        metadata=metadata
                    )
                    self.cache[entry.id] = entry

        except Exception as e:
            logger.error(f"Failed to load category {category}: {e}")

    def get_relevant_knowledge(self, topic: str, limit: int = 3) -> List[KnowledgeEntry]:
        """Get relevant knowledge from cache"""
        if not self.cache:
            return []

        # Simple relevance scoring based on content matching
        scored_entries = []
        topic_lower = topic.lower()

        for entry in self.cache.values():
            score = self._calculate_relevance(entry.content.lower(), topic_lower)
            if score > 0:
                scored_entries.append((score, entry))

        # Sort by score and return top entries
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in scored_entries[:limit]]

    def _calculate_relevance(self, content: str, topic: str) -> float:
        """Calculate relevance score"""
        # Simple keyword matching (would use better NLP in production)
        words = topic.split()
        matches = sum(1 for word in words if word in content)
        return matches / len(words) if words else 0.0

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _exists(self, entry_id: str) -> bool:
        """Check if entry exists"""
        try:
            result = self.collection.get(ids=[entry_id])
            return len(result["documents"]) > 0
        except:
            return False

    def _extract_context(self, content: str, query: str) -> str:
        """Extract relevant context from content"""
        # Find most relevant sentence
        sentences = content.split('. ')
        query_lower = query.lower()

        best_sentence = ""
        best_score = 0

        for sentence in sentences:
            score = self._calculate_relevance(sentence.lower(), query_lower)
            if score > best_score:
                best_score = score
                best_sentence = sentence

        return best_sentence

    async def update_from_meeting(
        self,
        transcript: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        action_items: List[Dict[str, Any]]
    ) -> None:
        """Update knowledge base from meeting results"""
        try:
            # Add decisions as knowledge
            for decision in decisions:
                await self.add_knowledge(
                    content=decision.get("decision", ""),
                    source="meeting",
                    category="meeting",
                    metadata={
                        "type": "decision",
                        "speaker": decision.get("speaker", ""),
                        "timestamp": decision.get("timestamp", "")
                    }
                )

            # Add action items
            for action in action_items:
                await self.add_knowledge(
                    content=action.get("text", ""),
                    source="meeting",
                    category="project",
                    metadata={
                        "type": "action_item",
                        "assigned_to": action.get("speaker", ""),
                        "timestamp": action.get("timestamp", "")
                    }
                )

            # Add important discussion points
            important_points = self._extract_important_points(transcript)
            for point in important_points:
                await self.add_knowledge(
                    content=point,
                    source="meeting_discussion",
                    category="meeting",
                    metadata={"type": "discussion_point"}
                )

            logger.info("Knowledge base updated from meeting")

        except Exception as e:
            logger.error(f"Failed to update from meeting: {e}")

    def _extract_important_points(self, transcript: List[Dict[str, Any]]) -> List[str]:
        """Extract important points from transcript"""
        important_points = []

        keywords = ["important", "critical", "key", "must", "priority", "deadline"]

        for entry in transcript:
            text = entry.get("text", "").lower()
            if any(keyword in text for keyword in keywords):
                important_points.append(entry.get("text", ""))

        return important_points[:5]  # Limit to top 5

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            total_entries = self.collection.count()

            # Count by category
            category_counts = {}
            for category in self.categories:
                results = self.collection.get(where={"category": category})
                category_counts[category] = len(results["documents"]) if results["documents"] else 0

            return {
                "total_entries": total_entries,
                "categories": category_counts,
                "cache_size": len(self.cache),
                "embedding_model": self.embedder.get_sentence_embedding_dimension()
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def export_knowledge(self) -> List[Dict[str, Any]]:
        """Export all knowledge as JSON"""
        try:
            results = self.collection.get()

            knowledge_list = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i]
                    knowledge_list.append({
                        "id": results["ids"][i],
                        "content": doc,
                        "metadata": metadata
                    })

            return knowledge_list

        except Exception as e:
            logger.error(f"Failed to export knowledge: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear knowledge cache"""
        self.cache.clear()


# Preset knowledge templates
class KnowledgeTemplates:
    @staticmethod
    def company_basics(company_name: str, industry: str) -> List[Dict[str, str]]:
        """Generate basic company knowledge"""
        return [
            {
                "content": f"{company_name} operates in the {industry} industry.",
                "source": "company_info",
                "category": "company"
            },
            {
                "content": f"Our company values innovation, collaboration, and customer success.",
                "source": "company_culture",
                "category": "company"
            },
            {
                "content": f"Standard meeting protocol includes agenda review, discussion, and action items.",
                "source": "meeting_protocol",
                "category": "company"
            }
        ]

    @staticmethod
    def personal_preferences(name: str, role: str) -> List[Dict[str, str]]:
        """Generate personal preference knowledge"""
        return [
            {
                "content": f"I am {name}, {role}.",
                "source": "personal",
                "category": "personal"
            },
            {
                "content": "I prefer data-driven decisions with clear metrics.",
                "source": "decision_style",
                "category": "personal"
            },
            {
                "content": "I value efficiency and clear communication in meetings.",
                "source": "meeting_preferences",
                "category": "personal"
            }
        ]