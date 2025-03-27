# tools/linkedin_profile_search_tool.py

import os
import time  # Import the time module
from typing import Type, Optional, Any, Dict, ClassVar

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ValidationInfo, field_validator, ConfigDict

# Try/except for linkedin_api import as it might not be installed
try:
    from linkedin_api import Linkedin

    linkedin_api_available = True
except ImportError:
    linkedin_api_available = False
    print("Warning: linkedin_api module not available. LinkedIn Profile Search Tool will provide simulated results.")


class LinkedInProfileSearchInput(BaseModel):
    """Input schema for the LinkedInProfileSearchTool."""
    keywords: str = Field(..., description="Keywords to search for in LinkedIn profiles.")
    limit: int = Field(default=10, description="Maximum number of profiles to return.")

    # V2 style validator
    @field_validator('keywords')
    @classmethod
    def keywords_not_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or v.isspace():
            raise ValueError("Keywords cannot be empty")
        return v

    model_config = ConfigDict(
        extra='forbid',  # Don't allow extra fields
        validate_assignment=True
    )


class LinkedInProfileSearchTool(BaseTool):
    name: str = "LinkedIn Profile Search Tool"
    description: str = "Searches for LinkedIn profiles based on keywords."
    args_schema: Type[BaseModel] = LinkedInProfileSearchInput
    rate_limit_pause: int = 5  # seconds between requests.  ADJUST THIS!

    # V2 style model config
    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True
    )

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__()
        self.username = username or os.environ.get("LINKEDIN_USERNAME")
        self.password = password or os.environ.get("LINKEDIN_PASSWORD")

        if linkedin_api_available and self.username and self.password:
            try:
                self.linkedin = Linkedin(self.username, self.password)
                self.available = True
            except Exception as e:
                print(f"Error initializing LinkedIn API: {e}")
                self.available = False
        else:
            self.available = False

    def _run(self, keywords: str, limit: int = 10) -> str:
        """Executes the LinkedIn profile search."""
        if not self.available:
            return self._simulate_results(keywords, limit)

        try:
            time.sleep(self.rate_limit_pause)  # Rate limiting
            results = self.linkedin.search_people(keywords=keywords, limit=limit)
            # Convert results to a more readable format.
            formatted_results = []
            for profile in results:
                public_id = profile.get('public_id', 'No Public ID')
                name = profile.get('name', 'No Name')
                headline = profile.get('headline', 'No Headline')
                # Add more fields as needed, handling missing data gracefully
                formatted_results.append(f"Name: {name}\nPublic ID: {public_id}\nHeadline: {headline}\n---")
            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error during LinkedIn search: {e}"

    def _simulate_results(self, keywords: str, limit: int) -> str:
        """Simulates LinkedIn search results when the API is not available."""
        # Generate some fake profiles based on the keywords
        words = keywords.split()
        profiles = []

        # Create some simulated profiles
        for i in range(min(limit, 5)):
            name = f"Sample Person {i + 1}"
            headline = f"Professional in {' '.join(words[:2])} industry"
            profile = f"Name: {name}\nPublic ID: sample_id_{i + 1}\nHeadline: {headline}\n---"
            profiles.append(profile)

        note = "\n[Note: These are simulated results as the LinkedIn API is not configured]"
        return "\n".join(profiles) + note