"""ADK Runner for executing agent workflows with persistence."""

from typing import Any
from uuid import UUID

from backend.app.core.session_manager import SessionManager
from backend.app.services.persistence_service import PersistenceService


class ADKRunner:
    """
    Wraps Google ADK Runner with session management and persistence.

    Coordinates ADK agent execution with SessionManager for session caching
    and PersistenceService for tracking all questions, answers, and state.
    """

    def __init__(
        self,
        session_id: UUID,
        session_manager: SessionManager,
        persistence_service: PersistenceService,
    ) -> None:
        """
        Initialize ADK Runner.

        Args:
            session_id: Unique session identifier
            session_manager: Session manager for ADK session caching
            persistence_service: Service for persisting Q&A and state
        """
        self.session_id = session_id
        self.session_manager = session_manager
        self.persistence_service = persistence_service
        self.adk_session: Any = None
        self.runner: Any = None

    async def initialize(self) -> None:
        """
        Initialize ADK runner with session.

        Creates or retrieves cached ADK session and sets up the runner
        with the greeter root agent.

        Note:
            In production with actual Google ADK:
            from google.adk import Runner
            from backend.app.agents.greeter import greeter
            self.runner = Runner(agent=greeter, session=self.adk_session)
        """
        # Get or create ADK session from cache
        self.adk_session = self.session_manager.get_or_create_session(self.session_id)

        # Placeholder: In production, create actual ADK Runner
        # For now, create a simple mock runner
        self.runner = {
            "session": self.adk_session,
            "agent": "greeter",
            "initialized": True,
        }

    async def run(self, message: str) -> dict[str, Any]:
        """
        Run agent workflow with message.

        Saves question to persistence, executes agent workflow,
        and saves answer to persistence.

        Args:
            message: User message to send to agent

        Returns:
            Dictionary with response text and execution thoughts
        """
        if not self.runner:
            await self.initialize()

        # Save question to database
        self.persistence_service.save_question(
            session_id=self.session_id,
            question_text=message,
            agent_name="user",
        )

        # Simulate agent execution
        simulation_result = await self._simulate_agent_execution(message)
        response_text = simulation_result["response"]

        # Save answer to database
        self.persistence_service.save_answer(
            session_id=self.session_id,
            agent_name="greeter",
            answer_text=response_text,
        )

        return simulation_result

    async def _simulate_agent_execution(self, message: str) -> dict[str, Any]:
        """
        Execute the real agent workflow using LiteLLM.
        """
        from litellm import completion
        from backend.app.agents.greeter import greeter
        from backend.app.agents.researcher import researcher
        from backend.app.agents.screenwriter import screenwriter
        from backend.app.agents.critic import critic
        from backend.app.config import Settings
        
        settings = Settings()
        
        thoughts = []
        context = {}
        
        # Helper to run an agent step
        async def run_agent_step(agent_name: str, agent_obj: Any, input_text: str) -> str:
            thoughts.append({
                "agent": agent_name,
                "text": f"Processing: {input_text[:50]}...",
                "status": "starting"
            })

            # Support both dict and object agent definitions
            if isinstance(agent_obj, dict):
                instruction = agent_obj.get("instruction", "")
                model = agent_obj.get("model", "gpt-3.5-turbo")
            else:
                instruction = getattr(agent_obj, "instruction", "")
                model = getattr(agent_obj, "model", "gpt-3.5-turbo")

            # Construct prompt
            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": input_text}
            ]

            try:
                masked_key = settings.LITELLM_API_KEY[:4] + "***" if settings.LITELLM_API_KEY else "None"
                print(f"DEBUG: Calling LiteLLM with base={settings.LITELLM_BASE_URL}, key={masked_key}, model={model}")

                response = completion(
                    model=model,
                    messages=messages,
                    api_base=settings.LITELLM_BASE_URL,
                    api_key=settings.LITELLM_API_KEY,
                    custom_llm_provider="openai"
                )
                content = response.choices[0].message.content

                thoughts.append({
                    "agent": agent_name,
                    "text": "Generated response",
                    "status": "completed"
                })
                return content
            except Exception as e:
                thoughts.append({
                    "agent": agent_name,
                    "text": f"Error: {str(e)}",
                    "status": "error"
                })
                return f"Error executing {agent_name}: {str(e)}"

        # 1. Greeter
        greeter_response = await run_agent_step("greeter", greeter, message)
        
        # 2. Researcher (if needed, for now we run it sequentially)
        research_query = f"Research context for: {message}"
        research_response = await run_agent_step("researcher", researcher, research_query)
        
        # 3. Screenwriter
        screenplay_input = f"Create a film concept based on this research:\n\n{research_response}"
        screenplay_response = await run_agent_step("screenwriter", screenwriter, screenplay_input)
        
        # 4. Critic
        critic_input = f"Critique this film concept:\n\n{screenplay_response}"
        critic_response = await run_agent_step("critic", critic, critic_input)
        
        final_response = f"""
# Film Concept Pitch

{screenplay_response}

---
**Critic's Notes:**
{critic_response}
"""
        
        return {
            "response": final_response,
            "thoughts": thoughts
        }

    async def save_state_snapshot(self, state: dict[str, Any]) -> None:
        """
        Save current session state snapshot.

        Args:
            state: State dictionary to snapshot
        """
        self.persistence_service.save_state_snapshot(
            session_id=self.session_id,
            state=state,
        )
