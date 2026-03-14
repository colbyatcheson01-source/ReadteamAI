"""
CrackMapExec service for lateral movement and network penetration testing.
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend import database


class CrackMapExecService:
    """Service class for CrackMapExec operations."""
    
    def __init__(self):
        """Initialize the CrackMapExec service."""
        self.cme_available = self._check_cme()
        self.cme_path = "cme"  # Default alias
    
    def _check_cme(self) -> bool:
        """Check if CrackMapExec is available on the system."""
        try:
            result = subprocess.run(
                ["cme", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try crackmapexec directly
        try:
            result = subprocess.run(
                ["crackmapexec", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if CrackMapExec is available."""
        return self.cme_available
    
    async def scan_targets(self, targets: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scan targets using CrackMapExec."""
        if not self.cme_available:
            return {
                "success": False,
                "error": "CrackMapExec is not available on this system"
            }
        
        # Create a scan in database
        scan_id = database.create_scan(
            target=targets,
            scan_type="cme_scan"
        )
        
        try:
            cmd = self._build_scan_command(targets, options)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse output
            results = self._parse_scan_output(result.stdout, result.stderr)
            
            database.update_scan_status(
                scan_id, "completed", progress=100,
                results=json.dumps(results)
            )
            
            return {
                "success": True,
                "scan_id": scan_id,
                "message": f"Scan completed: {results.get('summary', 'Unknown')}",
                "results": results
            }
            
        except subprocess.TimeoutExpired:
            database.update_scan_status(scan_id, "error", error="Scan timed out")
            return {
                "success": False,
                "scan_id": scan_id,
                "error": "Scan timed out after 5 minutes"
            }
        except Exception as e:
            database.update_scan_status(scan_id, "error", error=str(e))
            return {
                "success": False,
                "scan_id": scan_id,
                "error": f"Scan error: {str(e)}"
            }
    
    def _build_scan_command(self, targets: str, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the CrackMapExec command."""
        cmd = ["crackmapexec", "smb", targets]
        
        if options:
            # Add credentials if provided
            if options.get("username"):
                cmd.extend(["-u", options["username"]])
            if options.get("password"):
                cmd.extend(["-p", options["password"]])
            if options.get("domain"):
                cmd.extend(["-d", options["domain"]])
            if options.get("hash"):
                cmd.extend(["-H", options["hash"]])
            
            # Add module to run
            if options.get("module"):
                cmd.extend(["-M", options["module"]])
            
            # Add options
            if options.get("module_options"):
                for k, v in options["module_options"].items():
                    cmd.extend([f"-o", f"{k}={v}"])
            
            # Threads
            if options.get("threads"):
                cmd.extend(["--threads", str(options["threads"])])
            
            # Continue on success
            if options.get("continue_on_success"):
                cmd.append("--continue-on-success")
            
            # Show empty passwords
            if options.get("show_empty_passwords"):
                cmd.append("--show-empty-passwords")
        
        return cmd
    
    def _parse_scan_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse CrackMapExec output."""
        results = {
            "hosts": [],
            "summary": "",
            "found_credentials": []
        }
        
        # Parse each line
        for line in stdout.split('\n'):
            # Look for host information
            # Format: HOSTNAME IP STATUS [+] [message]
            if re.search(r'\d+\.\d+\.\d+\.\d+', line):
                host_match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+(\w+)\s+\[([^\]]+)\]', line)
                if host_match:
                    results["hosts"].append({
                        "ip": host_match.group(1),
                        "status": host_match.group(2),
                        "message": host_match.group(3)
                    })
            
            # Look for credentials
            if "[+]" in line and ("+" in line or "Pwn3d" in line):
                cred_match = re.search(r'\[(\w+):(\w+)\]', line)
                if cred_match:
                    results["found_credentials"].append({
                        "username": cred_match.group(1),
                        "password": cred_match.group(2)
                    })
        
        # Generate summary
        total_hosts = len(results["hosts"])
        pwned = sum(1 for h in results["hosts"] if "Pwn3d" in h.get("message", ""))
        results["summary"] = f"Scanned {total_hosts} hosts, {pwned} Pwn3d"
        
        return results
    
    async def login(self, target: str, credential: Dict[str, str], 
                   options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Attempt login using CrackMapExec."""
        if not self.cme_available:
            return {
                "success": False,
                "error": "CrackMapExec is not available"
            }
        
        try:
            cmd = ["crackmapexec", "smb", target]
            
            if credential.get("username"):
                cmd.extend(["-u", credential["username"]])
            if credential.get("password"):
                cmd.extend(["-p", credential["password"]])
            if credential.get("hash"):
                cmd.extend(["-H", credential["hash"]])
            if credential.get("domain"):
                cmd.extend(["-d", credential["domain"]])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse result
            success = "[+]" in result.stdout or "Pwn3d!" in result.stdout
            
            return {
                "success": success,
                "target": target,
                "credential": credential,
                "output": result.stdout[:2000]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_module(self, target: str, module: str, 
                        options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a CrackMapExec module on target."""
        if not self.cme_available:
            return {
                "success": False,
                "error": "CrackMapExec is not available"
            }
        
        try:
            cmd = ["crackmapexec", "smb", target, "-M", module]
            
            if options:
                if options.get("username"):
                    cmd.extend(["-u", options["username"]])
                if options.get("password"):
                    cmd.extend(["-p", options["password"]])
                if options.get("hash"):
                    cmd.extend(["-H", options["hash"]])
                if options.get("module_options"):
                    for k, v in options["module_options"].items():
                        cmd.extend(["-o", f"{k}={v}"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "success": True,
                "module": module,
                "target": target,
                "output": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_modules(self) -> Dict[str, Any]:
        """Get list of available CrackMapExec modules."""
        return {
            "success": True,
            "modules": [
                {
                    "name": "enum_av",
                    "description": "Enumerate antivirus products",
                    "category": "recon"
                },
                {
                    "name": "enum_chrome",
                    "description": "Dump Chrome passwords",
                    "category": "credentials"
                },
                {
                    "name": "enum_dns",
                    "description": "Dump DNS records",
                    "category": "recon"
                },
                {
                    "name": "enum_laps",
                    "description": "Dump LAPS passwords",
                    "category": "credentials"
                },
                {
                    "name": "enum_loggedon",
                    "description": "List logged on users",
                    "category": "recon"
                },
                {
                    "name": "enum_mssql",
                    "description": "Enumerate MSSQL servers",
                    "category": "recon"
                },
                {
                    "name": "enum_powershellhistory",
                    "description": "Dump PowerShell history",
                    "category": "credentials"
                },
                {
                    "name": "enum_rc.Local",
                    "description": "Dump auto-logon credentials",
                    "category": "credentials"
                },
                {
                    "name": "enum_sessions",
                    "description": "List sessions",
                    "category": "recon"
                },
                {
                    "name": "enum_smb",
                    "description": "Enumerate SMB shares",
                    "category": "recon"
                },
                {
                    "name": "enum_smb_hash",
                    "description": "Dump SMB hashes",
                    "category": "credentials"
                },
                {
                    "name": "enum_users",
                    "description": "Enumerate domain users",
                    "category": "recon"
                },
                {
                    "name": "enum_wifi",
                    "description": "Enumerate wifi networks",
                    "category": "recon"
                },
                {
                    "name": "fsi",
                    "description": "Force SPN iteration",
                    "category": "exploit"
                },
                {
                    "name": "get_keystrokes",
                    "description": "Hook and dump keystrokes",
                    "category": "exploit"
                },
                {
                    "name": "gpp_autologin",
                    "description": "Dump GPP autologin passwords",
                    "category": "credentials"
                },
                {
                    "name": "gpp_passwords",
                    "description": "Dump GPP passwords",
                    "category": "credentials"
                },
                {
                    "name": "handlekatz",
                    "description": "LSASS dump via handlekatz",
                    "category": "credentials"
                },
                {
                    "name": "iam",
                    "description": "Find interesting IAM objects",
                    "category": "recon"
                },
                {
                    "name": "implicitntlm",
                    "description": "Force NTLM authentication",
                    "category": "exploit"
                },
                {
                    "name": "invoke_sessionsecurity",
                    "description": "Dump session security secrets",
                    "category": "credentials"
                },
                {
                    "name": "lsassy",
                    "description": "Dump LSASS remotely",
                    "category": "credentials"
                },
                {
                    "name": "masskilled",
                    "description": "Kill processes on all targets",
                    "category": "exploit"
                },
                {
                    "name": "metinject",
                    "description": "Inject Meterpreter DLL",
                    "category": "exploit"
                },
                {
                    "name": "mimikatz",
                    "description": "Run Mimikatz module",
                    "category": "credentials"
                },
                {
                    "name": "multirdp",
                    "description": "Enable multiple RDP",
                    "category": "exploit"
                },
                {
                    "name": "netripper",
                    "description": "Capture network traffic",
                    "category": "exploit"
                },
                {
                    "name": "nick_the_cracker",
                    "description": "Crack hashes with hashcat",
                    "category": "credentials"
                },
                {
                    "name": "noop",
                    "description": "No-op module",
                    "category": "recon"
                },
                {
                    "name": "nopac",
                    "description": "Get PAC with no PAC",
                    "category": "exploit"
                },
                {
                    "name": "ntdsutil",
                    "description": "Dump NTDS.dit",
                    "category": "credentials"
                },
                {
                    "name": "objectexplorer",
                    "description": "AD object explorer",
                    "category": "recon"
                },
                {
                    "name": "rdp",
                    "description": "Enable/disable RDP",
                    "category": "exploit"
                },
                {
                    "name": "reg",
                    "description": "Query the registry",
                    "category": "recon"
                },
                {
                    "name": "scuffy",
                    "description": "SMB buffer overflow",
                    "category": "exploit"
                },
                {
                    "name": "secretsdump",
                    "description": "Dump SAM database",
                    "category": "credentials"
                },
                {
                    "name": "shellcode_launcher",
                    "description": "Inject shellcode",
                    "category": "exploit"
                },
                {
                    "name": "shinject",
                    "description": "Inject shellcode into process",
                    "category": "exploit"
                },
                {
                    "name": "smbexec",
                    "description": "Execute using SMB",
                    "category": "exploit"
                },
                {
                    "name": "spider",
                    "description": "Spider SMB shares",
                    "category": "recon"
                },
                {
                    "name": "spray",
                    "description": "Password spraying",
                    "category": "exploit"
                },
                {
                    "name": "ssh",
                    "description": "SSH commands",
                    "category": "exploit"
                },
                {
                    "name": "sudo",
                    "description": "Try sudo -k",
                    "category": "exploit"
                },
                {
                    "name": "updater",
                    "description": "Update CME",
                    "category": "util"
                },
                {
                    "name": "web_delivery",
                    "description": "SMB web delivery",
                    "category": "exploit"
                },
                {
                    "name": "wget",
                    "description": "Execute remote script",
                    "category": "exploit"
                },
                {
                    "name": "wmiexec",
                    "description": "Execute using WMI",
                    "category": "exploit"
                },
                {
                    "name": "wmipersist",
                    "description": "WMI persistence",
                    "category": "exploit"
                },
                {
                    "name": "zerologon",
                    "description": "Zerologon exploit",
                    "category": "exploit"
                }
            ]
        }
    
    def get_supported_protocols(self) -> Dict[str, Any]:
        """Get list of supported protocols."""
        return {
            "success": True,
            "protocols": [
                {"name": "smb", "port": 445, "description": "SMB/Windows"},
                {"name": "mssql", "port": 1433, "description": "MS SQL Server"},
                {"name": "ssh", "port": 22, "description": "SSH"},
                {"name": "ftp", "port": 21, "description": "FTP"},
                {"name": "rdp", "port": 3389, "description": "RDP"},
                {"name": "winrm", "port": 5985, "description": "WinRM"},
                {"name": "vnc", "port": 5900, "description": "VNC"}
            ]
        }


# Singleton instance
crackmapexec_service = CrackMapExecService()
