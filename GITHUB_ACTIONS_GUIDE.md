# 🚀 GitHub Actions Setup Guide (Beginner-Friendly)

## What is GitHub Actions?

**GitHub Actions** is like having a robot assistant that automatically runs tasks for you whenever you push code to GitHub.

### Real-World Analogy:
Imagine you're a chef (developer). Every time you finish cooking a dish (push code), a robot assistant automatically:
1. ✅ Checks if all ingredients are fresh (tests your code)
2. ✅ Tastes the food (runs tests)
3. ✅ Reports if the dish is good or needs fixing
4. ✅ Does this without you asking!

---

## 📋 What We Just Set Up

We created a **workflow file** at `.github/workflows/tests.yml` that tells GitHub Actions:

> "Every time code is pushed, automatically:
> 1. Set up Python
> 2. Install PostgreSQL database
> 3. Install all dependencies
> 4. Run database migrations
> 5. Run all pytest tests
> 6. Show me the results"

---

## 🎯 How It Works (Step by Step)

### Step 1: You Push Code
```bash
git push origin main
```

### Step 2: GitHub Detects the Push
- GitHub sees you pushed to the `main` branch
- It looks for `.github/workflows/` folder
- Finds `tests.yml` file
- Starts the workflow automatically

### Step 3: GitHub Creates a Virtual Machine
- GitHub spins up a fresh Ubuntu Linux server (like a clean computer)
- This is FREE for public repositories
- The server only exists for a few minutes (just to run tests)

### Step 4: Workflow Runs Each Step
Our workflow has these steps (they run in order):

1. **Checkout code** → Downloads your code
2. **Set up Python** → Installs Python 3.11
3. **Install PostgreSQL client** → Installs database tools
4. **Install dependencies** → Runs `pip install -r requirements.txt`
5. **Set up environment** → Creates `.env` file with test settings
6. **Wait for PostgreSQL** → Makes sure database is ready
7. **Run migrations** → Creates database tables
8. **Run tests** → Executes `pytest` command

