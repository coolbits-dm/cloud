# Policy Gap Analysis Report
- Generated at: 2025-09-11T07:48:30Z
- Source: reports/policy_collect_last_24h.json
- Analysis window: 2025-09-11T07:48:24Z
- Total violations: **2**
- Total gaps found: **2**

## Priority Summary
- High priority: **2**
- Medium priority: **0**
- Low priority: **0**

## Gaps by Type
- unknown_agent: 1
- permission_gap: 1

## High Priority Gaps

### unknown_agent
- **Agent/Scope**: nha:unknown
- **Count**: 1
- **Rationale**: Unknown agent has 1 violations - check agent configuration
- **Recommendation**: Verify agent ID configuration and registry entries

### permission_gap
- **Agent/Scope**: N/A
- **Count**: 1
- **Rationale**: Permission denied 1 times - check IAM policies
- **Recommendation**: Review and update IAM permissions in registry
