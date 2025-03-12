package com.astroshield.examples;

import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Example Kafka consumer for AstroShield Kafka topics.
 * This example demonstrates how to consume messages from AstroShield Kafka topics,
 * specifically focusing on the launch prediction topic.
 */
public class KafkaConsumerExample {
    private static final Logger logger = LoggerFactory.getLogger(KafkaConsumerExample.class);
    
    // Kafka configuration
    private static final String BOOTSTRAP_SERVERS = "kafka.astroshield.com:9092";
    private static final String GROUP_ID = "astroshield-example-consumer";
    private static final String TOPIC = "ss5.launch.prediction";
    
    // Security configuration
    private static final String SECURITY_PROTOCOL = "SASL_SSL";
    private static final String SASL_MECHANISM = "PLAIN";
    
    private final AtomicBoolean running = new AtomicBoolean(true);
    private final CountDownLatch shutdownLatch = new CountDownLatch(1);
    
    /**
     * Main method to start the Kafka consumer.
     * 
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        KafkaConsumerExample example = new KafkaConsumerExample();
        
        try {
            example.run();
        } catch (Exception e) {
            logger.error("Error running Kafka consumer", e);
        }
    }
    
    /**
     * Run the Kafka consumer.
     * 
     * @throws InterruptedException If the thread is interrupted
     */
    public void run() throws InterruptedException {
        logger.info("Starting Kafka consumer for topic: {}", TOPIC);
        
        // Register shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Shutting down Kafka consumer...");
            running.set(false);
            try {
                shutdownLatch.await();
            } catch (InterruptedException e) {
                logger.error("Error waiting for consumer to shutdown", e);
            }
        }));
        
        // Create consumer
        try (Consumer<String, String> consumer = createConsumer()) {
            // Subscribe to topic
            consumer.subscribe(Collections.singletonList(TOPIC));
            
            // Poll for messages
            while (running.get()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                records.forEach(record -> {
                    logger.info("Received message:");
                    logger.info("Topic: {}", record.topic());
                    logger.info("Partition: {}", record.partition());
                    logger.info("Offset: {}", record.offset());
                    logger.info("Key: {}", record.key());
                    logger.info("Value: {}", record.value());
                    
                    // Process the message
                    processMessage(record.value());
                });
                
                // Commit offsets
                consumer.commitSync();
            }
        } catch (Exception e) {
            logger.error("Error consuming messages", e);
        } finally {
            shutdownLatch.countDown();
        }
    }
    
    /**
     * Create a Kafka consumer with the appropriate configuration.
     * 
     * @return Configured Kafka consumer
     */
    private Consumer<String, String> createConsumer() {
        Properties props = new Properties();
        
        // Basic configuration
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        
        // Consumer configuration
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "100");
        
        // Security configuration
        props.put("security.protocol", SECURITY_PROTOCOL);
        props.put("sasl.mechanism", SASL_MECHANISM);
        
        // SASL configuration
        String saslJaasConfig = "org.apache.kafka.common.security.plain.PlainLoginModule required " +
                "username=\"astroshield-client\" " +
                "password=\"your-password-here\";";
        props.put("sasl.jaas.config", saslJaasConfig);
        
        return new KafkaConsumer<>(props);
    }
    
    /**
     * Process a message from the Kafka topic.
     * This is where you would implement your business logic to handle the message.
     * 
     * @param message The message to process
     */
    private void processMessage(String message) {
        try {
            // Here you would typically parse the JSON message and process it
            // For example, using Jackson or Gson to deserialize the JSON
            
            // Example structure of a launch prediction message:
            // {
            //   "header": {
            //     "messageId": "550e8400-e29b-41d4-a716-446655440000",
            //     "timestamp": "2023-05-01T12:00:00Z",
            //     "source": "ss5-prediction-engine",
            //     "messageType": "launch.prediction"
            //   },
            //   "payload": {
            //     "predictionId": "pred-12345",
            //     "launchSite": {
            //       "name": "Baikonur Cosmodrome",
            //       "latitude": 45.9644,
            //       "longitude": 63.3052
            //     },
            //     "predictedLaunchWindow": {
            //       "start": "2023-06-01T10:00:00Z",
            //       "end": "2023-06-01T14:00:00Z"
            //     },
            //     "confidence": 0.85,
            //     "launchVehicle": {
            //       "type": "Soyuz-2.1b",
            //       "payload": "Military Satellite"
            //     },
            //     "threatAssessment": {
            //       "level": "MEDIUM",
            //       "potentialTargets": ["SATELLITE-A", "SATELLITE-B"],
            //       "recommendedActions": ["INCREASE_ORBIT", "NOTIFY_OPERATORS"]
            //     }
            //   }
            // }
            
            logger.info("Successfully processed message: {}", message);
        } catch (Exception e) {
            logger.error("Error processing message", e);
        }
    }
} 