import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { validateMessage, validateMessageForTopic, loadSchema } from './validator';
import path from 'path';
import fs from 'fs';

// Define the type for the mocked fs module
type MockFsModule = {
  readFileSync: jest.Mock;
};

// Mock fs module
jest.mock('fs', () => ({
  readFileSync: jest.fn(),
}));

// Cast fs to our mocked type for easier use in tests
const mockedFs = fs as unknown as MockFsModule;

// Mock schema directory relative to __dirname
const mockSchemaDir = path.resolve(__dirname, '../schemas');

// Sample valid message for ss2.data.state-vector
const validStateVectorMessage = {
  header: {
    messageId: 'uuid-1234-test',
    messageTime: '2024-01-01T12:00:00Z',
    messageVersion: '1.0',
    subsystem: 'ss2',
    dataProvider: 'TestProvider',
    dataType: 'ss2.data.state-vector',
    dataVersion: '0.1.0'
  },
  payload: {
    noradId: '12345',
    objectName: 'TestSat',
    epochTime: '2024-01-01T12:00:00Z',
    referenceFrame: 'TEME',
    positionVector: { x: 7000, y: 0, z: 0, unit: 'km' },
    velocityVector: { x: 0, y: 7.5, z: 0, unit: 'km/s' },
    covarianceMatrix: [
      [1, 0, 0, 0, 0, 0],
      [0, 1, 0, 0, 0, 0],
      [0, 0, 1, 0, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 0, 0, 1, 0],
      [0, 0, 0, 0, 0, 1]
    ]
  }
};

// Sample invalid message (missing required header field)
const invalidMessageMissingHeader = {
  header: {
    // messageId is missing
    messageTime: '2024-01-01T12:00:00Z',
    messageVersion: '1.0',
    subsystem: 'ss2',
    dataProvider: 'TestProvider',
    dataType: 'ss2.data.state-vector',
    dataVersion: '0.1.0'
  },
  payload: { ...validStateVectorMessage.payload }
};

// Sample invalid message (incorrect payload type)
const invalidMessageWrongPayload = {
  header: { ...validStateVectorMessage.header },
  payload: {
    noradId: '12345',
    objectName: 'TestSat',
    epochTime: '2024-01-01T12:00:00Z',
    referenceFrame: 'TEME',
    positionVector: { x: 'not-a-number', y: 0, z: 0, unit: 'km' }, // Incorrect type
    velocityVector: { x: 0, y: 7.5, z: 0, unit: 'km/s' },
    covarianceMatrix: [
      [1, 0, 0, 0, 0, 0],
      [0, 1, 0, 0, 0, 0],
      [0, 0, 1, 0, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [0, 0, 0, 0, 1, 0],
      [0, 0, 0, 0, 0, 1]
    ]
  }
};

// Sample schema content (minimal for testing)
const sampleSchemaContent = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  title: "State Vector Message",
  type: "object",
  required: ["header", "payload"],
  properties: {
    header: {
      type: "object",
      required: ["messageId", "messageTime", "messageVersion", "subsystem", "dataProvider", "dataType", "dataVersion"],
      properties: {
        messageId: { type: "string" }
        // Add other header properties as needed for more specific tests
      }
    },
    payload: {
      type: "object",
      required: ["noradId", "epochTime", "positionVector", "velocityVector"],
      properties: {
        positionVector: {
          type: "object",
          required: ["x", "y", "z"],
          properties: {
            x: { type: "number" },
            y: { type: "number" },
            z: { type: "number" }
          }
        }
        // Add other payload properties
      }
    }
  }
};


describe('AstroShield Validator Utility (validator.js)', () => {

  beforeEach(() => {
    // Reset mocks before each test
    mockedFs.readFileSync.mockClear();
    // Mock reading the schema file
    // Use 'any' for arguments to bypass complex type checking for the mock
    mockedFs.readFileSync.mockImplementation((...args: any[]) => {
      const filePath = args[0]; // Assume first argument is the path
      // Ensure filePath is treated as string for path operations
      const pathString = filePath.toString(); 
      const schemaName = path.basename(pathString, '.schema.json');
      if (schemaName === 'ss2.data.state-vector') {
        return JSON.stringify(sampleSchemaContent);
      }
      throw new Error(`ENOENT: no such file or directory, open '${pathString}'`);
    });
  });

  test('loadSchema should load and cache schema', () => {
    const schemaName = 'ss2.data.state-vector';
    const schema = loadSchema(schemaName) as any;
    expect(schema).toBeDefined();
    expect(schema.title).toBe('State Vector Message');
    expect(mockedFs.readFileSync).toHaveBeenCalledTimes(1);
    expect(mockedFs.readFileSync).toHaveBeenCalledWith(path.join(mockSchemaDir, `${schemaName}.schema.json`), 'utf8');

    // Load again, should use cache
    const cachedSchema = loadSchema(schemaName);
    expect(cachedSchema).toBe(schema);
    expect(mockedFs.readFileSync).toHaveBeenCalledTimes(1);
  });

  test('loadSchema should throw error for non-existent schema', () => {
    const schemaName = 'non-existent-schema';
    expect(() => loadSchema(schemaName)).toThrow(`Failed to load schema ${schemaName}`);
    expect(mockedFs.readFileSync).toHaveBeenCalledWith(path.join(mockSchemaDir, `${schemaName}.schema.json`), 'utf8');
  });

  test('validateMessage should return valid for correct message', () => {
    const result = validateMessage(validStateVectorMessage, 'ss2.data.state-vector') as any;
    expect(result.valid).toBe(true);
    expect(result.errors).toBeNull();
  });

  test('validateMessage should return invalid for message missing required header field', () => {
    const result = validateMessage(invalidMessageMissingHeader, 'ss2.data.state-vector') as any;
    expect(result.valid).toBe(false);
    expect(result.errors).not.toBeNull();
    expect(JSON.stringify(result.errors)).toContain('messageId');
  });

  test('validateMessage should return invalid for message with incorrect payload type', () => {
    const result = validateMessage(invalidMessageWrongPayload, 'ss2.data.state-vector') as any;
    expect(result.valid).toBe(false);
    expect(result.errors).not.toBeNull();
    expect(JSON.stringify(result.errors)).toContain('/payload/positionVector/x');
    expect(JSON.stringify(result.errors)).toContain('number');
  });

  test('validateMessageForTopic should return valid for correct message and known topic', () => {
    const result = validateMessageForTopic(validStateVectorMessage, 'ss2.data.state-vector') as any;
    expect(result.isValid).toBe(true);
    expect(result.error).toBeNull();
  });

  test('validateMessageForTopic should return invalid for incorrect message and known topic', () => {
    const result = validateMessageForTopic(invalidMessageMissingHeader, 'ss2.data.state-vector') as any;
    expect(result.isValid).toBe(false);
    expect(result.error).not.toBeNull();
    expect(result.error).toContain('messageId');
  });

  test('validateMessageForTopic should return invalid for unknown topic', () => {
    const result = validateMessageForTopic(validStateVectorMessage, 'unknown.topic') as any;
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Unknown topic: unknown.topic');
  });

}); 