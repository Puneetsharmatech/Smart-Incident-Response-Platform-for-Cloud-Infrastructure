# azure-infra/outputs.tf
output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.sirp_rg.name
}

output "virtual_network_name" {
  description = "The name of the virtual network"
  value       = azurerm_virtual_network.sirp_vnet.name
}

output "backend_subnet_id" {
  description = "The ID of the backend subnet"
  value       = azurerm_subnet.backend_subnet.id
}

output "database_subnet_id" {
  description = "The ID of the database subnet"
  value       = azurerm_subnet.database_subnet.id
}

# azure-infra/outputs.tf (append this to your existing outputs.tf content)

output "backend_vm_public_ip" {
  description = "Public IP address of the Backend VM"
  value       = azurerm_public_ip.backend_vm_ip.ip_address
}

output "database_vm_public_ip" {
  description = "Public IP address of the Database VM"
  value       = azurerm_public_ip.database_vm_ip.ip_address
}

output "ssh_command_backend" {
  description = "SSH command to connect to the Backend VM"
  value       = "ssh ${var.vm_admin_username}@${azurerm_public_ip.backend_vm_ip.ip_address} -i ~/.ssh/id_rsa_sirp_project"
}

output "ssh_command_database" {
  description = "SSH command to connect to the Database VM"
  value       = "ssh ${var.vm_admin_username}@${azurerm_public_ip.database_vm_ip.ip_address} -i ~/.ssh/id_rsa_sirp_project"
}