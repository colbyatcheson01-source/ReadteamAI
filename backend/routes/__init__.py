"""
API routes for the Red Team Operations Dashboard.
"""
import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from backend import database
from backend.models import (
    ScanStartRequest, ScanResponse, ScanStatusResponse, ScanResultsResponse,
    ExploitExecuteRequest, ExploitResponse,
    SessionCommandRequest, SessionCommandResponse, SessionResponse,
    ReportExportRequest, ReportResponse,
    DashboardStatsResponse,
    VulnerabilityResponse, ExploitModuleResponse, PayloadModuleResponse,
    WiFiNetworkResponse, HealthCheckResponse, ErrorResponse
)
from backend.services.nmap import nmap_service
from backend.services.metasploit import metasploit_service
from backend.services.sqlmap import sqlmap_service
from backend.services.hydra import hydra_service
from backend.services.responder import responder_service
from backend.services.bloodhound import bloodhound_service
from backend.services.crackmapexec import crackmapexec_service


# Create router
router = APIRouter()


# ==================== Health Check ====================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "nmap": "available" if nmap_service.is_available() else "unavailable",
            "metasploit": "available" if metasploit_service.is_available() else "unavailable",
            "sqlmap": "available" if sqlmap_service.is_available() else "unavailable",
            "hydra": "available" if hydra_service.is_available() else "unavailable",
            "responder": "available" if responder_service.is_available() else "unavailable",
            "bloodhound": "available" if bloodhound_service.is_available() else "unavailable",
            "crackmapexec": "available" if crackmapexec_service.is_available() else "unavailable",
            "database": "connected"
        }
    }


# ==================== Scan Endpoints ====================

@router.post("/scan/start", response_model=ScanResponse)
async def start_scan(request: ScanStartRequest):
    """Start a network scan."""
    # Create scan in database
    scan_id = database.create_scan(
        target=request.target,
        scan_type=request.scan_type.value
    )
    
    # Start the scan asynchronously
    if request.scan_type.value == "wifi_scan":
        # WiFi scans are synchronous for now
        networks = nmap_service.get_wifi_networks()
        results = {"networks": networks}
        database.update_scan_status(
            scan_id, "completed", progress=100, 
            results=json.dumps(results)
        )
    else:
        # Other scans - in production this would be async
        database.update_scan_status(scan_id, "running", progress=10)
        # Note: In production, use a task queue (Celery, etc.)
        # For now, we'll just mark it as running
    
    scan = database.get_scan(scan_id)
    if scan:
        return ScanResponse(**scan)
    raise HTTPException(status_code=500, detail="Failed to create scan")


@router.get("/scan/{scan_id}/status", response_model=ScanStatusResponse)
async def get_scan_status(scan_id: int):
    """Get scan status."""
    scan = database.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return ScanStatusResponse(
        id=scan["id"],
        status=scan["status"],
        progress=scan.get("progress", 0),
        error=scan.get("error")
    )


@router.get("/scan/{scan_id}/results", response_model=ScanResultsResponse)
async def get_scan_results(scan_id: int):
    """Get scan results."""
    scan = database.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    results = None
    if scan.get("results"):
        try:
            results = json.loads(scan["results"])
        except json.JSONDecodeError:
            results = {"raw": scan["results"]}
    
    return ScanResultsResponse(
        id=scan["id"],
        target=scan["target"],
        scan_type=scan["scan_type"],
        status=scan["status"],
        timestamp=scan["timestamp"],
        results=results,
        error=scan.get("error")
    )


@router.get("/scans", response_model=list)
async def get_all_scans():
    """Get all scans."""
    scans = database.get_all_scans()
    return scans


# ==================== Exploit Endpoints ====================

@router.post("/exploit/execute", response_model=ExploitResponse)
async def execute_exploit(request: ExploitExecuteRequest):
    """Execute an exploit."""
    result = await metasploit_service.execute_exploit(
        target=request.target,
        exploit_module=request.exploit_module,
        payload=request.payload,
        options=request.options
    )
    
    if result.get("success"):
        return ExploitResponse(
            success=True,
            session_id=result.get("session_id"),
            message=result.get("message", "Exploit executed successfully"),
            details=result.get("details")
        )
    else:
        return ExploitResponse(
            success=False,
            session_id=result.get("session_id"),
            message=result.get("message", "Exploit execution failed"),
            details={"error": result.get("error")}
        )


# ==================== Session Endpoints ====================

