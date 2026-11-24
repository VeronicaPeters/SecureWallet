# SecureWallet API

SecureWallet API

A threat-modelling-led application security engineering project focused on identifying, analysing, and mitigating security risks in a simulated digital wallet application.

The project began with security architecture, data-flow analysis, and STRIDE-based threat modelling to identify potential attack paths, vulnerabilities, and security requirements.

Those findings informed the design and implementation of a Python FastAPI application with security controls covering authentication, authorization, wallet ownership, transaction integrity, input validation, rate limiting, and audit logging.

SecureWallet demonstrates the application security engineering lifecycle, from threat identification and risk analysis through secure implementation, security testing, and technical documentation.

> **Disclaimer:** This is an educational portfolio project. It does not connect to real banking infrastructure or process real money.

## Features

### Authentication and Account Security
- Customer registration and login.
- Argon2id password hashing.
- JWT-based authentication.
- Token expiration and server-side user validation.
- Generic authentication failure responses.
- Login rate limiting: 5 requests per minute per IP.
- Registration rate limiting: 5 requests per hour per IP.

### Wallet Management
- Automatic wallet creation during registration.
- Authenticated users can view their own wallets.
- Simulated wallet funding.
- Positive monetary amount validation.
- Server-side wallet ownership enforcement.

### Transaction Security
- Transfers between customer wallets.
- Atomic conditional debit and credit operations.
- Insufficient balance protection.
- Self-transfer prevention.
- Recipient balance limit enforcement.
- Idempotency keys to prevent ordinary duplicate transfer retries.
- Conflict detection when an idempotency key is reused with different transfer details.
- Transaction history scoped to the authenticated user's wallets.
- Paginated transaction history.

### Auditability
- Transaction audit events.
- Unique transaction references.
- Transaction timestamps and status records.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Application development |
| FastAPI | REST API framework |
| SQLAlchemy | Database ORM |
| SQLite | Development database |
| Pydantic | Request validation and serialization |
| Argon2 | Password hashing |
| PyJWT | JWT authentication |
| SlowAPI | API rate limiting |
| Pytest | Automated testing |
| HTTPX | API testing |
| Bandit | Python security analysis |
| Semgrep | Static application analysis |
| pip-audit | Dependency vulnerability auditing |
| Gitleaks | Secret detection |

## Project Structure

```text
SecureWallet/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── transactions.py
│   │   └── wallets.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── limiter.py
│   │   ├── security.py
│   │   └── token.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── docs/
│   ├── architecture/
│   │   ├── system-architecture.md
│   │   ├── data-flow-diagram.md
│   │   └── securewallet-dfd.png
│   │
│   ├── security-testing/
│   │   ├── security-assessment-report.md
│   │   └── security-test-plan.md
│   │
│   └── threat-model/
│       ├── threat-register.md
│       ├── stride-analysis.md
│       └── security-mitigations.md
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_wallets.py
│   └── test_transactions.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
````

## **Installation and Setup**

### **1. Clone the Repository**

```
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SecureWallet
```

### **2. Create and Activate a Virtual Environment**

```
python3 -m venv .venv
source .venv/bin/activate
```

### **3. Install Dependencies**

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### **4. Configure Environment Variables**

Create a local `.env` file:

```
APP_NAME=SecureWallet API
APP_VERSION=1.0.0
DATABASE_URL=sqlite:///./securewallet.db
JWT_SECRET_KEY=REPLACE_WITH_A_STRONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a strong secret rather than using the placeholder:

