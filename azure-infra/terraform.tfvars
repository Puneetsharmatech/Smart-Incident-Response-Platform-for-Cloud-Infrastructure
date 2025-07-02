# azure-infra/terraform.tfvars
# Replace 'YOUR_COMPLEX_PASSWORD_HERE' with a strong password
vm_admin_password = "Puneet8872423736@"

# Replace 'YOUR_PUBLIC_SSH_KEY_CONTENT_HERE' with the actual content of your .pub file
# E.g., ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDF/g...... user@machine
ssh_public_key    = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCuUUb7FGtOhAtZHzIPp8RgHY2waj8bNDtsvipxQlz+fyLAulcDlzC6LHzoJMqnWMI/4Ebe7I/AVrj9Iw9INVosZV674RcgPdjLLZSsu6cWCAPjiy5aQl2M5UPUb/yx64p3iOXst/nVEjK4hobqiZCNdfUBD11NzamaakMgnbd5d+iBFOgQqAs82276vP5D0qJWWsDstk5J3CXyV44HmqAKx8U7E9EfXXZyqCdsBE3Xu3diTcfRhGnJkPbJzbgfxh16f1OkvO8rfNpHehN8ooAGgdaZX2Rcjhj8c5D96dqCF2s6spUiU7DrW5ugSpAAs66tsuz3XBe+/ncdO8MlyM2L2w4GBij8iQ2PoNvvs1vQkEU0WvEsYZmdiqaRhrnTzN0meC+NBAeBjk9JRqf575G5zZzb/bYXXfbrv0bVthjGRWV25QwW3qMWv9ICzGWD90l6X6IH5FFX/qxv2vvIj/ccG3zfGA7s3ecwCoigotYbgmiLECUKvBf768sBOEswzKaSrgH57lvuD2l6ssK6qPl4uLJ11+E3NDmb5b/YJGZsUIW76cYI/NJDf7nd4I1t751tT0cFDStT5YlCs8sVXeyFvJuXM1rLRh5j3u6jUBO00ZoQhwb2TyPGl8p9zlP9ssbM2b214BN/VL/aEBCJicgsFNykVXsPOHl4AzKVW8pNlw== puneetsharma@Puneets-MacBook-Pro.local"

# Optionally override defaults:
# resource_group_name = "MyCustomSIRPRG"
# location            = "canadaeast" # Example: if you want a different region