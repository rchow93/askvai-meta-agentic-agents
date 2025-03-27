# crew.py
import os
import importlib.util
import subprocess  # For executing user code
from crewai import Agent, Task, Crew, LLM  # Import LLM directly from crewai
from crewai.flow import Flow, listen, start, router
from tools.dynamic_tool_creator import DynamicToolCreator, available_tools
from typing import Union, Optional, Dict, List, Any, Callable
from pydantic import BaseModel, Field, ConfigDict

# --- Configuration (Move to a config file later) ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Get from environment variable

# --- LLM Setup ---
# Use CrewAI's LLM class instead of ChatOpenAI directly
llm = LLM(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# --- Few-Shot Prompts (Move to separate files later) ---

AGENT_PROMPT = """
You are creating an agent for a CrewAI crew. Based on the user's problem description, define the following:
* Role: A short, descriptive title for the agent (e.g., "Market Researcher", "Data Analyst").
* Goal: The agent's objective in a single, clear sentence.
* Backstory: A brief paragraph providing context and personality for the agent.
* Tools: Comma seperated list of tools needed.

Example:
User Input: I need a crew to research market trends for a new product launch.
Role: Market Research Analyst
Goal: Identify and analyze current market trends relevant to the new product.
Backstory: A seasoned market analyst with expertise in identifying emerging trends and consumer behavior.
Tools: serper_dev_tool, website_search_tool
"""

TASK_PROMPT = """
You are creating a task for a CrewAI agent. Based on the user's problem and the agent's definition, define the following:
* Description: A clear, concise description of the task. Be specific!
* Expected Output: Describe what the successful completion of the task looks like.

Example:
User Input: Research market trends for a new product launch.
Agent Role: Market Research Analyst
Agent Goal: Identify and analyze current market trends relevant to the new product.
Description: "Conduct thorough research on current market trends related to {product_category}. Identify key competitors, consumer preferences, and emerging technologies. Focus on the last 6 months."
Expected Output: "A report summarizing the key market trends, major competitors, and potential opportunities for the new product."
"""

# --- Agent Definitions for the Meta-Crew ---

requirement_analyzer = Agent(
    role='Requirement Analyst',
    goal='Understand and extract key information from the user\'s problem description.',
    backstory="""An expert analyst skilled in breaking down complex problems
    into actionable requirements for AI agents. You focus on extracting the core needs,
    data sources, and desired outcomes.""",
    verbose=True,
    llm=llm,
)

agent_creator = Agent(
    role='Agent Creator',
    goal='Create agent definitions based on the analyzed requirements.',
    backstory="""A specialist in defining AI agents. You take requirements
    and translate them into clear, concise agent roles, goals, and backstories.
    You are also good at identifying necessary tools.""",
    verbose=True,
    llm=llm,
)

task_creator = Agent(
    role='Task Creator',
    goal='Define tasks for the generated agents based on the requirements.',
    backstory="""An expert in breaking down complex objectives into
    smaller, manageable tasks for AI agents. You ensure tasks are specific,
    measurable, achievable, relevant, and time-bound (SMART).""",
    verbose=True,
    llm=llm,
)

# Add a tool creator, initially it will be basic, but later we can expand.
tool_creator = Agent(
    role='Tool Selector',
    goal='Select necessary tools for the agents and tasks from the available tools.',
    backstory="""A specialist in identifying the best tools for a given task.
    You have a comprehensive knowledge of available tools and their capabilities.""",
    verbose=True,
    llm=llm,
    tools=[DynamicToolCreator()]  # Give the tool creator its own tool!
)

code_generator = Agent(
    role='Code Generator',
    goal='Generate Python code for the new crew based on agent and task definitions.',
    backstory="""An expert Python programmer skilled in generating clean,
    efficient, and well-documented code. You take agent and task definitions
    and output a complete, runnable CrewAI crew.""",
    verbose=True,
    llm=llm,
)

# Add a supervisor agent
supervisor_agent = Agent(
    role='Crew Supervisor',
    goal='Oversee the entire crew creation process and ensure quality.',
    backstory="""A highly experienced AI project manager, responsible for
    guiding the meta-crew, making critical decisions, and ensuring the
    final output meets the user's needs.""",
    verbose=True,
    llm=llm,
    allow_delegation=True
)


# --- Task Definitions for the Meta-Crew ---

def analyze_requirements(user_input):
    return Task(
        description=f"""Analyze the following user request:
        {user_input}
        Identify the overall goal, the specific actions needed,
        any required data sources, and the expected output format.
        """,
        agent=requirement_analyzer,
        expected_output="A clear and concise summary of the user's requirements."
    )


def create_agents(requirements_summary):
    return Task(
        description=f"""Based on the requirements:
        {requirements_summary}
        Create the necessary agent definitions. Use the following prompt for each agent:\n{AGENT_PROMPT}""",
        agent=agent_creator,
        expected_output="A list of agent definitions, including role, goal, backstory, and tools."
    )


def create_tasks(requirements_summary, agent_definitions):
    return Task(
        description=f"""Based on the requirements:
        {requirements_summary}
        and the agent definitions:
        {agent_definitions}
        Create the necessary tasks for the agents. Use the following prompt for each task:\n{TASK_PROMPT}""",
        agent=task_creator,
        expected_output="A list of task definitions, including description and expected output."
    )


def select_tools(requirements_summary, agent_definitions, task_definitions):
    return Task(
        description=f"""Based on the requirements: {requirements_summary},
        agent definitions: {agent_definitions}, and task definitions: {task_definitions},
        select the necessary tools from the available tools list.  Return a comma-separated
        list of tool names.
        """,
        agent=tool_creator,
        expected_output="A comma-separated list of tool names."  # Expect a string, not a list of tools
    )


def generate_code(agent_definitions, task_definitions, tool_definitions):
    return Task(
        description=f"""Generate a complete Python script that defines and executes
        the CrewAI crew based on the following:
        Agent Definitions: {agent_definitions}
        Task Definitions: {task_definitions}
        Tool Definitions: {tool_definitions}""",  # Pass tool names
        agent=code_generator,
        expected_output="A complete, runnable Python script for the new crew."
    )


def review_and_approve(requirements, agents, tasks, tools, code):
    return Task(
        description=f"""Review the proposed CrewAI crew and provide feedback.
        User Requirements: {requirements}
        Proposed Agents: {agents}
        Proposed Tasks: {tasks}
        Proposed Tools: {tools}
        Generated Code: {code}

        Provide a concise summary of the proposed crew, including the overall goal,
        the agents and their roles, the tasks, and the selected tools.  Also
        state whether the user approves the crew for execution ('yes'), wants to save
        the code ('save'), or rejects it ('no').  If 'no', provide specific feedback
        for improvement.
        """,
        agent=supervisor_agent,  # Use the supervisor for review
        expected_output="A summary of the crew and a 'yes', 'save', or 'no' decision.",
    )


def create_custom_tool(tool_description):
    return Task(
        description=f"""Create a custom CrewAI tool based on the following description:
        {tool_description}
        Output the complete Python code for the tool.  Make sure it subclasses
        BaseTool and includes name, description, args_schema (if needed), and _run().
        """,
        agent=code_generator,
        expected_output="Python code for a custom CrewAI tool.",
    )


def generate_user_code(user_request):
    return Task(
        description=f"""Generate Python code based on the user's request:
        {user_request}
        """,
        agent=code_generator,
        expected_output="Python code that fulfills the user's request.",
    )


# --- STATE MODEL ---
# Updated to use Pydantic V2 style
class CrewCreationState(BaseModel):
    user_input: str = Field(..., description="The user's problem description.")
    request_type: str = Field(default="", description="Type of request: 'crew', 'tool', or 'code'.")
    requirements: str = Field(default="", description="Analyzed requirements from the user input.")
    agents: str = Field(default="", description="Definitions of the agents.")
    tasks: str = Field(default="", description="Definitions of the tasks.")
    tools: str = Field(default="", description="Selected tools.")
    code: str = Field(default="", description="Generated Python code for the crew or tool.")
    user_code: str = Field(default="", description="Generated Python code for the user's request.")
    approval: str = Field(default="", description="User approval ('yes', 'save' or 'no').")
    feedback: str = Field(default="", description="User feedback if approval is 'no'.")

    # Use model_config with ConfigDict for Pydantic V2
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="ignore"  # Allow extra fields for compatibility
    )