```
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Do not commit `.env` or real secrets to source control.

### **5. Initialize the Database**

```
python -m app.core.init_db
```

### **6. Start the API**

```
uvicorn app.main:app --reload
```

The API will be available at:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs?utm_source=chatgpt.com)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc?utm_source=chatgpt.com)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health?utm_source=chatgpt.com)

## **API Endpoints**

| Method | Endpoint                 | Description                      |
| ------ | ------------------------ | -------------------------------- |
| POST   | `/auth/register`         | Register a customer              |
| POST   | `/auth/login`            | Authenticate a customer          |
| GET    | `/auth/me`               | Retrieve authenticated user      |
| GET    | `/wallets/me`            | Retrieve own wallet              |
| POST   | `/wallets/fund`          | Simulate wallet funding          |
| POST   | `/transactions/transfer` | Transfer funds between wallets   |
| GET    | `/transactions/me`       | Retrieve own transaction history |

Protected endpoints require a valid bearer token.

### **Example: Customer Registration**

```
POST /auth/register
Content-Type: application/json
```

```
{
  "email": "alice@example.com",
  "password": "SecureWallet-Example-2026!",
  "full_name": "Alice Example"
}
```

### **Example: Customer Login**

```
POST /auth/login
Content-Type: application/json
```

```
{
  "email": "alice@example.com",
  "password": "SecureWallet-Example-2026!"
}
```

The API returns an access token for authenticated requests.

### **Example: Wallet Transfer**

Transfer requests require an authenticated user and an `Idempotency-Key` header.

```
POST /transactions/transfer
Authorization: Bearer <ACCESS_TOKEN>
Idempotency-Key: transfer-unique-001
Content-Type: application/json
```

```
{
  "receiver_wallet_id": 2,
  "amount": "250.00"
}
```

A retry with the same key and the same transfer details returns the original transaction instead of processing another debit.

Reusing the key with different transfer details returns HTTP `409 Conflict`.

## **Security Design and Controls**

| Security Area          | Implemented Control                                          |
| ---------------------- | ------------------------------------------------------------ |
| Password Storage       | Argon2id password hashing                                    |
| Authentication         | Signed JWT access tokens                                     |
| Token Validation       | Signature and expiration validation                          |
| Identity Enforcement   | User identity derived from authenticated server-side context |
| Authorization          | Wallet ownership checks                                      |
| Input Validation       | Pydantic schemas and constrained fields                      |
| Financial Integrity    | Conditional balance updates and transaction rollback         |
| Duplicate Requests     | Idempotency keys and database uniqueness constraint          |
| Abuse Prevention       | Login and registration rate limiting                         |
| Data Access            | SQLAlchemy ORM queries                                       |
| Transaction Visibility | User-scoped transaction history                              |
| Auditability           | Transaction audit events                                     |
| Pagination             | Bounded transaction-history queries                          |

## **Security Testing**

Run the automated test suite:

```
pytest -q
```

Run the security tools:

### **Bandit**

```
bandit -r app -ll
```

### **Dependency Vulnerability Audit**

```
pip-audit
```

### **Semgrep**

```
semgrep scan --config auto app
```

### **Gitleaks**

```
gitleaks detect --source . --no-git
```

Refer to:

`docs/security-testing/security-assessment-report.md`

for assessment results, testing coverage and limitations.

## **Architecture and Threat Modelling**

The project includes supporting security documentation:

- System architecture.
- Data flow diagram (DFD).
- STRIDE threat analysis.
- Security threat register.
- Security mitigation documentation.
- Security test plan.
- Security assessment report.

These documents demonstrate the security engineering process from initial threat identification through implementation and verification.

## **Known Limitations and Future Improvements**

- SQLite is used for local development. PostgreSQL concurrency behaviour has not yet been validated.
- Rate limiting currently uses in-memory storage. A production multi-worker deployment should use shared storage such as Redis.
- Concurrent requests using the same idempotency key require further testing and robust conflict handling.
- Wallet funding is simulated and does not verify external payment settlement.
- A production financial ledger would require a properly designed double-entry accounting model.
- Administrative account-management endpoints and their RBAC controls are not implemented.
- No independent penetration test or production deployment assessment has been completed.

## **Project Objective**

SecureWallet is an application security engineering portfolio project demonstrating how security requirements can be translated into:

1. Secure application architecture.
2. Threat modelling and risk identification.
3. Security-focused application development.
4. Authentication and authorization controls.
5. Financial transaction integrity protections.
6. Automated security testing.
7. Technical security documentation.

The objective is to demonstrate practical application security engineering skills through a complete, security-focused API development project.
