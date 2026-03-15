from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import subprocess
import re
import requests
import os

router = APIRouter(prefix="/ai", tags=["ai"])

# LM Studio configuration - read from environment variables
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "sk-local")

# System prompt for the RedTeam AI assistant
SYSTEM_PROMPT = """You are an expert Red Team AI Assistant specializing in cybersecurity operations.

You can help users with:
- Nmap network scanning and host discovery
- Metasploit framework for exploitation
- SQLMap for SQL injection testing
- Hydra for password brute-forcing
- Responder for LLMNR/NBT-NS poisoning and hash capture
- BloodHound for Active Directory enumeration
- CrackMapExec for network pivoting

When users ask about security operations, provide helpful guidance. If they want to run scans or exploits, guide them to use the appropriate tools in the dashboard. Be helpful, but remind users to only test systems they have permission to test.

Always be ready to explain security concepts, suggest tools for specific tasks, and help with reconnaissance, vulnerability assessment, and exploitation techniques."""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    actions: Optional[List[dict]] = None


# Tool patterns for suggesting actions
TOOL_MAPPINGS = {
    "nmap": {
        "patterns": [r"scan", r"port", r"network", r"discover", r"find hosts"],
        "description": "Network scanning and discovery"
    },
    "metasploit": {
        "patterns": [r"exploit", r"payload", r"msf", r"meterpreter"],
        "description": "Metasploit Framework for exploitation"
    },
    "sqlmap": {
        "patterns": [r"sql", r"injection", r"database"],
        "description": "SQL injection testing"
    },
    "hydra": {
        "patterns": [r"brute", r"password", r"login", r"crack"],
        "description": "Password brute-forcing"
    },
    "responder": {
        "patterns": [r"responder", r"hash", r"ntlm", r"poisoning"],
        "description": "LLMNR/NBT-NS responder"
    },
    "bloodhound": {
        "patterns": [r"bloodhound", r"ad", r"active directory", r"domain"],
        "description": "Active Directory enumeration"
    },
    "crackmapexec": {
        "patterns": [r"cme", r"crackmapexec", r"smb", r"winrm"],
        "description": "Network pivoting and Windows domain exploitation"
    }
}


