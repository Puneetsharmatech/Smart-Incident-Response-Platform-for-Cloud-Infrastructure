# azure-infra/variables.tf
variable "resource_group_name" {
  description = "Name of the resource group to create"
  type        = string
  default     = "SmartIncidentResponseRG"
}

variable "location" {
  description = "Azure region where resources will be deployed"
  type        = string
  default     = "eastus" # You can change this to a region closer to you
}

variable "vnet_name" {
  description = "Name of the Virtual Network"
  type        = string
  default     = "SmartIncidentResponseVNet"
}

variable "backend_subnet_name" {
  description = "Name of the subnet for the backend VM"
  type        = string
  default     = "BackendSubnet"
}

variable "database_subnet_name" {
  description = "Name of the subnet for the database VM"
  type        = string
  default     = "DatabaseSubnet"
}

variable "vm_admin_username" {
  description = "Administrator username for the VMs"
  type        = string
  default     = "adminuser"
}

variable "vm_admin_password" {
  description = "Administrator password for the VMs (should be complex)"
  type        = string
  sensitive   = true # Mark as sensitive to prevent displaying in logs
}

variable "backend_vm_name" {
  description = "Name of the backend VM"
  type        = string
  default     = "SIRPBackendVM"
}

variable "database_vm_name" {
  description = "Name of the database VM"
  type        = string
  default     = "SIRPDatabaseVM"
}

variable "vm_size" {
  description = "Size of the virtual machines"
  type        = string
  default     = "Standard_B2s" # A cost-effective size for testing/dev
}

variable "ssh_public_key" {
  description = "Public SSH key for VM authentication (e.g., ~/.ssh/id_rsa.pub)"
  type        = string
  # No default, users must provide this for secure SSH access
}