# AstroShield Integration Quick Start Guide

This guide provides step-by-step instructions to quickly get started with the AstroShield integration package.

## Prerequisites

Before you begin, ensure you have:

- API credentials (contact jack@lattis.io to obtain)
- Kafka cluster access information (provided with your subscription)
- Development environment with one of the following:
  - Python 3.8+
  - Java 11+
  - Node.js 14+

## 1. API Integration

### Step 1: Configure Authentication

Choose one of the authentication methods:

#### JWT Authentication

```python
# Python example
import requests

auth_url = "https://api.astroshield.com/auth/token"
credentials = {
    "username": "your-username",
    "password": "your-password"
}

response = requests.post(auth_url, json=credentials)
token = response.json()["token"]

# Use token in subsequent requests
headers = {
    "Authorization": f"Bearer {token}"
}
```

#### API Key Authentication

```python
# Python example
headers = {
    "X-API-Key": "your-api-key"
}
```

### Step 2: Make API Requests

```python
# Python example - Get spacecraft list
import requests

url = "https://api.astroshield.com/v1/spacecraft"
headers = {
    "Authorization": "Bearer your-token"  # or "X-API-Key": "your-api-key"
}

response = requests.get(url, headers=headers)
spacecraft_list = response.json()
```

### Step 3: Handle Responses and Errors

```python
# Python example - Error handling
import requests

def make_api_request(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            # Handle authentication error
            print("Authentication failed. Refresh your token.")
        elif e.response.status_code == 429:
            # Handle rate limiting
            print("Rate limit exceeded. Implement backoff.")
        else:
            print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
    return None
```

## 2. Kafka Integration

### Step 1: Configure Kafka Client

Create a file named `kafka.properties` with the following content:

```properties
bootstrap.servers=kafka.astroshield.com:9093
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="your-username" password="your-password";
```

### Step 2: Create a Kafka Consumer

#### Python (using confluent-kafka)

```python
# Install with: pip install confluent-kafka
from confluent_kafka import Consumer
import json

# Configure consumer
conf = {
    'bootstrap.servers': 'kafka.astroshield.com:9093',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'your-username',
    'sasl.password': 'your-password',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Create consumer
consumer = Consumer(conf)

# Subscribe to topic
consumer.subscribe(['ss5.launch.prediction'])

# Process messages
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
            
        # Process message
        try:
            value = json.loads(msg.value().decode('utf-8'))
            print(f"Received message: {value}")
            # Process the message according to your application logic
        except Exception as e:
            print(f"Error processing message: {e}")
            
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

#### Java (using Kafka Client)

```java
// See examples/java/KafkaConsumerExample.java for complete code
import org.apache.kafka.clients.consumer.*;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class KafkaConsumerExample {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put("bootstrap.servers", "kafka.astroshield.com:9093");
        props.put("security.protocol", "SASL_SSL");
        props.put("sasl.mechanism", "PLAIN");
        props.put("sasl.jaas.config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"your-username\" password=\"your-password\";");
        props.put("group.id", "my-consumer-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList("ss5.launch.prediction"));
        
        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Offset = %d, Key = %s, Value = %s%n", 
                                     record.offset(), record.key(), record.value());
                    // Process the message according to your application logic
                }
            }
        } finally {
            consumer.close();
        }
    }
}
```

### Step 3: Create a Kafka Producer

#### JavaScript (using node-rdkafka)

```javascript
// Install with: npm install node-rdkafka
const Kafka = require('node-rdkafka');

// Configure producer
const producer = new Kafka.Producer({
  'bootstrap.servers': 'kafka.astroshield.com:9093',
  'security.protocol': 'SASL_SSL',
  'sasl.mechanism': 'PLAIN',
  'sasl.username': 'your-username',
  'sasl.password': 'your-password',
  'dr_cb': true  // Delivery report callback
});

// Connect to the broker
producer.connect();

// Wait for the ready event before proceeding
producer.on('ready', function() {
  try {
    // Create a message
    const message = {
      header: {
        messageId: "msg-" + Date.now(),
        timestamp: new Date().toISOString(),
        source: "my-application"
      },
      payload: {
        // Message-specific payload
        // See schema definitions for required fields
      }
    };
    
    // Send the message
    producer.produce(
      'ss5.telemetry.data',  // Topic
      null,                  // Partition (null = librdkafka assigns)
      Buffer.from(JSON.stringify(message)),  // Message content
      'key',                 // Optional message key
      Date.now()             // Optional timestamp
    );
    
    console.log('Message sent successfully');
  } catch (err) {
    console.error('Error producing message:', err);
  }
});

// Log any errors
producer.on('event.error', function(err) {
  console.error('Error from producer:', err);
});

// Delivery report handler
producer.on('delivery-report', function(err, report) {
  if (err) {
    console.error('Delivery failed:', err);
  } else {
    console.log('Delivery successful:', report);
  }
});

// Wait for messages to be delivered before exiting
setTimeout(function() {
  producer.flush(10000, function() {
    producer.disconnect();
  });
}, 5000);
```

## 3. Testing Your Integration

### API Testing with Postman

1. Import the Postman collection from `postman/AstroShield_API.postman_collection.json`
2. Import the environment from `postman/AstroShield_API.postman_environment.json`
3. Update the environment variables with your credentials
4. Run the collection to test all endpoints

### Kafka Testing

1. Use the consumer examples to verify you can receive messages from the topics
2. Use the producer examples to send test messages to the topics
3. Verify message format against the JSON schemas in the `schemas/` directory

## Next Steps

- Review the full API documentation in `api/openapi.yaml`
- Explore the example code in the `examples/` directory
- Implement error handling and retry logic
- Set up monitoring for your integration
- Contact jack@lattis.io if you need assistance

## Troubleshooting

If you encounter issues:

1. Verify your credentials and connection settings
2. Check the [README.md](README.md) for common issues and solutions
3. Review the logs for error messages
4. Contact jack@lattis.io for support 