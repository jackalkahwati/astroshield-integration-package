#!/usr/bin/env node

/**
 * AstroShield Kafka Producer Example
 * 
 * This script demonstrates how to produce messages to AstroShield Kafka topics
 * using the node-rdkafka library, which provides bindings for the librdkafka C library.
 * 
 * Prerequisites:
 * - Node.js 14+
 * - npm install node-rdkafka uuid
 */

const Kafka = require('node-rdkafka');
const { v4: uuidv4 } = require('uuid');

// Kafka configuration
const kafkaConfig = {
  'metadata.broker.list': 'kafka.astroshield.com:9092',
  'security.protocol': 'sasl_ssl',
  'sasl.mechanisms': 'PLAIN',
  'sasl.username': 'astroshield-client',
  'sasl.password': 'your-password-here',
  'dr_cb': true  // Delivery report callback
};

// Topic to produce to
const TOPIC = 'ss5.telemetry.data';

// Create a producer instance
const producer = new Kafka.Producer(kafkaConfig);

// Connect to the Kafka broker
producer.connect();

// Wait for the ready event before proceeding
producer.on('ready', () => {
  console.log('Producer ready');
  
  // Generate and send sample messages
  sendSampleMessages();
});

// Handle errors
producer.on('event.error', (err) => {
  console.error('Error from producer:', err);
});

// Handle delivery reports
producer.on('delivery-report', (err, report) => {
  if (err) {
    console.error('Delivery failed:', err);
  } else {
    console.log('Message delivered to topic:', report.topic, 'partition:', report.partition, 'offset:', report.offset);
  }
});

/**
 * Send sample telemetry messages to the Kafka topic
 */
function sendSampleMessages() {
  // Send 5 sample messages
  for (let i = 0; i < 5; i++) {
    const message = createSampleTelemetryMessage();
    
    try {
      // Convert message to Buffer
      const buffer = Buffer.from(JSON.stringify(message));
      
      // Send message to Kafka
      producer.produce(
        TOPIC,                // Topic
        null,                 // Partition (null = librdkafka determines the partition)
        buffer,               // Message content
        message.header.messageId,  // Optional key
        Date.now()            // Timestamp
      );
      
      console.log(`Produced message: ${message.header.messageId}`);
    } catch (err) {
      console.error('Error producing message:', err);
    }
  }
  
  // Wait for any outstanding messages to be delivered
  producer.flush(10000, () => {
    console.log('All messages flushed');
    producer.disconnect();
  });
}

/**
 * Create a sample telemetry message
 * 
 * @returns {Object} Sample telemetry message
 */
function createSampleTelemetryMessage() {
  // Generate a random spacecraft ID between 1 and 10
  const spacecraftId = Math.floor(Math.random() * 10) + 1;
  
  // Generate random values for telemetry data
  const batteryLevel = Math.random() * 100;
  const temperature = 20 + (Math.random() * 30 - 15);  // Between 5 and 35 degrees
  const fuelLevel = Math.random() * 100;
  const attitudeX = Math.random() * 360;
  const attitudeY = Math.random() * 360;
  const attitudeZ = Math.random() * 360;
  
  // Create message
  return {
    header: {
      messageId: uuidv4(),
      timestamp: new Date().toISOString(),
      source: 'example-producer',
      messageType: 'telemetry.data'
    },
    payload: {
      spacecraftId: `SAT-${spacecraftId}`,
      timestamp: new Date().toISOString(),
      subsystem: 'power',
      measurements: [
        {
          name: 'battery_level',
          value: batteryLevel.toFixed(2),
          unit: 'percent'
        },
        {
          name: 'temperature',
          value: temperature.toFixed(2),
          unit: 'celsius'
        },
        {
          name: 'fuel_level',
          value: fuelLevel.toFixed(2),
          unit: 'percent'
        }
      ],
      attitude: {
        x: attitudeX.toFixed(2),
        y: attitudeY.toFixed(2),
        z: attitudeZ.toFixed(2),
        unit: 'degrees'
      },
      status: {
        overall: batteryLevel > 20 ? 'NOMINAL' : 'WARNING',
        issues: batteryLevel <= 20 ? ['LOW_BATTERY'] : []
      }
    }
  };
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('Disconnecting producer...');
  producer.disconnect();
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  producer.disconnect();
  process.exit(1);
}); 