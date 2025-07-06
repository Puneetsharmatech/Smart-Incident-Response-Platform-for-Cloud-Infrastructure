# terraform/outputs.tf

# This file defines output values that Terraform will display after a successful
# deployment. These outputs are useful for easily retrieving important information
# about your deployed Azure resources, such as connection details.

# Output the public IP address of the Virtual Machine.
# This is the IP address you will use to access your VM from the internet (e.g., via SSH, or for your web app).
output "public_ip_address" {
  description = "The public IP address of the Incident Response VM."
  # The 'value' field references the 'ip_address' attribute of the 'azurerm_public_ip' resource
  # that we named 'main' in our main.tf file.
  value       = azurerm_public_ip.main.ip_address
}

# Output the SSH command to connect to the VM.
# This provides a ready-to-use command string for your terminal.
output "ssh_command" {
  description = "SSH command to connect to the VM."
  # It constructs the SSH command using the admin_username variable and the VM's public IP address.
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.main.ip_address}"
}

# Output the name of the resource group created.
# Useful for verifying the resource group name or for other scripts.
output "resource_group_name" {
  description = "The name of the resource group created."
  value       = azurerm_resource_group.main.name
}

