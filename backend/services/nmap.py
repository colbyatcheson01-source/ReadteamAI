"""
Nmap service for network scanning operations.
"""
import subprocess
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import re

from backend import database


class NmapService:
    """Service class for Nmap network scanning."""
    
    def __init__(self):
        """Initialize the Nmap service."""
        self.nmap_available = self._check_nmap()
        self.nmap_path = "nmap"  # Default to system nmap
    
    def _check_nmap(self) -> bool:
        """Check if Nmap is available on the system."""
        try:
            result = subprocess.run(
                ["nmap", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if Nmap is available."""
        return self.nmap_available
    
    def _build_nmap_command(self, target: str, scan_type: str, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the Nmap command based on scan type and options."""
        cmd = ["nmap", "-oX", "-"]  # Output XML to stdout
        
        # Add scan type arguments
        if scan_type == "syn_scan":
            cmd.append("-sS")
        elif scan_type == "tcp_scan":
            cmd.append("-sT")
        elif scan_type == "udp_scan":
            cmd.append("-sU")
        elif scan_type == "service_scan":
            cmd.extend(["-sV", "-sC"])
        elif scan_type == "vuln_scan":
            cmd.extend(["--script", "vuln"])
        elif scan_type == "os_detect":
            cmd.append("-O")
        elif scan_type == "wifi_scan":
            # WiFi scanning requires special handling
            cmd.extend(["--script", "broadcast-wifi-discover"])
        else:
            # Default Nmap scan
            cmd.append("-sS")
        
        # Add timing template
        cmd.append("-T4")
        
        # Add default ports if not specified
        if not options or "ports" not in options:
            cmd.append("-p1-1000")
        
        # Add custom options
        if options:
            if "ports" in options:
                cmd.extend(["-p", options["ports"]])
            if "scripts" in options:
                cmd.extend(["--script", options["scripts"]])
            if "timing" in options:
                cmd.extend(["-T", options["timing"]])
            if options.get("detect_os"):
                cmd.append("-O")
            if options.get("service_detection"):
                cmd.append("-sV")
        
        # Add target
        cmd.append(target)
        
        return cmd
    
    def _parse_xml_output(self, xml_output: str) -> Dict[str, Any]:
        """Parse Nmap XML output."""
        try:
            root = ET.fromstring(xml_output)
            results = {
                "scan_info": {},
                "hosts": []
            }
            
            # Parse scan info
            scan_info = root.find("scaninfo")
            if scan_info is not None:
                results["scan_info"] = {
                    "type": scan_info.get("type"),
                    "protocol": scan_info.get("protocol"),
                    "services": scan_info.get("numservices")
                }
            
            # Parse hosts
            for host in root.findall("host"):
                host_data = {
                    "ip": host.find("address").get("addr") if host.find("address") is not None else "unknown",
                    "status": host.find("status").get("state") if host.find("status") is not None else "unknown",
                    "hostname": host.find("hostnames/hostname").get("name") if host.find("hostnames/hostname") is not None else None,
                    "ports": [],
                    "os": None,
                    "services": []
                }
                
                # Parse ports
                ports_elem = host.find("ports")
                if ports_elem is not None:
                    for port in ports_elem.findall("port"):
                        port_data = {
                            "portid": port.get("portid"),
                            "protocol": port.get("protocol"),
                            "state": port.find("state").get("state") if port.find("state") is not None else "unknown",
                            "service": None
                        }
                        
                        # Get service info
                        service = port.find("service")
                        if service is not None:
                            port_data["service"] = {
                                "name": service.get("name"),
                                "product": service.get("product"),
                                "version": service.get("version"),
                                "extrainfo": service.get("extrainfo")
                            }
                            host_data["services"].append({
                                "port": port.get("portid"),
                                "name": service.get("name"),
                                "product": service.get("product"),
                                "version": service.get("version")
                            })
                        
                        host_data["ports"].append(port_data)
                
                # Parse OS
                os_elem = host.find("osmatch")
                if os_elem is not None:
                    host_data["os"] = os_elem.get("name")
                
                results["hosts"].append(host_data)
            
            return results
            
        except ET.ParseError as e:
            return {"error": f"Failed to parse XML: {str(e)}", "hosts": []}
    
    async def start_scan(self, scan_id: int, target: str, scan_type: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start an Nmap scan."""
        if not self.nmap_available:
            error_msg = "Nmap is not available on this system"
            database.update_scan_status(scan_id, "failed", error=error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        # Update scan status to running
        database.update_scan_status(scan_id, "running", progress=10)
        
        try:
            # Build the command
            cmd = self._build_nmap_command(target, scan_type, options)
            
            # Execute the scan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # Parse the XML output
                scan_results = self._parse_xml_output(result.stdout)
                
                # Update database with results
                results_json = json.dumps(scan_results)
                database.update_scan_status(scan_id, "completed", progress=100, results=results_json)
                
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "results": scan_results
                }
            else:
                error_msg = result.stderr or "Scan failed with no output"
                database.update_scan_status(scan_id, "failed", error=error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except subprocess.TimeoutExpired:
            error_msg = "Scan timed out after 5 minutes"
            database.update_scan_status(scan_id, "failed", error=error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Scan error: {str(e)}"
            database.update_scan_status(scan_id, "failed", error=error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_wifi_networks(self) -> List[Dict[str, Any]]:
        """Get WiFi networks using Nmap."""
        if not self.nmap_available:
            return []
        
        # Note: WiFi scanning typically requires root and monitor mode
        # This is a simplified version
        try:
            cmd = ["nmap", "--script", "broadcast-wifi-discover", "-e", "wlan0mon"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse the output for WiFi networks
                networks = self._parse_wifi_output(result.stdout)
                return networks
            else:
                return []
                
        except Exception:
            return []
    
    def _parse_wifi_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse Nmap WiFi discovery output."""
        networks = []
        
        # Simple regex-based parsing for WiFi networks
        # In a real implementation, this would parse the Nmap script output
        bssid_pattern = re.compile(r'BSSID: ([0-9a-fA-F:]+)')
        ssid_pattern = re.compile(r'SSID: (.+)')
        signal_pattern = re.compile(r'Signal: (-?\d+)')
        
        lines = output.split('\n')
        current_network = {}
        
        for line in lines:
            bssid_match = bssid_pattern.search(line)
            if bssid_match:
                if current_network.get('bssid'):
                    networks.append(current_network)
                current_network = {'bssid': bssid_match.group(1)}
            
            ssid_match = ssid_pattern.search(line)
            if ssid_match:
                current_network['ssid'] = ssid_match.group(1)
            
            signal_match = signal_pattern.search(line)
            if signal_match:
                current_network['signal'] = int(signal_match.group(1))
        
        if current_network.get('bssid'):
            networks.append(current_network)
        
        return networks
    
    def get_service_info(self, target: str, port: int) -> Optional[Dict[str, Any]]:
        """Get detailed service information for a specific port."""
        if not self.nmap_available:
            return None
        
        try:
            cmd = ["nmap", "-sV", "-p", str(port), "-oX", "-", target]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                scan_results = self._parse_xml_output(result.stdout)
                if scan_results.get("hosts"):
                    host = scan_results["hosts"][0]
                    for port_data in host.get("ports", []):
                        if str(port_data.get("portid")) == str(port):
                            return port_data.get("service")
            
            return None
        except Exception:
            return None


# Singleton instance
nmap_service = NmapService()
