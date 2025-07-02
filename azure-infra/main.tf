# azure-infra/main.tf
resource "azurerm_resource_group" "sirp_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_virtual_network" "sirp_vnet" {
  name                = var.vnet_name
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name
  address_space       = ["10.0.0.0/16"] # Define your VNet address space
}

resource "azurerm_subnet" "backend_subnet" {
  name                 = var.backend_subnet_name
  resource_group_name  = azurerm_resource_group.sirp_rg.name
  virtual_network_name = azurerm_virtual_network.sirp_vnet.name
  address_prefixes     = ["10.0.1.0/24"] # Subnet for backend VM
}

resource "azurerm_subnet" "database_subnet" {
  name                 = var.database_subnet_name
  resource_group_name  = azurerm_resource_group.sirp_rg.name
  virtual_network_name = azurerm_virtual_network.sirp_vnet.name
  address_prefixes     = ["10.0.2.0/24"] # Subnet for database VM
}

# Network Security Group for the Backend Subnet
resource "azurerm_network_security_group" "backend_nsg" {
  name                = "${var.backend_subnet_name}-nsg"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*" # BE CAREFUL: Limit this to your IP for production!
    destination_address_prefix = "*"
  }

 security_rule {
    name                       = "Allow8000"
    priority                   = 140
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000" # Standard HTTP port (for testing)
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80" # Standard HTTP port (for testing)
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443" # Standard HTTPS port (for testing)
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Allow FastAPI port (e.g., 8000 for development, or 80 if reverse proxied)
  # You might adjust this based on how you deploy FastAPI
  security_rule {
    name                       = "AllowFastAPI"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000" # Common FastAPI development port
    source_address_prefix      = "198.58.131.49/32" # Allow internal VNet communication
    destination_address_prefix = "*"
  }
}

# Network Security Group for the Database Subnet
resource "azurerm_network_security_group" "database_nsg" {
  name                = "${var.database_subnet_name}-nsg"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*" # BE CAREFUL: Limit this to your IP for production!
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowMySQL"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3306" # MySQL standard port
    source_address_prefix      = azurerm_subnet.backend_subnet.address_prefixes[0] # ONLY allow access from Backend Subnet
    destination_address_prefix = "*"
  }
}

# Associate NSGs with Subnets
resource "azurerm_subnet_network_security_group_association" "backend_nsg_association" {
  subnet_id                 = azurerm_subnet.backend_subnet.id
  network_security_group_id = azurerm_network_security_group.backend_nsg.id
}

resource "azurerm_subnet_network_security_group_association" "database_nsg_association" {
  subnet_id                 = azurerm_subnet.database_subnet.id
  network_security_group_id = azurerm_network_security_group.database_nsg.id
}



# azure-infra/main.tf (append this to your existing main.tf content)

# Public IP for Backend VM (for initial SSH access and potential frontend access)
resource "azurerm_public_ip" "backend_vm_ip" {
  name                = "${var.backend_vm_name}-ip"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name
  allocation_method   = "Static"
  sku                 = "Standard" # Use Standard SKU for better features and availability
}

# Network Interface for Backend VM
resource "azurerm_network_interface" "backend_vm_nic" {
  name                = "${var.backend_vm_name}-nic"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.backend_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.backend_vm_ip.id
  }
}

# Backend Virtual Machine
resource "azurerm_linux_virtual_machine" "backend_vm" {
  name                = var.backend_vm_name
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name
  size                = var.vm_size
  admin_username      = var.vm_admin_username
  admin_password      = var.vm_admin_password
  disable_password_authentication = false # Keep password auth for initial setup if needed

  network_interface_ids = [
    azurerm_network_interface.backend_vm_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS" # Or "20.04-LTS" or "22.04-LTS" for a newer version
    version   = "latest"
  }

  custom_data = base64encode(<<EOT
    #!/bin/bash
    sudo apt-get update -y
    sudo apt-get upgrade -y
    # You can add more initial setup commands here, e.g., install Python or Docker
    # echo "Hello from Backend VM custom_data!" >> /home/${var.vm_admin_username}/setup_log.txt
  EOT
  )

  # SSH Key for authentication (recommended over password for long-term)
  admin_ssh_key {
    username   = var.vm_admin_username
    public_key = var.ssh_public_key
  }
}


# Public IP for Database VM (for initial SSH access)
resource "azurerm_public_ip" "database_vm_ip" {
  name                = "${var.database_vm_name}-ip"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Network Interface for Database VM
resource "azurerm_network_interface" "database_vm_nic" {
  name                = "${var.database_vm_name}-nic"
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.database_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.database_vm_ip.id
  }
}

# Database Virtual Machine
resource "azurerm_linux_virtual_machine" "database_vm" {
  name                = var.database_vm_name
  location            = azurerm_resource_group.sirp_rg.location
  resource_group_name = azurerm_resource_group.sirp_rg.name
  size                = var.vm_size
  admin_username      = var.vm_admin_username
  admin_password      = var.vm_admin_password
  disable_password_authentication = false

  network_interface_ids = [
    azurerm_network_interface.database_vm_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS" # Or "20.04-LTS" or "22.04-LTS" for a newer version
    version   = "latest"
  }

  custom_data = base64encode(<<EOT
    #!/bin/bash
    sudo apt-get update -y
    sudo apt-get upgrade -y
    # You can add more initial setup commands here, e.g., install MySQL
    # echo "Hello from Database VM custom_data!" >> /home/${var.vm_admin_username}/setup_log.txt
  EOT
  )

  admin_ssh_key {
    username   = var.vm_admin_username
    public_key = var.ssh_public_key
  }
}