@router.get("/sessions", response_model=list)
async def get_sessions():
    """Get all sessions."""
    sessions = database.get_all_sessions()
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int):
    """Get a specific session."""
    session = database.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/command", response_model=SessionCommandResponse)
async def run_session_command(session_id: int, request: SessionCommandRequest):
    """Run a command in a session."""
    result = await metasploit_service.run_session_command(
        session_id=session_id,
        command=request.command,
        timeout=request.timeout
    )
    
    return SessionCommandResponse(
        success=result.get("success", False),
        output=result.get("output", ""),
        exit_code=result.get("exit_code"),
        error=result.get("error")
    )


@router.delete("/sessions/{session_id}")
async def close_session(session_id: int):
    """Close a session."""
    result = metasploit_service.close_session(session_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


# ==================== Network/WiFi Endpoints ====================

@router.get("/networks", response_model=list)
async def get_wifi_networks():
    """Get WiFi networks from Nmap scan."""
    if not nmap_service.is_available():
        raise HTTPException(status_code=503, detail="Nmap not available")
    
    networks = nmap_service.get_wifi_networks()
    
    # Format response
    formatted_networks = []
    for network in networks:
        formatted_networks.append({
            "bssid": network.get("bssid", ""),
            "ssid": network.get("ssid", "Hidden"),
            "signal": network.get("signal", 0),
            "channel": network.get("channel", 0),
            "encryption": network.get("encryption", "Unknown"),
            "mode": network.get("mode", "Master")
        })
    
    return formatted_networks


# ==================== Vulnerability Endpoints ====================

@router.get("/vulnerabilities", response_model=list)
async def get_vulnerabilities(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, description="Maximum number of results")
):
    """Get vulnerabilities from CVE database."""
    vulnerabilities = database.get_vulnerabilities(severity=severity, limit=limit)
    return vulnerabilities


@router.get("/vulnerabilities/{cve_id}")
async def get_vulnerability(cve_id: str):
    """Get a specific vulnerability by CVE ID."""
    vulnerability = database.get_vulnerability(cve_id)
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vulnerability


# ==================== Exploit Module Endpoints ====================

@router.get("/exploits", response_model=list)
async def get_exploit_modules(
    platform: Optional[str] = Query(None, description="Filter by platform")
):
    """Get available exploit modules."""
    exploits = metasploit_service.get_exploit_modules(platform=platform)
    return exploits


# ==================== Payload Module Endpoints ====================

@router.get("/payloads", response_model=list)
async def get_payload_modules(
    platform: Optional[str] = Query(None, description="Filter by platform")
):
    """Get available payload modules."""
    payloads = metasploit_service.get_payload_modules(platform=platform)
    return payloads


# ==================== Report Endpoints ====================

@router.post("/reports/export", response_model=ReportResponse)
async def export_report(request: ReportExportRequest):
    """Export a report."""
    report_id = database.create_report(
        title=request.title,
        data=json.dumps(request.data),
        report_type=request.report_type.value
    )
    
    report = database.get_report(report_id)
    if report:
        return ReportResponse(
            id=report["id"],
            title=report["title"],
            timestamp=report["timestamp"],
            report_type=report["report_type"],
            data=request.data
        )
    raise HTTPException(status_code=500, detail="Failed to create report")


@router.get("/reports", response_model=list)
async def get_reports():
    """Get all reports."""
    reports = database.get_all_reports()
    return reports


@router.get("/reports/{report_id}")
async def get_report(report_id: int):
    """Get a specific report."""
    report = database.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Parse the data JSON
    try:
        data = json.loads(report["data"])
    except json.JSONDecodeError:
        data = {"raw": report["data"]}
    
    return {
        "id": report["id"],
        "title": report["title"],
        "timestamp": report["timestamp"],
        "report_type": report["report_type"],
        "data": data
    }


# ==================== Dashboard Endpoints ====================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    stats = database.get_dashboard_stats()
    return stats


# ==================== SQLmap Endpoints ====================

@router.post("/sqlmap/scan")
async def sqlmap_scan(
    target: str = Query(..., description="Target URL"),
    method: str = Query("GET", description="HTTP method"),
    data: str = Query(None, description="POST data"),
    cookies: str = Query(None, description="HTTP cookies"),
    level: int = Query(1, ge=1, le=5, description="Scan level"),
    risk: int = Query(1, ge=1, le=3, description="Scan risk"),
    dbms: str = Query(None, description="Target DBMS")
):
    """Run a SQLmap scan on a target URL."""
    options = {
        "method": method,
        "data": data,
        "cookies": cookies,
        "level": level,
        "risk": risk,
        "dbms": dbms
    }
    result = await sqlmap_service.scan_target(target, options)
    return result


