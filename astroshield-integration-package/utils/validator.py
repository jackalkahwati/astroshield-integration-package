"""
Client-side validation utility for AstroShield messages

This utility provides methods to validate messages against JSON schemas
before sending them to Kafka or the API.
"""
import os
import json
import jsonschema
from jsonschema import ValidationError
from typing import Dict, Any, Tuple, List, Optional


class SchemaValidator:
    """
    Validator for AstroShield messages using JSON Schema validation
    """
    
    def __init__(self, schema_dir: Optional[str] = None):
        """
        Initialize the validator with schema directory
        
        Args:
            schema_dir: Directory containing JSON schema files. If None, uses ../schemas relative to this file.
        """
        if schema_dir is None:
            schema_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schemas')
        
        self.schema_dir = schema_dir
        self.schema_cache = {}
    
    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load a schema from file
        
        Args:
            schema_name: Name of the schema without extension (e.g., 'ss0.sensor.heartbeat')
            
        Returns:
            Loaded JSON schema
            
        Raises:
            FileNotFoundError: If schema file does not exist
            json.JSONDecodeError: If schema is not valid JSON
        """
        if schema_name in self.schema_cache:
            return self.schema_cache[schema_name]
        
        schema_path = os.path.join(self.schema_dir, f"{schema_name}.schema.json")
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        self.schema_cache[schema_name] = schema
        return schema
    
    def validate_message(self, message: Dict[str, Any], schema_name: str) -> Tuple[bool, Optional[List[str]]]:
        """
        Validate a message against its schema
        
        Args:
            message: Message to validate
            schema_name: Schema name without extension
            
        Returns:
            Tuple of (is_valid, errors) where errors is a list of error messages or None if valid
        """
        try:
            schema = self.load_schema(schema_name)
            jsonschema.validate(instance=message, schema=schema)
            return True, None
        except FileNotFoundError as e:
            return False, [f"Schema not found: {e}"]
        except json.JSONDecodeError as e:
            return False, [f"Invalid schema JSON: {e}"]
        except ValidationError as e:
            return False, [self._format_validation_error(e)]
    
    def validate_message_for_topic(self, message: Dict[str, Any], topic: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a message for a specific topic
        
        Args:
            message: Message to validate
            topic: Kafka topic (used to determine schema)
            
        Returns:
            Tuple of (is_valid, error_message) where error_message is None if valid
        """
        # Map topic to schema name
        topic_to_schema = {
            'ss0.sensor.heartbeat': 'ss0.sensor.heartbeat',
            'ss2.data.state-vector': 'ss2.data.state-vector',
            'ss4.ccdm.detection': 'ss4.ccdm.detection',
            'ss5.launch.prediction': 'ss5.launch.prediction',
            'ss5.telemetry.data': 'ss5.telemetry.data',
            'ss5.conjunction.events': 'ss5.conjunction.events',
            'ss5.cyber.threats': 'ss5.cyber.threats',
            'maneuvers.detected': 'maneuvers.detected'
        }
        
        schema_name = topic_to_schema.get(topic)
        if not schema_name:
            return False, f"Unknown topic: {topic}"
        
        is_valid, errors = self.validate_message(message, schema_name)
        
        if not is_valid and errors:
            return False, "\n".join(errors)
        
        return is_valid, None
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """
        Format a validation error into a human-readable string
        
        Args:
            error: ValidationError from jsonschema
            
        Returns:
            Formatted error message
        """
        path = "/".join(str(p) for p in error.path) if error.path else ""
        path_prefix = f"{path}: " if path else ""
        
        return f"{path_prefix}{error.message}"


# Create a default validator instance for easy import
default_validator = SchemaValidator()

# Module-level functions that use the default validator
def validate_message(message: Dict[str, Any], schema_name: str) -> Tuple[bool, Optional[List[str]]]:
    """
    Validate a message against its schema using the default validator
    
    Args:
        message: Message to validate
        schema_name: Schema name without extension
        
    Returns:
        Tuple of (is_valid, errors) where errors is a list of error messages or None if valid
    """
    return default_validator.validate_message(message, schema_name)

def validate_message_for_topic(message: Dict[str, Any], topic: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a message for a specific topic using the default validator
    
    Args:
        message: Message to validate
        topic: Kafka topic (used to determine schema)
        
    Returns:
        Tuple of (is_valid, error_message) where error_message is None if valid
    """
    return default_validator.validate_message_for_topic(message, topic) 