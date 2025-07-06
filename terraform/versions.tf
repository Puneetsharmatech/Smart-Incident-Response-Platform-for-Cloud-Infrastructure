# terraform/versions.tf

# This block defines the required version of Terraform itself.
# It ensures that your Terraform configuration is run with a compatible version,
# preventing potential issues due to syntax or feature changes in newer/older versions.
terraform {
  required_version = ">= 1.0.0" # Specifies that Terraform version 1.0.0 or newer is required.

  # This block defines where Terraform stores its state file.
  # The state file maps real-world cloud resources to your Terraform configuration.
  # "local" means the state file (terraform.tfstate) will be stored in the current directory.
  # For production, you'd typically use a remote backend like Azure Storage Account for collaboration and safety.
  backend "local" {}
}

# This block configures the Azure Resource Manager (azurerm) provider.
# The provider is the plugin that Terraform uses to interact with Azure.
provider "azurerm" {
  # The 'features' block is required by the azurerm provider.
  # It's a placeholder for future provider-specific features or settings.
  features {}

  # Explicitly setting the subscription_id here is a robust way to ensure
  # Terraform targets the correct Azure subscription. This helps avoid
  # authentication issues if you have multiple subscriptions or if environment
  # variables aren't consistently set.
  # REPLACE THIS WITH YOUR ACTUAL AZURE SUBSCRIPTION ID IF IT'S DIFFERENT!
  subscription_id = "a8715d58-743d-4b54-b671-230ce91aab9b"
}

