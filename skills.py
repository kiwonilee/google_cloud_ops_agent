import os
import vertexai
from dotenv import load_dotenv
from google.adk.tools import FunctionTool

# 1. Load environment configurations dynamically at the absolute top of module loading
load_dotenv()

# 2. Centralized Eager Module Constants (Highly recommended best practice)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcp-sandbox-kwlee")
LOCATION = os.getenv("GCP_RESOURCES_LOCATION", "us-central1")


def search_skills(query: str) -> str:
  """Search for relevant skills in the Vertex AI skill registry.

  Args:
      query: The search query (e.g., 'GKE node upgrade').

  Returns:
      A list of matching skills or an error message.
  """
  print(f"\n[Skill Search] Querying registry for playbooks matching '{query}' in project '{PROJECT_ID}' ({LOCATION})...")
  
  try:
    # Initialize Vertex AI Client. SDK automatically resolves Application Default Credentials (ADC)!
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    # Call retrieve to perform semantic search
    response = client.skills.retrieve(
        query=query,
        config={"top_k": 2}
    )
    
    results = []
    results.append(f"SUCCESS: Skills retrieved successfully!")
    results.append(f"Found {len(response.retrieved_skills)} matching skills.")
    for i, retrieved in enumerate(response.retrieved_skills):
      results.append(f"  [{i+1}] Skill Name: {retrieved.skill_name}")
      results.append(f"  [{i+1}] Description: {retrieved.description}")
    return "\n".join(results)
  except Exception as e:
    return f"FAILED: Retrieve skills failed: {e}"


search_skills_tool = FunctionTool(search_skills)
