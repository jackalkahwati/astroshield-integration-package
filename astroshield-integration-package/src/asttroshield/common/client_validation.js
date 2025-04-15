/**
 * AstroShield Client-Side Validation Module
 * 
 * This module provides utilities for validating message structures
 * before transmitting them to AstroShield systems.
 */

const Ajv = require('ajv');
const ajv = new Ajv({ allErrors: true, coerceTypes: true });

// Load schemas for different message types
const maneuverSchema = require('../schemas/maneuver.schema.json');
const observationSchema = require('../schemas/observation.schema.json');
const objectDetailsSchema = require('../schemas/object_details.schema.json');
const alertSchema = require('../schemas/alert.schema.json');

// Add schemas to validator
ajv.addSchema(maneuverSchema, 'maneuver');
ajv.addSchema(observationSchema, 'observation');
ajv.addSchema(objectDetailsSchema, 'objectDetails');
ajv.addSchema(alertSchema, 'alert');

/**
 * Validates a message against its corresponding schema
 * 
 * @param {Object} message - The message to validate
 * @param {String} messageType - The type of message ('maneuver', 'observation', 'objectDetails', 'alert')
 * @returns {Object} Object with isValid flag and any validation errors
 */
function validateMessage(message, messageType) {
  if (!messageType || !ajv.getSchema(messageType)) {
    return {
      isValid: false,
      errors: [{ message: `Unknown message type: ${messageType}` }]
    };
  }

  const validate = ajv.getSchema(messageType);
  const isValid = validate(message);

  return {
    isValid,
    errors: isValid ? null : validate.errors
  };
}

/**
 * Formats validation errors into a more readable structure
 * 
 * @param {Array} errors - Array of AJV validation errors
 * @returns {Array} Formatted error messages
 */
function formatValidationErrors(errors) {
  if (!errors || !Array.isArray(errors)) {
    return [];
  }
  
  return errors.map(error => {
    const path = error.instancePath || '';
    const property = error.params.missingProperty || '';
    
    switch (error.keyword) {
      case 'required':
        return `Missing required property: ${property}`;
      case 'type':
        return `Invalid type at ${path}: expected ${error.params.type}`;
      case 'format':
        return `Invalid format at ${path}: expected ${error.params.format}`;
      case 'enum':
        return `Invalid value at ${path}: must be one of [${error.params.allowedValues}]`;
      case 'maximum':
      case 'minimum':
        return `Value ${error.params.comparison} ${error.params.limit} at ${path}`;
      default:
        return `Validation error at ${path}: ${error.message}`;
    }
  });
}

/**
 * Validates a batch of messages of the same type
 * 
 * @param {Array} messages - Array of messages to validate
 * @param {String} messageType - The type of messages
 * @returns {Object} Object with overall validity and detailed results for each message
 */
function validateBatch(messages, messageType) {
  if (!Array.isArray(messages)) {
    return {
      isValid: false,
      message: 'Input is not an array of messages',
      results: []
    };
  }

  const results = messages.map((message, index) => {
    const result = validateMessage(message, messageType);
    return {
      index,
      isValid: result.isValid,
      errors: result.isValid ? null : formatValidationErrors(result.errors)
    };
  });

  const isValid = results.every(result => result.isValid);

  return {
    isValid,
    message: isValid 
      ? `All ${messages.length} messages are valid`
      : `${results.filter(r => !r.isValid).length} of ${messages.length} messages have validation errors`,
    results
  };
}

/**
 * Validates a message and throws an error if invalid
 * 
 * @param {Object} message - The message to validate
 * @param {String} messageType - The type of message
 * @throws {Error} If validation fails
 */
function validateOrThrow(message, messageType) {
  const result = validateMessage(message, messageType);
  
  if (!result.isValid) {
    const errorMessages = formatValidationErrors(result.errors);
    throw new Error(`Invalid ${messageType} message: ${errorMessages.join('; ')}`);
  }
  
  return true;
}

module.exports = {
  validateMessage,
  validateBatch,
  validateOrThrow,
  formatValidationErrors
}; 