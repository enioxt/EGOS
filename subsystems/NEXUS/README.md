# 🧠 EVA & GUARANI - NEXUS Subsystem

**Version:** 1.0.0
**Status:** Active (Core Logic Stable, Tests Passing)

## Overview

NEXUS (Neural Evolution and Xenial Unified System) is the modular analysis engine for the EVA & GUARANI Operational System (EGOS). Its primary responsibility is to analyze source code, understand its structure, map dependencies between components, calculate relevant metrics (like complexity), and provide suggestions for improvement.

## Core Components

*   **`NEXUSCore` (`core/nexus_core.py`):** Implements the core analysis logic. It uses AST (Abstract Syntax Tree) parsing (`core/ast_visitor.py`) to inspect Python code. Key functions include:
    *   `analyze_code()`: Analyzes a single file for metrics (lines, complexity) and structure (imports, functions, classes).
    *   `analyze_dependencies()`: Analyzes imports across multiple files to build a dependency graph (identifying which files import others and which are imported by others). See method docstring for detailed return structure.
    *   `analyze_workspace()`: Orchestrates the analysis of all Python files in the project.
    *   `suggest_improvements()`: Provides suggestions based on configurable thresholds (e.g., high complexity, high import count, lack of docstrings).
    *   `export_analysis()`: Exports analysis results (currently supports JSON and Markdown).
*   **`NexusService` (`service.py`):** Intended as the primary service layer for NEXUS. It initializes `NEXUSCore` with appropriate configuration and logging. Currently, its role in handling Mycelium communication needs further definition and implementation. It defines handler methods (`handle_analyze_file_request`, etc.) but doesn't yet actively subscribe them via the Mycelium interface in its `start` method.
*   **`NexusAnalyzer` (`core/analyzer.py`):** **[Review Needed/Potential Refactor]** This class currently handles direct Mycelium interactions (subscribing to topics, publishing results/events) for analysis requests and updates. This functionality might be better integrated into `NexusService` or refactored into a dedicated communication handler module to separate concerns more clearly (core analysis vs. network interaction).
*   **`CodeVisitor` (`core/ast_visitor.py`):** An `ast.NodeVisitor` subclass responsible for traversing the code's AST and extracting structural information and calculating cognitive complexity.

## Key Features

*   **AST-Based Analysis:** Provides detailed insights into code structure beyond simple text matching.
*   **Dependency Mapping:** Identifies direct import relationships between Python modules.
*   **Complexity Calculation:** Calculates cognitive complexity based on control flow, nesting, boolean operators, and jumps.
*   **Improvement Suggestions:** Offers basic refactoring and documentation suggestions.
*   **Extensible:** Designed to be potentially extended with more advanced analysis techniques.

## Integration

*   **KOIOS:** Uses `KoiosLogger` (via `get_koios_logger`) for standardized logging. Relies on KOIOS standards for structure and documentation.

### NEXUS Value Proposition vs. Other Tools

While standard linters (`pylint`, `flake8`) detect import errors and IDEs provide immediate feedback, NEXUS's dependency analysis offers unique value within EGOS:

*   **Integrated Analysis Engine:** NEXUS serves as the central analysis engine for EGOS. Its primary goal is to generate a structured *dataset* describing the workspace's dependency landscape.
*   **Structured Data for Subsystems:** This dataset (including explicit categorization of internal, external, and unresolved imports) is designed for programmatic consumption by other EGOS subsystems like ATLAS (visualization) and KOIOS (reporting/suggestions).
*   **Customization & Context:** The analysis is tailored to the specific `subsystems` structure and conventions of the EGOS project.
*   **Beyond Error Checking:** Unlike linters focused on errors, NEXUS provides a comprehensive inventory and categorization for systemic understanding and further automated processing.

