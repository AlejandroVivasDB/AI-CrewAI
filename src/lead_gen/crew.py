import os
from datetime import datetime
import json
from typing import Union, List, Tuple, Dict
from dotenv import load_dotenv
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
# from tools import SearchAndContents, FindSimilar, GetContents, SearchInternet, SearchInstagram, OpenPage
from langchain.chat_models import ChatOpenAI
from langchain_core.agents import AgentFinish

from lead_gen.tools.research import FindSimilar, GetContents, OpenPage, SearchAndContents, SearchInstagram, SearchInternet, SearchInternetNearCity
import yaml

load_dotenv()

@CrewBase
class SalesTeamSupportCrew:
    """Sales Team Support Crew for Dualboot Partners"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def llm(self):
        llm = ChatOpenAI(
            openai_api_key= os.getenv('OPENAI_API_KEY'),
            temperature=1,
            model_name="gpt-4"
        )
        return llm

    def step_callback(
        self,
        agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish],
        agent_name,
        *args,
    ):
        with st.chat_message("AI"):
            if isinstance(agent_output, str):
                try:
                    agent_output = json.loads(agent_output)
                except json.JSONDecodeError:
                    pass

            if isinstance(agent_output, list) and all(
                isinstance(item, tuple) for item in agent_output
            ):
                for action, description in agent_output:
                    st.write(f"Agent Name: {agent_name}")
                    st.write(f"Tool used: {getattr(action, 'tool', 'Unknown')}")
                    st.write(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}")
                    st.write(f"{getattr(action, 'log', 'Unknown')}")
                    with st.expander("Show observation"):
                        st.markdown(f"Observation\n\n{description}")

            elif isinstance(agent_output, AgentFinish):
                st.write(f"Agent Name: {agent_name}")
                output = agent_output.return_values
                st.write(f"I finished my task:\n{output['output']}")

            else:
                st.write(type(agent_output))
                st.write(agent_output)
    
    @agent
    def rag_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["rag_agent"],
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "RAG Agent"),
        )
    
    @agent
    def opportunity_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["opportunity_research_agent"],
            tools=[SearchInternet(), OpenPage()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Opportunity Research Agent"),
        )
    
    @agent
    def industry_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["industry_analyst_agent"],
            tools=[SearchInternet(), OpenPage()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Industry Analyst Agent"),
        )
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["writer_agent"],
            tools=[],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Writer Agent"),
        )
    
    @task
    def index_information_task(self) -> Task:
        return Task(
            config=self.tasks_config["index_information"],
            agent=self.rag_agent(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M')}_index_information.md",
        )

    @task
    def research_opportunities_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_opportunities"],
            agent=self.opportunity_research_agent(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M')}_research_opportunities.md",
        )
    
    @task
    def analyze_industry_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_industry"],
            agent=self.industry_analyst_agent(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M')}_analyze_industry.md",
        )
    
    @task
    def write_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_report"],
            agent=self.writer_agent(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M')}_write_report.md",
        )
  
    @crew
    def crew(self) -> Crew:
        """Creates the Sales Team Support Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2,
        )
