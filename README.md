https://chatgpt.com/c/697cf3e5-0678-8333-9072-ce3164307ee4

https://chatgpt.com/c/697cf172-a9b0-832d-8d4b-9703777a44ac

https://chatgpt.com/c/697cf172-a9b0-832d-8d4b-9703777a44ac

ESG Research Questions: https://chatgpt.com/c/697726ec-959c-8330-a9ac-9a29c0a0ed57 

Yes — this is very doable, and you’re already structured in a way that makes it clean 👍

I’ve created a **fully working Streamlit app** in the canvas that does exactly what you asked:

### What this Streamlit page does

**1. Parses your literature review into sections**

* Uses the `## Section Title` Markdown structure
* Each section becomes a structured record:

  * `section`
  * `content`
  * `parsed_at` timestamp

**2. Persists results locally**

* Automatically stores:

  * **CSV** → `data/literature_review_sections.csv`
  * **JSON** → `data/literature_review_sections.json`
* Appends new parses instead of overwriting (audit-friendly)

**3. Lets you re-browse and filter**

* Interactive table of stored sections
* Filter by section name
* Download CSV anytime

**4. Keeps LLM completely optional**

* No model calls
* No hallucination risk
* This fits perfectly with your *constraint-first, verification-before-reasoning* philosophy

---

### Why this design fits your research direction

This mirrors a **document intelligence → verification → reasoning** pipeline:

```
Raw ESG Disclosure
   ↓
Section-level parsing (this app)
   ↓
Claim extraction (next step)
   ↓
Constraint validation (XBRL, taxonomy, numeric)
   ↓
Optional LLM reasoning / summarization
```

You now have:

* Deterministic storage ✅
* Reproducible parsing ✅
* Audit trail via timestamps ✅
* A clean insertion point for constraint-aware logic ✅

---

### Natural next upgrades (when you’re ready)

If you want, the **next logical extensions** are:

1. **Sentence-level ESG claim extraction**

   * Regex + FinBERT classification
2. **Similarity search**

   * TF-IDF / embeddings across sections
3. **Constraint hooks**

   * Map claims → XBRL tags
   * Flag unverifiable statements
4. **LLM as *post-verifier*, not generator**

   * Summarize *only validated* claims

If you want, next I can:

* Add **claim-level tables**
* Add **XBRL schema hooks**
* Add **similarity + retrieval**
* Or refactor this into a **modular research prototype** (paper-ready)

Just tell me how deep you want to go 👌
# research_holistic_tools
