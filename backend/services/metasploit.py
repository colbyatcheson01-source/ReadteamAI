"""
Metasploit service for exploitation and post-exploitation operations.
"""
import subprocess
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend import database


class MetasploitService:
    """Service class for Metasploit RPC operations."""
    
    def __init__(self):
        """Initialize the Metasploit service."""
        self.msf_available = self._check_msf()
        self.msf_path = "msfconsole"  # Default to system msfconsole
        self.msfrpc_available = self._check_msfrpc()
        self.rpc_connection = None
    
    def _check_msf(self) -> bool:
        """Check if Metasploit is available on the system."""
        try:
            result = subprocess.run(
                ["msfconsole", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_msfrpc(self) -> bool:
        """Check if msfrpc is available."""
        try:
            import msgrpc
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        """Check if Metasploit is available."""
        return self.msf_available
    
    def is_rpc_available(self) -> bool:
        """Check if Metasploit RPC is available."""
        return self.msfrpc_available
    
    async def execute_exploit(self, target: str, exploit_module: str, payload: str, 
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a Metasploit exploit."""
        if not self.msf_available:
            return {
                "success": False,
                "error": "Metasploit is not available on this system"
            }
        
        # Create a session in the database
        session_id = database.create_session(
            target=target,
            exploit=exploit_module,
            payload=payload
        )
        
        try:
            # Build the Metasploit command
            cmd = self._build_exploit_command(target, exploit_module, payload, options)
            
            # Execute the exploit
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            # Parse the output for session information
            session_info = self._parse_exploit_output(result.stdout, result.stderr)
            
            if session_info.get("session_created"):
                # Update session in database
                database.update_session(
                    session_id=session_id,
                    uid=session_info.get("session_uid"),
                    pid=session_info.get("session_pid"),
                    status="active"
                )
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "Exploit successful, session created",
                    "details": session_info
                }
            else:
                database.update_session(session_id, status="failed")
                return {
                    "success": False,
                    "session_id": session_id,
                    "message": "Exploit failed or no session created",
                    "error": session_info.get("error", "Unknown error")
                }
                
        except subprocess.TimeoutExpired:
            database.update_session(session_id, status="error")
            return {
                "success": False,
                "session_id": session_id,
                "error": "Exploit timed out after 2 minutes"
            }
        except Exception as e:
            database.update_session(session_id, status="error")
            return {
                "success": False,
                "session_id": session_id,
                "error": f"Exploit error: {str(e)}"
            }
    
    def _build_exploit_command(self, target: str, exploit_module: str, payload: str, 
                               options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the Metasploit command."""
        # Using resource file approach for better automation
        resource_commands = [
            f"use {exploit_module}",
            f"set RHOST {target}",
            f"set PAYLOAD {payload}"
        ]
        
        if options:
            if "rport" in options:
                resource_commands.append(f"set RPORT {options['rport']}")
            if "lhost" in options:
                resource_commands.append(f"set LHOST {options['lhost']}")
            if "lport" in options:
                resource_commands.append(f"set LPORT {options['lport']}")
        
        resource_commands.append("exploit -z")
        resource_commands.append("exit")
        
        # Join commands with semicolons for single-line execution
        cmd_string = "; ".join(resource_commands)
        
        return ["msfconsole", "-q", "-x", cmd_string]
    
    def _parse_exploit_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse Metasploit exploit output."""
        result = {
            "session_created": False,
            "session_uid": None,
            "session_pid": None,
            "output": stdout,
            "error": None
        }
        
        # Check for session creation indicators
        if "session opened" in stdout.lower() or "session created" in stdout.lower():
            result["session_created"] = True
            
            # Try to extract session UID
            import re
            session_match = re.search(r'session\s+(\d+)', stdout)
            if session_match:
                result["session_uid"] = session_match.group(1)
        
        # Check for errors
        if "exploit failed" in stdout.lower() or "exploit completed" in stdout.lower():
            if "no session was created" in stdout.lower():
                result["error"] = "No session was created"
            elif "exploit failed" in stdout.lower():
                result["error"] = "Exploit failed"
        
        if stderr and not result.get("error"):
            result["error"] = stderr[:500]  # Limit error length
        
        return result
    
    async def run_session_command(self, session_id: int, command: str, 
                                   timeout: int = 30) -> Dict[str, Any]:
        """Run a command in an active Metasploit session."""
        session = database.get_session(session_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        if session["status"] != "active":
            return {
                "success": False,
                "error": f"Session is not active (status: {session['status']})"
            }
        
        # Try to use Metasploit session command if available
        if self.msf_available:
            try:
                cmd = [
                    "msfconsole", "-q", "-x",
                    f"sessions -i {session['id']} -c '{command}'"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "success": True,
                    "output": result.stdout,
                    "exit_code": result.returncode
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Command timed out"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Command error: {str(e)}"
                }
        
        # Fallback: simulate command execution
        # In a real implementation, this would use the actual session
        return {
            "success": True,
            "output": f"[Simulated] Executed command on session {session_id}: {command}",
            "exit_code": 0
        }
    
    def get_exploit_modules(self, platform: str = None, module_type: str = "exploit") -> List[Dict[str, Any]]:
        """Get available exploit modules from Metasploit."""
        # First check database cache
        exploits = database.get_exploit_modules(platform=platform, module_type=module_type)
        
        if exploits:
            return exploits
        
        # If no cached data, try to get from Metasploit
        if self.msf_available:
            try:
                cmd = ["msfconsole", "-q", "-x", f"show {module_type}; exit"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse the output for modules
                modules = self._parse_module_list(result.stdout, module_type)
                
                # Cache the modules
                for module in modules:
                    database.add_exploit_module(**module)
                
                return modules
                
            except Exception:
                pass
        
        # Return mock data if Metasploit is not available
        return self._get_mock_exploits(platform)
    
    def get_payload_modules(self, platform: str = None, module_type: str = "payload") -> List[Dict[str, Any]]:
        """Get available payload modules from Metasploit."""
        # First check database cache
        payloads = database.get_payload_modules(platform=platform, module_type=module_type)
        
        if payloads:
            return payloads
        
        # If no cached data, try to get from Metasploit
        if self.msf_available:
            try:
                cmd = ["msfconsole", "-q", "-x", f"show {module_type}; exit"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse the output for modules
                modules = self._parse_module_list(result.stdout, module_type)
                
                # Cache the modules
                for module in modules:
                    database.add_payload_module(**module)
                
                return modules
                
            except Exception:
                pass
        
        # Return mock data if Metasploit is not available
        return self._get_mock_payloads(platform)
    
    def _parse_module_list(self, output: str, module_type: str) -> List[Dict[str, Any]]:
        """Parse Metasploit module list output."""
        modules = []
        
        import re
        # Simple parsing - extract module names
        # This is a simplified version
        lines = output.split('\n')
        for line in lines:
            # Look for module names (typically in format: name  description)
            if line.strip().startswith('exploit/') or line.strip().startswith('payload/'):
                parts = line.strip().split()
                if parts:
                    module_name = parts[0]
                    modules.append({
                        "name": module_name.split('/')[-1],
                        "full_name": module_name,
                        "module_type": module_type,
                        "description": " ".join(parts[1:]) if len(parts) > 1 else ""
                    })
        
        return modules
    
    def _get_mock_exploits(self, platform: str = None) -> List[Dict[str, Any]]:
        """Return mock exploit data when Metasploit is not available."""
        mock_exploits = [
            {
                "name": " eternalblue",
                "full_name": "exploit/windows/smb/ms17_010_eternalblue",
                "module_type": "exploit",
                "rank": "great",
                "platform": "Windows",
                "arch": "x64",
                "description": "MS17-010 EternalBlue SMB Remote Code Execution"
            },
            {
                "name": " exploit",
                "full_name": "exploit/multi/http/wp_crop_rce",
                "module_type": "exploit",
                "rank": "excellent",
                "platform": "PHP",
                "arch": "PHP",
                "description": "WordPress Crop image Command Execution"
            },
            {
                "name": " java_rmi",
                "full_name": "exploit/multi/misc/java_rmi_server",
                "module_type": "exploit",
                "rank": "excellent",
                "platform": "Java",
                "arch": "Java",
                "description": "Java RMI Server Insecure Configuration Code Execution"
            },
            {
                "name": " ftp",
                "full_name": "exploit/unix/ftp/vsftpd_234_backdoor",
                "module_type": "exploit",
                "rank": "excellent",
                "platform": "Unix",
                "arch": "x86",
                "description": "VSFTPD v2.3.4 Backdoor Command Execution"
            },
            {
                "name": " ssh",
                "full_name": "exploit/linux/ssh/ubiquiti_airos_template_exec",
                "module_type": "exploit",
                "rank": "great",
                "platform": "Linux",
                "arch": "x86",
                "description": "Ubiquiti airOS SSH Command Injection"
            }
        ]
        
        if platform:
            return [e for e in mock_exploits if platform.lower() in (e.get("platform") or "").lower()]
        
        return mock_exploits
    
    def _get_mock_payloads(self, platform: str = None) -> List[Dict[str, Any]]:
        """Return mock payload data when Metasploit is not available."""
        mock_payloads = [
            {
                "name": " shell_bind_tcp",
                "full_name": "generic/shell_bind_tcp",
                "module_type": "payload",
                "platform": "Multi",
                "arch": "x86",
                "description": "Generic Shell Bind TCP"
            },
            {
                "name": " shell_reverse_tcp",
                "full_name": "generic/shell_reverse_tcp",
                "module_type": "payload",
                "platform": "Multi",
                "arch": "x86",
                "description": "Generic Shell Reverse TCP"
            },
            {
                "name": " windows_bind_tcp",
                "full_name": "windows/meterpreter/bind_tcp",
                "module_type": "payload",
                "platform": "Windows",
                "arch": "x64",
                "description": "Windows Meterpreter Bind TCP"
            },
            {
                "name": " windows_reverse_tcp",
                "full_name": "windows/meterpreter/reverse_tcp",
                "module_type": "payload",
                "platform": "Windows",
                "arch": "x64",
                "description": "Windows Meterpreter Reverse TCP"
            },
            {
                "name": " linux_bind_tcp",
                "full_name": "linux/x86/shell/bind_tcp",
                "module_type": "payload",
                "platform": "Linux",
                "arch": "x86",
                "description": "Linux x86 Shell Bind TCP"
            },
            {
                "name": " linux_reverse_tcp",
                "full_name": "linux/x86/shell/reverse_tcp",
                "module_type": "payload",
                "platform": "Linux",
                "arch": "x86",
                "description": "Linux x86 Shell Reverse TCP"
            }
        ]
        
        if platform:
            return [p for p in mock_payloads if platform.lower() in (p.get("platform") or "").lower()]
        
        return mock_payloads
    
    def close_session(self, session_id: int) -> Dict[str, Any]:
        """Close a Metasploit session."""
        session = database.get_session(session_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        # Try to close the session in Metasploit
        if self.msf_available:
            try:
                cmd = ["msfconsole", "-q", "-x", f"sessions -k {session_id}; exit"]
                subprocess.run(cmd, capture_output=True, timeout=10)
            except Exception:
                pass
        
        # Close the session in database
        database.close_session(session_id)
        
        return {
            "success": True,
            "message": f"Session {session_id} closed"
        }


# Singleton instance
metasploit_service = MetasploitService()
