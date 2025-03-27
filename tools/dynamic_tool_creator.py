# tools/dynamic_tool_creator.py
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Type, Union, Callable
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Import tool classes without instantiating them
try:
    from crewai_tools import (
        SerperDevTool,
        BrowserbaseLoadTool,
        CodeDocsSearchTool,
        CodeInterpreterTool,
        CSVSearchTool,
        DallETool,
        DirectorySearchTool,
        DOCXSearchTool,
        DirectoryReadTool,
        EXASearchTool,
        FileReadTool,
        FirecrawlSearchTool,
        FirecrawlCrawlWebsiteTool,
        FirecrawlScrapeWebsiteTool,
        GithubSearchTool,
        JSONSearchTool,
        LlamaIndexTool,
        MultiOnTool,
        NL2SQLTool,
        PDFSearchTool,
        PGSearchTool,
        QdrantVectorSearchTool,
        RagTool,
        ScrapeElementFromWebsiteTool,
        ScrapegraphScrapeTool,
        SeleniumScrapingTool,
        SnowflakeSearchTool,
        TXTSearchTool,
        VisionTool,
        WebsiteSearchTool,
        WeaviateVectorSearchTool,
        YoutubeChannelSearchTool,
        YoutubeVideoSearchTool,
    )
except ImportError as e:
    print(f"Warning: Error importing some crewai_tools: {e}")


    # Define fallbacks for missing tools
    class DummyTool:
        def __init__(self, *args, **kwargs):
            pass


    SerperDevTool = BrowserbaseLoadTool = CodeDocsSearchTool = DummyTool
    # Continue setting other tools to DummyTool as needed

# Try to import S3 tools, but don't fail if they're not available
try:
    from crewai_tools.aws.s3 import S3ReaderTool, S3WriterTool

    s3_reader_class = S3ReaderTool
    s3_writer_class = S3WriterTool
except ImportError:
    s3_reader_class = None
    s3_writer_class = None

# Try to import custom tools
try:
    from .linkedin_profile_search_tool import LinkedInProfileSearchTool
except ImportError:
    class LinkedInProfileSearchTool(BaseTool):
        name = "LinkedIn Profile Search Tool"
        description = "Searches for LinkedIn profiles based on keywords."

        def _run(self, *args, **kwargs):
            return "LinkedIn Profile Search Tool is not available (missing dependency)"


# Define a class for tool information to use proper type annotations
class ToolInfo(BaseModel):
    class_ref: Any  # Reference to the class
    factory: Optional[Callable] = None  # Factory function to create the instance if needed
    instance: Optional[Any] = None  # Lazily initialized instance
    required_keys: List[str]

    model_config = {
        "arbitrary_types_allowed": True
    }


# Helper function to create factory functions for tools with parameters
def db_uri_factory(cls, db_uri=''):
    return lambda: cls(db_uri=db_uri)


