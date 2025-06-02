# Distributed Order System Report

## Overview
This report describes the implementation of a distributed order management system that incorporates key distributed system concepts such as fault tolerance, distributed communication, sharding, monitoring, and stress testing. The system consists of multiple warehouse nodes (HCM, HN, DN), an Airflow orchestration layer, and a stress testing tool.

---

## Required Criteria

### 1. Fault Tolerance
- The system uses health checks on warehouse nodes before assigning orders.
- If a node is unreachable or unhealthy, the Airflow DAG assigns the order to an alternative node.
- Failed order processing tasks are automatically retried up to 3 times with a 1-minute delay between retries.
- This multi-layered fault tolerance (health checks, fallback nodes, and retries) ensures the system continues operating despite node failures or temporary issues.
- Testing confirmed the retry mechanism works: when the HCM node returned a 500 error, the task was marked for retry with proper logging.

### 2. Distributed Communication
- Communication between the Airflow orchestration layer and warehouse nodes is done via HTTP REST APIs.
- Each warehouse node exposes endpoints for health checks and order processing.
- The system is designed to run on multiple machines, with nodes accessible via network URLs.

### 3. Sharding or Replication
- The system implements sharding by region.
- Orders are routed to warehouse nodes based on the `region` field in the order.
- Each node maintains its own local SQLite database storing orders for its shard.
- There is no explicit replication between nodes.

### 4. Simple Monitoring / Logging
- Each warehouse node logs key events such as order creation and errors.
- Health check endpoints provide basic monitoring data including node status and current load (order count).
- The Airflow DAG logs order ingestion, warehouse assignment, and order processing results.
- The stress test script logs submission success and failure details.

### 5. Basic Stress Test
- The `simulate_orders.py` script generates concurrent order submissions to the Airflow API.
- It supports configurable number of orders and concurrency level.
- Logs provide detailed results including success rate and throughput.

---

## Optional Criteria (Selected)

The current system does not explicitly implement most optional features. Below is an assessment:

- **System Recovery (Rejoin after Failure):** Not explicitly implemented. Nodes do not have a mechanism to rejoin or sync after failure.
- **Load Balancing:** Basic load balancing is indirectly achieved by fallback assignment to healthy nodes, but no advanced load balancing algorithm is implemented.
- **Consistency Guarantees:** No explicit consistency protocol; each node manages its own data shard independently.
- **Leader Election:** Not implemented.
- **Security Features:** Basic HTTP communication without authentication or encryption.
- **Deployment Automation:** Docker Compose files exist for some components, but full automated deployment is not detailed.

---

## Summary

| Criterion                 | Implemented | Notes                                      |
|---------------------------|-------------|--------------------------------------------|
| Fault Tolerance           | Yes         | Health checks and fallback assignment      |
| Distributed Communication | Yes         | HTTP REST APIs between Airflow and nodes   |
| Sharding                 | Yes         | Orders sharded by region to separate nodes |
| Replication              | No          | No data replication between nodes          |
| Monitoring / Logging     | Yes         | Logs and health check endpoints             |
| Basic Stress Test        | Yes         | simulate_orders.py script                    |
| System Recovery          | No          |                                            |
| Load Balancing           | Partial     | Fallback assignment only                     |
| Consistency Guarantees   | No          |                                            |
| Leader Election          | No          |                                            |
| Security Features        | No          |                                            |
| Deployment Automation    | Partial     | Some Docker Compose files present           |

---

## Recommendations for Improvement

- Implement replication or distributed consensus for data consistency and fault tolerance.
- Add leader election for coordination and failover.
- Enhance security with authentication and encrypted communication.
- Automate deployment fully using Docker Compose or Kubernetes.
- Implement system recovery mechanisms for nodes to rejoin after failure.
- Add advanced load balancing algorithms based on node load metrics.

---

## Testing Plan

### Component Tests
1. Warehouse Nodes
   - Health check endpoints (GET /health)
   - Order creation (POST /order)
   - Order retrieval (GET /order/<id>)
   - Error handling and validation
   - Database operations

2. Airflow Workflow
   - Order ingestion with validation
   - Warehouse assignment with health checks
   - Order processing with retries
   - Error handling and logging

3. Stress Testing
   - Concurrent order submissions
   - Node failure scenarios
   - Recovery behavior
   - Performance metrics

### Integration Tests
1. End-to-End Order Flow
   - Order submission through stress test script
   - Airflow DAG execution
   - Warehouse node processing
   - Database persistence

2. Fault Tolerance
   - Node failure handling
   - Retry mechanism
   - Fallback node assignment

3. Distributed Communication
   - Inter-service HTTP communication
   - Request/response validation
   - Error handling

### Deployment
1. Docker Compose Services
   - Warehouse nodes (HCM, HN, DN)
   - Airflow components (webserver, scheduler, PostgreSQL)
   - Network configuration
   - Volume management

2. Monitoring
   - Log aggregation
   - Health check status
   - Performance metrics

## Conclusion

The distributed order system demonstrates core distributed system concepts with a practical implementation of fault tolerance, sharding, distributed communication, monitoring, and stress testing. The system's architecture and implementation provide a solid foundation for further enhancements to meet advanced distributed system requirements.

The testing plan outlined above would validate all critical components and their interactions, ensuring the system meets its distributed computing requirements and maintains reliability under various conditions.
