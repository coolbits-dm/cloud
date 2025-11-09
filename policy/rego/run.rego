# CoolBits.ai OPA Policies
# M9.3 - Policy-as-Code

package policy.run

# Deny if missing required labels
deny[msg] {
    input.kind == "Service"
    not input.metadata.labels.env
    msg := "label 'env' is mandatory"
}

deny[msg] {
    input.kind == "Service"
    not input.metadata.labels.owner
    msg := "label 'owner' is mandatory"
}

deny[msg] {
    input.kind == "Service"
    not input.metadata.labels.cost_center
    msg := "label 'cost_center' is mandatory"
}

# Deny if image is not signed
deny[msg] {
    input.kind == "Service"
    not input.spec.template.metadata.annotations["cosign.sig.valid"]
    msg := "image must be signed with cosign"
}

# Deny if resource limits are too high
deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.containers[_].resources.limits.memory
    memory := input.spec.template.spec.containers[_].resources.limits.memory
    memory > "8Gi"
    msg := "memory limit too high, max 8Gi allowed"
}

deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.containers[_].resources.limits.cpu
    cpu := input.spec.template.spec.containers[_].resources.limits.cpu
    cpu > "4"
    msg := "CPU limit too high, max 4 cores allowed"
}

# Deny if security context is missing
deny[msg] {
    input.kind == "Service"
    not input.spec.template.spec.containers[_].securityContext.runAsNonRoot
    msg := "containers must run as non-root"
}

# Deny if health checks are missing
deny[msg] {
    input.kind == "Service"
    not input.spec.template.spec.containers[_].livenessProbe
    msg := "liveness probe is mandatory"
}

deny[msg] {
    input.kind == "Service"
    not input.spec.template.spec.containers[_].readinessProbe
    msg := "readiness probe is mandatory"
}

# Deny if environment variables contain secrets
deny[msg] {
    input.kind == "Service"
    env := input.spec.template.spec.containers[_].env[_]
    env.name == "PASSWORD"
    msg := "PASSWORD environment variable not allowed, use Secret Manager"
}

deny[msg] {
    input.kind == "Service"
    env := input.spec.template.spec.containers[_].env[_]
    env.name == "API_KEY"
    msg := "API_KEY environment variable not allowed, use Secret Manager"
}

deny[msg] {
    input.kind == "Service"
    env := input.spec.template.spec.containers[_].env[_]
    env.name == "SECRET"
    msg := "SECRET environment variable not allowed, use Secret Manager"
}

# Deny if ports are not secure
deny[msg] {
    input.kind == "Service"
    port := input.spec.template.spec.containers[_].ports[_]
    port.containerPort == 22
    msg := "SSH port 22 not allowed"
}

deny[msg] {
    input.kind == "Service"
    port := input.spec.template.spec.containers[_].ports[_]
    port.containerPort == 23
    msg := "Telnet port 23 not allowed"
}

# Deny if privileged mode is enabled
deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.containers[_].securityContext.privileged
    msg := "privileged containers not allowed"
}

# Deny if host network is used
deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.hostNetwork
    msg := "host network not allowed"
}

# Deny if host PID is used
deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.hostPID
    msg := "host PID not allowed"
}

# Deny if host IPC is used
deny[msg] {
    input.kind == "Service"
    input.spec.template.spec.hostIPC
    msg := "host IPC not allowed"
}