# Dictionary to store tool information, but not create instances yet
available_tools: Dict[str, Dict[str, Any]] = {
    "SerperDevTool": {"class_ref": SerperDevTool, "factory": None, "instance": None,
                      "required_keys": ["SERPER_API_KEY"]},
    "BrowserbaseLoadTool": {"class_ref": BrowserbaseLoadTool, "factory": None, "instance": None,
                            "required_keys": ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"]},
    "CodeDocsSearchTool": {"class_ref": CodeDocsSearchTool, "factory": None, "instance": None, "required_keys": []},
    "CodeInterpreterTool": {"class_ref": CodeInterpreterTool, "factory": None, "instance": None, "required_keys": []},
    "CSVSearchTool": {"class_ref": CSVSearchTool, "factory": None, "instance": None, "required_keys": []},
    "DallETool": {"class_ref": DallETool, "factory": None, "instance": None, "required_keys": ["OPENAI_API_KEY"]},
    "DirectorySearchTool": {"class_ref": DirectorySearchTool, "factory": None, "instance": None, "required_keys": []},
    "DOCXSearchTool": {"class_ref": DOCXSearchTool, "factory": None, "instance": None, "required_keys": []},
    "DirectoryReadTool": {"class_ref": DirectoryReadTool, "factory": None, "instance": None, "required_keys": []},
    "EXASearchTool": {"class_ref": EXASearchTool, "factory": None, "instance": None, "required_keys": ["EXA_API_KEY"]},
    "FileReadTool": {"class_ref": FileReadTool, "factory": None, "instance": None, "required_keys": []},
    "FirecrawlSearchTool": {"class_ref": FirecrawlSearchTool, "factory": None, "instance": None,
                            "required_keys": ["FIRECRAWL_API_KEY"]},
    "FirecrawlCrawlWebsiteTool": {"class_ref": FirecrawlCrawlWebsiteTool, "factory": None, "instance": None,
                                  "required_keys": ["FIRECRAWL_API_KEY"]},
    "FirecrawlScrapeWebsiteTool": {"class_ref": FirecrawlScrapeWebsiteTool, "factory": None, "instance": None,
                                   "required_keys": ["FIRECRAWL_API_KEY"]},
    "GithubSearchTool": {"class_ref": GithubSearchTool, "factory": None, "instance": None,
                         "required_keys": ["GITHUB_TOKEN"]},
    "JSONSearchTool": {"class_ref": JSONSearchTool, "factory": None, "instance": None, "required_keys": []},
    "LlamaIndexTool": {"class_ref": LlamaIndexTool, "factory": None, "instance": None, "required_keys": []},
    "MultiOnTool": {"class_ref": MultiOnTool, "factory": None, "instance": None, "required_keys": ["MULTION_API_KEY"]},
    "NL2SQLTool": {"class_ref": NL2SQLTool, "factory": db_uri_factory(NL2SQLTool), "instance": None,
                   "required_keys": []},
    "PDFSearchTool": {"class_ref": PDFSearchTool, "factory": None, "instance": None, "required_keys": []},
    "PGSearchTool": {"class_ref": PGSearchTool, "factory": db_uri_factory(PGSearchTool), "instance": None,
                     "required_keys": []},
    "QdrantVectorSearchTool": {"class_ref": QdrantVectorSearchTool, "factory": None, "instance": None,
                               "required_keys": ["QDRANT_URL", "QDRANT_API_KEY"]},
    "RagTool": {"class_ref": RagTool, "factory": None, "instance": None, "required_keys": []},
    "ScrapeElementFromWebsiteTool": {"class_ref": ScrapeElementFromWebsiteTool, "factory": None, "instance": None,
                                     "required_keys": []},
    "ScrapegraphScrapeTool": {"class_ref": ScrapegraphScrapeTool, "factory": None, "instance": None,
                              "required_keys": ["SCRAPEGRAPH_API_KEY"]},
    "SeleniumScrapingTool": {"class_ref": SeleniumScrapingTool, "factory": None, "instance": None, "required_keys": []},
    "SnowflakeSearchTool": {"class_ref": SnowflakeSearchTool, "factory": db_uri_factory(SnowflakeSearchTool),
                            "instance": None, "required_keys": []},
    "TXTSearchTool": {"class_ref": TXTSearchTool, "factory": None, "instance": None, "required_keys": []},
    "VisionTool": {"class_ref": VisionTool, "factory": None, "instance": None, "required_keys": ["OPENAI_API_KEY"]},
    "WebsiteSearchTool": {"class_ref": WebsiteSearchTool, "factory": None, "instance": None, "required_keys": []},
    "WeaviateVectorSearchTool": {"class_ref": WeaviateVectorSearchTool, "factory": None, "instance": None,
                                 "required_keys": ["WEAVIATE_CLUSTER_URL", "WEAVIATE_API_KEY"]},
    "YoutubeChannelSearchTool": {"class_ref": YoutubeChannelSearchTool, "factory": None, "instance": None,
                                 "required_keys": []},
    "YoutubeVideoSearchTool": {"class_ref": YoutubeVideoSearchTool, "factory": None, "instance": None,
                               "required_keys": []},
    "linkedin_profile_search_tool": {"class_ref": LinkedInProfileSearchTool, "factory": None, "instance": None,
                                     "required_keys": ["LINKEDIN_USERNAME", "LINKEDIN_PASSWORD"]},
}

# Add S3 tools if available
if s3_reader_class:
    available_tools["S3ReaderTool"] = {
        "class_ref": s3_reader_class,
        "factory": None,
        "instance": None,
        "required_keys": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    }

if s3_writer_class:
    available_tools["S3WriterTool"] = {
        "class_ref": s3_writer_class,
        "factory": None,
        "instance": None,
        "required_keys": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    }


# Function to safely instantiate a tool on demand
def get_tool_instance(tool_name: str) -> Optional[Any]:
    """Get or create a tool instance, checking for required environment variables."""
    if tool_name not in available_tools:
        return None

    tool_info = available_tools[tool_name]

    # Check if we already have an instance
    if tool_info["instance"] is not None:
        return tool_info["instance"]

    # Check if all required environment variables are set
    if not all(os.environ.get(key) for key in tool_info["required_keys"]):
        print(f"Skipping tool '{tool_name}' due to missing environment variables")
        return None

    # Create the instance
    try:
        if tool_info["factory"]:
            tool_info["instance"] = tool_info["factory"]()
        else:
            tool_info["instance"] = tool_info["class_ref"]()
        return tool_info["instance"]
    except Exception as e:
        print(f"Failed to instantiate tool '{tool_name}': {e}")
        return None


# Create a model for the input to the DynamicToolCreator
class DynamicToolCreatorInput(BaseModel):
    requirements: str = Field(..., description="Requirements for the task to select appropriate tools for.")


class DynamicToolCreator(BaseTool):
    """Selects tools from a predefined library based on task requirements."""
    name: str = "Dynamic Tool Selector"
    description: str = "Selects the most appropriate tools for a given task from a predefined library."
    args_schema: Type[BaseModel] = DynamicToolCreatorInput

    # Define model_config instead of Config class
    model_config = {
        "arbitrary_types_allowed": True
    }

    def _run(self, requirements):
        """Analyzes requirements and selects tools."""
        try:
            print(f"DynamicToolCreator received requirements: {requirements}")

            # Get list of available tool names that have their env vars set
            available_tool_names = [
                name for name in available_tools.keys()
                if all(os.environ.get(key) for key in available_tools[name]["required_keys"])
            ]

            # Since we can't use the LLM directly (invoke method issue), let's implement
            # a simple keyword-based tool selection algorithm
            selected_tools = []

            # Define keyword-to-tool mappings for common tools
            keyword_tools = {
                "web": ["SerperDevTool", "WebsiteSearchTool", "BrowserbaseLoadTool"],
                "search": ["SerperDevTool", "WebsiteSearchTool", "EXASearchTool"],
                "article": ["WebsiteSearchTool", "SerperDevTool"],
                "news": ["WebsiteSearchTool", "SerperDevTool"],
                "scrape": ["WebsiteSearchTool", "ScrapeElementFromWebsiteTool", "SeleniumScrapingTool"],
                "image": ["DallETool", "VisionTool"],
                "code": ["CodeDocsSearchTool", "CodeInterpreterTool"],
                "data": ["CSVSearchTool", "JSONSearchTool"],
                "file": ["FileReadTool", "DirectoryReadTool"],
                "read": ["FileReadTool", "DirectoryReadTool", "PDFSearchTool", "DOCXSearchTool"],
                "database": ["NL2SQLTool", "PGSearchTool"],
                "linkedin": ["linkedin_profile_search_tool"],
                "youtube": ["YoutubeChannelSearchTool", "YoutubeVideoSearchTool"],
                "github": ["GithubSearchTool"],
                "pdf": ["PDFSearchTool"],
                "document": ["DOCXSearchTool", "PDFSearchTool", "TXTSearchTool"],
                "directory": ["DirectorySearchTool", "DirectoryReadTool"],
                "trend": ["SerperDevTool"],
                "summary": ["SerperDevTool"],
                "electric vehicle": ["SerperDevTool", "WebsiteSearchTool"],
                "summarize": ["SerperDevTool", "WebsiteSearchTool"],
                "analysis": ["CodeInterpreterTool", "CSVSearchTool"]
            }

            # Search for keywords in requirements and add associated tools
            requirements_lower = requirements.lower()
            for keyword, tools in keyword_tools.items():
                if keyword.lower() in requirements_lower:
                    for tool in tools:
                        if tool in available_tool_names and tool not in selected_tools:
                            selected_tools.append(tool)

            # If no tools were found, default to some general-purpose tools
            if not selected_tools:
                default_tools = ["SerperDevTool", "WebsiteSearchTool"]
                for tool in default_tools:
                    if tool in available_tool_names:
                        selected_tools.append(tool)

            print(f"DynamicToolCreator selected tools: {', '.join(selected_tools)}")

            # Return comma-separated string of tool names
            return ','.join(selected_tools)

        except Exception as e:
            print(f"Error in DynamicToolCreator: {e}")
            return "SerperDevTool"  # Default fallback tool