def call_lm_studio(messages: List[dict]) -> Optional[str]:
    """Call LM Studio API and return the response."""
    try:
        # Build the messages array with system prompt
        all_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        payload = {
            "model": LM_STUDIO_MODEL,
            "messages": all_messages,
            "temperature": 0.7,
            "max_tokens": -1,  # No limit
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {LM_STUDIO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        print(f"LM Studio error: {e}")
        return None


def analyze_user_intent(user_message: str) -> dict:
    """Analyze user message to determine intent and suggest actions."""
    message_lower = user_message.lower()
    intent = {
        "type": "general",
        "confidence": 0.0,
        "suggested_tools": [],
        "response": ""
    }
    
    # Check for tool-specific patterns
    for tool, info in TOOL_MAPPINGS.items():
        for pattern in info["patterns"]:
            if re.search(pattern, message_lower):
                intent["suggested_tools"].append({
                    "tool": tool,
                    "description": info["description"]
                })
                intent["confidence"] += 0.3
    
    # Determine intent type
    if any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
        intent["type"] = "help"
    elif any(word in message_lower for word in ["scan", "find", "discover", "check"]):
        intent["type"] = "scan"
    elif any(word in message_lower for word in ["exploit", "attack", "run"]):
        intent["type"] = "exploit"
    elif any(word in message_lower for word in ["report", "results", "findings"]):
        intent["type"] = "report"
    elif any(word in message_lower for word in ["explain", "what is", "how does"]):
        intent["type"] = "explanation"
    
    return intent


def generate_fallback_response(user_message: str, intent: dict) -> str:
    """Generate a fallback response when LM Studio is not available."""
    
    if intent["type"] == "help":
        return """I can help you with various Red Team operations:

**Available Tools:**
- **Nmap**: Network scanning, port discovery, and host detection
- **Metasploit**: Exploitation framework for penetration testing  
- **SQLMap**: SQL injection vulnerability scanning
- **Hydra**: Password brute-forcing and credential attacks
- **Responder**: LLMNR/NBT-NS poisoning for hash capture
- **BloodHound**: Active Directory enumeration and privilege path analysis
- **CrackMapExec**: Network pivoting and Windows domain exploitation

Just tell me what you'd like to do, for example:
- "Scan 192.168.1.1 for open ports"
- "Run an exploit against the target"
- "Check for SQL vulnerabilities in the target URL"
- "Capture NTLM hashes with Responder" """

    if intent["type"] == "scan":
        if intent["suggested_tools"]:
            tools = ", ".join([t["tool"] for t in intent["suggested_tools"]])
            return f"I'll help you with scanning. Based on your request, I can use: {tools}\n\nPlease provide the target IP address or network range you'd like to scan."
        return "I understand you want to perform a scan. Please specify the target (IP address or network) and what you'd like to scan for."

    if intent["type"] == "exploit":
        if intent["suggested_tools"]:
            tools = ", ".join([t["tool"] for t in intent["suggested_tools"]])
            return f"I can help with exploitation using: {tools}\n\nPlease provide:\n1. Target information (IP, hostname)\n2. The specific exploit or vulnerability you'd like to target"
        return "I understand you want to run an exploit. Please provide the target system and the type of exploit you'd like to attempt."

    if intent["type"] == "explanation":
        return "I'd be happy to explain various Red Team concepts and tools. What specific topic would you like to learn about?"

    if intent["type"] == "report":
        return "I can help you generate reports. You can view your scan results and reports in the Reports section of the dashboard."

    # Default response
    if intent["confidence"] > 0.5:
        tools = ", ".join([t["tool"] for t in intent["suggested_tools"]])
        return f"I understand you're interested in: {tools}. How would you like to proceed?"

    return """I'm here to assist with Red Team operations. You can ask me to:

- **Scan networks**: "Scan 192.168.1.0/24"
- **Find vulnerabilities**: "Check for SQL injection on target.com"
- **Run exploits**: "Exploit the target with Metasploit"
- **Capture hashes**: "Start Responder on the network"
- **Enumerate AD**: "Run BloodHound analysis"

What would you like to do?"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat messages and return AI responses using LM Studio."""
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get the last user message
    user_message = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break
    
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    # Analyze intent for suggested actions
    intent = analyze_user_intent(user_message)
    
    # Try to call LM Studio
    messages_for_api = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    response_text = call_lm_studio(messages_for_api)
    
    # If LM Studio is not available, use fallback
    if not response_text:
        response_text = generate_fallback_response(user_message, intent)
    
    # Build suggested actions if relevant tools found
    actions = None
    if intent["suggested_tools"]:
        actions = []
        for tool_info in intent["suggested_tools"]:
            actions.append({
                "type": "tool_suggestion",
                "tool": tool_info["tool"],
                "description": tool_info["description"]
            })
    
    return ChatResponse(
        message=response_text,
        actions=actions
    )


@router.get("/status")
async def get_ai_status():
    """Check LM Studio connection status."""
    try:
        headers = {
            "Authorization": f"Bearer {LM_STUDIO_API_KEY}"
        }
        response = requests.get("http://localhost:1234/v1/models", headers=headers, timeout=5)
        if response.status_code == 200:
            models = response.json()
            return {
                "status": "connected",
                "provider": "LM Studio",
                "models": models.get("data", [])
            }
    except:
        pass
    
    return {
        "status": "disconnected",
        "provider": "LM Studio",
        "message": "LM Studio is not running. Please start LM Studio and load a model."
    }


@router.get("/capabilities")
async def get_capabilities():
    """Return available AI capabilities."""
    return {
        "name": "RedTeam AI Assistant",
        "version": "1.0.0",
        "provider": "LM Studio (local)",
        "capabilities": [
            "Network scanning and discovery",
            "Vulnerability assessment",
            "Exploitation assistance",
            "Report generation",
            "Security tool guidance"
        ],
        "available_tools": list(TOOL_MAPPINGS.keys())
    }