# --- FLOW DEFINITION ---
# Modified to be more compatible with CrewAI's initialization
class CrewCreationFlow(Flow):
    # Helper functions for state access
    def get_state_value(self, key, default=None):
        """Helper function to access state values regardless of state type (dict or object)"""
        if isinstance(self.state, dict):
            return self.state.get(key, default)
        else:
            return getattr(self.state, key, default)

    def set_state_value(self, key, value):
        """Helper function to set state values regardless of state type (dict or object)"""
        if isinstance(self.state, dict):
            self.state[key] = value
        else:
            setattr(self.state, key, value)

    @start()
    def start_flow(self):
        print("Starting Crew Creation Flow...")
        return "analyze_requirements"

    @listen("analyze_requirements")
    def analyze(self):
        # Debug: Print the entire state at the beginning of analysis
        print(f"DEBUG - State at beginning of analyze method: {self.state}")

        # Try to access with direct dictionary access for debugging
        if isinstance(self.state, dict) and "user_input" in self.state:
            direct_access = self.state["user_input"]
            print(f"DEBUG - Direct dictionary access found user_input: {direct_access}")
        else:
            print("DEBUG - Direct dictionary access failed. State is not a dict or doesn't contain 'user_input'")

        # Access state safely using the helper method
        user_input = self.get_state_value("user_input")
        print(f"DEBUG - get_state_value result for 'user_input': {user_input}")

        if not user_input:
            print("Error: No user input found in state")
            return "rejected"

        # Continue with the rest of the method...
        result = analyze_requirements(user_input).execute()
        self.set_state_value("requirements", result)
        print(f"Requirements Analysis: {result}")

        # VERY BASIC request type detection.  Improve this!
        if "crew" in user_input.lower():
            self.set_state_value("request_type", "crew")
            return "create_agents"
        elif "tool" in user_input.lower():
            self.set_state_value("request_type", "tool")
            return "create_custom_tool"  # We'll route directly to tool creation
        else:
            self.set_state_value("request_type", "code")
            return "generate_user_code"  # Route to general code generation

    @listen("create_agents")
    def create_agents_step(self):
        requirements = self.get_state_value("requirements")
        result = create_agents(requirements).execute()
        self.set_state_value("agents", result)
        print(f"Agents Created: {result}")
        return "create_tasks"

    @listen("create_tasks")
    def create_tasks_step(self):
        requirements = self.get_state_value("requirements")
        agents = self.get_state_value("agents")
        result = create_tasks(requirements, agents).execute()
        self.set_state_value("tasks", result)
        print(f"Tasks Created: {result}")
        return "select_tools"

    @listen("select_tools")
    def select_tools_step(self):
        requirements = self.get_state_value("requirements")
        agents = self.get_state_value("agents")
        tasks = self.get_state_value("tasks")
        result = select_tools(requirements, agents, tasks).execute()
        self.set_state_value("tools", result)
        print(f"Tools Selected: {result}")
        return "generate_code"

    @listen("generate_code")  # For Crew generation
    def generate_code_step(self):
        agents = self.get_state_value("agents")
        tasks = self.get_state_value("tasks")
        tools = self.get_state_value("tools")
        result = generate_code(agents, tasks, tools).execute()
        self.set_state_value("code", result)
        print(f"Code Generated:\n{result}")
        return "review_and_approve"

    @listen("create_custom_tool")  # Added for direct tool creation
    def create_custom_tool_step(self):
        tool_description = self.get_state_value("requirements")  # Use requirements as the description
        result = create_custom_tool(tool_description).execute()
        print(f"Custom Tool Code Generated:\n{result}")

        # DYNAMICALLY ADD THE TOOL:
        try:
            # 1. Write to a temporary file
            tool_path = "tools/temp_tool.py"
            with open(tool_path, "w") as f:
                f.write(result)

            # 2. Import the tool using importlib instead of direct import
            import importlib.util
            spec = importlib.util.spec_from_file_location("temp_tool", tool_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 3. Look for a class that subclasses BaseTool
            from crewai.tools import BaseTool
            tool_class = None
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, BaseTool) and obj != BaseTool:
                    tool_class = obj
                    break

            if not tool_class:
                raise ValueError("No BaseTool subclass found in the generated code")

            # 4. Instantiate and add to available_tools
            new_tool_instance = tool_class()  # Instantiate the new tool
            available_tools[new_tool_instance.name] = {
                "class_ref": tool_class,
                "factory": None,
                "instance": new_tool_instance,
                "required_keys": []
            }
            print(f"New tool '{new_tool_instance.name}' added to available tools.")
            self.set_state_value("tools", new_tool_instance.name)  # Update the state with the new tool name
            self.set_state_value("code", result)  # Also save the code in case the user wants to save.

        except Exception as e:
            print(f"Error creating custom tool: {e}")
            # Handle the error appropriately (e.g., set state, trigger a different path)
            return "rejected"  # Or some other error handling path

        return "review_and_approve"  # Go to review, even for tools

    @listen("generate_user_code")  # Added for general code generation
    def generate_user_code_step(self):
        user_input = self.get_state_value("user_input")
        result = generate_user_code(user_input).execute()  # Pass the user input directly
        self.set_state_value("user_code", result)  # Store the generated code
        print(f"User Code Generated:\n{result}")
        return "review_and_approve"  # Go to review for general code too.

    @listen("review_and_approve")
    def review_and_approve_step(self):
        # Get state values safely
        request_type = self.get_state_value("request_type")
        requirements = self.get_state_value("requirements")
        agents = self.get_state_value("agents", "")
        tasks = self.get_state_value("tasks", "")
        tools = self.get_state_value("tools", "")
        code = self.get_state_value("code", "")
        user_code = self.get_state_value("user_code", "")
        user_input = self.get_state_value("user_input", "")

        # Modified to handle different request types
        if request_type == "crew":
            result = review_and_approve(requirements, agents, tasks, tools, code).execute()
        elif request_type == "tool":
            result = review_and_approve(requirements, "", "", tools,
                                        code).execute()  # Pass empty strings for unused parts
        else:  # "code"
            result = review_and_approve(user_input, "", "", "",
                                        user_code).execute()  # Pass user input as requirements, and user_code

        print(f"Review and Approve: {result}")

        if "yes" in result.lower():
            self.set_state_value("approval", "yes")
            if request_type == "crew":
                return "execute_crew"  # Route to direct execution
            elif request_type == "code":
                return "run_user_code"  # New route for direct code execution
            else:  # tool
                return "save_code"  # save the tool code.
        elif "save" in result.lower():
            self.set_state_value("approval", "save")
            return "save_code"  # Route to saving the code
        else:
            self.set_state_value("approval", "no")
            self.set_state_value("feedback", result)  # Store the full feedback
            return "rejected"  # Route to feedback

    @listen("save_code")
    def save_code(self):
        request_type = self.get_state_value("request_type")
        code = self.get_state_value("code", "")
        user_code = self.get_state_value("user_code", "")

        if request_type == 'tool':
            filename = "generated_tool.py"
        else:
            filename = "generated_crew.py"

        content = code if request_type != "code" else user_code

        print(f"Approved! Saving code to {filename}")
        with open(filename, "w") as f:
            f.write(content)  # saving the crew code.
        print(f"\nCode saved to {filename}. You can run it with: python {filename}")
        return "end"

    @listen("execute_crew")
    def execute_crew(self):
        print("Crew Approved! Executing directly...")
        print("!!! WARNING: Executing dynamically generated code.  Use with extreme caution !!!")

        try:
            # Dynamically import and run the generated crew
            module_name = "generated_crew"  # Assuming the file is named generated_crew.py
            spec = importlib.util.spec_from_file_location(module_name, "generated_crew.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Assuming the crew is defined in a function called 'create_crew' within the generated code.
            if hasattr(module, 'create_crew'):  # Check if create_crew function exists
                crew_instance = module.create_crew()  # Call the function to get crew instance
                if isinstance(crew_instance, Crew):  # Check if it's a Crew instance
                    result = crew_instance.kickoff()
                    print("Generated Crew Result:", result)
                else:
                    print("Error: 'create_crew' did not return a Crew instance.")
            else:
                print("Error: 'create_crew' function not found in generated_crew.py")

        except Exception as e:
            print(f"Error executing generated crew: {e}")
        return "end"

    @listen("run_user_code")
    def run_user_code(self):
        user_code = self.get_state_value("user_code", "")

        print("User Code Approved! Executing directly...")
        print("!!! WARNING: Executing dynamically generated code. EXTREME CAUTION ADVISED !!!")
        # Use subprocess.run, NOT exec()
        try:
            # Write the code to a temporary file
            temp_file = "temp_user_code.py"
            with open(temp_file, "w") as f:
                f.write(user_code)

            # Execute the code in a separate process
            result = subprocess.run(
                ["python", temp_file], capture_output=True, text=True, check=False
            )

            print("User Code Output:")
            print(result.stdout)
            if result.stderr:
                print("User Code Errors:")
                print(result.stderr)

            # Clean up the temporary file (optional)
            os.remove(temp_file)

        except Exception as e:
            print(f"Error executing user code: {e}")
        return "end"

    @listen("rejected")
    def handle_rejection(self):
        feedback = self.get_state_value("feedback", "No feedback provided")
        print(f"Crew Rejected. Feedback: {feedback}")
        return "end"

    @router(start_flow)
    def route_flow(self):
        return "analyze_requirements"


# Add this corrected SimpleCrewFlow class to your crew.py file

# This is a fixed version of the SimpleCrewFlow class to add to your crew.py file

class SimpleCrewFlow(Flow):
    """A simplified flow that directly uses attributes for state."""

    def __init__(self, user_input: str):
        """Initialize with user input directly as an attribute."""
        super().__init__()
        self.user_input = user_input
        self.request_type = None
        self.requirements = None
        self.agents = None
        self.tasks = None
        self.tools = None
        self.code = None
        print(f"SimpleCrewFlow initialized with user input: {self.user_input}")

    @start()
    def start_flow(self):
        print(f"Starting Simple Crew Flow with user input: {self.user_input}")
        return "analyze_requirements"

    @listen("analyze_requirements")
    def analyze(self):
        print(f"Analyzing requirements for: {self.user_input}")

        # Create and run the task
        task = analyze_requirements(self.user_input)
        result = task.execute()

        self.requirements = result
        print(f"Requirements Analysis: {result}")

        # Default to crew creation unless explicitly requested otherwise
        if "tool" in self.user_input.lower():
            self.request_type = "tool"
            return "create_custom_tool"
        else:
            self.request_type = "crew"
            return "create_agents"

    @listen("create_agents")
    def create_agents_step(self):
        print(f"Creating agents based on requirements...")

        # Use the AGENT_PROMPT from the main file
        task = create_agents(self.requirements)
        result = task.execute()

        self.agents = result
        print(f"Agents Created: {result}")
        return "create_tasks"

    @listen("create_tasks")
    def create_tasks_step(self):
        print(f"Creating tasks for agents...")

        # Use the TASK_PROMPT from the main file
        task = create_tasks(self.requirements, self.agents)
        result = task.execute()

        self.tasks = result
        print(f"Tasks Created: {result}")
        return "select_tools"

    @listen("select_tools")
    def select_tools_step(self):
        print(f"Selecting appropriate tools...")

        task = select_tools(self.requirements, self.agents, self.tasks)
        result = task.execute()

        self.tools = result
        print(f"Tools Selected: {result}")
        return "generate_code"

    @listen("generate_code")
    def generate_code_step(self):
        print(f"Generating Python code for the crew...")

        task = generate_code(self.agents, self.tasks, self.tools)
        result = task.execute()

        self.code = result
        print(f"Code Generated: (length: {len(result)})")
        return "save_code"

    @listen("create_custom_tool")
    def create_custom_tool_step(self):
        print(f"Creating custom tool...")

        tool_description = self.requirements
        task = create_custom_tool(tool_description)
        result = task.execute()

        self.code = result
        print(f"Custom Tool Code Generated: (length: {len(result)})")
        return "save_code"

    @listen("save_code")
    def save_code(self):
        if self.request_type == 'tool':
            filename = "generated_tool.py"
        else:
            filename = "generated_crew.py"

        print(f"Saving code to {filename}")
        with open(filename, "w") as f:
            f.write(self.code)
        print(f"Code saved to {filename}")
        return filename  # Return the filename so main.py can report it

    @router(start_flow)
    def route_flow(self):
        return "analyze_requirements"