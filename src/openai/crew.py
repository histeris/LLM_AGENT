from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.Rag import data_penyakit, data_obat
import json

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
   			allow_delegation=False,
			max_iter=30
		)
		
	@agent
	def symptoms_analyzer_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['symptoms_analyzer_agent'],
			verbose=True,
			tools=[data_penyakit],
   			allow_delegation=False,
			max_iter=30
		)

	@agent
	def virtual_pharmacist_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['virtual_pharmacist_agent'],
			verbose=True,
			tools=[data_obat],
			allow_delegation=False,
			max_iter=30
		)
	
	@agent
	def output_handler_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['output_handler_agent'],
			verbose=True,
			allow_delegation=False,
			max_iter=30,
		)

	@task
	def classification_task(self) -> Task:
		return Task(
			config=self.tasks_config['classification_task'],
			output_file='classification_task_report.md'
		)
  
	@task
	def symptoms_analyzer_task(self) -> Task:
		return Task(
			config=self.tasks_config['symptoms_analyzer_task'],
			output_file='symptoms_analyzer_task_report.md'
		)

	@task
	def drug_recommendation_task(self) -> Task:
		return Task(
			config=self.tasks_config['drug_recommendation_task'],
			output_file='drug_recommendation_task_report.md'
		)
	
	@task
	def output_handler_task(self) -> Task:
		return Task(
			config=self.tasks_config['output_handler_task'],
			output_file='output_handler_task_report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Kru AI Virtual Dokter"""
		return Crew(
			agents=[
				self.classification_agent(),
				self.symptoms_analyzer_agent(),
				self.virtual_pharmacist_agent(),
				self.output_handler_agent()
			],
			tasks=[
				self.classification_task(),
				self.symptoms_analyzer_task(),
				self.drug_recommendation_task(),
				self.output_handler_task()
			],
			process=Process.sequential,
        	verbose=True,
    	)
	def run(self, inputs: dict):

		result_text = self.classification_agent().execute_task(
			self.classification_task(),
			inputs
		)

		try:
			classification_result = json.loads(result_text)
			label = classification_result.get("label", "").lower()
			data = classification_result.get("data", inputs)
		except json.JSONDecodeError:
			raise Exception("Gagal membaca hasil klasifikasi. Pastikan output dalam format JSON.")

		if label == "gejala":
			# Jalankan analisa gejala
			analysis_result = self.symptoms_analyzer_agent().execute_task(
				self.symptoms_analyzer_task(),
				data
			)

			#2. Jalankan rekomendasi obat berdasarkan hasil analisis
			drug_result = self.virtual_pharmacist_agent().execute_task(
				self.drug_recommendation_task(),
				analysis_result
			)
			final_result = {
				"analisis": analysis_result,
				"rekomendasi_obat": drug_result
			}
		elif label == "penyakit":
			# Langsung ke apoteker
			drug_result = self.virtual_pharmacist_agent().execute_task(
				self.drug_recommendation_task(),
				data
			)
			final_result = drug_result
		else:
			final_result = "Tidak dapat mengklasifikasikan input. Mohon perjelas."

		# Opsional: tampilkan hasil akhir via output handler
		self.output_handler_agent().execute_task(
			self.output_handler_task(),
			{'hasil_akhir': final_result}
		)

		return final_result

	
