"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanType(str, Enum):
    NMAP = "nmap"
    SYN_SCAN = "syn_scan"
    TCP_SCAN = "tcp_scan"
    UDP_SCAN = "udp_scan"
    SERVICE_SCAN = "service_scan"
    VULN_SCAN = "vuln_scan"
    WIFI_SCAN = "wifi_scan"
    OS_DETECT = "os_detect"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


class ReportType(str, Enum):
    GENERAL = "general"
    SCAN = "scan"
    EXPLOIT = "exploit"
    SESSION = "session"


# Request Models
class ScanStartRequest(BaseModel):
    """Request model for starting a scan."""
    target: str = Field(..., description="Target IP or network range")
    scan_type: ScanType = Field(default=ScanType.NMAP, description="Type of scan to perform")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional scan options")


class ExploitExecuteRequest(BaseModel):
    """Request model for executing an exploit."""
    target: str = Field(..., description="Target IP address")
    exploit_module: str = Field(..., description="Exploit module path")
    payload: str = Field(default="generic/shell_bind_tcp", description="Payload module path")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional exploit options")


class SessionCommandRequest(BaseModel):
    """Request model for running a command in a session."""
    command: str = Field(..., description="Command to execute")
    timeout: int = Field(default=30, description="Command timeout in seconds")


class ReportExportRequest(BaseModel):
    """Request model for exporting a report."""
    title: str = Field(..., description="Report title")
    report_type: ReportType = Field(default=ReportType.GENERAL, description="Type of report")
    data: Dict[str, Any] = Field(..., description="Report data")


# Response Models
class ScanResponse(BaseModel):
    """Response model for scan operations."""
    id: int
    target: str
    scan_type: str
    status: str
    timestamp: str
    progress: Optional[int] = 0
    results: Optional[str] = None
    error: Optional[str] = None


class ScanStatusResponse(BaseModel):
    """Response model for scan status."""
    id: int
    status: str
    progress: int
    error: Optional[str] = None


class ScanResultsResponse(BaseModel):
    """Response model for scan results."""
    id: int
    target: str
    scan_type: str
    status: str
    timestamp: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExploitResponse(BaseModel):
    """Response model for exploit execution."""
    success: bool
    session_id: Optional[int] = None
    message: str
    details: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response model for session operations."""
    id: int
    target: str
    exploit: Optional[str] = None
    payload: Optional[str] = None
    uid: Optional[str] = None
    pid: Optional[int] = None
    opened: str
    closed: Optional[str] = None
    status: str


class SessionCommandResponse(BaseModel):
    """Response model for session command execution."""
    success: bool
    output: str
    exit_code: Optional[int] = None
    error: Optional[str] = None


class VulnerabilityResponse(BaseModel):
    """Response model for vulnerability data."""
    id: int
    cve_id: str
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss_score: Optional[float] = None
    published_date: Optional[str] = None
    affected_products: Optional[str] = None
    exploit_available: bool = False


class ExploitModuleResponse(BaseModel):
    """Response model for exploit module."""
    id: int
    name: str
    full_name: str
    module_type: str
    rank: Optional[str] = None
    disclosure_date: Optional[str] = None
    platform: Optional[str] = None
    arch: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


class PayloadModuleResponse(BaseModel):
    """Response model for payload module."""
    id: int
    name: str
    full_name: str
    module_type: str
    platform: Optional[str] = None
    arch: Optional[str] = None
    description: Optional[str] = None


class ReportResponse(BaseModel):
    """Response model for report operations."""
    id: int
    title: str
    timestamp: str
    report_type: str
    data: Dict[str, Any]


class DashboardStatsResponse(BaseModel):
    """Response model for dashboard statistics."""
    total_scans: int
    completed_scans: int
    active_sessions: int
    total_reports: int
    total_vulnerabilities: int
    high_severity_vulnerabilities: int
    recent_scans: List[Dict[str, Any]]


class WiFiNetworkResponse(BaseModel):
    """Response model for WiFi network."""
    bssid: str
    ssid: str
    signal: int
    channel: int
    encryption: str
    mode: str


class NmapHost(BaseModel):
    """Response model for Nmap host."""
    ip: str
    status: str
    hostname: Optional[str] = None
    os: Optional[str] = None
    ports: List[Dict[str, Any]] = Field(default_factory=list)
    services: List[Dict[str, Any]] = Field(default_factory=list)


class NmapScanResponse(BaseModel):
    """Response model for Nmap scan results."""
    scan_id: int
    target: str
    scan_type: str
    status: str
    hosts: List[NmapHost] = Field(default_factory=list)
    raw_output: Optional[str] = None
    error: Optional[str] = None


# Error Response
class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# Health Check
class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
