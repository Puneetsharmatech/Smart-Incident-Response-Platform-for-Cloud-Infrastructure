# azure-infra/versions.tf
terraform {
  required_version = ">= 1.0.0" # Specify your desired Terraform version

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Use a compatible AzureRM provider version
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {} # Required for the AzureRM provider
}