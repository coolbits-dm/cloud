# CoolBits.ai Makefile
# ===================

.PHONY: m-gate help

# M-gate target for milestone transitions
m-gate:
	@bash scripts/m_gate.sh $(M)

# Help target
help:
	@echo "CoolBits.ai Make Targets:"
	@echo "  m-gate M=<milestone>  - Run M-gate for milestone transition"
	@echo "  help                  - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make m-gate M=M15     - Run M15 gate"
	@echo "  make m-gate M=M16     - Run M16 gate"