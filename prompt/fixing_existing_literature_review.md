Great prompt already — it’s **structurally solid and PhD-level** 👍
What’s missing (and what you’re feeling) is that it **tells the model *how to write***, but not **how to *search, verify, and ground references***.

Below is an **improved version** that keeps your structure intact but **adds a reference-discovery + verification layer**, so the output is not just eloquent but *bibliographically strong*.

---

## 🌐 Ultra-General Academic Literature Review Prompt

### *(Field-Independent, PhD-Level, Reference-Grounded)*

---

### 📌 System / Instruction Prompt

> You are an **academic research assistant** producing a **doctoral-level literature review**.
>
> Your task is to:
>
> 1. **Identify, verify, and synthesize authoritative academic sources**
> 2. Provide **critical analysis, conceptual clarity, and explicit reasoning**
> 3. Ground **every substantive claim** in **traceable scholarly references**
>
> The output must be suitable for submission to a **peer-reviewed journal or conference**.

You must prioritize:

* Peer-reviewed journals, conference proceedings, and foundational books
* Canonical and highly cited works where applicable
* Recent high-impact studies when discussing emerging trends

Avoid hallucinated citations.
If a claim cannot be confidently referenced, **explicitly state the uncertainty**.

---

### 🧩 User Prompt (Universal, Reference-Driven Template)

```
Write a structured literature review titled:

"<INSERT TITLE HERE>"

Context:
- The topic belongs to an academic or scientific field.
- The literature spans multiple approaches, methods, or perspectives.
- The goal is not only synthesis, but also *systematic reference discovery*:
  identifying which works define, challenge, or extend the field.

Before writing:
- Identify the core sub-themes of the topic.
- For each sub-theme, identify representative and influential sources.
- Prefer sources with DOI, arXiv ID, PubMed ID, or stable publisher URLs.

Follow the exact section structure below.
Do not merge sections.
Do not skip sections.
Use formal academic prose.
Avoid bullet points unless conceptually necessary.

### Citation Requirements
- Every factual or methodological claim must be supported by an in-text citation.
- Use (Author, Year) format.
- Include DOI or stable URL whenever available.
- Reuse citations consistently rather than inventing near-duplicates.
- If multiple studies support a claim, cite them collectively.

---

## Required Sections and Content Expectations

### 1. Background and Scope
- Introduce the research area and its academic significance.
- Define conceptual and methodological boundaries.
- Cite foundational surveys or seminal works that establish the field.

### 2. Historical Development of the Field
- Trace chronological development using landmark publications.
- Identify paradigm shifts supported by key references.
- Explicitly link changes in approach to limitations in earlier work.

### 3. Dominant Approaches and Methods
- Describe widely adopted models or frameworks.
- Ground descriptions in original or authoritative sources.
- Cite surveys or benchmarks that justify dominance.

### 4. Motivations for Alternative or Extended Approaches
- Identify documented limitations in dominant methods.
- Cite papers that explicitly critique or extend prior work.
- Explain how proposed alternatives respond to cited shortcomings.

### 5. Comparative Analysis of Key Contributions
- Compare representative studies across approaches.
- Use citations to support claims of performance, scalability, or validity.
- Highlight methodological trade-offs grounded in evidence.

### 6. Data, Evidence, and Evaluation Practices
- Describe commonly used datasets, benchmarks, or corpora.
- Cite dataset papers, benchmark introductions, or evaluation standards.
- Discuss known biases or assumptions with supporting references.

### 7. Applications and Impact
- Cite applied studies or real-world deployments.
- Distinguish speculative applications from empirically validated ones.
- Reference cross-disciplinary influence where documented.

### 8. Limitations and Open Challenges
- Identify unresolved issues acknowledged in the literature.
- Cite discussion or limitations sections from key works.
- Avoid speculation not supported by sources.

### 9. Emerging Trends and Future Directions
- Reference recent surveys, position papers, or roadmap articles.
- Clearly separate emerging evidence from established consensus.
- Justify importance using citations.

### 10. Alternative Perspectives and Related Paradigms
- Discuss adjacent or competing paradigms with proper attribution.
- Cite comparative or interdisciplinary work.
- Clarify conceptual differences using authoritative sources.

### 11. Annotated Bibliography
- Include 8–15 representative references.
- For each reference:
  - Full citation
  - One-sentence contribution summary
  - DOI, arXiv ID, or stable URL
  - (Optional) Citation count or influence indicator if known

---

## Output Constraints
- Formal academic tone
- No first-person narration
- No unverifiable claims
- Explicit reasoning supported by citations
- Clear separation between evidence, interpretation, and critique

Generate the full literature review now.
```

---

## 🔑 Why this version works better

### What you fixed (without breaking reuse):

* ✅ Explicit **reference discovery phase**
* ✅ Citation **verification constraints**
* ✅ Clear rules against hallucinated sources
* ✅ Encourages **surveys + seminal papers first**
* ✅ Makes **evidence vs interpretation** explicit

### What stays reusable:

* Field-independent
* Same section structure
* Works for NLP, ML, medicine, economics, social sciences, engineering

---

## 🚀 Optional “Power-Up” (if you want)

If you later want **tool-assisted grounding**, add this line:

> *When uncertain about a reference, prefer well-known survey papers and explicitly flag gaps rather than fabricating citations.*

Or a **two-stage workflow**:

1. *Generate reference map only*
2. *Generate literature review from that map*

If you want, I can:

* Convert this into a **two-prompt pipeline**
* Create a **reference-first extraction prompt**
* Tailor it specifically for **NLP / ML / ESG / medical** reviews

Just tell me the direction 👌
