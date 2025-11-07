# Three System Applications

This repository contains three distinct applications:

1. **Network Analysis Application** - Analyzes communication networks for failure points, routing optimization, and device placement
2. **Car Monitoring System** - Handles car data monitoring with rate-limited service and priority-based update scheduling
3. **Weather Alert System** - Robust weather alert system for truck fleet management

## Project Structure

```
.
├── network_analysis/          # Network analysis application
│   ├── __init__.py
│   ├── network.py            # Network representation (nodes, links)
│   ├── rules.py              # Customizable rulesets
│   ├── analyzer.py           # Analysis engine
│   └── main.py               # Entry point
│
├── car_monitoring/           # Car monitoring system
│   ├── __init__.py
│   ├── car_simulator.py      # Car data simulation
│   ├── monitoring_client.py  # Rate-limited client
│   ├── update_scheduler.py   # Priority-based scheduler
│   └── main.py               # Entry point
│
├── weather_alert/            # Weather alert system
│   ├── __init__.py
│   ├── weather_service.py    # Weather data and alerts
│   ├── fleet_manager.py      # Fleet management
│   ├── alert_system.py       # Alert delivery system
│   └── main.py               # Entry point
│
├── requirements.txt
└── README.md
```

## Installation

All applications use only Python 3.7+ standard library - no external dependencies required.

```bash
# Ensure Python 3.7+ is installed
python --version

# No pip install needed - all dependencies are standard library
```

## Usage

### 1. Network Analysis Application

Analyzes communication networks to identify failure points, find optimal routes, and suggest device placements.

```bash
# Option 1: Run from within the directory
cd network_analysis
python main.py

# Option 2: Run from parent directory as module
python -m network_analysis.main
```

**Features:**
- Failure point identification based on customizable rules
- Optimal routing (latency, reliability, or balanced)
- Device placement suggestions (repeaters, etc.)
- Customizable rulesets for evaluation
- Network health scoring

**Key Components:**
- `Network`: Represents nodes and links
- `NetworkRules`: Customizable evaluation rules
- `NetworkAnalyzer`: Performs analysis operations

### 2. Car Monitoring System

Simulates cars sending data to a rate-limited monitoring service and handles update notifications with priority-based scheduling.

```bash
# Option 1: Run from within the directory
cd car_monitoring
python main.py

# Option 2: Run from parent directory as module
python -m car_monitoring.main
```

**Features:**
- Rate-limited client (configurable requests/second)
- Priority-based request queuing
- Update scheduling based on priority:
  - Critical: Immediate
  - High: Within 1 minute
  - Medium: Within 5 minutes
  - Low: Within 30 minutes
- Automatic retry logic
- Multiple car support

**Key Components:**
- `CarSimulator`: Generates car data
- `MonitoringClient`: Handles rate limiting and queuing
- `UpdateScheduler`: Schedules updates based on priority

### 3. Weather Alert System

Robust weather alert system for truck fleet that ensures critical alerts reach drivers immediately.

```bash
# Option 1: Run from within the directory
cd weather_alert
python main.py

# Option 2: Run from parent directory as module
python -m weather_alert.main
```

**Features:**
- Real-time weather monitoring
- Critical alert immediate delivery (multiple channels)
- Multiple delivery methods:
  - In-cab alerts (highest priority)
  - SMS notifications
  - Push notifications
  - Email alerts
- Retry logic for failed deliveries
- Fleet management integration
- Operator and maintenance record tracking

**Key Components:**
- `WeatherService`: Provides weather data and alerts
- `FleetManager`: Manages trucks, operators, and maintenance
- `WeatherAlertSystem`: Handles alert delivery with robustness

## Design Decisions

### Network Analysis
- **Customizable Rules**: Rules can be enabled/disabled, weighted, and have thresholds adjusted
- **Multiple Routing Algorithms**: Supports latency-optimized, reliability-optimized, and balanced routing
- **Failure Point Detection**: Uses multiple criteria (load, reliability, connectivity, criticality)

### Car Monitoring
- **Rate Limiting**: Token bucket algorithm ensures service limits are respected
- **Priority Queuing**: Critical requests are processed first
- **Update Scheduling**: Non-critical updates can be deferred to reduce system load
- **Threading**: Asynchronous processing for responsiveness

### Weather Alert System
- **Multi-Channel Delivery**: Critical alerts use multiple channels for redundancy
- **Priority-Based Processing**: Critical alerts are processed immediately
- **Retry Logic**: Failed critical alerts are retried automatically
- **Fleet Integration**: Considers truck status, location, and operator information

## Customization

### Network Analysis Rules

Rules can be customized in `network_analysis/rules.py`:

```python
rules = NetworkRules()
rules.update_rule("node_load", threshold=0.7, weight=1.5)
rules.update_rule("reliability", threshold=0.95, weight=2.0)
```

### Car Monitoring Rate Limits

Adjust rate limits in `car_monitoring/monitoring_client.py`:

```python
client = MonitoringClient("http://service.com", max_requests_per_second=20)
```

### Weather Alert Delivery

Modify delivery methods in `weather_alert/alert_system.py`:

```python
# Customize delivery methods based on severity
if alert.severity == WeatherSeverity.CRITICAL:
    delivery_methods = ["in_cab", "sms", "push", "email"]
```

## Testing

Each application includes sample data and can be run directly:

```bash
# Test network analysis
python network_analysis/main.py

# Test car monitoring
python car_monitoring/main.py

# Test weather alerts
python weather_alert/main.py
```

## Extending the Systems

### Network Analysis
- Add new rule types in `rules.py`
- Implement new routing algorithms in `analyzer.py`
- Add support for different network topologies

### Car Monitoring
- Integrate with real monitoring service API
- Add more sophisticated update scheduling logic
- Implement update server communication

### Weather Alert System
- Integrate with real weather APIs
- Add GPS tracking integration
- Implement driver acknowledgment system
- Add historical alert analytics

## Notes

- All systems are designed to be production-ready foundations
- Error handling and robustness are built-in
- Systems can be extended with real API integrations
- Threading is used for concurrent operations
- All systems include comprehensive logging and status reporting

## License

This project is provided as-is for demonstration purposes.

