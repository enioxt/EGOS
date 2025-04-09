# Prompt Design Document (PDD) Template - EGOS

**PDD ID:** `[Assign Unique ID, e.g., PDD-SYS-NNN]`
**Title:** `[Concise, Descriptive Title of Prompt's Purpose]`
**Version:** `1.0`
**Status:** `Draft | Active | Deprecated`
**Author(s):** `[Your Name/Team]`
**Date Created:** `YYYY-MM-DD`
**Last Updated:** `YYYY-MM-DD`

---

## 1. Goal / Objective

*   **What specific task is this prompt designed to accomplish?**
*   **What problem does it solve within the EGOS system or workflow?**
*   **What is the desired outcome or state after the prompt is successfully executed?**

---

## 2. Context / Use Case

*   **When and where is this prompt typically used?** (e.g., During code generation, documentation update, strategic analysis, specific user interaction)
*   **Which subsystem(s) primarily use or are related to this prompt?** (e.g., CORUJA, KOIOS, specific MCP)
*   **Are there any preconditions or specific states required before using this prompt?**

---

## 3. Target AI Model(s)

*   **Which specific LLM(s) is this prompt primarily designed or optimized for?** (e.g., Gemini Pro 2.5, Claude 3 Sonnet, GPT-4 Turbo, internal fine-tuned model)
*   **Are there known variations needed for different models?**
*   **Are there any known limitations or compatibility issues with certain models?**

---

## 4. Input Variables / Parameters

*List all dynamic inputs the prompt requires. Use placeholder notation (e.g., `{variable_name}`).*

| Variable Name       | Type        | Description & Source                                     |
| :------------------ | :---------- | :------------------------------------------------------- |
| `{example_input_1}` | `string`    | Description of what this input is and where it comes from. |
| `{example_input_2}` | `dict/json` | Description...                                           |
| `{code_snippet}`    | `string`    | Represents a block of code provided as context.          |
| *...add more rows as needed...* |

---

## 5. Prompt Text

*Paste the full prompt text below. Use Markdown code blocks for clarity. Clearly indicate where input variables are inserted.*

```prompt
This is the main body of the prompt.

Include necessary context, instructions, role-playing directives, and specify desired output format here.

Use placeholders like {example_input_1} or {code_snippet} where dynamic content will be injected.

Ensure the prompt is clear, concise, and unambiguous for the target AI model.
```

---

## 6. Output Format / Constraints

*   **Describe the desired structure of the AI's response.** (e.g., Markdown, JSON object with specific keys, plain text, list of items)
*   **Are there specific formatting requirements?** (e.g., Code blocks for code, specific headings)
*   **Are there constraints on the output?** (e.g., Maximum length, specific tone - professional/formal/creative, must include/exclude certain information)
*   **If JSON, provide an example schema or structure.**

---

## 7. Evaluation Metrics / Criteria

*   **How will the effectiveness or quality of this prompt's output be assessed?**
*   **List specific, measurable criteria where possible.**
    *   *Example: Accuracy - Does the output correctly answer the query based on provided context? (Scale: Yes/No or 1-5)*
    *   *Example: Relevance - Is the output directly relevant to the prompt's goal? (Scale: 1-5)*
    *   *Example: Format Adherence - Does the output match the specified format/constraints? (Yes/No)*
    *   *Example: ETHIK Compliance - Does the output adhere to ETHIK guidelines? (Pass/Fail/Needs Review)*
    *   *Example: Clarity/Readability - Is the output easy to understand? (Scale: 1-5)*
    *   *Example: Task Completion - Did the prompt successfully achieve its stated goal? (Yes/No)*
*   **How will feedback be collected?** (e.g., Automated checks, human review, user ratings)

---

## 8. Examples (Optional but Recommended)

*Provide one or more examples demonstrating the prompt in action.*

**Example 1:**

*   **Input Variables:**
    *   `{example_input_1}`: "Value A"
    *   `{example_input_2}`: `{"key": "Value B"}`
*   **Expected/Desired Output:**
    ```markdown
    This is an example of the desired output structure based on the inputs "Value A" and Value B.
    ```

**Example 2:**
*   *(...)*

---

## 9. Potential Risks / Biases

*   **Identify any known risks associated with this prompt.** (e.g., Potential for generating factually incorrect information, producing biased language, generating insecure code, misuse if context is insufficient)
*   **Are there known biases in the target model(s) that this prompt might trigger?**
*   **What mitigation strategies are in place or recommended?** (e.g., Input validation, output filtering, specific instructions in the prompt to avoid bias)

---

## 10. Related Documents / Links

*   [Link to relevant MQP section]
*   [Link to specific subsystem README (e.g., CORUJA)]
*   [Link to related code file(s)]
*   [Link to other relevant PDDs]
*   [Link to associated GitHub Issue/Task]

---

## 11. Revision History

| Version | Date       | Author(s)     | Summary of Changes                                  |
| :------ | :--------- | :------------ | :-------------------------------------------------- |
| `1.0`   | `YYYY-MM-DD` | `[Your Name]` | Initial draft.                                      |
|         |            |               |                                                     |

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