*   **MYCELIUM:** Intended to interact via `MyceliumInterface`. Currently, `NexusAnalyzer` handles subscriptions and event publishing. `NexusService` defines request handlers but doesn't actively bind them yet. Requires clarification/refactoring.
    *   **[TODO: Action Item - 2025-04-03]** Clearly define the responsibility boundary between `NexusService` and `NexusAnalyzer` for Mycelium communication. Options include consolidating into `NexusService`, creating a dedicated `NexusCommunicationHandler`, or clarifying existing roles. Update relevant class docstrings and this README once decided.
*   **ATLAS:** Analysis results from NEXUS (especially dependency information) are intended to be visualized by the ATLAS subsystem.

## Current Status & Next Steps (Post-Recovery)

*   Core logic migrated from previous structure.
*   Critical test blockers resolved; all tests currently passing.
*   Dependency analysis refactored for better accuracy and structure.
*   Complexity calculation logic fixed.
*   Basic README and docstring improvements added.
*   Next steps involve:
    *   Refining/Clarifying the roles of `NexusService` and `NexusAnalyzer` regarding Mycelium interaction. **(See TODO above in Mycelium Integration section)**
    *   Implementing Mycelium request handling within `NexusService` (dependent on role clarification).
    *   Adding more detailed documentation and usage examples.
    *   Further review of AST/dependency logic for edge cases if required.

## Configuration

Configuration for thresholds (e.g., complexity) and logging is passed via a dictionary to the `NEXUSCore` constructor, typically managed and provided by `NexusService` based on its own configuration.

Example `core_config` structure (passed to `NEXUSCore`):
```json
{
  "analysis": {
    "suggestions": {
      "cognitive_load_threshold_high": 50,
      "imports_threshold": 15,
      "imported_by_threshold": 10
    }
  }
}
```

## Usage Example (Directly using NEXUSCore)

```python
import logging
from pathlib import Path
from subsystems.NEXUS.core.nexus_core import NEXUSCore

# Assuming project_root and a suitable logger are defined
project_root = Path('.').resolve() # Example: Current directory
logger = logging.getLogger("TestNexus")
logging.basicConfig(level=logging.INFO)

# Minimal config
config = {
    'analysis': {
        'suggestions': {
            'cognitive_load_threshold_high': 50,
            'imports_threshold': 15,
            'imported_by_threshold': 10
        }
    }
}

# Initialize Core
nexus = NEXUSCore(config=config, logger=logger, project_root=project_root)

# Analyze the workspace
workspace_analysis = nexus.analyze_workspace()

# Export results
json_output = nexus.export_analysis(workspace_analysis, format='json')
md_output = nexus.export_analysis(workspace_analysis, format='md')

# Print suggestions
suggestions = nexus.suggest_improvements(workspace_analysis)
print("\nSuggestions:")
for suggestion in suggestions:
    print(f"- [{suggestion['severity'].upper()}] {suggestion['file']}: {suggestion['message']}")

```

*(Note: Direct Mycelium interaction example removed pending clarification of Service/Analyzer roles)*

## Features

### 1. Module Analysis
- Dependency tracking
- Relationship mapping
- Code quality metrics
- Complexity analysis
- Coverage tracking
- Real-time updates via Mycelium

### 2. Caching System
- In-memory result caching
- Configurable cache duration
- Automatic cache invalidation
- Cache size management
- Performance optimization

### 3. Mycelium Integration
- Real-time analysis requests
- Live dependency updates
- Module status notifications
- System-wide alerts
- Batch processing support
- Retry mechanisms

### 4. Metrics Collection
- Dependency metrics
- Complexity measurements
- Code coverage tracking
- Quality assessments
- Custom metric support

### 5. Visualization
- Dependency graphs
- Relationship maps
- Metric visualizations
- Multiple export formats
- Interactive viewing

## Usage

### Basic Analysis

```python
from nexus.core.analyzer import NexusAnalyzer
from mycelium import MyceliumClient

# Initialize
mycelium = MyceliumClient()
analyzer = NexusAnalyzer(mycelium_client=mycelium)

# Analyze a module
result = await analyzer.analyze_module("my_module")
print(result["dependencies"])
```