### Step 5: Results Are Shown
- ✅ Green checkmark = All tests passed!
- ❌ Red X = Some tests failed (you'll see which ones)
- You can click to see detailed logs

---

## 👀 How to View GitHub Actions Results

### Method 1: On GitHub Website

1. **Go to your repository** on GitHub:
   ```
   https://github.com/Shreyaa-Shere/legalease-ai-contract-analyzer
   ```

2. **Click the "Actions" tab** (at the top of the page, next to "Code", "Issues", etc.)

3. **You'll see a list of workflow runs:**
   - Each push creates a new run
   - Click on any run to see details

4. **Click on a workflow run** to see:
   - All the steps that ran
   - Which steps passed (✅) or failed (❌)
   - Detailed logs for each step

5. **Click on "Run pytest tests"** to see:
   - All your test results
   - Which tests passed
   - Which tests failed (with error messages)

### Method 2: Badge in README (Optional)

You can add a badge to your README that shows test status:
```markdown
![Tests](https://github.com/Shreyaa-Shere/legalease-ai-contract-analyzer/workflows/Run%20Tests/badge.svg)
```

---

## 📊 What Each Section Does (Detailed Explanation)

### 1. **name: Run Tests**
```yaml
name: Run Tests
```
- This is just a label for the workflow
- Shows up in the GitHub Actions tab

### 2. **on: (When to Run)**
```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:
```

**BEGINNER EXPLANATION:**
- `push: branches: main` = Run when code is pushed to `main` branch
- `pull_request: branches: main` = Run when someone opens a pull request to `main`
- `workflow_dispatch` = Allows you to manually click a button to run tests

### 3. **jobs: test (The Main Job)**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```
- `jobs` = List of tasks to run
- `test` = Name of this job
- `runs-on: ubuntu-latest` = Use the latest Ubuntu Linux (free virtual machine)

### 4. **services: postgres (Database)**
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_legalease_db
```

**BEGINNER EXPLANATION:**
- `services` = Things that need to run alongside your code
- `postgres` = PostgreSQL database
- `image: postgres:15` = Use PostgreSQL version 15
- `env` = Environment variables (database username, password, database name)
- This creates a temporary database just for testing

### 5. **steps: (What to Do)**
Each `step` is an action that runs in sequence:

#### Step 1: Checkout Code
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```
- Downloads your repository code to the virtual machine
- `uses: actions/checkout@v4` = Uses GitHub's official "checkout" action

#### Step 2: Set Up Python
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```
- Installs Python 3.11
- Caches pip packages (makes future runs faster)

#### Step 3: Install PostgreSQL Client
```yaml
- name: Install PostgreSQL client
  run: |
    sudo apt-get update
    sudo apt-get install -y libpq-dev postgresql-client
```
- `sudo` = Run as administrator
- `apt-get` = Package manager (installs software)
- Installs PostgreSQL client libraries (needed for `psycopg2`)

#### Step 4: Install Dependencies
```yaml
- name: Install dependencies
  run: |
    cd backend
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
- `cd backend` = Go to backend folder
- `pip install -r requirements.txt` = Install all Python packages

#### Step 5: Set Up Environment Variables
```yaml
- name: Set up environment variables
  run: |
    cd backend
    cat > .env << EOF
    SECRET_KEY=test-secret-key-for-github-actions
    DB_NAME=test_legalease_db
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=localhost
    DB_PORT=5432
    EOF
```
- Creates a `.env` file with test database settings
- `cat > .env` = Create new file called `.env`
- `<< EOF ... EOF` = Everything between these markers goes in the file

#### Step 6: Wait for PostgreSQL
```yaml
- name: Wait for PostgreSQL
  run: |
    until pg_isready -h localhost -p 5432 -U postgres; do
      echo "Waiting for PostgreSQL to start..."
      sleep 2
    done
```
- Checks if database is ready before proceeding
- `until ... do` = Keep checking until database is ready
- `pg_isready` = Command that checks if PostgreSQL is running

#### Step 7: Run Migrations
```yaml
- name: Run database migrations
  run: |
    cd backend
    python manage.py migrate --noinput
```
- Creates database tables
- `--noinput` = Don't ask for confirmation (automated)

#### Step 8: Run Tests
```yaml
- name: Run pytest tests
  run: |
    cd backend
    pytest -v --tb=short
```
- **This is the main step!**
- Runs all your pytest tests
- `-v` = Verbose (show detailed output)
- `--tb=short` = Short error messages if tests fail

---

## 🔧 Common Issues & Solutions

### Issue 1: Tests Fail in GitHub Actions but Pass Locally
**Possible Causes:**
- Different environment (clean vs your local)
- Missing environment variables
- Database connection issues

**Solution:**
- Check the workflow logs to see the exact error
- Make sure all required environment variables are set

### Issue 2: PostgreSQL Connection Error
**Error:** `could not connect to server`

**Solution:**
- Make sure the `Wait for PostgreSQL` step is included
- Check that database credentials match in the `.env` setup

### Issue 3: Missing Dependencies
**Error:** `ModuleNotFoundError`

**Solution:**
- Check that all packages are in `requirements.txt`
- Verify the "Install dependencies" step runs successfully

---

## 🎓 Key Concepts for Beginners

### What is CI/CD?
- **CI (Continuous Integration)** = Automatically test code when pushed
- **CD (Continuous Deployment)** = Automatically deploy if tests pass
- We've implemented CI (testing), CD can be added later

### What is a Workflow?
- A workflow is a set of automated steps
- Defined in YAML file (`.yml` or `.yaml`)
- Lives in `.github/workflows/` folder

### What is a Job?
- A job is a task that runs on a virtual machine
- Can have multiple jobs (they run in parallel)
- Each job has multiple steps (they run in sequence)

### What is a Step?
- A step is a single action
- Steps run one after another
- Each step can run a command or use an action

### What is an Action?
- A reusable piece of code
- Like a function you can call
- Examples: `actions/checkout@v4`, `actions/setup-python@v5`

---

## 📈 Next Steps (Optional Enhancements)

### 1. Add Test Coverage
Show percentage of code covered by tests:
```yaml
- name: Generate coverage report
  run: |
    cd backend
    pytest --cov=contracts --cov-report=xml
```

### 2. Add Code Quality Checks
Run linters (check code style):
```yaml
- name: Run flake8
  run: |
    pip install flake8
    flake8 backend/
```

### 3. Add Frontend Tests
Test your React frontend:
```yaml
- name: Run frontend tests
  run: |
    cd frontend
    npm install
    npm test
```

### 4. Add Deployment
Automatically deploy if tests pass:
```yaml
- name: Deploy to production
  if: success()
  run: |
    # Deploy code here
```

---

## ✅ Summary

**What We Did:**
1. ✅ Created `.github/workflows/tests.yml` file
2. ✅ Configured workflow to run on every push
3. ✅ Set up PostgreSQL database for testing
4. ✅ Configured Python and dependencies
5. ✅ Set up to run pytest tests automatically
6. ✅ Pushed to GitHub

**What Happens Now:**
- Every time you push code, GitHub automatically runs tests
- You'll see results in the "Actions" tab
- ✅ = Tests passed
- ❌ = Tests failed (check logs to see why)

**Where to See Results:**
1. Go to your GitHub repository
2. Click "Actions" tab
3. Click on any workflow run
4. See detailed test results!

---

## 🎉 Congratulations!

You now have **automated testing** set up! This is a professional development practice that:
- ✅ Catches bugs early
- ✅ Ensures code quality
- ✅ Shows confidence in your code
- ✅ Makes collaboration easier

**Your tech stack progress:**
- ✅ Django REST API
- ✅ React + Tailwind
- ✅ PostgreSQL
- ✅ OpenAI
- ✅ PyTest
- ✅ **GitHub Actions (CI/CD)** ← You just added this!

**Remaining:**
- Celery (async processing)
- AWS EC2 + S3 (deployment)

Great job! 🚀

