{ ... }:
{
    networking.firewall.allowedTCPPorts = [ 22 53 80 443 8000 8053 8080 8443 9000 ];
    networking.firewall.enable = false; # Disable for now, firewall messes with DHCP and DNS
    networking.firewall.allowedUDPPorts = [ 53 51820 ];
}
