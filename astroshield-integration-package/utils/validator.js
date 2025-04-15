/**
 * Client-side validation utility for AstroShield messages
 * 
 * This utility provides methods to validate messages against JSON schemas
 * before sending them to Kafka or the API.
 */
const Ajv = require('ajv');
const addFormats = require('ajv-formats');
const fs = require('fs');
const path = require('path');

// Initialize validator
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

// Cache for loaded schemas
const schemaCache = {};

/**
 * Load a schema from file
 * @param {string} schemaName - Name of the schema without extension (e.g., 'ss0.sensor.heartbeat')
 * @returns {Object} Loaded JSON schema
 */
function loadSchema(schemaName) {
  if (schemaCache[schemaName]) {
    return schemaCache[schemaName];
  }
  
  try {
    const schemaPath = path.resolve(__dirname, '../schemas', `${schemaName}.schema.json`);
    const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
    schemaCache[schemaName] = schema;
    return schema;
  } catch (error) {
    throw new Error(`Failed to load schema ${schemaName}: ${error.message}`);
  }
}

/**
 * Validate a message against its schema
 * 
 * @param {Object} message - Message to validate
 * @param {string} schemaName - Schema name without extension
 * @returns {Object} Validation result with valid flag and any errors
 */
function validateMessage(message, schemaName) {
  try {
    const schema = loadSchema(schemaName);
    const validate = ajv.compile(schema);
    const valid = validate(message);
    
    return {
      valid,
      errors: validate.errors || null
    };
  } catch (error) {
    return {
      valid: false,
      errors: [{ message: error.message }]
    };
  }
}

/**
 * Format validation errors into a human-readable string
 * 
 * @param {Array} errors - Validation errors from Ajv
 * @returns {string} Formatted error message
 */
function formatErrors(errors) {
  if (!errors || errors.length === 0) {
    return '';
  }
  
  return errors.map(error => {
    const path = error.instancePath || '';
    const property = error.params.missingProperty 
      ? `missing property '${error.params.missingProperty}'` 
      : (error.params.additionalProperty 
        ? `additional property '${error.params.additionalProperty}'`
        : '');
    
    return `${path} ${error.message} ${property}`.trim();
  }).join('\n');
}

/**
 * Validate a message for a specific topic and format errors if any
 * 
 * @param {Object} message - Message to validate
 * @param {string} topic - Kafka topic (used to determine schema)
 * @returns {Object} Result with isValid flag and formatted error message
 */
function validateMessageForTopic(message, topic) {
  // Map topic to schema name
  const topicToSchema = {
    'ss0.sensor.heartbeat': 'ss0.sensor.heartbeat',
    'ss2.data.state-vector': 'ss2.data.state-vector',
    'ss4.ccdm.detection': 'ss4.ccdm.detection',
    'ss5.launch.prediction': 'ss5.launch.prediction',
    'ss5.telemetry.data': 'ss5.telemetry.data',
    'ss5.conjunction.events': 'ss5.conjunction.events',
    'ss5.cyber.threats': 'ss5.cyber.threats',
    'maneuvers.detected': 'maneuvers.detected'
  };
  
  const schemaName = topicToSchema[topic];
  if (!schemaName) {
    return {
      isValid: false,
      error: `Unknown topic: ${topic}`
    };
  }
  
  const result = validateMessage(message, schemaName);
  
  return {
    isValid: result.valid,
    error: result.valid ? null : formatErrors(result.errors)
  };
}

module.exports = {
  validateMessage,
  validateMessageForTopic,
  formatErrors,
  loadSchema
}; 