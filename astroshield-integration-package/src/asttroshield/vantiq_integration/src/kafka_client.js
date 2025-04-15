/**
 * Kafka client module for AstroShield-Vantiq integration
 * Provides reusable functions for Kafka connectivity
 */
const { Kafka } = require('kafkajs');
const logger = require('../../common/logger') || console;

/**
 * Connect to Kafka and create a client
 * @param {Object} config - Configuration object
 * @param {string} config.clientId - Client ID for Kafka connection
 * @param {Array<string>|string} config.brokers - List of Kafka brokers or comma-separated string
 * @param {Object} [config.ssl] - SSL configuration
 * @param {Object} [config.sasl] - SASL authentication configuration
 * @returns {Object} Kafka client object
 */
async function connectToKafka(config) {
  if (!config.clientId) {
    throw new Error('clientId is required');
  }
  
  // Parse brokers if provided as string
  const brokers = Array.isArray(config.brokers) 
    ? config.brokers 
    : (typeof config.brokers === 'string' ? config.brokers.split(',') : null);
  
  if (!brokers || brokers.length === 0) {
    throw new Error('At least one broker is required');
  }
  
  try {
    const kafka = new Kafka({
      clientId: config.clientId,
      brokers: brokers,
      ssl: config.ssl || false,
      sasl: config.sasl || undefined,
      retry: {
        initialRetryTime: 100,
        retries: 8
      }
    });
    
    logger.info('Created Kafka client', { clientId: config.clientId });
    
    return { kafka };
  } catch (error) {
    logger.error('Failed to create Kafka client', { error: error.message });
    throw error;
  }
}

/**
 * Create and connect a Kafka producer
 * @param {Object} kafka - Kafka client 
 * @returns {Object} Kafka producer
 */
async function createProducer(kafka) {
  try {
    const producer = kafka.producer();
    await producer.connect();
    logger.info('Connected Kafka producer');
    return producer;
  } catch (error) {
    logger.error('Failed to connect Kafka producer', { error: error.message });
    throw error;
  }
}

/**
 * Standardize message before publishing: add provenance, confidence, and traceability fields.
 * @param {Object} message - Original message
 * @param {Object} options - Additional provenance/traceability info
 * @returns {Object} Standardized message
 */
function standardizeMessage(message, options = {}) {
  return {
    ...message,
    source: options.source || message.source || 'ML',
    model_version: options.model_version || message.model_version || 'ml-v1.0',
    confidence: options.confidence || message.confidence,
    traceId: options.traceId || message.traceId || require('uuid').v4(),
    parentMessageIds: options.parentMessageIds || message.parentMessageIds,
    prediction_timestamp: options.prediction_timestamp || new Date().toISOString(),
  };
}

/**
 * Publish a message to Kafka
 * @param {Object} producer - Kafka producer
 * @param {string} topic - Kafka topic to publish to
 * @param {Object} message - Message to publish
 * @param {string} [key] - Optional message key (defaults to message.id)
 * @param {Object} [options] - Additional provenance/traceability info
 * @returns {Object} Result of the send operation
 */
async function publishToKafka(producer, topic, message, key, options = {}) {
  if (!producer) {
    throw new Error('Producer is required');
  }
  
  if (!topic) {
    throw new Error('Topic is required');
  }
  
  if (!message) {
    throw new Error('Message is required');
  }
  
  try {
    // Use message.id as key if not specified 
    const messageKey = key || message.id;
    
    const standardizedMessage = standardizeMessage(message, options);
    
    const result = await producer.send({
      topic,
      messages: [
        {
          value: JSON.stringify(standardizedMessage),
          key: messageKey
        }
      ]
    });
    
    logger.debug('Published message to Kafka', { 
      topic, 
      messageId: standardizedMessage.id || 'unknown'
    });
    
    return result;
  } catch (error) {
    logger.error('Failed to publish message to Kafka', { 
      topic, 
      messageId: message.id || 'unknown',
      error: error.message 
    });
    throw error;
  }
}

/**
 * Publish multiple messages to Kafka in a batch
 * @param {Object} producer - Kafka producer
 * @param {string} topic - Kafka topic to publish to
 * @param {Array<Object>} messages - Array of messages to publish
 * @param {Object} [options] - Additional provenance/traceability info
 * @returns {Object} Result of the send operation
 */
async function publishBatchToKafka(producer, topic, messages, options = {}) {
  if (!producer) {
    throw new Error('Producer is required');
  }
  
  if (!topic) {
    throw new Error('Topic is required');
  }
  
  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    throw new Error('Non-empty array of messages is required');
  }
  
  try {
    const kafkaMessages = messages.map(message => ({
      value: JSON.stringify(standardizeMessage(message, options)),
      key: message.id || undefined
    }));
    
    const result = await producer.send({
      topic,
      messages: kafkaMessages
    });
    
    logger.debug('Published batch of messages to Kafka', { 
      topic, 
      messageCount: messages.length
    });
    
    return result;
  } catch (error) {
    logger.error('Failed to publish batch of messages to Kafka', {
      topic,
      messageCount: messages.length,
      error: error.message
    });
    throw error;
  }
}

/**
 * Set up a Kafka consumer with message handler
 * @param {Object} config - Configuration object
 * @param {string} topic - Kafka topic to consume from
 * @param {Function} messageHandler - Handler function for messages
 * @returns {Object} Kafka consumer
 */
async function setupConsumer(config, topic, messageHandler) {
  if (!config) {
    throw new Error('Config is required');
  }
  
  if (!topic) {
    throw new Error('Topic is required');
  }
  
  if (!messageHandler || typeof messageHandler !== 'function') {
    throw new Error('Message handler function is required');
  }
  
  try {
    const { kafka } = await connectToKafka(config);
    const consumer = kafka.consumer({ groupId: config.groupId });
    
    await consumer.connect();
    logger.info('Connected Kafka consumer', { groupId: config.groupId });
    
    await consumer.subscribe({ topic, fromBeginning: false });
    logger.info('Subscribed to topic', { topic });
    
    await consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        try {
          const messageValue = message.value.toString();
          const parsedMessage = JSON.parse(messageValue);
          await messageHandler(parsedMessage);
        } catch (error) {
          logger.error('Error processing message', { 
            topic, 
            partition, 
            error: error.message 
          });
        }
      }
    });
    
    logger.info('Kafka consumer is running', { topic, groupId: config.groupId });
    
    return consumer;
  } catch (error) {
    logger.error('Failed to set up Kafka consumer', { 
      topic, 
      groupId: config.groupId,
      error: error.message 
    });
    throw error;
  }
}

/**
 * Disconnect a Kafka consumer
 * @param {Object} consumer - Kafka consumer
 */
async function disconnectConsumer(consumer) {
  if (consumer) {
    try {
      await consumer.disconnect();
      logger.info('Disconnected Kafka consumer');
    } catch (error) {
      logger.error('Error disconnecting Kafka consumer', { error: error.message });
      throw error;
    }
  }
}

/**
 * Disconnect a Kafka producer
 * @param {Object} producer - Kafka producer
 */
async function disconnectProducer(producer) {
  if (producer) {
    try {
      await producer.disconnect();
      logger.info('Disconnected Kafka producer');
    } catch (error) {
      logger.error('Error disconnecting Kafka producer', { error: error.message });
      throw error;
    }
  }
}

module.exports = {
  connectToKafka,
  createProducer,
  standardizeMessage,
  publishToKafka,
  publishBatchToKafka, 
  setupConsumer,
  disconnectConsumer,
  disconnectProducer
};