# Content Transformation Agent System

A multi-agent system that transforms content between formats, styles, and complexity levels, ensuring factual accuracy and high-quality output through human-in-the-loop verification and a RAG-powered knowledge base.

---

## Multi-Agent Architecture

The system is built around four core agents, each with a dedicated role:

| Agent                             | Role & Implementation                                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Style Analysis Agent**          | Analyzes input content to determine format, style, and complexity. (`improved_content_system.py`, `rag_knowledge_base.py`)           |
| **Transformation Planning Agent** | Designs the step-by-step plan for converting content to the target format/style/complexity. (`improved_content_system.py`)           |
| **Content Conversion Agent**      | Executes the actual transformation using style guides and examples. (`improved_content_system.py`, `rag_knowledge_base.py`)          |
| **Quality Control Agent**         | Validates output for factual accuracy, style/format adherence, and quality metrics. (`improved_content_system.py`, `test_system.py`) |

Agents are coordinated using a workflow that can be extended with LangGraph for advanced orchestration.

---

## Agent Coordination & Workflow

- **Transformation Workflow:**
  - The system orchestrates agents in sequence: analysis → planning → conversion → quality control.
  - The workflow is modular and can be extended or visualized using LangGraph.
- **Content Types:**
  - Supports various formats (blog, LinkedIn, Twitter, newsletter, podcast) and styles (Gen Z, Formal, Yoda, etc.)
- **User Feedback:**
  - Human-in-the-loop verification is built in. Users can approve, reject, or edit facts before transformation.
  - Feedback is incorporated into the workflow for iterative improvement.

---

## RAG Enhancement: Knowledge Base & Factual Accuracy

- **Knowledge Base:**
  - Built from style guides (`style_guides/`) and example transformations (`generated_stylized_content/`).
  - Indexed using FAISS for fast semantic retrieval.
- **Retrieval:**
  - System retrieves the most relevant style guide and example for each transformation.
  - Guarantees inclusion of exact style/format/complexity and topic if available.
- **Factual Accuracy:**
  - All transformations preserve verified facts from the master content.
  - No new facts are introduced unless verified by the user.
- **Verification:**
  - Quality Control Agent checks output for factual preservation, style/format match, and overall quality.
  - Human verification step is required before transformation (unless auto-verified mode is used).

---

## How Requirements Are Accomplished

| Requirement                                | Implementation/Location                                                 |
| ------------------------------------------ | ----------------------------------------------------------------------- |
| Style Analysis Agent                       | `improved_content_system.py`, `rag_knowledge_base.py`                   |
| Transformation Planning Agent              | `improved_content_system.py`                                            |
| Content Conversion Agent                   | `improved_content_system.py`, `rag_knowledge_base.py`                   |
| Quality Control Agent                      | `improved_content_system.py`, `test_system.py`                          |
| Agent Coordination (LangGraph-ready)       | Modular workflow in `improved_content_system.py`                        |
| Handling various content types             | Format/style/complexity selection in CLI & code                         |
| User feedback incorporation                | Human-in-the-loop verification in CLI & workflow                        |
| RAG knowledge base (style guides/examples) | `rag_knowledge_base.py`, `style_guides/`, `generated_stylized_content/` |
| Retrieval of similar transformation cases  | FAISS-based retrieval in `rag_knowledge_base.py`                        |
| Factual accuracy during transformation     | Fact extraction, verification, and preservation logic                   |
| Verification system for output quality     | Quality metrics, human review, and test suite                           |

---

## Example Transformation Workflow

1. **Input:** "The Benefits of Meditation" (user provides title or content)
2. **Style Analysis Agent:** Determines current format/style/complexity
3. **Transformation Planning Agent:** Plans steps to convert to, e.g., "Gen Z Twitter Thread, Newbie"
4. **Content Conversion Agent:**
   - Retrieves relevant style guide and example from RAG knowledge base
   - Applies transformation, preserving all verified facts
5. **Quality Control Agent:**
   - Checks factual accuracy, style/format/complexity match, readability, engagement
   - Presents quality metrics and requests user feedback

---

## Example: Factual Preservation & Quality Metrics

**Original Fact:** "Meditation reduces stress by 40% according to 2023 study"

**Transformations:**
- **Formal Professional:** "Research indicates a 40% stress reduction through meditation"
- **Gen Z:** "The tea: meditation can reduce stress by 40%"
- **Yoda Style:** "Reduce stress by 40%, meditation does, studies show"
- **Sherlock Holmes:** "The evidence is clear: meditation produces a 40% reduction in stress levels"

**Quality Metrics Provided:**
- Factual Accuracy: 100% (all facts preserved)
- Style Adherence: High (matches selected style)
- Format Compliance: Yes
- Complexity Match: Yes
- Readability: High
- Engagement: High

---

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
export ULTRASAFE_API_KEY="your_api_key_here"
```

### Interactive CLI (Recommended)
```bash
cd task_b
python improved_content_system.py
```

### Demo the System
```bash
cd task_b
python demo_improved_system.py
```

---

## Technical Implementation

- `improved_content_system.py`: Main agent workflow and CLI
- `rag_knowledge_base.py`: RAG system for style guides and examples
- `data_models.py`: Data structures and models
- `demo_improved_system.py`: System demonstration
- `test_system.py`: Test suite for validation

---

## FAISS Index: Loading & Querying

The system uses a FAISS-based RAG knowledge base for fast retrieval of style guides and examples.

### Loading the FAISS Index

The FAISS index is loaded automatically by the system. If you need to load it manually (for example, in your own scripts), use:

```python
from rag_knowledge_base import RAGKnowledgeBase
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
rag = RAGKnowledgeBase(embeddings)
rag.load_index("rag_faiss_index")  # Loads index from disk
```

> **Note:**
> Due to recent security updates, loading the FAISS index requires `allow_dangerous_deserialization=True` internally. This is handled for you in the code. Only load indexes you trust.

### Querying the Knowledge Base

You can retrieve relevant style guides and examples for a given query:

```python
results = rag.retrieve_relevant_context(
    query="How to write a Gen Z Twitter thread about meditation?",
    target_format="twitter_thread",
    target_style="gen_z",
    target_complexity="newbie",
    target_topic="meditation_for_beginners"
)

# Access style guides and examples
style_guides = results["style_guides"]
examples = results["examples"]
```

### CLI Usage

- The interactive CLI and demo scripts handle index loading and querying automatically.
- To rebuild or update the index, use:

```bash
python build_rag_index.py
```
And follow the prompts to rebuild, update, save, or load the index.

---

## File Structure

```
task_b/
├── improved_content_system.py      # Main system with human verification
├── demo_improved_system.py         # Demo of the improved system
├── rag_knowledge_base.py           # RAG knowledge base
├── data_models.py                  # Data models
├── interactive_cli.py              # Interactive CLI interface
├── test_system.py                  # Test suite
├── requirements.txt                # Dependencies
├── README.md                       # This file
└── SYSTEM_DOCUMENTATION.md         # Complete system documentation
```

---

**🎉 This system ensures factual accuracy, style/format/complexity transformation, and high output quality through a coordinated multi-agent workflow and RAG-powered knowledge base!** 