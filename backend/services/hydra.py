"""
Hydra service for password cracking and brute-force attacks.
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend import database


class HydraService:
    """Service class for Hydra password cracking operations."""
    
    def __init__(self):
        """Initialize the Hydra service."""
        self.hydra_available = self._check_hydra()
        self.hydra_path = "hydra"  # Default to system hydra
    
    def _check_hydra(self) -> bool:
        """Check if Hydra is available on the system."""
        try:
            result = subprocess.run(
                ["hydra", "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if Hydra is available."""
        return self.hydra_available
    
    async def brute_force(self, target: str, service: str, username: str = None, 
                         password_list: str = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a Hydra brute force attack."""
        if not self.hydra_available:
            return {
                "success": False,
                "error": "Hydra is not available on this system"
            }
        
        # Create a session in the database
        session_id = database.create_session(
            target=target,
            exploit=f"hydra_{service}",
            payload="brute_force"
        )
        
        try:
            # Build the Hydra command
            cmd = self._build_hydra_command(target, service, username, password_list, options)
            
            # Execute the attack
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Parse the output for credentials
            credentials = self._parse_hydra_output(result.stdout, result.stderr)
            
            if credentials:
                database.update_session(
                    session_id=session_id,
                    status="completed",
                    uid=json.dumps(credentials)
                )
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": f"Found {len(credentials)} valid credentials",
                    "credentials": credentials
                }
            else:
                database.update_session(session_id=session_id, status="completed")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "No valid credentials found",
                    "credentials": []
                }
                
        except subprocess.TimeoutExpired:
            database.update_session(session_id, status="error")
            return {
                "success": False,
                "session_id": session_id,
                "error": "Brute force timed out after 5 minutes"
            }
        except Exception as e:
            database.update_session(session_id, status="error")
            return {
                "success": False,
                "session_id": session_id,
                "error": f"Brute force error: {str(e)}"
            }
    
    def _build_hydra_command(self, target: str, service: str, username: str = None,
                           password_list: str = None, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the Hydra command."""
        cmd = ["hydra", "-t", "4", "-V"]  # 4 tasks, verbose
        
        # Add username or username list
        if username:
            cmd.extend(["-l", username])
        elif options and options.get("user_list"):
            cmd.extend(["-L", options["user_list"]])
        else:
            cmd.extend(["-l", "admin"])  # Default username
        
        # Add password or password list
        if password_list:
            cmd.extend(["-P", password_list])
        elif options and options.get("pass_list"):
            cmd.extend(["-P", options["pass_list"]])
        else:
            # Use default password list path
            cmd.extend(["-P", "/usr/share/wordlists/rockyou.txt"])
        
        # Add service
        cmd.append(target)
        cmd.append(service)
        
        # Add port if specified
        if options and options.get("port"):
            cmd.extend(["-s", str(options["port"])])
        
        # Add additional options
        if options:
            if options.get("threads"):
                cmd.extend(["-t", str(options["threads"])])
            if options.get("timeout"):
                cmd.extend(["-w", str(options["timeout"])])
        
        return cmd
    
    def _parse_hydra_output(self, stdout: str, stderr: str) -> List[Dict[str, Any]]:
        """Parse Hydra output for valid credentials."""
        credentials = []
        
        # Look for successful login patterns
        # Format: [login][password] host:port service
        login_pattern = r'\[(\w+)\]\[(\w+)\]\s+host:.*?service:\s*(\w+)'
        matches = re.findall(login_pattern, stdout)
        
        for match in matches:
            credentials.append({
                "username": match[0],
                "password": match[1],
                "service": match[2]
            })
        
        # Alternative pattern: login:password
        alt_pattern = r'(\w+):(\w+)@.*?(?:ssh|ftp|smb|http|mysql|postgres|rdp|vnc)'
        alt_matches = re.findall(alt_pattern, stdout, re.IGNORECASE)
        
        for match in alt_matches:
            # Check if not already found
            if not any(c['username'] == match[0] and c['password'] == match[1] for c in credentials):
                credentials.append({
                    "username": match[0],
                    "password": match[1],
                    "service": "unknown"
                })
        
        return credentials
    
    def get_supported_services(self) -> Dict[str, Any]:
        """Get list of services supported by Hydra."""
        return {
            "success": True,
            "services": [
                {"name": "ssh", "port": 22, "description": "SSH"},
                {"name": "ftp", "port": 21, "description": "FTP"},
                {"name": "smb", "port": 445, "description": "SMB"},
                {"name": "http", "port": 80, "description": "HTTP"},
                {"name": "https", "port": 443, "description": "HTTPS"},
                {"name": "mysql", "port": 3306, "description": "MySQL"},
                {"name": "postgres", "port": 5432, "description": "PostgreSQL"},
                {"name": "mssql", "port": 1433, "description": "MS SQL"},
                {"name": "oracle", "port": 1521, "description": "Oracle"},
                {"name": "rdp", "port": 3389, "description": "RDP"},
                {"name": "vnc", "port": 5900, "description": "VNC"},
                {"name": "pop3", "port": 110, "description": "POP3"},
                {"name": "imap", "port": 143, "description": "IMAP"},
                {"name": "smtp", "port": 25, "description": "SMTP"},
                {"name": "ldap", "port": 389, "description": "LDAP"},
                {"name": "telnet", "port": 23, "description": "Telnet"},
            ]
        }
    
    async def spray_passwords(self, target: str, service: str, password: str,
                             user_list: str = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Spray a single password against multiple users."""
        if not self.hydra_available:
            return {
                "success": False,
                "error": "Hydra is not available on this system"
            }
        
        try:
            cmd = ["hydra", "-t", "4", "-V"]
            
            # Add user list
            if user_list:
                cmd.extend(["-L", user_list])
            elif options and options.get("user_list"):
                cmd.extend(["-L", options["user_list"]])
            else:
                cmd.extend(["-l", "admin"])
            
            # Single password
            cmd.extend(["-p", password])
            
            cmd.append(target)
            cmd.append(service)
            
            if options and options.get("port"):
                cmd.extend(["-s", str(options["port"])])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse results
            credentials = self._parse_hydra_output(result.stdout, result.stderr)
            
            return {
                "success": True,
                "password": password,
                "found": len(credentials),
                "credentials": credentials
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_default_wordlists(self) -> Dict[str, Any]:
        """Get information about default wordlists."""
        return {
            "success": True,
            "wordlists": [
                {"name": "rockyou.txt", "path": "/usr/share/wordlists/rockyou.txt", "description": "Common passwords"},
                {"name": "fasttrack.txt", "path": "/usr/share/wordlists/fasttrack.txt", "description": "Fast track wordlist"},
                {"name": "darkweb2017.txt", "path": "/usr/share/wordlists/darkweb2017.txt", "description": "Dark web top passwords"},
                {"name": "sqlmap.txt", "path": "/usr/share/sqlmap/data/txt/wordlist.txt", "description": "SQLmap wordlist"},
            ]
        }


# Singleton instance
hydra_service = HydraService()
