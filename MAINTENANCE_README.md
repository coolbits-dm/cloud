# CoolBits.ai Automated Maintenance

This directory contains automated maintenance scripts and routines for CoolBits.ai infrastructure.

## 🚀 Quick Start

### Run Maintenance Now
```bash
# Daily maintenance
python automated_maintenance.py --run

# Weekly validation
python weekly_validator.py --run

# Full operational checklist
python operational_checklist.py --all
```

### Setup Automated Scheduling
```bash
# Start automated maintenance scheduler
python automated_maintenance.py --setup

# Setup weekly validation
python weekly_validator.py --schedule
```

## 📋 Maintenance Scripts

### Daily Maintenance
- **Linux/Mac**: `scripts/daily_maintenance.sh`
- **Windows**: `scripts/daily_maintenance.bat`
- **Python**: `python automated_maintenance.py --run`

### Weekly Maintenance
- **Linux/Mac**: `scripts/weekly_maintenance.sh`
- **Windows**: `scripts/weekly_maintenance.bat`
- **Python**: `python weekly_validator.py --run`

### Monthly Maintenance
- **Linux/Mac**: `scripts/monthly_maintenance.sh`
- **Python**: `python operational_checklist.py --monthly`

## 🔧 System Services

### Linux (systemd)
```bash
# Install service
sudo cp scripts/coolbits-maintenance.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coolbits-maintenance
sudo systemctl start coolbits-maintenance
```

### Windows Service
```bash
# Install service
scripts/install_windows_service.bat

# Or manually
python coolbits_maintenance_service.py install
python coolbits_maintenance_service.py start
```

## 📊 Monitoring Dashboard

Start the monitoring dashboard:
```bash
streamlit run monitoring_dashboard.py
```

Access at: http://localhost:8501

## 📋 Operational Checklist

### Daily Checks
- [ ] CI pipeline runs on every commit
- [ ] Health endpoints respond
- [ ] Log files are rotated
- [ ] Uptime monitoring is active

### Weekly Checks
- [ ] Run weekly validation
- [ ] Test canary deployment
- [ ] Test RBAC/HMAC security
- [ ] Test dashboard API connectivity
- [ ] Review security audit logs

### Monthly Checks
- [ ] Rotate HMAC keys
- [ ] Review security policies
- [ ] Test disaster recovery
- [ ] Update dependencies
- [ ] Review monitoring dashboards

## 🚨 Emergency Procedures

### Rollback Deployment
```bash
python rollback_manager.py emergency
```

### Revoke Compromised Keys
```bash
python hmac_key_manager.py revoke --key-id <KEY_ID>
```

### Activate Maintenance Mode
```bash
python automated_maintenance.py --maintenance-mode
```

## 📞 Support

- **Primary**: Andrei (CEO)
- **Technical**: oPyGPT03
- **Security**: oGrok08 (CISO)
- **AI/ML**: oGrok09 (CAIO)

## 📈 Success Criteria

- [ ] All automated tests pass
- [ ] No critical security vulnerabilities
- [ ] System performance within SLA
- [ ] Documentation up to date
- [ ] Team trained on procedures

## 🔄 Continuous Improvement

This maintenance system is designed to evolve with CoolBits.ai infrastructure. Regular reviews and updates ensure optimal performance and reliability.

---

**CoolBits.ai Infrastructure Team** | Last Updated: 2025-09-10
