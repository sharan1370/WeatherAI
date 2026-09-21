from crewai import Crew, Process
#crew-creates the workflows
#Controls how tasks are executed
from agents.weather_agents import weather_agent #importing the weather afent
from tasks.weather_tasks import weather_task#importing the weather task
weather_crew = Crew(
    agents=[
        weather_agent,
    ],
    tasks=[
        weather_task,
    ],
    process=Process.sequential,
    verbose=True,
)
