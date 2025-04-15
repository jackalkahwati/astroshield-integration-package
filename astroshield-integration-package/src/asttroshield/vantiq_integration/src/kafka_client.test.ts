import { describe, test, expect, afterAll, jest, beforeEach, afterEach } from '@jest/globals';
// We don't need to mock uuid anymore
// Require the module under test
const { standardizeMessage } = require('./kafka_client'); 

// Mock the missing logger module
jest.mock('../../common/logger', () => null, { virtual: true });

// Mock Date.toISOString to get predictable timestamps
const mockISODate = '2024-08-15T10:00:00.000Z';
const originalDate = Date;
global.Date = class extends Date {
  toISOString() {
    return mockISODate;
  }
} as any;

// Restore original Date object after tests
afterAll(() => {
  global.Date = originalDate;
});

// Regex to check for UUID format
const uuidRegex = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

describe('Kafka Client Utilities (kafka_client.js)', () => {

  // No beforeEach/afterEach needed for uuid mock anymore

  describe('standardizeMessage', () => {

    const baseMessage = {
      id: 'msg-001',
      payload: { data: 'test' }
    };

    test('should add standard header fields and generate UUID traceId if missing', () => {
      const standardized = standardizeMessage(baseMessage) as any;
      expect(standardized).toHaveProperty('source', 'ML');
      expect(standardized).toHaveProperty('model_version', 'ml-v1.0');
      expect(standardized.traceId).toBeDefined(); // Check if traceId exists
      expect(standardized.traceId).toMatch(uuidRegex); // Check if it looks like a UUID
      expect(standardized).toHaveProperty('parentMessageIds', undefined);
      expect(standardized).toHaveProperty('prediction_timestamp', mockISODate);
      expect(standardized.payload).toEqual({ data: 'test' });
    });

    test('should use provided options for header fields, including traceId', () => {
      const options = {
        source: 'TestSystem',
        model_version: 'test-v2.1',
        confidence: 0.95,
        traceId: 'trace-id-given', // << Use this specific traceId
        parentMessageIds: ['parent-id-1', 'parent-id-2'],
        prediction_timestamp: '2024-08-14T09:00:00.000Z'
      };
      const standardized = standardizeMessage(baseMessage, options) as any;
      expect(standardized.source).toBe('TestSystem');
      expect(standardized.model_version).toBe('test-v2.1');
      expect(standardized.confidence).toBe(0.95);
      expect(standardized.traceId).toBe('trace-id-given'); // Check the provided traceId is used
      expect(standardized.parentMessageIds).toEqual(['parent-id-1', 'parent-id-2']);
      expect(standardized.prediction_timestamp).toBe('2024-08-14T09:00:00.000Z');
      expect(standardized.payload).toEqual({ data: 'test' });
    });

    test('should preserve existing traceId in the message', () => {
      const messageWithExistingFields = {
        id: 'msg-002',
        source: 'OriginalSource',
        traceId: 'original-trace', // << Keep this specific traceId
        payload: { value: 42 }
      };
      const standardized = standardizeMessage(messageWithExistingFields) as any;
      expect(standardized.id).toBe('msg-002');
      expect(standardized.source).toBe('OriginalSource');
      expect(standardized.model_version).toBe('ml-v1.0');
      expect(standardized.traceId).toBe('original-trace'); // Check the original traceId is preserved
      expect(standardized.payload).toEqual({ value: 42 });
    });

    test('should handle message without existing header fields gracefully, generating traceId', () => {
      const simplePayload = { data: 'simple' };
      const standardized = standardizeMessage(simplePayload) as any;
      expect(standardized).toHaveProperty('source', 'ML');
      expect(standardized).toHaveProperty('model_version', 'ml-v1.0');
      expect(standardized.traceId).toBeDefined(); // Check if traceId exists
      expect(standardized.traceId).toMatch(uuidRegex); // Check if it looks like a UUID
      expect(standardized).toHaveProperty('prediction_timestamp', mockISODate);
      expect(standardized.data).toBe('simple');
    });

    test('should correctly handle confidence score provided in options', () => {
      const options = { confidence: 0.88 };
      const standardized = standardizeMessage(baseMessage, options) as any; 
      expect(standardized.confidence).toBe(0.88);
      expect(standardized.payload).toEqual({ data: 'test' }); 
    });

    test('should correctly handle confidence score existing in message', () => {
      const messageWithConfidence = {
        id: 'msg-003',
        confidence: 0.75,
        payload: { score: 10 }
      };
      const standardized = standardizeMessage(messageWithConfidence) as any; 
      expect(standardized.confidence).toBe(0.75);
      expect(standardized.payload).toEqual({ score: 10 });
    });

    test('should prioritize confidence from options over existing in message', () => {
      const messageWithConfidence = {
        id: 'msg-004',
        confidence: 0.70,
        payload: { score: 20 }
      };
      const options = { confidence: 0.90 };
      const standardized = standardizeMessage(messageWithConfidence, options) as any; 
      expect(standardized.confidence).toBe(0.90);
      expect(standardized.payload).toEqual({ score: 20 });
    });

  });

  // Add tests for publishToKafka and setupConsumer later, likely needing Kafka mocks
}); 