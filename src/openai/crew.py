from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# from src.openai.tools.Rag import Search_tool, alo_dokter, halo_doc, halo_sehat, bpom_id, interaksi_obat, penyakit_alo_dokter, penyakit_halo_sehat, icd, who
from tools.rag import data_penyakit, data_obat

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class researcher():
	"""Openai crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def classification_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['classification_agent'],
			verbose=True,
   			allow_delegation=True,
			max_iter=30
		)
		
	@agent
	def analisa_penyakit(self) -> Agent:
		return Agent(
			config=self.agents_config['analisa_penyakit'],
			verbose=True,
			tools=[data_penyakit],
   			allow_delegation=True,
			max_iter=30
		)

	@agent
	def apoteker_virtual(self) -> Agent:
		return Agent(
			config=self.agents_config['apoteker_virtual'],
			verbose=True,
			tools=[data_obat],
			allow_delegation=False,
			max_iter=30
		)
	
	@agent
	def output_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['output_manager'],
			verbose=True,
			allow_delegation=False,
			max_iter=30
		)

	@task
	def classification_task(self) -> Task:
		return Task(
			config=self.tasks_config['classification_task'],
		)
  
	@task
	def analisis_penyakit_dari_gejala_task(self) -> Task:
		return Task(
			config=self.tasks_config['analisis_penyakit_dari_gejala_task'],
		)

	@task
	def rekomendasi_obat_task(self) -> Task:
		return Task(
			config=self.tasks_config['rekomendasi_obat_task'],
		)
	
	@task
	def output_manager_task(self) -> Task:
		return Task(
			config=self.tasks_config['output_manager_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Kru AI Virtual Dokter"""
		return Crew(
			agents=[
				self.classification_agent(),
				self.analisa_penyakit(),
				self.apoteker_virtual(),
				self.output_manager()
			],
			tasks=[
				self.classification_task(),
				self.analisis_penyakit_dari_gejala_task(),
				self.rekomendasi_obat_task(),
				self.output_manager_task()
			],
			process=Process.sequential,
        	verbose=True,
    	)
