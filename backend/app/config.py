# backend/app/config.py

import os
from dotenv import load_dotenv # Used to load environment variables from a .env file
                               # during local development.

# Load environment variables from a .env file.
# This function looks for a file named '.env' in the current directory or parent directories.
# Variables loaded from .env will override existing system environment variables if they have the same name.
# This is primarily for local development convenience; on Azure, Managed Identity handles authentication.
load_dotenv()

# Define a Settings class to hold our application configuration.
# Using a class helps organize settings and allows for type hinting.
class Settings:
    # Azure Subscription ID:
    # This ID is essential for the Azure SDK to know which subscription to query metrics from.
    # It's loaded from the environment variable AZURE_SUBSCRIPTION_ID.
    # The default value provided here should be replaced with your actual Azure Subscription ID.
    AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID", "a8715d58-743d-4b54-b671-230ce91aab9b") # <<< REPLACE THIS WITH YOUR ACTUAL SUBSCRIPTION ID

    # Azure Resource Group Name:
    # This specifies the resource group where our VM and other resources are located.
    # It's used to construct the resource ID for metric queries.
    AZURE_RESOURCE_GROUP_NAME: str = os.getenv("AZURE_RESOURCE_GROUP_NAME", "SmartIncidentResponseRG") # Default matches Terraform variable

    # Azure VM Name:
    # This is the name of the Virtual Machine for which we want to fetch metrics.
    AZURE_VM_NAME: str = os.getenv("AZURE_VM_NAME", "IncidentResponseVM") # Default matches Terraform variable

    # Backend API Host:
    # The IP address the FastAPI application will listen on. "0.0.0.0" means it will listen
    # on all available network interfaces, making it accessible from outside the VM.
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    # Backend API Port:
    # The port the FastAPI application will listen on. We opened port 8000 in our NSG.
    API_PORT: int = int(os.getenv("API_PORT", 8000))

# Create an instance of the Settings class.
# This instance will be imported and used throughout our FastAPI application.
settings = Settings()
