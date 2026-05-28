import os
import sys
import vertexai
from dotenv import load_dotenv
from vertexai.agent_engines import AdkApp

# -----------------------------------------------------------------------------
# Dynamic Working Directory Alignment
# -----------------------------------------------------------------------------
# Dynamically change the current working directory (CWD) to the parent folder
# of the project root (~/workspace/agents/). This guarantees that:
# 1. The local package imports use the canonical 'google_cloud_ops_agent.agent' path.
# 2. The GenAI SDK packages the extra files preserving the 'google_cloud_ops_agent/' namespace.
# 3. The remote Control Plane successfully unpickles the agent with zero ModuleNotFoundErrors.
# -----------------------------------------------------------------------------
project_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
os.chdir(project_parent)
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

# Load configurations dynamically from .env
load_dotenv(os.path.join(project_parent, "google_cloud_ops_agent/.env"))

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcp-sandbox-kwlee")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")  # Agent Engine is deployed regionally

# 1. Initialize the modern AgentPlatform Client
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Import the SRE root agent using the fully qualified package namespace
from google_cloud_ops_agent.agent import root_agent

# 2. Wrap SRE agent inside AdkApp wrapper
adk_app = AdkApp(agent=root_agent)

# -----------------------------------------------------------------------------
# Environment variables dynamically loaded from .env
# -----------------------------------------------------------------------------
sre_env_keys = [
    "GEMINI_MODEL",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GCP_RESOURCES_LOCATION",
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY",
    "OTEL_SEMCONV_STABILITY_OPT_IN",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
]
env_vars = {key: os.environ[key] for key in sre_env_keys if key in os.environ}

# -----------------------------------------------------------------------------
# Explicitly append Production Runtime URIs to the env_vars payload dictionary
# -----------------------------------------------------------------------------
env_vars["ADK_ENABLE_FEATURES"] = "SKILL_TOOLSET"
env_vars["ADK_SESSION_SERVICE_URI"] = "agentengine://"
env_vars["ADK_MEMORY_SERVICE_URI"] = "agentengine://"
env_vars["ADK_ARTIFACT_SERVICE_URI"] = "gs://adk-sandbox-bucket"

# -----------------------------------------------------------------------------
# Production Single-Step Deployment Flow (Simultaneous Session & Memory Activation)
# -----------------------------------------------------------------------------
print(f"Deploying 'google_cloud_ops_agent' to AgentPlatform in a single step...")

# Construct the custom service account email and staging bucket dynamically
service_account_email = f"google-cloud-ops-agent-sa@{PROJECT_ID}.iam.gserviceaccount.com"
staging_bucket_uri = os.environ.get("ADK_ARTIFACT_SERVICE_URI", f"gs://adk-sandbox-bucket")

# Deploy and activate session and memory services simultaneously using the official agent=adk_app specs
remote_agent = client.agent_engines.create(
    agent=adk_app,
    config={
        "display_name": "Google Cloud Ops Agent",
        "description": "Managed AI Ops Architect for GCP SRE Operations",
        "requirements": [
            "google-genai",
            "google-auth",
            "google-adk",
            "google-cloud-aiplatform[agent_engines,adk]",
            "python-dotenv",
            "pydantic",
            "cloudpickle",
        ],
        "extra_packages": [
            "google_cloud_ops_agent/agent.py",
            "google_cloud_ops_agent/tools.py",
            "google_cloud_ops_agent/skills.py",
        ],
        "env_vars": env_vars,
        "service_account": service_account_email,
        "staging_bucket": staging_bucket_uri,
    }
)

print(f"\nSUCCESS: Agent deployed successfully to Agent Runtime!")
print(f"AgentPlatform Resource Name: {remote_agent.api_resource.name}")
print(f"To run chat sessions on this deployed agent, use the resource URI: {remote_agent.api_resource.name}")
