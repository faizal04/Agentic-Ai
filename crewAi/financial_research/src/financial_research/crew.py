from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from crewai.llms import cache as crewai_cache


def _skip_unsupported_cache_breakpoint(message: dict) -> dict:
    """Groq does not accept CrewAI's cache_breakpoint message property."""
    return message


# CrewAI 1.15.21 adds this field to every prompt. Its Groq adapter currently
# forwards it unchanged, which makes Groq reject every request.
crewai_cache.mark_cache_breakpoint = _skip_unsupported_cache_breakpoint


@CrewBase
class FinancialResearch():
    """FinancialResearch crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()],
            use_system_prompt=False,
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'], # type: ignore[index]
            verbose=True,
            use_system_prompt=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FinancialResearch crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
