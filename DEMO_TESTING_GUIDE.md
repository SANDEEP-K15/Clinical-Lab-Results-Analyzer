# Clinical Lab AI Analyzer — Demo & Testing Guide

Use this checklist to test and explain the app during your presentation.

**Before you start:**
1. Backend running: `python run_server.py` (in `backend/` folder)
2. Frontend running: `npm run dev` (in `frontend/` folder)
3. Open: http://localhost:5173
4. Groq API key set in `backend/.env`

---

## 1. Manual Input

### Test 1.1 — Single Normal Result
| Field | Enter |
|-------|-------|
| Test Name | Hemoglobin |
| Value | 14.5 |
| Unit | g/dL |

**Click:** Analyze Results

**Expected UI:**
- Summary: 1 Normal, 0 Warning, 0 Critical
- Badge: **✓ NORMAL** (green)
- Reference range shown: 12 – 17.5 g/dL
- AI explanation explains value is within range
- Shows: Why flagged, What it means, Suggested next step

---

### Test 1.2 — Warning Result
| Field | Enter |
|-------|-------|
| Test Name | Hemoglobin |
| Value | 8.2 |
| Unit | g/dL |

**Expected UI:**
- Badge: **⚠️ WARNING** (yellow)
- Summary: 1 Warning
- AI explains value is **below** normal range
- Suggests clinical review (not a diagnosis)

---

### Test 1.3 — Critical Result
| Field | Enter |
|-------|-------|
| Test Name | Hemoglobin |
| Value | 6.5 |
| Unit | g/dL |

**Expected UI:**
- Badge: **🔴 CRITICAL** (red)
- AI explains value crosses critical threshold
- Suggests prompt clinical review

---

### Test 1.4 — Multiple Tests
Add 3 rows:
| Test Name | Value | Unit |
|-----------|-------|------|
| Hemoglobin | 14.5 | g/dL |
| WBC | 12500 | cells/uL |
| Glucose | 90 | mg/dL |

**Expected UI:**
- All 3 results shown
- Mixed severities (Normal + Warning + Normal)
- Results ordered: Warning first, then Normal

---

### Test 1.5 — Unknown Test
| Field | Enter |
|-------|-------|
| Test Name | Random Test |
| Value | 5 |
| Unit | mg/dL |

**Expected UI:**
- Badge: **? UNKNOWN** (gray)
- Text: "Reference range unavailable"
- No fake reference range invented

---

## 2. CSV Upload

### Test 2.1 — Normal Labs
**File:** `test_data/normal_labs.csv`

**Expected UI:**
- Preview shows 5 rows
- Summary: **5 Normal**, 0 Warning, 0 Critical
- All badges green ✓ NORMAL
- AI explanation for every result

---

### Test 2.2 — Warning Labs
**File:** `test_data/warning_labs.csv`

**Expected UI:**
- Summary: **5 Warning**
- All badges yellow ⚠️ WARNING
- Each card explains why below/above range
- Suggested next steps shown

---

### Test 2.3 — Critical Labs
**File:** `test_data/critical_labs.csv`

**Expected UI:**
- Summary: **5 Critical**
- All badges red 🔴 CRITICAL
- Urgent language in explanations
- Prompt review suggested

---

### Test 2.4 — Mixed Labs (Routing Demo)
**File:** `test_data/mixed_labs.csv`

**Expected UI:**
- Mixed severities in one response
- Results **reordered** by severity:
  1. Critical first
  2. Warning second
  3. Normal last
- (Not in the same order as the CSV file)

---

### Test 2.5 — Kaggle Sample
**File:** `test_data/kaggle_sample.csv`

**Expected UI:**
- 3 results from real Kaggle dataset
- Hemoglobin, WBC, Platelet Count
- All classified correctly

---

## 3. UI Features to Show

| Feature | What to say | Expected |
|---------|-------------|----------|
| **Tabs** | "Two ways to enter data" | Manual Input + CSV Upload |
| **Summary cards** | "Quick overview of all results" | Total, Critical, Warning, Normal counts |
| **Severity badges** | "Color + text, not color alone" | Red / Yellow / Green labels |
| **Reference range** | "Compared against configured ranges" | Shown on every card |
| **Why flagged / Why normal** | "Explainable AI — not just 'abnormal'" | Normal → "Why is this normal?"; Warning/Critical → "Why was this flagged?" |
| **Clinical significance** | "What the test measures" | Plain language explanation |
| **Next step** | "Actionable suggestion" | e.g. clinical review |
| **Disclaimer** | "Educational only, not diagnosis" | Shown on every card |
| **Filters** | "Filter by severity" | All / Critical / Warning / Normal |
| **Loading state** | "Shows analysis progress" | Spinner + step labels |
| **Empty state** | "Before any analysis" | "No laboratory results yet" |

---

## 4. Backend Features (Quick mention)

| Feature | How to verify |
|---------|---------------|
| Health check | http://localhost:8000/health → `{"status": "healthy"}` |
| API docs | http://localhost:8000/docs → Swagger UI |
| Agent pipeline | Classify → Route → Explain |
| MCP tools | Reference lookup, Validate, Classify |
| Groq AI | Real explanations (not "temporarily unavailable") |
| Kaggle dataset | `GET /dataset/info` shows dataset metadata |

---

## 5. Error Cases (Optional)

| Test | Input | Expected UI |
|------|-------|-------------|
| Wrong unit | Hemoglobin + mg/dL | Error message about unit mismatch |
| Empty name | Blank test name | Error: "Test name is required" |
| Backend off | Stop backend, analyze | "Unable to analyze the laboratory results" |

---

## 6. 5-Minute Demo Script

**Say this while demoing:**

1. **"We accept lab results manually or via CSV."**
   → Show Manual Input tab, then CSV Upload tab

2. **"Results are classified deterministically — Normal, Warning, or Critical."**
   → Upload `warning_labs.csv`

3. **"Critical results are shown first — severity routing."**
   → Upload `mixed_labs.csv`

4. **"Every result gets an AI explanation — not just a label."**
   → Point to Why flagged, What it means, Next step

5. **"We use Groq LLM for explanations, but classification is rule-based."**
   → Mention backend + MCP architecture

6. **"Built with Kaggle real lab dataset."**
   → Upload `kaggle_sample.csv`

---

## 7. Supported Tests

| Test Name | Unit | Normal Range |
|-----------|------|--------------|
| Hemoglobin | g/dL | 12 – 17.5 |
| WBC | cells/uL | 4000 – 11000 |
| Platelet Count | cells/uL | 150000 – 450000 |
| Glucose | mg/dL | 70 – 99 |
| Creatinine | mg/dL | 0.6 – 1.2 |

---

## 8. One-Line Summary for Evaluator

> "This app takes lab results, classifies them by severity using reference ranges, routes critical results first, and uses Groq AI to explain every result in plain clinical language — with full transparency into why each result was flagged."
