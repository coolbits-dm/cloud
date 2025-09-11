# CoolBits.ai @oPipe - NHA Registry Canonical
# Single source of truth for all Non-Human Agents

from dataclasses import dataclass, field
from typing import List, Dict, Literal, Optional
import json
import yaml
import re
import sys
from pathlib import Path

Category = Literal["personal", "biz_channels", "biz_tools", "seo_tools", "agency", "dev_tools", "infra", "security", "mlops", "ops"]

@dataclass
class Channel:
    kind: Literal["http", "ws", "cli", "sdk", "ui"]
    endpoint: str  # url, command sau package
    auth: Literal["none", "hmac", "jwt", "oauth", "sa_key", "kms"] = "none"

@dataclass
class Capability:
    name: str
    description: str
    scopes: List[str] = field(default_factory=list)  # e.g. ["read:logs","write:rag"]

@dataclass
class SLO:
    latency_p95_ms: int = 1000
    error_rate_max: float = 0.05
    availability_pct: float = 99.0

@dataclass
class Identity:
    key_id: Optional[str] = None
    secret_ref: Optional[str] = None  # gcp secret name / dpapi ref

@dataclass
class NHA:
    id: str                 # ex: "nha:opypgpt03"
    name: str               # ex: "@oPyGPT03"
    category: Category
    owner: str              # ex: "andrei" / "platform"
    status: Literal["active", "paused", "deprecated"] = "active"
    channels: List[Channel] = field(default_factory=list)
    capabilities: List[Capability] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)   # IAM roles logical (ex: "run.invoker")
    secrets: List[str] = field(default_factory=list)       # logical secret names
    tags: List[str] = field(default_factory=list)          # "provider:openai", "env:prod"
    slo: SLO = field(default_factory=SLO)
    notes: str = ""

@dataclass
class Registry:
    version: str
    nhas: List[NHA]

def load_yaml(path: str) -> Registry:
    """Load registry from YAML file with validation"""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Map to dataclasses; validate uniqueness
    ids, names = set(), set()
    nhas = []
    
    for x in data["nhas"]:
        if x["id"] in ids:
            raise SystemExit(f"Duplicate id: {x['id']}")
        if x["name"] in names:
            raise SystemExit(f"Duplicate name: {x['name']}")
        
        ids.add(x["id"])
        names.add(x["name"])
        
        # Convert channels
        channels = []
        for ch in x.get("channels", []):
            channels.append(Channel(**ch))
        
        # Convert capabilities
        capabilities = []
        for cap in x.get("capabilities", []):
            capabilities.append(Capability(**cap))
        
        # Convert SLO
        slo_data = x.get("slo", {})
        slo = SLO(**slo_data)
        
        # Create NHA
        nha_data = {k: v for k, v in x.items() if k not in ["channels", "capabilities", "slo"]}
        nha_data["channels"] = channels
        nha_data["capabilities"] = capabilities
        nha_data["slo"] = slo
        
        nhas.append(NHA(**nha_data))
    
    return Registry(version=data.get("version", "dev"), nhas=nhas)

def dump_json(reg: Registry, out: str = "cblm/opipe/nha/out/registry.json"):
    """Export registry to JSON format"""
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "version": reg.version,
            "count": len(reg.nhas),
            "nhas": [
                {
                    **vars(n),
                    "channels": [vars(c) for c in n.channels],
                    "capabilities": [vars(c) for c in n.capabilities],
                    "slo": vars(n.slo)
                } for n in reg.nhas
            ]
        }, f, ensure_ascii=False, indent=2)

