LLM Agent For Medication Purpose,

Welcome to our project powered by crewai, we make a multi agenting system that uses data from Indonesian pharmateuical dataset for our data to use them in our agenting system. our project consist of a few files with each of them have its on use, First off

1. AI-agent-clean and AI-agent.git have were added from the GitHub.

2. file .added_flags shows the data that have been vectorized using chromadb, if u delete them the files in the folder, u will need to wait approximately 10-15 min for csv to vectorized to chromadb again, .added_flags will be useful for future development if we want to train the agents.

3. knowledge is for future development for preferences in the ai_agents.

4. Src contains the main structure/core for the agent to be running, it consists of 2 folder such as config and tools

a. config have 2 files 
- agents.yaml -> this where we uses prompt engineering to make new or changes to our agents such as customizing instructions, goals, even adding a new one.
- tasks.yaml -> this consist of the task that the agents gonna do, it consists of task description, and which agents gonna do the task and the expected output form the task

b. Tools have several file consist of the tools that were used by our agents.
- Rag.py is the tools that were used for our specific agent to search through our data to help them create a more specific output.
- detect language is just a tools to detect the language we're using.

c. crew.py is where we initialize our crew and tools the crew we're using.

d. main.py where we run the whole thing and add the inputs.

e. application.py where we connect the agent to be shown to our telegram.

f. memoryParser.py parsing raw data (disease information), then convert to list of dictionary

5. .gitignore were used to ignore a few files such as api_key and the a few data which are to big to push.

6. Evaluation.ipynb are our evaluation to evaluate our agents using ragas.

7. classification_task_report.md, symptoms_analyzer_task_report.md, output_handler_task_report.md, drug_recommendation_task_report.md are the output from each agent in the format of markdown, these cant be used to evaluate each agent and identify which have a better performance.

8. df_penyakit.xlsx,data_obat_final_update.csv, data_penyakit_alodokter_cleaned.csv are used as a dataset for our agents as a tools.

9. memory.json are our chat history from our bots in telegram in json, are used to evaluate the bot overall performance.

10. pyproject.toml is a configuration standard file for python