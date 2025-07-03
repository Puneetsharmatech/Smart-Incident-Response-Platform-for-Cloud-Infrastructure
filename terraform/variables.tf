# terraform/variables.tf

# This file defines input variables for your Terraform configuration.
# Variables allow you to parameterize your infrastructure, making it reusable
# and easy to customize without modifying the core resource definitions.

# Variable for the Azure region where resources will be deployed.
# This determines the physical location of your Azure services.
variable "location" {
  description = "The Azure region where resources will be deployed."
  type        = string
  default     = "East US" # You can change this to your preferred region, e.g., "Canada Central"
}

# Variable for the name of the resource group.
# A resource group is a logical container for your Azure resources.
variable "resource_group_name" {
  description = "The name of the resource group to create."
  type        = string
  default     = "SmartIncidentResponseRG"
}

# Variable for the virtual network (VNet) name.
# A VNet is a logically isolated section of the Azure cloud, where you can launch
# Azure resources in a network that you define.
variable "vnet_name" {
  description = "The name of the Virtual Network."
  type        = string
  default     = "SmartIncidentResponseVNet"
}

# Variable for the subnet name.
# Subnets allow you to segment the VNet into smaller, isolated networks.
variable "subnet_name" {
  description = "The name of the subnet."
  type        = string
  default     = "BackendSubnet" # This subnet will host our backend VM.
}

# Variable for the Virtual Machine name.
variable "vm_name" {
  description = "The name of the Virtual Machine."
  type        = string
  default     = "IncidentResponseVM"
}

# Variable for the VM size (e.g., Standard_B2s, Standard_D2s_v3).
# This determines the number of CPUs, memory, and disk performance.
# Standard_B2s is a cost-effective choice for development.
variable "vm_size" {
  description = "The size of the Virtual Machine."
  type        = string
  default     = "Standard_B2s"
}

# Variable for the admin username for the VM.
# This will be the username you use to SSH into the Ubuntu VM.
variable "admin_username" {
  description = "The username for the administrative user on the VM."
  type        = string
  default     = "azureuser"
}

# Variable for the admin password for the VM.
# IMPORTANT: For production, always use SSH keys or Azure Key Vault for secrets.
# Marking as 'sensitive = true' prevents it from being shown in logs.
variable "admin_password" {
  description = "The password for the administrative user on the VM."
  type        = string
  sensitive   = true # Marks the variable as sensitive so it's not displayed in logs
}

# Variable for the public IP address name.
# A public IP address allows your VM to be accessible from the internet.
variable "public_ip_name" {
  description = "The name of the Public IP address."
  type        = string
  default     = "IncidentResponsePublicIP"
}

# Variable for the Network Security Group (NSG) name.
# An NSG acts as a virtual firewall, controlling inbound and outbound traffic to your VM.
variable "nsg_name" {
  description = "The name of the Network Security Group."
  type        = string
  default     = "IncidentResponseNSG"
}

