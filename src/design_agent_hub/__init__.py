"""Design Agent Hub: provider-neutral design workflow tools."""

from dotenv import load_dotenv

# Load local development settings for both the REST API and MCP process.
# Production deployments should inject environment variables from a secret manager.
load_dotenv()

__version__ = "0.1.0"
