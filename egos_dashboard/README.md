# EGOS Monitoring Dashboard

This dashboard provides a real-time view of the EGOS ecosystem's status, enabling monitoring of all subsystems, key metrics, and system health.

## Features

- **System Status Overview**: Key metrics and status indicators for all subsystems
- **Health Visualization**: Visual representation of system health through radar charts
- **Subsystem Details**: In-depth metrics and charts for each subsystem
- **Real-time Updates (Simulated)**: Connects to a mock NATS client to simulate live data updates.
- **Multi-language Support**: Interface available in English and Portuguese
- **Dark/Light Mode**: Adjustable theme for different lighting conditions, with improved contrast in light mode.
- **Comprehensive Logging**: Utilizes `KoiosLogger` to track user actions and system events according to EGOS standards.

## Architecture

```
egos_dashboard/
├── app.py                  # Main application script
├── requirements.txt        # Python dependencies
├── logs/                   # Directory for dashboard logs
└── src/
    ├── __init__.py
    ├── config.py           # Configuration settings
    ├── data_simulation.py  # Simulation data generators (Not used with mock client)
    ├── koios_logger.py     # Standardized logging module
    ├── nats_client.py      # NATS connectivity (uses mock implementation)
    ├── nats_mock.py        # Mock NATS client for demonstration
    ├── theming.py          # CSS styles for dark/light modes
    ├── translations.py     # Multilingual support
    └── ui_components.py    # Streamlit UI rendering functions
```

## Running the Dashboard

### Prerequisites

- Python 3.9+
- Required packages (see requirements.txt)

### Installation

1.  Navigate to the main EGOS project directory.
2.  Ensure your virtual environment is activated.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Execution

1.  Navigate to the dashboard directory:
    ```bash
    cd egos_dashboard
    ```
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
3.  Open your browser at [http://localhost:8501](http://localhost:8501)

## Using with Mock NATS

The dashboard currently uses a built-in mock NATS client (`nats_mock.py`) to simulate data flow. Simply run the dashboard as described above, and click the "Connect to Live Data" button to start receiving simulated status, metrics, and alert messages.

## Future Development

- Integrate with the real MYCELIUM NATS network once stable.
- Refine UI/UX based on feedback.
- Deploy the dashboard to a hosting platform (e.g., Streamlit Community Cloud).

## Security Note

Follow the EGOS Security Practices when extending this dashboard, particularly regarding data handling and potential future external connections.
