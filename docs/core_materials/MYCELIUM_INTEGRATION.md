# Mycelium Integration Guide

## Overview

Mycelium is the central nervous system of the EGOS project, providing real-time communication and coordination between all subsystems. This document details the integration patterns, message formats, and best practices for using Mycelium across the EGOS ecosystem.

**Version**: 2.0.0
**Last Updated**: 2024-03-21
**Status**: Production Ready

## Core Concepts

### Message Types

1. **Commands**
   - Request specific actions
   - Require acknowledgment
   - May trigger state changes

2. **Events**
   - Notify of state changes
   - No acknowledgment required
   - Historical record

3. **Status Updates**
   - Report current state
   - Regular intervals
   - Health monitoring

4. **Alerts**
   - Signal important conditions
   - May require attention
   - Priority levels

### Standard Message Format

```json
{
    "id": "msg-uuid",
    "timestamp": "2024-03-21T10:30:00Z",
    "type": "command|event|status|alert",
    "source": "subsystem-name",
    "data": {
        "key": "value"
    },
    "metadata": {
        "version": "1.0",
        "priority": "high|medium|low"
    }
}
```

## Subsystem Integration

### CRONOS

#### Topics
- `cronos.backup.request`
- `cronos.backup.status`
- `cronos.restore.request`
- `cronos.restore.status`
- `cronos.alert`

#### Example Messages

```json
// Backup Request
{
    "id": "backup-123",
    "type": "command",
    "source": "cronos",
    "data": {
        "target": "project_files",
        "strategy": "incremental"
    }
}

// Backup Status
{
    "id": "status-456",
    "type": "status",
    "source": "cronos",
    "data": {
        "backup_id": "backup-123",
        "status": "completed",
        "files_processed": 100
    }
}
```

### ETHIK

#### Topics
- `ethik.validate.request`
- `ethik.validate.result`
- `ethik.policy.update`
- `ethik.alert`

#### Example Messages

```json
// Validation Request
{
    "id": "validate-123",
    "type": "command",
    "source": "ethik",
    "data": {
        "content": "code_or_text",
        "policy": "security"
    }
}

// Validation Result
{
    "id": "result-456",
    "type": "event",
    "source": "ethik",
    "data": {
        "request_id": "validate-123",
        "valid": true,
        "issues": []
    }
}
```

### ATLAS

#### Topics
- `atlas.map.request`
- `atlas.map.update`
- `atlas.relationship.update`
- `atlas.alert`

#### Example Messages

```json
// Map Request
{
    "id": "map-123",
    "type": "command",
    "source": "atlas",
    "data": {
        "target": "system",
        "depth": 3
    }
}

// Relationship Update
{
    "id": "rel-456",
    "type": "event",
    "source": "atlas",
    "data": {
        "source": "module_a",
        "target": "module_b",
        "type": "depends_on"
    }
}
```

### NEXUS

#### Topics
- `nexus.analyze.request`
- `nexus.analyze.result`
- `nexus.dependency.update`
- `nexus.module.update`
- `nexus.alert`

#### Example Messages

```json
// Analysis Request
{
    "id": "analyze-123",
    "type": "command",
    "source": "nexus",
    "data": {
        "target": "module_name",
        "type": "dependencies"
    }
}

// Analysis Result
{
    "id": "result-456",
    "type": "event",
    "source": "nexus",
    "data": {
        "request_id": "analyze-123",
        "dependencies": ["dep1", "dep2"]
    }
}
```

## Best Practices

### 1. Message Design
- Use clear, descriptive topic names
- Include all necessary context
- Keep payloads concise
- Use standard formats
- Version message schemas

### 2. Error Handling
- Implement retry logic
- Use exponential backoff
- Handle timeouts gracefully
- Log failures appropriately
- Provide clear error messages

### 3. Performance
- Batch related messages
- Use appropriate QoS levels
- Monitor queue sizes
- Implement rate limiting
- Clean up resources

### 4. Security
- Validate message content
- Implement access control
- Use secure connections
- Monitor for anomalies
- Handle sensitive data appropriately

### 5. Monitoring
- Track message rates
- Monitor queue depths
- Alert on failures
- Log important events
- Measure latency

## Implementation Examples

### Python Client

```python
from mycelium import MyceliumClient

# Initialize client
client = MyceliumClient()

# Subscribe to topic
@client.subscribe("subsystem.event")
async def handle_event(message):
    print(f"Received: {message.data}")

# Publish message
await client.publish(
    "subsystem.command",
    {
        "action": "process",
        "data": {"key": "value"}
    }
)
```

### Error Handling

```python
async def publish_with_retry(client, topic, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            await client.publish(topic, data)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
    return False
```

## Testing

### Unit Tests

```python
def test_message_handling():
    client = MockMyceliumClient()
    handler = MessageHandler(client)

    result = handler.process_message({
        "type": "command",
        "data": {"action": "test"}
    })

    assert result.success == True
```

### Integration Tests

```python
async def test_subsystem_communication():
    client1 = MyceliumClient()
    client2 = MyceliumClient()

    await client1.publish("test.topic", {"msg": "hello"})
    response = await client2.receive("test.topic")

    assert response.data["msg"] == "hello"
```

## Monitoring

### Metrics to Track

1. Message Rates
   - Published/second
   - Consumed/second
   - By topic
   - By type

2. Latency
   - End-to-end
   - Processing time
   - Queue time

3. Errors
   - Failed publishes
   - Failed deliveries
   - Retry counts

4. Resources
   - Queue depth
   - Memory usage
   - Connection count

### Alerting

```python
async def monitor_queue_depth(client, threshold=1000):
    depth = await client.get_queue_depth()
    if depth > threshold:
        await alert_team(f"Queue depth {depth} exceeds threshold")
```

## Future Enhancements

1. **Message Schemas**
   - Formal schema definitions
   - Automatic validation
   - Version management
   - Documentation generation

2. **Advanced Routing**
   - Content-based routing
   - Priority queues
   - Dead letter queues
   - Message filtering

3. **Security**
   - Enhanced authentication
   - Message encryption
   - Access control lists
   - Audit logging

4. **Performance**
   - Message compression
   - Batch processing
   - Connection pooling
   - Load balancing

5. **Monitoring**
   - Enhanced metrics
   - Visual dashboards
   - Predictive alerts
   - Performance analysis

## Troubleshooting

### Common Issues

1. **Connection Problems**
   - Check network connectivity
   - Verify credentials
   - Review firewall rules
   - Check server status

2. **Message Delivery**
   - Verify topic names
   - Check queue limits
   - Monitor disk space
   - Review message format

3. **Performance**
   - Analyze message rates
   - Check resource usage
   - Review batch settings
   - Monitor latency

## License

Copyright (c) 2024 EGOS Project
Licensed under the MIT License

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
