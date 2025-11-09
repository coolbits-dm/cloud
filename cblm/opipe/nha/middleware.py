# CoolBits.ai @oPipe - NHA Enforcement Middleware for FastAPI
# Middleware care interceptează toate request-urile și aplică policy enforcement

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Callable, Any
from .enforcer import enforce_request


class NhaEnforcementMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, action_resolver: Callable[[Request], Dict[str, Any]]):
        """
        action_resolver: func(Request) -> dict cu:
          {
            "nha_id": "...",              # obligatoriu (din header/JWT/etc.)
            "action": "rag:ingest",       # obligatoriu
            "scope": "write:rag",         # opțional
            "require_secret": "nha/opypgpt03/hmac", # opțional
            "extras": {"path": "..."}     # audit context (opțional)
          }
        """
        super().__init__(app)
        self.action_resolver = action_resolver

    async def dispatch(self, request: Request, call_next):
        # Resolve action context from request
        ctx = await self._resolve(request)

        # Enforce policy
        res = enforce_request(
            ctx["nha_id"],
            ctx["action"],
            payload={},
            scope=ctx.get("scope"),
            require_secret=ctx.get("require_secret"),
            extras=ctx.get("extras"),
        )

        # Handle enforcement result
        if not res.allowed and res.decision == "DENY":
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": res.reason,
                    "trace_id": res.trace_id,
                    "nha_id": res.nha_id,
                    "action": res.action,
                    "policy_version": res.policy_version,
                },
            )

        # Add enforcement headers to response
        response = await call_next(request)
        response.headers["X-Policy-Trace-ID"] = res.trace_id
        response.headers["X-Policy-Decision"] = res.decision
        response.headers["X-Policy-Version"] = res.policy_version

        return response

    async def _resolve(self, request: Request) -> dict:
        """Resolve NHA context from request"""
        # Try to get from headers first
        nha_id = request.headers.get("X-NHA-ID", "").strip()
        action = request.headers.get("X-NHA-ACTION", "").strip()
        scope = request.headers.get("X-NHA-SCOPE", "").strip() or None
        req_secret = request.headers.get("X-NHA-REQUIRE-SECRET", "").strip() or None

        # If not in headers, try to resolve from request context
        if not nha_id or not action:
            # Fallback: map based on route and method
            nha_id = nha_id or "nha:unknown"
            action = action or f"http:{request.method.lower()}:{request.url.path}"

        # Extract additional context
        extras = {
            "path": str(request.url.path),
            "method": request.method,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent", ""),
            "remote_addr": request.client.host if request.client else "unknown",
        }

        return {
            "nha_id": nha_id,
            "action": action,
            "scope": scope,
            "require_secret": req_secret,
            "extras": extras,
        }


class NhaActionResolver:
    """Helper class for resolving actions from request patterns"""

    def __init__(self):
        # Route to action mapping
        self.route_mappings = {
            "/api/rag/ingest": "rag:ingest",
            "/api/rag/search": "rag:search",
            "/api/agents": "agents:read",
            "/api/export": "export:data",
            "/api/chaos": "chaos:run",
            "/api/slo": "slo:check",
            "/api/monitor": "monitoring:read",
            "/api/backup": "backup:create",
            "/api/restore": "restore:execute",
        }

        # Method to scope mapping
        self.method_scopes = {
            "GET": "read",
            "POST": "write",
            "PUT": "write",
            "PATCH": "write",
            "DELETE": "delete",
        }

    def resolve_from_headers(self, request: Request) -> dict:
        """Resolve from X-NHA-* headers"""
        nha_id = request.headers.get("X-NHA-ID", "").strip()
        action = request.headers.get("X-NHA-ACTION", "").strip()
        scope = request.headers.get("X-NHA-SCOPE", "").strip() or None
        req_secret = request.headers.get("X-NHA-REQUIRE-SECRET", "").strip() or None

        return {
            "nha_id": nha_id,
            "action": action,
            "scope": scope,
            "require_secret": req_secret,
        }

    def resolve_from_route(self, request: Request) -> dict:
        """Resolve from route patterns"""
        path = request.url.path
        method = request.method

        # Check exact route matches
        if path in self.route_mappings:
            action = self.route_mappings[path]
        else:
            # Generic HTTP action
            action = f"http:{method.lower()}:{path}"

        # Determine scope from method
        scope_prefix = self.method_scopes.get(method, "read")

        # Extract scope from action if it contains colon
        if ":" in action:
            action_parts = action.split(":")
            if len(action_parts) >= 2:
                scope = f"{scope_prefix}:{action_parts[1]}"
            else:
                scope = f"{scope_prefix}:{action_parts[0]}"
        else:
            scope = f"{scope_prefix}:{action}"

        return {
            "nha_id": "nha:unknown",  # Will be overridden by auth
            "action": action,
            "scope": scope,
            "require_secret": None,
        }

    def resolve_from_jwt(self, request: Request) -> dict:
        """Resolve from JWT claims (placeholder for future implementation)"""
        # TODO: Implement JWT parsing and claim extraction
        # For now, return empty context
        return {
            "nha_id": "nha:unknown",
            "action": "unknown",
            "scope": None,
            "require_secret": None,
        }


def create_action_resolver(
    resolver_type: str = "headers",
) -> Callable[[Request], Dict[str, Any]]:
    """Factory function to create action resolvers"""
    resolver = NhaActionResolver()

    if resolver_type == "headers":
        return resolver.resolve_from_headers
    elif resolver_type == "route":
        return resolver.resolve_from_route
    elif resolver_type == "jwt":
        return resolver.resolve_from_jwt
    else:
        # Default: try headers first, fallback to route
        def hybrid_resolver(request: Request) -> dict:
            header_result = resolver.resolve_from_headers(request)
            if header_result["nha_id"] and header_result["action"]:
                return header_result
            return resolver.resolve_from_route(request)

        return hybrid_resolver


# Convenience function for FastAPI integration
def add_nha_enforcement(app, resolver_type: str = "headers"):
    """Add NHA enforcement middleware to FastAPI app"""
    action_resolver = create_action_resolver(resolver_type)
    app.add_middleware(NhaEnforcementMiddleware, action_resolver=action_resolver)
    return app
