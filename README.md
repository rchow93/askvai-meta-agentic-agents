```markdown
# AskVAI (https://www.askvai.com) - Using AI for Good 
# CrewAI Meta-Crew: Dynamic AI Workflow Generation
# Using Agentic Agents to Democratize AI for building a more Inclusive and Accessible World.
*** Note this is still in development and not production ready. Working through a few issues. ***

## Overview

**Imagine describing a complex task to an AI, and it automatically assembles a team of specialized AI
agents, equips them with the right tools, and generates the code to execute that task. ** That's the 
vision behind the CrewAI Meta-Crew. This project is a powerful demonstration of **dynamic AI agent 
and workflow generation**, built using the [CrewAI framework](https://www.crewai.com/).

This application allows you to:

1. **Describe your problem in natural language.** This can be a high-level description of a task you 
   want to automate, a specific tool you need, or even a request for arbitrary Python code.
2. **Dynamically select LLMs.** Choose different Large Language Models (LLMs) for your worker agents 
   and your supervisor agent from a predefined list (easily extensible).
3. **Have a "Meta-Crew" of AI agents analyze your request.** This Meta-Crew is itself a CrewAI crew, 
   with specialized agents for:
    * Understanding your requirements.
    * Generating agent definitions (role, goal, backstory).
    * Generating task definitions.
    * Selecting appropriate tools from a built-in library.
    * *Potentially* generating custom CrewAI tools if needed (currently a framework, code generation 
      itself is a placeholder).
    * Generating the complete, runnable Python code for a *new* CrewAI crew tailored to your request.
    * Reviewing and approving the generated crew/tool/code.
4. **Choose what to do with the generated code:**
    * **Save:** Save the generated Python code to a file (`generated_crew.py` for crews, 
      `tools/generated_tool.py` for tools). This is the **safest and recommended** option.
    * **Run (USE WITH EXTREME CAUTION):** Directly execute the generated code within the current process. 
      This is for demonstration/development *only* and carries significant security risks.
    * **Reject:** Discard the generated code and provide feedback (currently, feedback is only logged).

This project is inspired by the need for:

* **Rapid AI Workflow Prototyping:** Quickly create and test AI-powered workflows without extensive 
  manual coding.
* **Adaptable AI Systems:** Build systems that can handle a wide range of tasks by dynamically assembling 
  the necessary components.
* **Democratization of AI:** Lower the barrier to entry for creating sophisticated AI agent teams.
* **Automation of Automation:** Automate the *creation* of AI workflows, not just the tasks within them.
* **Exploration:** Provide a sandbox for exploring the capabilities of CrewAI and LLMs.

**THIS IS NOT A PRODUCTION-READY APPLICATION.** It's a proof-of-concept and demonstration of advanced CrewAI 
features. The dynamic code execution features, in particular, are *extremely risky* and should *never* be used 
in a production environment without robust sandboxing and security measures.

## How it Improves User Productivity

This Meta-Crew approach offers significant productivity benefits:

* **Drastically Reduced Development Time:** Go from a natural language problem description to a working 
  (or nearly working) CrewAI crew in minutes, instead of hours or days.
* **Flexibility and Adaptability:** The system can handle a wide range of tasks because it dynamically 
  creates agents, selects tools, and generates code.
* **Simplified Workflow Design:** You don't need to manually define every agent, task, and tool. The 
  Meta-Crew handles the complexity.
* **Empowerment of Non-Programmers:** The natural language interface makes it easier for users with less 
  coding experience to leverage the power of multi-agent AI.
* **Rapid Iteration and Experimentation:** Quickly test different crew configurations, agent roles, and 
  task structures. The review/approval/rejection loop allows for iterative refinement.
* **Automation of Repetitive Tasks:** Once a crew is generated and validated, it can be used to automate 
  repetitive tasks, freeing up human time. The *Meta-Crew* itself automates the *creation* of these automation tools.
* **Dynamic Tool Selection:** The `DynamicToolCreator` agent automatically selects the best tools for the job 
  from a predefined library, saving you the effort of manually configuring tools. It also includes a mechanism 
  to signal when a *new* tool needs to be created.
* **Custom Tool Creation (Framework):** The system is designed to support the dynamic creation of *new* tools, 
  further increasing flexibility (currently a placeholder for the code generation part).
* **LLM Choice:** You can choose different LLMs for the worker agents and the supervisor agent, optimizing for 
  cost and performance.

## Project Structure

```
meta_crew_project/
├── config/ # YAML configuration files (for the generated crew)
│   ├── agents.yaml # Agent definitions (will be populated by the meta-crew)
│   └── tasks.yaml # Task definitions (will be populated by the meta-crew)
├── tools/ # Custom tools
│   ├── __init__.py # Makes 'tools' a package, defines available tools
│   ├── dynamic_tool_creator.py # The DynamicToolCreator tool
│   └── linkedin_profile_search_tool.py # Example custom tool
├── crew.py # Meta-Crew definition (agents, tasks, flow) + Target Crew
├── llms.py # Defines available LLMs and the get_llm function
└── .env # Environment variables (API keys)
```

* **`config/`:** This directory contains YAML files that define the structure of the *generated* crew 
(the `MarketingPostsCrew` in this example). The Meta-Crew will use these as a *template* when generating
 new crews. You can modify these files to change the default structure of the generated crews. *These are 
 NOT used by the Meta-Crew itself.*
* **`tools/`:** This directory contains custom tools.
    * `dynamic_tool_creator.py`: The `DynamicToolCreator` class, which selects tools from the `available_tools` 
    dictionary (defined in `tools/__init__.py`). It also includes the logic to *signal* when a new tool needs to 
    be created.
    * `linkedin_profile_search_tool.py`: An example custom tool for searching LinkedIn profiles. This demonstrates 
    how to create a `BaseTool` subclass. It's included in the `available_tools` library.
    * `__init__.py`: Makes the `tools` directory a Python package. It also defines the `available_tools` dictionary, 
    which is the "toolbox" of pre-built tools. This is where you would add any custom tools you create.
* **`crew.py`:** This file now contains *two* main parts:
    * **`CrewCreationFlow`:** This class defines the *Meta-Crew* itself. It uses CrewAI Flows to manage the entire 
    workflow of analyzing user input, generating agent/task/tool definitions, generating code, and handling user interaction.
    * **`MarketingPostsCrew`:** This class defines the *target* crew – the type of crew that the Meta-Crew will 
    generate code *for*. It's a concrete example of a CrewAI crew. The Meta-Crew's `code_generator` agent will use this 
    (and the YAML files) as a template to generate code for new crews.
* **`llms.py`:** This file defines the available LLMs and provides a function (`get_llm`) to instantiate them based on 
user selection. This makes it easy to add new LLMs or change the default configurations.
* **`.env`:** Stores sensitive information, like your OpenAI API key and LinkedIn credentials. *Do not commit this 
file to version control.*

## Dependencies

```bash
pip install crewai crewai-tools langchain-openai python-dotenv linkedin_api requests beautifulsoup4
```

* **crewai:** The core CrewAI framework.
* **crewai-tools:** Provides pre-built tools and the base classes for creating custom tools.
* **langchain-openai:** For interacting with OpenAI's LLMs (you can adapt this to use other LLM providers, 
like Ollama).
* **python-dotenv:** For loading environment variables from the .env file.
* **pydantic:** Used for data validation and defining the structure of the flow's state.
* **importlib:** Used for dynamically importing the generated code (used with extreme caution).
* **linkedin-api:** Used by the LinkedInProfileSearchTool.
* **requests:** Used by the LinkedInProfileSearchTool for making HTTP requests.
* **beautifulsoup4:** Used by the LinkedInProfileSearchTool for parsing HTML.

## Setup

### Clone the Repository (if applicable):

```bash
git clone <your_repository_url>
cd <your_repository_name>
```

### Install Dependencies:

```bash
pip install -r requirements.txt  # If you have a requirements.txt
```

(Or use `uv` as described in the CrewAI documentation: `uv pip install ...`)

### Set Environment Variables:

Create a `.env` file in the root directory of your project and add your API keys and credentials:

```
OPENAI_API_KEY=your_actual_openai_api_key
LINKEDIN_USERNAME=your_linkedin_username
LINKEDIN_PASSWORD=your_linkedin_password
# Add other API keys as needed by your tools (e.g., SERPER_API_KEY)
```

Replace the placeholders with your actual API keys and credentials. Never commit your `.env` 
file to version control.

### Install CrewAI Tools:

```bash
crewai install
```

## Running the Application

Navigate to the project directory: Make sure you're in the `meta_crew_project` directory in your terminal.

Run `crew.py`:

```bash
python crew.py
```

### Provide Input:

The script will first prompt you to select LLMs:

* It will display a numbered list of available LLMs (defined in `llms.py`).
* Enter the number corresponding to the LLM you want to use for the worker agents.
* Enter the number corresponding to the LLM you want to use for the supervisor agent.

Then, the script will prompt you to enter a description of the problem you want to solve 
(or the code/tool you want to generate). For example:

* To create a crew: "I need a crew to find LinkedIn profiles of software engineers in London and 
extract their skills."
* To create a tool: "Create a tool to translate text from English to French."
* To generate code: "Write a Python function that takes a list of numbers and returns the sum."

### Review and Approve:

The script will print a summary of the proposed crew (or tool, or code) and ask for your approval. 
You have three options:

* **yes:**
    * If you requested a crew, the generated crew will be executed directly. A strong warning 
  will be displayed before execution. The output of the generated crew will be printed to the console.
    * If you requested a tool, the generated tool code will be saved to `tools/temp_tool.py`, dynamically 
  imported, and added to the `available_tools` dictionary.
    * If you requested general code, the code will be executed directly. A very strong warning will be displayed.
* **save:** The generated code (for a crew or a tool) will be saved to a file (`generated_crew.py` for crews, 
`tools/temp_tool.py` for tools). You can then review the code and run it manually.
* **no:** The process will terminate, and feedback (if any) will be displayed.

## Code Walkthrough

### `llms.py`:

This file defines the available LLMs and how to instantiate them.

* **available_llms:** A dictionary mapping user-friendly names (like "openai[gpt-4o-mini]") to LLM 
configurations. Each configuration includes:
    * **provider:** The LLM provider (e.g., "openai", "ollama").
    * **model:** The specific model name.
    * **class:** The class to use to instantiate the LLM (e.g., `ChatOpenAI`, `Ollama`).
    * **default_kwargs:** Default keyword arguments for the LLM constructor (e.g., temperature, base_url).
* **get_llm(llm_choice, \*\*kwargs):** This function takes the user's LLM choice and any additional keyword 
arguments, instantiates the correct LLM class, and returns the LLM instance.

### `tools/dynamic_tool_creator.py`:

This is the key to dynamic tool selection.

* **available_tools:** A dictionary mapping tool names to dictionaries containing the tool instance and a list 
of required environment variables (`required_keys`). This is how the system knows which API keys are needed for each tool.
* **DynamicToolCreator:**
    * **_run(self, requirements: str) -> list:** This method first filters `available_tools` to include only 
  tools for which all required environment variables are set. Then, it uses an LLM prompt to select tools based 
  on the task requirements. If no suitable tools are found, it returns a string starting with "CREATE_TOOL:", 
  signaling that a new tool should be created.

### `tools/linkedin_profile_search_tool.py`:

An example custom tool that demonstrates how to integrate with an external API (in this case, the unofficial 
`linkedin-api`). It includes:

* Input validation using Pydantic.
* Authentication using environment variables.
* Rate limiting (using `time.sleep`).
* Error handling.

### `crew.py`:

This file defines the `CrewCreationFlow` class, which orchestrates the entire Meta-Crew using CrewAI Flows.

* **CrewCreationState:** A Pydantic model that defines the state of the flow. This is how data is passed between the 
different steps (tasks).
* **@start, @listen, @router:** These decorators define the flow logic.
* **Agents:** The Meta-Crew agents (`requirement_analyzer`, `agent_creator`, etc.) are defined. The LLMs for these 
agents are set dynamically based on user input.
* **Tasks:** The tasks are defined and chained together.
* **select_llms:** This method prompts the user to choose LLMs.
* **create_custom_tool_step:** This method handles dynamic tool creation (currently a placeholder).
* **review_and_approve_step:** This method presents the generated information to the user and gets their approval.
* **execute_crew:** This method dynamically imports and executes the generated crew code (with strong warnings).
* **run_user_code:** This method directly executes user-provided code (with even stronger warnings).
* **handle_rejection:** Handles the case where the user rejects the generated output.

### `main.py`:

The entry point. It gets user input, creates a `CrewCreationFlow` instance, and starts the flow.

## LinkedIn Tool: Important Considerations

The `LinkedInProfileSearchTool` uses the `linkedin-api` library, which is unofficial and may violate LinkedIn's terms 
of service. Use it responsibly and ethically, and be aware of the risks (account suspension or banning). Implement 
robust rate limiting and error handling. Consider using an alternative data source or a paid API if you need reliable 
and compliant access to LinkedIn data.

## Security Warning (EXTREMELY IMPORTANT)

This project includes features for dynamically generating and executing code. This is inherently risky and should be 
used with extreme caution.

* Never run generated code directly in a production environment.
* Always review the generated code carefully before executing it.
* Use a sandboxed environment (like a Docker container) to isolate the generated code. This is not implemented in the 
current code, but it's essential for any real-world use.
* Sanitize and validate user input to prevent prompt injection attacks.
* Consider using a less powerful LLM for code generation to reduce the risk of malicious code.
* The "run" option is provided for demonstration and development purposes only.
* The best approach is to avoid executing generated code directly whenever possible. Always save the code to a file 
and have a human review it before execution.

## Future Improvements

* **Robust Code Generation:** Implement the `generate_code` task to generate complete, runnable CrewAI code. This 
will involve creating a template and using the LLM to fill in the details. This is a major area for development.
* **Advanced Tool Creation:** Implement the `create_custom_tool` task to generate new tools based on descriptions. 
This is a complex task that will require careful prompt engineering and potentially multiple LLM calls.
* **Improved Error Handling:** Add more comprehensive error handling throughout the application.
* **User Interface:** Create a user-friendly interface (e.g., using Streamlit) to make the application easier to use.
* **Feedback Loop:** Implement a feedback loop where the user can provide feedback on the generated crew/tool/code, 
and the system can use that feedback to improve its performance.
* **Sandboxing:** Integrate a sandboxing mechanism (e.g., Docker) to safely execute generated code.
* **More Robust Request Type Detection:** Improve the logic in the `analyze` method to more accurately determine 
whether the user is requesting a crew, a tool, or general code. Consider using a dedicated agent for this.
* **Pydantic Output for `review_and_approve`:** Use a Pydantic model to define the expected output structure for 
the `review_and_approve` task. This will make the parsing of the user's response much more robust.
* **More sophisticated tool selection prompt:** Improve the prompt engineering for the `DynamicToolCreator` to 
make it more reliable and to handle more complex tool selection scenarios.
* **YAML Generation:** Instead of generating Python code directly, generate YAML configuration files for the 
agents and tasks. This might be easier for the LLM and more maintainable.
* **Agent Memory:** Explore using agent memory to allow the Meta-Crew to learn from past interactions and 
improve its performance over time.
```