### Subscribing to Updates

```python
@mycelium.subscribe("nexus.dependency.update")
async def handle_dependency_update(message):
    module = message.data["module"]
    dependencies = message.data["dependencies"]
    print(f"Module {module} dependencies updated: {dependencies}")
```

### Publishing Analysis Requests

```python
await mycelium.publish(
    "nexus.analyze.request",
    {
        "target": "my_module",
        "type": "dependencies",
        "include_metadata": True
    }
)
```

## Configuration

Configuration is managed through `nexus_config.json`:

```json
{
    "analysis": {
        "timeout": 30,
        "max_depth": 10,
        "include_metadata": true
    },
    "cache": {
        "enabled": true,
        "duration": 300
    },
    "mycelium": {
        "topics": {
            "analyze_request": "nexus.analyze.request",
            "analyze_result": "nexus.analyze.result"
        }
    }
}
```

See `config/nexus_config.json` for full configuration options.

## Integration with Other Subsystems

### ETHIK Integration
- Ethical validation of analysis operations
- Compliance checking of dependencies
- Security assessment coordination

### ATLAS Integration
- System-wide relationship mapping
- Visual representation updates
- Cross-module connection tracking

### CRONOS Integration
- State preservation of analysis results
- Backup of relationship data
- Historical analysis tracking

## Error Handling

NEXUS implements comprehensive error handling:
1. Graceful degradation on analysis failures
2. Retry mechanisms for Mycelium communication
3. Cache fallbacks for temporary issues
4. Detailed error reporting via Mycelium alerts
5. Automatic recovery procedures

## Testing

Run tests with pytest:
```bash
cd subsystems/NEXUS
pytest tests/
```

Key test areas:
- Core analysis functionality
- Mycelium message handling
- Cache behavior
- Error scenarios
- Integration points

## Monitoring

NEXUS provides monitoring through:
1. Mycelium alerts
2. Metric collection
3. Performance tracking
4. Health checks
5. Status reporting

## Best Practices

1. **Analysis Requests**
   - Include specific analysis types
   - Set appropriate timeouts
   - Handle results asynchronously

2. **Caching**
   - Monitor cache hit rates
   - Adjust cache duration as needed
   - Implement cache warming

3. **Mycelium Usage**
   - Handle message failures gracefully
   - Implement retry logic
   - Monitor message queues

4. **Performance**
   - Batch related operations
   - Use appropriate cache settings
   - Monitor resource usage

## Troubleshooting

Common issues and solutions:

1. **Slow Analysis**
   - Check cache settings
   - Verify analysis depth
   - Monitor system resources

2. **Message Failures**
   - Check Mycelium connection
   - Verify topic configuration
   - Review retry settings

3. **Cache Issues**
   - Check cache size limits
   - Verify cleanup intervals
   - Monitor memory usage

## Contributing

1. Follow coding standards
2. Add tests for new features
3. Update documentation
4. Submit pull requests
5. Review existing issues

## Version History

### 2.0.0 (2024-03-21)
- Added Mycelium integration
- Enhanced caching system
- Improved error handling
- Added metric collection
- Updated documentation

### 1.0.0 (2024-02-15)
- Initial release
- Basic analysis functionality
- Simple caching
- Core features

## Future Enhancements

1. **Analysis**
   - Advanced code analysis
   - Machine learning integration
   - Pattern recognition
   - Custom analyzers

2. **Integration**
   - Additional subsystem connections
   - External tool integration
   - API enhancements
   - Plugin system

3. **Performance**
   - Distributed analysis
   - Enhanced caching
   - Parallel processing
   - Resource optimization

4. **Visualization**
   - Interactive graphs
   - Real-time updates
   - Custom layouts
   - Export options

5. **Security**
   - Enhanced scanning
   - Vulnerability tracking
   - Compliance checking
   - Access control

## License

Copyright (c) 2024 EGOS Project
Licensed under the MIT License

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
