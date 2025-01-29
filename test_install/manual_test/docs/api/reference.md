# Head AI API Reference

## Core Modules

### Assistant Module
```python
from src.assistant import Assistant

# Initialize assistant
assistant = Assistant(config_path='config.json')
```

#### Methods
- `start()`: Start the assistant
- `stop()`: Stop the assistant
- `process_voice(audio_data)`: Process voice input
- `process_text(text)`: Process text input

### Voice Recognition
```python
from src.voice import VoiceRecognizer

# Initialize voice recognizer
recognizer = VoiceRecognizer()
```

#### Methods
- `start_listening()`: Start listening for voice input
- `stop_listening()`: Stop listening
- `calibrate()`: Calibrate microphone

### UI Module
```python
from src.ui import MainWindow

# Create main window
window = MainWindow()
```

#### Methods
- `show()`: Display the window
- `hide()`: Hide the window
- `update_display(text)`: Update display text

## Plugin System

### Creating Plugins
```python
from src.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Custom Plugin"
    
    def process(self, input_data):
        # Process input
        return result
```

### Plugin Interface
Required methods:
- `__init__()`: Initialize plugin
- `process()`: Process input data
- `cleanup()`: Clean up resources

## Event System

### Event Types
- `VOICE_INPUT`: Voice input received
- `TEXT_INPUT`: Text input received
- `RESPONSE_READY`: Response ready
- `ERROR`: Error occurred

### Event Handling
```python
def handle_event(event):
    if event.type == 'VOICE_INPUT':
        # Handle voice input
        pass
```

## Configuration

### Config File Format
```json
{
    "voice": {
        "activation_phrase": "Hey Assistant",
        "sensitivity": 0.5
    },
    "ui": {
        "theme": "dark",
        "font_size": 12
    }
}
```

### Loading Config
```python
from src.config import load_config

config = load_config('config.json')
```

## Error Handling

### Custom Exceptions
```python
class AssistantError(Exception):
    pass

class VoiceError(AssistantError):
    pass
```

### Error Handling Example
```python
try:
    assistant.process_voice(audio_data)
except VoiceError as e:
    logger.error(f"Voice processing error: {e}")
```

## Logging

### Setup Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Usage
```python
logger = logging.getLogger(__name__)
logger.info("Assistant started")
logger.error("Error occurred", exc_info=True)
```

## Examples

### Basic Usage
```python
from src.assistant import Assistant
from src.config import load_config

# Load configuration
config = load_config('config.json')

# Initialize assistant
assistant = Assistant(config)

# Start assistant
assistant.start()

# Process input
response = assistant.process_text("Hello!")

# Clean up
assistant.stop()
```

### Plugin Example
```python
from src.plugins import BasePlugin

class WeatherPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "Weather Plugin"
    
    def process(self, location):
        # Get weather data
        return weather_data
```

## Best Practices

### Performance
- Use async/await for I/O operations
- Implement proper cleanup
- Cache frequently used data

### Security
- Validate all inputs
- Use secure connections
- Handle sensitive data properly

### Error Handling
- Implement proper exception handling
- Log errors appropriately
- Provide user-friendly error messages
