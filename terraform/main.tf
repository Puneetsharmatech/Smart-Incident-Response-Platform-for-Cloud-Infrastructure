# terraform/main.tf

# This file defines all the Azure resources that Terraform will create and manage.
# It uses the variables defined in variables.tf for customization.

# 1. Configure the Azure Resource Group
# A resource group is a logical container for related Azure resources.
# It helps organize your infrastructure and manage it as a single unit.
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name # Uses the resource_group_name variable
  location = var.location            # Uses the location variable
  tags = {
    Project   = "SmartIncidentResponse" # Tags help categorize and identify resources
    ManagedBy = "Terraform"
  }
}

# 2. Create a Virtual Network (VNet)
# A VNet is a logically isolated network in Azure. It's your private cloud network.
resource "azurerm_virtual_network" "main" {
  name                = var.vnet_name           # Uses the vnet_name variable
  address_space       = ["10.0.0.0/16"]         # Defines the IP address range for the VNet (a large range)
  location            = azurerm_resource_group.main.location # Inherits location from the resource group
  resource_group_name = azurerm_resource_group.main.name     # Links to the resource group
  tags = {
    Project = "SmartIncidentResponse"
  }
}

# 3. Create a Subnet within the VNet
# Subnets allow you to segment your VNet's IP address space into smaller, manageable parts.
# Our VM will be placed in this subnet.
resource "azurerm_subnet" "main" {
  name                 = var.subnet_name                    # Uses the subnet_name variable
  resource_group_name  = azurerm_resource_group.main.name   # Links to the resource group
  virtual_network_name = azurerm_virtual_network.main.name  # Links to the VNet
  address_prefixes     = ["10.0.1.0/24"]                    # Defines the IP address range for this specific subnet
}

# 4. Create a Public IP Address for the VM
# A Public IP address allows your VM to be accessible from the internet.
resource "azurerm_public_ip" "main" {
  name                = var.public_ip_name          # Uses the public_ip_name variable
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static" # "Static" ensures the IP address doesn't change after restarts.
  sku                 = "Basic"  # "Basic" SKU is sufficient for development and testing.
  tags = {
    Project = "SmartIncidentResponse"
  }
}

# 5. Create a Network Security Group (NSG)
# An NSG acts as a virtual firewall for your VM, controlling inbound and outbound network traffic.
resource "azurerm_network_security_group" "main" {
  name                = var.nsg_name            # Uses the nsg_name variable
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags = {
    Project = "SmartIncidentResponse"
  }

  # Security Rule: Allow SSH (Port 22) access
  # This rule allows you to connect to your VM via SSH from any IP address.
  # IMPORTANT: For production environments, restrict 'source_address_prefix' to known IPs or VPN ranges for security.
  security_rule {
    name                       = "AllowSSH"
    priority                   = 100 # Rules are processed in order of priority (lower number = higher priority)
    direction                  = "Inbound" # Applies to incoming traffic
    access                     = "Allow"   # Action to take (Allow or Deny)
    protocol                   = "Tcp"     # Protocol (Tcp, Udp, Icmp, or *)
    source_port_range          = "*"       # Any source port
    destination_port_range     = "22"      # Target port for SSH
    source_address_prefix      = "*"       # Allow from any source IP address (for ease of setup)
    destination_address_prefix = "*"       # Apply to any destination IP address within the NSG's scope
  }

  # Security Rule: Allow HTTP (Port 80) access
  # For our frontend or any web server running on the VM.
  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Security Rule: Allow HTTPS (Port 443) access
  # For secure web server traffic.
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Security Rule: Allow FastAPI (Port 8000) access
  # This is the port our Python FastAPI backend will listen on.
  security_rule {
    name                       = "AllowFastAPI"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# 6. Create a Network Interface for the VM
# A network interface allows a VM to communicate with other resources in Azure and the internet.
resource "azurerm_network_interface" "main" {
  name                = "${var.vm_name}-nic" # Naming convention for the NIC
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags = {
    Project = "SmartIncidentResponse"
  }

  ip_configuration {
    name                          = "internal" # Name of the IP configuration
    subnet_id                     = azurerm_subnet.main.id # Associates with our subnet
    private_ip_address_allocation = "Dynamic" # Assigns a private IP dynamically from the subnet
    public_ip_address_id          = azurerm_public_ip.main.id # Associates with our public IP
  }
}

# 7. Associate the NSG with the Network Interface
# This step applies the firewall rules defined in the NSG to our VM's network interface.
resource "azurerm_network_interface_security_group_association" "main" {
  network_interface_id      = azurerm_network_interface.main.id # Links to the network interface
  network_security_group_id = azurerm_network_security_group.main.id # Links to the NSG
}

# 8. Create the Virtual Machine (Ubuntu 24.04 LTS)
# This is the actual server where our backend application will run.
resource "azurerm_linux_virtual_machine" "main" {
  name                  = var.vm_name             # Uses the vm_name variable
  resource_group_name   = azurerm_resource_group.main.name
  location              = azurerm_resource_group.main.location
  size                  = var.vm_size             # Uses the vm_size variable (e.g., Standard_B2s)
  admin_username        = var.admin_username      # Uses the admin_username variable
  admin_password        = var.admin_password      # Uses the admin_password variable
  disable_password_authentication = false # Set to true if you were using SSH keys instead of password

  network_interface_ids = [
    azurerm_network_interface.main.id, # Attaches the network interface to the VM
  ]

  # OS Disk configuration for the VM
  os_disk {
    caching              = "ReadWrite"        # Caching settings for performance
    storage_account_type = "Standard_LRS"     # Storage type: Standard Locally Redundant Storage (cost-effective)
  }

  # Source Image Reference: Specifies the operating system image to use.
  # We are explicitly selecting Ubuntu 24.04 LTS (Noble Numbat).
  source_image_reference {
    publisher = "Canonical"                 # The publisher of the image (Ubuntu's official publisher)
    offer     = "0001-com-ubuntu-server-jammy" # The offer name for Ubuntu 24.04 LTS
    sku       = "22_04-lts"                 # The specific SKU for the LTS version
    version   = "latest"                    # Always use the latest available version of this SKU
  }

  # Identity: Enable System Assigned Managed Identity for the VM.
  # This is a crucial security feature. It allows your VM to authenticate to
  # other Azure services (like Azure Monitor) without storing credentials
  # (like API keys or service principal passwords) directly on the VM.
  # Azure automatically manages the identity's lifecycle and token rotation.
  identity {
    type = "SystemAssigned" # Creates an identity tied to the VM's lifecycle.
  }

  tags = {
    Project = "SmartIncidentResponse"
  }
}

# 9. Grant the VM's Managed Identity "Monitoring Reader" Role
# This role assignment gives the VM's identity read-only access to monitoring data
# (metrics, logs) within the specified scope. This adheres to the principle of
# least privilege, giving the VM only the permissions it needs.
resource "azurerm_role_assignment" "vm_monitoring_reader" {
  # The scope defines where the role assignment applies.
  # Here, it's the entire resource group, meaning the VM can read monitoring
  # data for all resources within "SmartIncidentResponseRG".
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Monitoring Reader" # A built-in Azure role for reading monitoring data.
  # The principal_id is the unique ID of the VM's System-Assigned Managed Identity.
  # Terraform automatically gets this ID after the VM is created with an identity.
  principal_id         = azurerm_linux_virtual_machine.main.identity[0].principal_id
}