@router.get("/sqlmap/databases")
async def sqlmap_get_databases(target: str = Query(...)):
    """Enumerate databases using SQLmap."""
    result = sqlmap_service.get_databases(target)
    return result


@router.get("/sqlmap/tables")
async def sqlmap_get_tables(target: str = Query(...), database: str = Query(...)):
    """Enumerate tables in a database."""
    result = sqlmap_service.get_tables(target, database)
    return result


@router.get("/sqlmap/options")
async def sqlmap_get_options():
    """Get available SQLmap options."""
    return sqlmap_service.get_target_options()


# ==================== Hydra Endpoints ====================

@router.post("/hydra/bruteforce")
async def hydra_bruteforce(
    target: str = Query(..., description="Target host"),
    service: str = Query(..., description="Service to attack"),
    username: str = Query(None, description="Username"),
    password_list: str = Query(None, description="Path to password list"),
    port: int = Query(None, description="Target port"),
    threads: int = Query(4, ge=1, le=32, description="Number of threads")
):
    """Run a Hydra brute force attack."""
    options = {
        "pass_list": password_list,
        "port": port,
        "threads": threads
    }
    result = await hydra_service.brute_force(target, service, username, password_list, options)
    return result


@router.get("/hydra/services")
async def hydra_get_services():
    """Get supported Hydra services."""
    return hydra_service.get_supported_services()


@router.get("/hydra/wordlists")
async def hydra_get_wordlists():
    """Get default Hydra wordlists."""
    return hydra_service.get_default_wordlists()


# ==================== Responder Endpoints ====================

@router.post("/responder/start")
async def responder_start(
    interface: str = Query("eth0", description="Network interface"),
    analyze_mode: bool = Query(False, description="Run in analyze mode")
):
    """Start Responder listener."""
    options = {"analyze_mode": analyze_mode}
    result = await responder_service.start_listener(interface, options)
    return result


@router.post("/responder/stop")
async def responder_stop():
    """Stop Responder listener."""
    return responder_service.stop_listener()


@router.get("/responder/hashes")
async def responder_get_hashes():
    """Get captured hashes."""
    return responder_service.get_hashes()


@router.get("/responder/status")
async def responder_status():
    """Get Responder status."""
    return responder_service.get_status()


@router.get("/responder/options")
async def responder_get_options():
    """Get Responder options."""
    return responder_service.get_options()


# ==================== BloodHound Endpoints ====================

@router.post("/bloodhound/collect")
async def bloodhound_collect(
    target: str = Query(..., description="Target domain"),
    collector: str = Query("sharp", description="Collector type"),
    username: str = Query(None, description="Username"),
    password: str = Query(None, description="Password"),
    domain: str = Query(None, description="Domain")
):
    """Collect AD data using BloodHound."""
    options = {
        "collector": collector,
        "username": username,
        "password": password,
        "domain": domain
    }
    result = await bloodhound_service.collect_data(target, options)
    return result


@router.get("/bloodhound/queries")
async def bloodhound_queries():
    """Get predefined BloodHound queries."""
    return bloodhound_service.get_predefined_queries()


@router.get("/bloodhound/query")
async def bloodhound_query(
    query: str = Query(..., description="Query type"),
    target: str = Query(None, description="Target node")
):
    """Query BloodHound database."""
    options = {"target": target} if target else None
    result = await bloodhound_service.query_graph(query, options)
    return result


@router.get("/bloodhound/status")
async def bloodhound_status():
    """Get BloodHound status."""
    return bloodhound_service.get_status()


# ==================== CrackMapExec Endpoints ====================

@router.post("/cme/scan")
async def cme_scan(
    targets: str = Query(..., description="Target hosts"),
    username: str = Query(None, description="Username"),
    password: str = Query(None, description="Password"),
    domain: str = Query(None, description="Domain"),
    hash: str = Query(None, description="NTLM hash"),
    module: str = Query(None, description="Module to run")
):
    """Scan targets using CrackMapExec."""
    options = {
        "username": username,
        "password": password,
        "domain": domain,
        "hash": hash,
        "module": module
    }
    result = await crackmapexec_service.scan_targets(targets, options)
    return result


@router.get("/cme/modules")
async def cme_modules():
    """Get available CrackMapExec modules."""
    return crackmapexec_service.get_available_modules()


@router.get("/cme/protocols")
async def cme_protocols():
    """Get supported CrackMapExec protocols."""
    return crackmapexec_service.get_supported_protocols()
