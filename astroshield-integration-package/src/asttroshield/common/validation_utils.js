/**
 * AstroShield Validation Utilities
 * 
 * This module provides comprehensive validation functions for AstroShield data formats
 * to ensure data integrity before sending to or after receiving from APIs.
 */

const Joi = require('joi');
const { ValidationError } = require('./errors');

// Schema definitions for common data types
const schemas = {
  // Space object schema
  spaceObject: Joi.object({
    objectId: Joi.string().required(),
    name: Joi.string().required(),
    type: Joi.string().valid('SATELLITE', 'DEBRIS', 'ASTEROID', 'UNKNOWN').required(),
    noradId: Joi.string().optional(),
    size: Joi.number().positive().optional(),
    mass: Joi.number().positive().optional(),
    lastUpdated: Joi.date().iso().required()
  }),

  // Observation schema
  observation: Joi.object({
    observationId: Joi.string().required(),
    objectId: Joi.string().required(),
    timestamp: Joi.date().iso().required(),
    position: Joi.object({
      x: Joi.number().required(),
      y: Joi.number().required(),
      z: Joi.number().required(),
      frame: Joi.string().valid('ECI', 'ECEF').required()
    }).required(),
    velocity: Joi.object({
      x: Joi.number().required(),
      y: Joi.number().required(),
      z: Joi.number().required(),
      frame: Joi.string().valid('ECI', 'ECEF').required()
    }).required(),
    source: Joi.string().required(),
    confidence: Joi.number().min(0).max(1).required()
  }),

  // Maneuver schema
  maneuver: Joi.object({
    maneuverId: Joi.string().required(),
    objectId: Joi.string().required(),
    timestamp: Joi.date().iso().required(),
    deltaV: Joi.object({
      x: Joi.number().required(),
      y: Joi.number().required(),
      z: Joi.number().required(),
      frame: Joi.string().valid('ECI', 'ECEF').required()
    }).required(),
    confidence: Joi.number().min(0).max(1).required(),
    detectionSource: Joi.string().required()
  }),

  // Conjunction event schema
  conjunction: Joi.object({
    eventId: Joi.string().required(),
    primaryObjectId: Joi.string().required(),
    secondaryObjectId: Joi.string().required(),
    timeOfClosestApproach: Joi.date().iso().required(),
    missDistance: Joi.number().positive().required(),
    probability: Joi.number().min(0).max(1).required(),
    relativeVelocity: Joi.number().positive().required()
  }),

  // Authentication token schema
  authToken: Joi.object({
    accessToken: Joi.string().required(),
    refreshToken: Joi.string().optional(),
    expiresIn: Joi.number().integer().positive().required(),
    tokenType: Joi.string().valid('Bearer').required()
  })
};

/**
 * Validate data against a predefined schema
 * 
 * @param {string} schemaName - Name of the schema to validate against
 * @param {Object} data - Data to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validated and possibly transformed data
 * @throws {ValidationError} If validation fails
 */
function validate(schemaName, data, options = {}) {
  const schema = schemas[schemaName];
  
  if (!schema) {
    throw new Error(`Schema '${schemaName}' not found`);
  }

  const defaultOptions = {
    abortEarly: false,
    stripUnknown: true,
    presence: 'required'
  };

  const validationOptions = { ...defaultOptions, ...options };
  
  const { error, value } = schema.validate(data, validationOptions);
  
  if (error) {
    const details = error.details.map(detail => detail.message).join('; ');
    throw new ValidationError(`Validation failed for ${schemaName}: ${details}`, error.details);
  }
  
  return value;
}

/**
 * Create a custom validation schema
 * 
 * @param {Object} schemaDefinition - Joi schema definition
 * @returns {Object} Joi schema object
 */
function createSchema(schemaDefinition) {
  return Joi.object(schemaDefinition);
}

/**
 * Validate a custom object against a provided schema
 * 
 * @param {Object} schema - Joi schema to validate against
 * @param {Object} data - Data to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validated and possibly transformed data
 * @throws {ValidationError} If validation fails
 */
function validateCustom(schema, data, options = {}) {
  const defaultOptions = {
    abortEarly: false,
    stripUnknown: true
  };

  const validationOptions = { ...defaultOptions, ...options };
  
  const { error, value } = schema.validate(data, validationOptions);
  
  if (error) {
    const details = error.details.map(detail => detail.message).join('; ');
    throw new ValidationError(`Custom validation failed: ${details}`, error.details);
  }
  
  return value;
}

/**
 * Check if an object is a valid date
 * 
 * @param {*} date - Date to validate
 * @returns {boolean} True if valid date
 */
function isValidDate(date) {
  if (date instanceof Date) {
    return !isNaN(date.getTime());
  }
  
  if (typeof date === 'string') {
    const parsedDate = new Date(date);
    return !isNaN(parsedDate.getTime());
  }
  
  return false;
}

/**
 * Check if a string is a valid UUID
 * 
 * @param {string} uuid - UUID to validate
 * @returns {boolean} True if valid UUID
 */
function isValidUUID(uuid) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

module.exports = {
  validate,
  validateCustom,
  createSchema,
  isValidDate,
  isValidUUID,
  schemas
}; 