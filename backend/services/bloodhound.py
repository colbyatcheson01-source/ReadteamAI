"""
BloodHound service for Active Directory enumeration and attack path analysis.
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend import database


class BloodHoundService:
    """Service class for BloodHound AD enumeration operations."""
    
    def __init__(self):
        """Initialize the BloodHound service."""
        self.bloodhound_available = self._check_bloodhound()
        self.bloodhound_path = "bloodhound"  # Default
        self.neo4j_available = self._check_neo4j()
    
    def _check_bloodhound(self) -> bool:
        """Check if BloodHound is available on the system."""
        try:
            result = subprocess.run(
                ["bloodhound", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_neo4j(self) -> bool:
        """Check if Neo4j is available."""
        try:
            result = subprocess.run(
                ["cypher-shell", "-u", "neo4j", "-p", "password", "-c", "RETURN 1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if BloodHound is available."""
        return self.bloodhound_available
    
    def is_neo4j_available(self) -> bool:
        """Check if Neo4j database is available."""
        return self.neo4j_available
    
    async def collect_data(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collect AD data using BloodHound collectors."""
        if not self.bloodhound_available:
            return {
                "success": False,
                "error": "BloodHound is not available on this system"
            }
        
        # Create a scan in database
        scan_id = database.create_scan(
            target=target,
            scan_type="ad_enumeration"
        )
        
        try:
            # Determine which collector to use
            collector = options.get("collector", "sharp") if options else "sharp"
            
            cmd = self._build_collector_command(target, collector, options)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            # Parse output for collected data
            collected = self._parse_collector_output(result.stdout, result.stderr)
            
            database.update_scan_status(
                scan_id, "completed", progress=100,
                results=json.dumps(collected)
            )
            
            return {
                "success": True,
                "scan_id": scan_id,
                "message": f"AD data collection completed: {collected.get('summary', 'Unknown')}",
                "collected": collected
            }
            
        except subprocess.TimeoutExpired:
            database.update_scan_status(scan_id, "error", error="Collection timed out")
            return {
                "success": False,
                "scan_id": scan_id,
                "error": "Collection timed out after 5 minutes"
            }
        except Exception as e:
            database.update_scan_status(scan_id, "error", error=str(e))
            return {
                "success": False,
                "scan_id": scan_id,
                "error": f"Collection error: {str(e)}"
            }
    
    def _build_collector_command(self, target: str, collector: str, 
                                  options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the BloodHound collector command."""
        if collector == "sharp":
            cmd = ["sharpbloodhound"]
        else:
            # Default to Python collector
            cmd = ["python3", "/usr/share/bloodhound/BloodHound.py", "-c", "All"]
        
        if options:
            if options.get("username"):
                cmd.extend(["-u", options["username"]])
            if options.get("password"):
                cmd.extend(["-p", options["password"]])
            if options.get("domain"):
                cmd.extend(["-d", options["domain"]])
            if options.get("dc"):
                cmd.extend(["-dc", options["dc"]])
        
        return cmd
    
    def _parse_collector_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse BloodHound collector output."""
        result = {
            "computers": 0,
            "users": 0,
            "groups": 0,
            "domains": 0,
            "ous": 0,
            "summary": ""
        }
        
        # Parse computer count
        if "computers collected" in stdout.lower():
            match = re.search(r'(\d+)\s+computers?', stdout, re.IGNORECASE)
            if match:
                result["computers"] = int(match.group(1))
        
        # Parse user count
        if "users collected" in stdout.lower():
            match = re.search(r'(\d+)\s+users?', stdout, re.IGNORECASE)
            if match:
                result["users"] = int(match.group(1))
        
        # Parse group count
        if "groups collected" in stdout.lower():
            match = re.search(r'(\d+)\s+groups?', stdout, re.IGNORECASE)
            if match:
                result["groups"] = int(match.group(1))
        
        # Parse domain count
        if "domains collected" in stdout.lower():
            match = re.search(r'(\d+)\s+domains?', stdout, re.IGNORECASE)
            if match:
                result["domains"] = int(match.group(1))
        
        result["summary"] = f"Collected {result['computers']} computers, {result['users']} users, {result['groups']} groups"
        
        return result
    
    async def query_graph(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the BloodHound Neo4j database."""
        if not self.neo4j_available:
            return {
                "success": False,
                "error": "Neo4j database is not available"
            }
        
        try:
            # Build Cypher query
            cypher_query = self._build_cypher_query(query, options)
            
            cmd = [
                "cypher-shell",
                "-u", "neo4j",
                "-p", "password",
                "-c", cypher_query
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "query": query,
                "results": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_cypher_query(self, query: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Build a Cypher query based on the requested query type."""
        query = query.lower()
        
        if query == "domain_admins":
            return "MATCH (u:User)-[:MemberOf*1..]->(g:Group) WHERE g.name CONTAINS 'DOMAIN ADMINS' RETURN u.name, u.enabled"
        
        elif query == "domain_computers":
            return "MATCH (c:Computer) RETURN c.name, c.operatingsystem, c.enabled"
        
        elif query == "high_value_targets":
            return "MATCH (n) WHERE n.highvalue = true RETURN n.name, labels(n)"
        
        elif query == "shortest_path":
            target = options.get("target", "DOMAIN ADMIN@TEST.LOCAL") if options else "DOMAIN ADMIN@TEST.LOCAL"
            return f"MATCH p=shortestPath((u:User)-[*1..]->(g:Group {{name:'{target}'}})) RETURN p"
        
        elif query == "unconstrained_delegation":
            return "MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name"
        
        elif query == "as_rep_roastable":
            return "MATCH (u:User {dontreqpreauth:true}) RETURN u.name, u.dnshostname"
        
        elif query == "kerberoastable":
            return "MATCH (u:User) WHERE ANY(tag IN u.serviceprincipalnames WHERE tag CONTAINS 'MSSQL') RETURN u.name, u.serviceprincipalnames"
        
        elif query == "owned_users":
            return "MATCH (u:User {owned:true}) RETURN u.name, u.dnshostname"
        
        else:
            return f"MATCH (n) WHERE n.name CONTAINS '{query}' RETURN n.name LIMIT 10"
    
    def get_predefined_queries(self) -> Dict[str, Any]:
        """Get list of predefined BloodHound queries."""
        return {
            "success": True,
            "queries": [
                {
                    "name": "Domain Admins",
                    "description": "Find all Domain Admins",
                    "query": "domain_admins"
                },
                {
                    "name": "Domain Computers",
                    "description": "List all domain computers",
                    "query": "domain_computers"
                },
                {
                    "name": "High Value Targets",
                    "description": "Find high value targets",
                    "query": "high_value_targets"
                },
                {
                    "name": "Shortest Path to DA",
                    "description": "Find shortest path to Domain Admin",
                    "query": "shortest_path"
                },
                {
                    "name": "Unconstrained Delegation",
                    "description": "Find computers with unconstrained delegation",
                    "query": "unconstrained_delegation"
                },
                {
                    "name": "AS-REP Roastable",
                    "description": "Find AS-REP roastable users",
                    "query": "as_rep_roastable"
                },
                {
                    "name": "Kerberoastable",
                    "description": "Find Kerberoastable users",
                    "query": "kerberoastable"
                },
                {
                    "name": "Owned Users",
                    "description": "Find owned users",
                    "query": "owned_users"
                }
            ]
        }
    
    async def get_attack_paths(self, start_node: str, end_node: str) -> Dict[str, Any]:
        """Find attack paths between two nodes."""
        if not self.neo4j_available:
            return {
                "success": False,
                "error": "Neo4j database is not available"
            }
        
        try:
            cypher = f"MATCH p=shortestPath((start {{name:'{start_node}'}})-[*1..15]->(end {{name:'{end_node}'}})) RETURN p"
            
            cmd = [
                "cypher-shell",
                "-u", "neo4j",
                "-p", "password",
                "-c", cypher
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "start": start_node,
                "end": end_node,
                "path": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get BloodHound and Neo4j status."""
        return {
            "bloodhound_available": self.bloodhound_available,
            "neo4j_available": self.neo4j_available,
            "status": "ready" if self.bloodhound_available and self.neo4j_available else "partial"
        }


# Singleton instance
bloodhound_service = BloodHoundService()
