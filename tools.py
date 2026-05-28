import os
import google.auth
import google.auth.transport.requests
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

"""MCP Configuration constants for the Google Cloud Ops Agent."""
MCP_SERVICES = {
    "cloud_run": {
        "prefix": "run_",
        "default_endpoint": "https://run.googleapis.com/mcp"
    },
    "kubernetes_engine": {
        "prefix": "gke_",
        "default_endpoint": "https://container.googleapis.com/mcp"
    },
    "network_management": {
        "prefix": "nic_",
        "default_endpoint": "https://networkmanagement.googleapis.com/mcp"
    },
    "gemini_cloud_assist": {
        "prefix": "gca_",
        "default_endpoint": "https://geminicloudassist.googleapis.com/mcp"
    },
    "cloud_logging": {
        "prefix": "logging_",
        "default_endpoint": "https://logging.googleapis.com/mcp"
    },
    "cloud_monitoring": {
        "prefix": "monitoring_",
        "default_endpoint": "https://monitoring.googleapis.com/mcp"
    },
    "error_reporting": {
        "prefix": "error_",
        "default_endpoint": "https://clouderrorreporting.googleapis.com/mcp"
    },
}

# Authenticate using default credentials
try:
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    credentials, _ = google.auth.default(scopes=scopes)
except Exception:
    credentials = None


def _get_dynamic_headers(context=None):
    """Provides a header containing the latest access token."""
    if credentials:
        try:
            credentials.refresh(google.auth.transport.requests.Request())
            return {"Authorization": f"Bearer {credentials.token}"}
        except Exception:
            pass
    return {}


# Instantiate and expose active toolsets directly in a list
active_mcp_toolsets = []
for name, config in MCP_SERVICES.items():
    env_key = f"MCP_ENDPOINT_{name.upper()}"
    url = os.getenv(env_key, config["default_endpoint"])
    if url:
        toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=url,
                timeout=30.0,
                sse_read_timeout=600.0
            ),
            tool_name_prefix=config["prefix"],
            header_provider=_get_dynamic_headers
        )
        active_mcp_toolsets.append(toolset)
