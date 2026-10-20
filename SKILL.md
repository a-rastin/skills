---
name: intern
description: "Analyzes patient clinical data including history and physical exam (Persian and/or English), EKG, labs, para-clinical data, and imaging to deliver a comprehensive interpretation, structured clinical approach, prioritized differential diagnosis (DDX), and evidence-based next steps. Use for case review, diagnostic reasoning, workup planning, or intern-style analysis of multimodal patient presentations. Educational and research use only — not medical advice or a substitute for licensed clinician judgment."
type: workflow
lifecycle: active
---

# Intern — Clinical Case Analysis

Perform systematic, bias-aware analysis of patient data to produce an intern-level clinical assessment. Inputs may be bilingual (Persian/English), free-text, structured, or multimodal (images of EKG, labs, imaging, reports).

**Hard safety boundary**: This skill is for education, research, case discussion, and decision-support drafting only. It does not diagnose, treat, or replace professional medical judgment. Always note that outputs require review by a licensed clinician. Do not claim certainty or urgency thresholds that could influence real care without human oversight. If inputs suggest an emergency, explicitly recommend immediate professional evaluation.

## Inputs Accepted

- History & Physical Examination (H&P / Ph/E) in Persian, English, or mixed.
- EKG / ECG tracings or reports (images or text).
- Laboratory data (CBC, chemistry, ABG, cultures, etc.).
- Para-clinical data (spirometry, EEG, nerve conduction, etc.).
- Imaging (X-ray, CT, MRI, ultrasound reports or images).
- Additional context (vitals, medications, allergies, PMH).

If data is incomplete, note gaps and how they affect certainty.

## Workflow

1. **Organize & Summarize Data**
   - Extract and structure all available information by category: demographics, chief complaint, HPI, PMH/PSH, medications, allergies, social/family history, ROS, vital signs, physical exam findings, EKG interpretation, labs (with reference ranges and trends if available), imaging findings, other para-clinical.
   - Translate/summarize Persian text accurately; preserve key medical terms.
   - For images: describe visible findings objectively (e.g., EKG rate, rhythm, intervals, ST changes; CXR opacities, etc.). Use available tools to inspect images if needed.

2. **Deep Analysis & Research**
   - Identify key abnormal findings, patterns, and red flags.
   - Cross-reference findings against standard knowledge. For uncommon presentations, rare disease considerations, guideline updates, or conflicting data, perform targeted research (web search, guideline sites, recent literature) and cite sources.
   - Note data quality, limitations, and missing critical information.

3. **Comprehensive Interpretation**
   - Provide an integrated summary of what the current data show.
   - Highlight most significant positive and negative findings.
   - Discuss clinical significance and possible pathophysiologic links.

4. **Clinical Approach**
   - Frame the case systematically (e.g., problem-oriented or by organ system).
   - Prioritize problems by acuity.
   - Outline immediate stabilization considerations if relevant (always with disclaimer).
   - Suggest a logical sequence of reasoning.

5. **Differential Diagnosis (DDX)**
   - Generate a prioritized DDX (most likely → less likely → must-not-miss).
   - For each diagnosis: supporting evidence, refuting evidence, and probability assessment (qualitative: high/moderate/low).
   - Use frameworks when helpful (e.g., VINDICATE for broad DDX, anatomic/physiologic approaches).
   - Explicitly list must-not-miss diagnoses even if lower probability.
   - Perform a bias check: note potential anchoring, availability, confirmation, premature closure, or attribution biases and how the analysis counters them.

6. **Next Steps**
   - Recommend specific investigations, monitoring, consultations, or interventions with clear rationale (diagnostic yield, risk/benefit, urgency).
   - Order by priority (stat vs. routine).
   - Suggest follow-up parameters and thresholds for reassessment.
   - Note what additional history or exam elements would be valuable.

7. **Output Format**
   Structure the final response as:
   - **Data Summary**
   - **Interpretation**
   - **Clinical Approach**
   - **Differential Diagnosis** (table or prioritized list preferred)
   - **Next Steps**
   - **Bias & Uncertainty Notes**
   - **Disclaimer**

## Bias-Aware Practices

- Explicitly challenge the first hypothesis: "What else could this be?"
- Seek disconfirming evidence.
- Consider atypical presentations and patient-specific context (age, comorbidities, geography, language barriers).
- Avoid over-reliance on recent similar cases.
- Document reasoning transparently.

## Research Guidance

When research is needed:
- Prefer high-quality sources (guidelines from AHA, ESC, IDSA, NICE, UpToDate-style summaries, PubMed, Cochrane).
- Distinguish established knowledge from emerging evidence.
- Cite key references inline.

## Common Pitfalls to Avoid

- Premature diagnostic closure.
- Ignoring Persian medical terminology nuances.
- Over-interpreting single lab values without context.
- Recommending treatments without adequate data or safety caveats.
- Failing to note when imaging or EKG requires specialist review.

Always end with a clear statement that this is educational support only and professional clinical correlation is required.
