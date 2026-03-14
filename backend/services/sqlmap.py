"""
SQLmap service for automated SQL injection testing.
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend import database


class SQLMapService:
    """Service class for SQLmap operations."""
    
    def __init__(self):
        """Initialize the SQLmap service."""
        self.sqlmap_available = self._check_sqlmap()
        self.sqlmap_path = "sqlmap"  # Default to system sqlmap
    
    def _check_sqlmap(self) -> bool:
        """Check if SQLmap is available on the system."""
        try:
            result = subprocess.run(
                ["sqlmap", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if SQLmap is available."""
        return self.sqlmap_available
    
    async def scan_target(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a SQLmap scan on a target URL."""
        if not self.sqlmap_available:
            return {
                "success": False,
                "error": "SQLmap is not available on this system"
            }
        
        # Create a scan in the database
        scan_id = database.create_scan(
            target=target,
            scan_type="sql_injection"
        )
        
        try:
            # Build the SQLmap command
            cmd = self._build_scan_command(target, options)
            
            # Execute the scan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Parse the output for vulnerabilities
            vulnerabilities = self._parse_scan_output(result.stdout, result.stderr, target)
            
            if vulnerabilities:
                # Store vulnerabilities in database
                for vuln in vulnerabilities:
                    database.add_vulnerability(
                        cve=f"SQLi-{vuln['parameter']}",
                        severity="CRITICAL",
                        title=f"SQL Injection in {vuln['parameter']}",
                        description=vuln.get("title", "SQL injection vulnerability detected"),
                        cvss=9.8,
                        service="HTTP",
                        port=80,
                        solution="Use parameterized queries",
                        references=[target],
                        exploitable=True
                    )
                
                database.update_scan_status(
                    scan_id, "completed", progress=100,
                    results=json.dumps({"vulnerabilities": vulnerabilities})
                )
                
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "message": f"Found {len(vulnerabilities)} SQL injection vulnerabilities",
                    "vulnerabilities": vulnerabilities
                }
            else:
                database.update_scan_status(
                    scan_id, "completed", progress=100,
                    results=json.dumps({"vulnerabilities": []})
                )
                
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "message": "No SQL injection vulnerabilities found",
                    "vulnerabilities": []
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
    
    def _build_scan_command(self, target: str, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the SQLmap command."""
        cmd = ["sqlmap", "-u", target, "--batch", "--json-output"]
        
        if options:
            if options.get("method") in ["GET", "POST"]:
                cmd.extend(["--method", options["method"]])
            if options.get("data"):
                cmd.extend(["--data", options["data"]])
            if options.get("cookies"):
                cmd.extend(["--cookie", options["cookies"]])
            if options.get("level"):
                cmd.extend(["--level", str(options["level"])])
            if options.get("risk"):
                cmd.extend(["--risk", str(options["risk"])])
            if options.get("threads"):
                cmd.extend(["--threads", str(options["threads"])])
            if options.get("dbms"):
                cmd.extend(["--dbms", options["dbms"]])
        
        # Always add these for automation
        cmd.extend(["--smart", "--random-agent"])
        
        return cmd
    
    def _parse_scan_output(self, stdout: str, stderr: str, target: str) -> List[Dict[str, Any]]:
        """Parse SQLmap output for vulnerabilities."""
        vulnerabilities = []
        
        # Check for vulnerable parameters
        if "Parameter:" in stdout:
            param_matches = re.findall(r'Parameter: (\w+)', stdout)
            for param in param_matches:
                vulnerabilities.append({
                    "parameter": param,
                    "type": "boolean-based blind",
                    "title": f"SQL Injection in parameter '{param}'",
                    "target": target
                })
        
        # Check for different vulnerability types
        if " UNION query" in stdout:
            vulnerabilities.append({
                "parameter": "*",
                "type": "UNION query",
                "title": "UNION SQL Injection",
                "target": target
            })
        
        if " stacked queries" in stdout:
            vulnerabilities.append({
                "parameter": "*",
                "type": "stacked queries",
                "title": "Stacked Queries SQL Injection",
                "target": target
            })
        
        # Check for error-based
        if "error-based" in stdout.lower():
            vulnerabilities.append({
                "parameter": "*",
                "type": "error-based",
                "title": "Error-based SQL Injection",
                "target": target
            })
        
        # Check for time-based
        if "time-based blind" in stdout.lower():
            vulnerabilities.append({
                "parameter": "*",
                "type": "time-based blind",
                "title": "Time-based Blind SQL Injection",
                "target": target
            })
        
        # If we found vulnerabilities but couldn't parse details, add a generic one
        if "is vulnerable" in stdout.lower() and not vulnerabilities:
            vulnerabilities.append({
                "parameter": "unknown",
                "type": "generic",
                "title": "SQL Injection Vulnerability",
                "target": target
            })
        
        return vulnerabilities
    
    def get_databases(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enumerate databases using SQLmap."""
        if not self.sqlmap_available:
            return {"success": False, "error": "SQLmap is not available"}
        
        try:
            cmd = ["sqlmap", "-u", target, "--dbs", "--batch"]
            
            if options:
                if options.get("dbms"):
                    cmd.extend(["--dbms", options["dbms"]])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse database names
            databases = []
            in_databases_section = False
            for line in result.stdout.split('\n'):
                if "available databases" in line.lower():
                    in_databases_section = True
                    continue
                if in_databases_section and line.strip():
                    # Extract database name (format: [*] database_name)
                    match = re.search(r'\[\*\]\s+(\w+)', line)
                    if match:
                        databases.append(match.group(1))
            
            return {
                "success": True,
                "databases": databases
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_tables(self, target: str, database: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enumerate tables in a database using SQLmap."""
        if not self.sqlmap_available:
            return {"success": False, "error": "SQLmap is not available"}
        
        try:
            cmd = ["sqlmap", "-u", target, "-D", database, "--tables", "--batch"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse table names
            tables = []
            in_tables_section = False
            for line in result.stdout.split('\n'):
                if "Database:" in line and database in line:
                    in_tables_section = True
                    continue
                if in_tables_section and line.strip():
                    match = re.search(r'\| ([\w_]+) \|', line)
                    if match:
                        tables.append(match.group(1))
            
            return {
                "success": True,
                "database": database,
                "tables": tables
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def dump_table(self, target: str, database: str, table: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dump data from a table using SQLmap."""
        if not self.sqlmap_available:
            return {"success": False, "error": "SQLmap is not available"}
        
        try:
            cmd = ["sqlmap", "-u", target, "-D", database, "-T", table, "--dump", "--batch"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            # Parse dumped data (simplified)
            rows = []
            columns = []
            
            return {
                "success": True,
                "database": database,
                "table": table,
                "message": "Data dumped successfully",
                "output": result.stdout[:5000]  # Limit output
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_target_options(self) -> Dict[str, Any]:
        """Get available options for SQLmap scans."""
        if not self.sqlmap_available:
            return {"success": False, "error": "SQLmap is not available"}
        
        try:
            cmd = ["sqlmap", "--hh"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Parse options (simplified)
            return {
                "success": True,
                "options": {
                    "methods": ["GET", "POST"],
                    "dbms": ["MySQL", "PostgreSQL", "Oracle", "MSSQL", "SQLite"],
                    "levels": [1, 2, 3, 4, 5],
                    "risks": [1, 2, 3],
                    "threads": [1, 2, 3, 4, 5, 6, 7, 8]
                }
            }
        except Exception:
            # Return default options if can't get from sqlmap
            return {
                "success": True,
                "options": {
                    "methods": ["GET", "POST"],
                    "dbms": ["MySQL", "PostgreSQL", "Oracle", "MSSQL", "SQLite"],
                    "levels": [1, 2, 3, 4, 5],
                    "risks": [1, 2, 3],
                    "threads": [1, 2, 3, 4, 5, 6, 7, 8]
                }
            }


# Singleton instance
sqlmap_service = SQLMapService()
