# MediRewards_Engine

MediRewards_Engine is a production-quality, transactional loyalty and rewards backend management system. It allows customers to earn points through pharmacy-related activities, redeem points for rewards, and maintain a complete, auditable history of all points transactions.

---

## Project Context & Domain Choice

I chose the pharmacy domain for this assignment because of my previous experience working on two pharmacy-related projects: **SVPharma** and **Pharmiq**. Being familiar with these business workflows allowed me to focus my efforts on designing and implementing a robust backend system rather than learning a new domain from scratch.

My goal was to build a simple yet complete loyalty engine demonstrating core backend engineering concepts:
* **Event Processing**: Processing customer activities to award points.
* **Event Idempotency**: Ensuring duplicate events do not reward points twice.
* **Configurable Rules Engine**: Keeping business rules (base points, bonuses, caps) in an external JSON configuration file so they can be tweaked without touching application code.
* **Immutable Ledger**: Maintaining a complete, audit-safe ledger rather than a mutable state.
* **Redemption & Reversals**: Deducting points for rewards and handling returns/cancellations through compensating negative ledger entries.

While a real-world production system might award points only after successful order delivery, this project awards points immediately upon event processing and handles returns or cancellations through reversal events. This trade-off keeps the workflow straightforward while fully covering the assignment's transactional requirements.

---

## Quick Start (Under 1 Minute)

To set up and run the application immediately:

```bash
# 1. Clone the repository (if not already done)
git clone <repository_url>
cd MediRewards_Engine

# 2. Set up virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# For PowerShell:
.\.venv\Scripts\Activate.ps1
# For Command Prompt:
# .\.venv\Scripts\activate.bat
# For Bash:
# source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Seed database with sample data (highly recommended)
python seed_sample_data.py

# 6. Start the server
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) (which redirects to `/docs`) in your browser to view the interactive API documentation and try out the endpoints.

---

### Layer Breakdown
1. **API Routers (`app/routes/`)**: Expose REST endpoints, validate requests using Pydantic, manage transaction commits, and format response payloads.
2. **Schemas (`app/schemas/`)**: Define Pydantic validation structures, enforcing constraint checks (e.g., non-negative amounts, supported event types).
3. **Services (`app/services/`)**: Implement business logic (points calculations, database insertions, balance verification, double reversal checks).
4. **Models (`app/models/`)**: Define the database schemas using SQLAlchemy declarative mapping.
5. **Rules Engine (`app/services/rules_engine.py`)**: Computes points dynamically using external rules without hardcoding.

---

## Features

1. **Configurable Rules Engine**: Loyalty point base rewards and bonuses (high-value purchases, weekends) are loaded from a JSON configuration file.
2. **Strict Event Idempotency**: Employs a database unique constraint on `event_id` and handles potential concurrency collisions gracefully.
3. **Immutable Points Ledger**: Does not maintain mutable point balances. Instead, balances are dynamically calculated by summing historical `CREDIT`, `DEBIT`, and `REVERSAL` entries, ensuring a bulletproof audit trail.
4. **Validation Constraints**: Restricts point redemptions to positive balances (preventing negative balances on rewards).
5. **Compensating Reversals**: Supports reversing events (due to returns, cancellations, or failures) by inserting negative compensating ledger entries.
6. **Double Reversal Protection**: Rejections are enforced if a reversal is attempted on an already reversed event.

---

## Example API Requests (Postman Collection)

For rapid manual testing, we have provided a pre-configured Postman Collection:
1. Locate the file [MediRewards_Engine.postman_collection.json](MediRewards_Engine/MediRewards_Engine.postman_collection.json) at the root of the project.
2. Open Postman and click on **Import** in the top-left corner.
3. Drag and drop the collection JSON file.
4. The collection includes environment variables (like `{{base_url}}` pointing to `http://127.0.0.1:8000`) and pre-configured request payloads.

---

## Running the Automated Tests

Execute the unit and integration tests with pytest using the following command in the project root directory:
```bash
python -m pytest app/tests/ -v
```

---

## Design Decisions

### 1. Reversal Balance Policy (Negative Balances)
* **Decision**: We allow points balances to temporarily drop below zero when an event is reversed (e.g. order cancellation/return) even if the user spent their points on a reward in the meantime.
* **Rationale**: Reversals represent physical business realities (goods returned, payments failed). Preventing a reversal due to insufficient balance would allow users to abuse the system by immediately redeeming points and returning goods.
* **Trade-off**: Balance calculation must handle negative values, and negative balances are locked out of redemption until the user earns back points to reach a positive balance.

### 2. No Hardcoded Rules
* **Decision**: All rules (base points, thresholds, weekend bonuses, maximum caps) are configured in `app/config/rules.json`.
* **Rationale**: Business rules change frequently. Keeping them in JSON allows configuration updates without modifying code logic or redeploying code.
* **Trade-off**: Adds a minor file-reading overhead on startup, which is mitigated by caching the rules in memory.

### 3. Signed Ledger Points
* **Decision**: We store point values as signed integers (`points` can be negative for `DEBIT` and `REVERSAL` types) rather than absolute values with sign-swapping in Python.
* **Rationale**: Makes balance queries highly efficient and safe from database bugs. The SQL sum is simply `SUM(points)`, avoiding complex CASE-WHEN SQL blocks.

---

## AI Tool Usage

I used Google Gemini to write the code, but the entire architectural logic is my own, which I designed based on my self-taught experience and learning from software engineering tutorials. 

For the rules engine, I structured it using an external JSON config file so that the business rules are extremely easy to modify and readable even for a non-technical reader. The ledger calculates balances dynamically by summing historical ledger entries to maintain a clean audit history. This setup trades off a minor database query overhead for bulletproof data integrity, preventing any sync issues.

During development, I had to manually correct and rewrite what Gemini generated for the database session setup in tests and route registrations to ensure they matched the structure of the FastAPI application. I had initially planned to use CodeRabbit for further code reviews, but skipped it due to the overnight time constraints of the assignment.