def dump_markdown(reg: Registry, out: str = "cblm/opipe/nha/out/registry.md"):
    """Export registry to Markdown format"""
    md_content = f"""# CoolBits.ai NHA Registry

**Version**: {reg.version}  
**Total Agents**: {len(reg.nhas)}  
**Generated**: {Path(__file__).stat().st_mtime}

## Summary by Category

"""
    
    # Group by category
    categories = {}
    for nha in reg.nhas:
        if nha.category not in categories:
            categories[nha.category] = []
        categories[nha.category].append(nha)
    
    for category, nhas in categories.items():
        md_content += f"### {category.replace('_', ' ').title()}\n"
        md_content += f"**Count**: {len(nhas)}\n\n"
        
        for nha in nhas:
            md_content += f"- **{nha.name}** (`{nha.id}`)\n"
            md_content += f"  - Owner: {nha.owner}\n"
            md_content += f"  - Status: {nha.status}\n"
            md_content += f"  - Channels: {len(nha.channels)}\n"
            md_content += f"  - Capabilities: {len(nha.capabilities)}\n"
            md_content += f"  - Permissions: {', '.join(nha.permissions) if nha.permissions else 'None'}\n"
            md_content += f"  - Tags: {', '.join(nha.tags) if nha.tags else 'None'}\n"
            if nha.notes:
                md_content += f"  - Notes: {nha.notes}\n"
            md_content += "\n"
    
    with open(out, "w", encoding="utf-8") as f:
        f.write(md_content)

def dump_by_category(reg: Registry, out: str = "cblm/opipe/nha/out/by-category.md"):
    """Export registry grouped by category with tables"""
    md_content = f"""# CoolBits.ai NHA Registry - By Category

**Version**: {reg.version}  
**Total Agents**: {len(reg.nhas)}

"""
    
    # Group by category
    categories = {}
    for nha in reg.nhas:
        if nha.category not in categories:
            categories[nha.category] = []
        categories[nha.category].append(nha)
    
    for category, nhas in sorted(categories.items()):
        md_content += f"## {category.replace('_', ' ').title()}\n\n"
        
        # Create table
        md_content += "| ID | Name | Owner | Status | Channels | Permissions | Tags |\n"
        md_content += "|----|------|-------|--------|----------|-------------|------|\n"
        
        for nha in sorted(nhas, key=lambda x: x.id):
            channels_str = f"{len(nha.channels)}" if nha.channels else "0"
            perms_str = ", ".join(nha.permissions[:3]) if nha.permissions else "None"
            if len(nha.permissions) > 3:
                perms_str += "..."
            tags_str = ", ".join(nha.tags[:2]) if nha.tags else "None"
            if len(nha.tags) > 2:
                tags_str += "..."
            
            md_content += f"| `{nha.id}` | {nha.name} | {nha.owner} | {nha.status} | {channels_str} | {perms_str} | {tags_str} |\n"
        
        md_content += "\n"
    
    with open(out, "w", encoding="utf-8") as f:
        f.write(md_content)

def get_nha_by_id(reg: Registry, nha_id: str) -> Optional[NHA]:
    """Get NHA by ID"""
    for nha in reg.nhas:
        if nha.id == nha_id:
            return nha
    return None

def get_nhas_by_category(reg: Registry, category: Category) -> List[NHA]:
    """Get all NHAs in a category"""
    return [nha for nha in reg.nhas if nha.category == category]

def get_nhas_by_owner(reg: Registry, owner: str) -> List[NHA]:
    """Get all NHAs owned by a specific owner"""
    return [nha for nha in reg.nhas if nha.owner == owner]

def get_active_nhas(reg: Registry) -> List[NHA]:
    """Get all active NHAs"""
    return [nha for nha in reg.nhas if nha.status == "active"]

def validate_registry(reg: Registry) -> List[str]:
    """Validate registry for business rules"""
    errors = []
    
    # Check required fields
    for nha in reg.nhas:
        if not nha.id.startswith("nha:"):
            errors.append(f"NHA {nha.name} has invalid ID format: {nha.id}")
        
        if not nha.channels:
            errors.append(f"NHA {nha.name} has no channels defined")
        
        if not nha.owner:
            errors.append(f"NHA {nha.name} has no owner")
        
        # Check for required tags
        required_tags = ["env", "service"]
        nha_tags = [tag.split(':')[0] for tag in nha.tags]
        for tag in required_tags:
            if tag not in nha_tags:
                errors.append(f"NHA {nha.name} missing required tag: {tag}")
    
    return errors

if __name__ == "__main__":
    try:
        reg = load_yaml("cblm/opipe/nha/agents.yaml")
        
        # Validate
        errors = validate_registry(reg)
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        # Generate artifacts
        dump_json(reg)
        dump_markdown(reg)
        dump_by_category(reg)
        
        print(f"✅ Registry loaded: {len(reg.nhas)} agents")
        print(f"✅ Artifacts generated in cblm/opipe/nha/out/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
