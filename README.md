<h1 align="center">Mini LLM Flow - LLM Framework in 100 Lines</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://zachary62.github.io/miniLLMFlow/)

An [100-line](minillmflow/__init__.py) minimalist LLM framework for [agents](https://minillmflow.github.io/miniLLMFlow/agent.html), [task decomposition](https://minillmflow.github.io/miniLLMFlow/decomp.html), [RAG](https://minillmflow.github.io/miniLLMFlow/rag.html), etc.

- Install via  ```pip install minillmflow```, or just copy the [source codes](minillmflow/__init__.py) (only 100 lines)

- **Pro tip:** Build LLM apps with LLMs assistants (ChatGPT, Claude, Cursor.ai, etc.)

  - **Claude (preferred):** Create a project, dump the [docs](docs), and ask it to write LLM workflow!
   
  - **ChatGPT:** Check out [GPT assistant](https://chatgpt.com/g/g-677464af36588191b9eba4901946557b-mini-llm-flow-assistant)

Documentation: https://minillmflow.github.io/miniLLMFlow/

## Why Mini LLM Flow?

Mini LLM Flow is designed to be **the framework used by LLMs**. In the future, LLM projects will be *self-programmed* by LLMs themselves: Users specify requirements, and LLMs will design, build, and maintain. Current LLMs are:

1. **👍 Good at Low-level Details:** LLMs can handle details like *wrappers, tools, and prompts*, which don't belong in a framework. Current frameworks are over-engineered, making them hard for humans (and LLMs) to maintain.

2. **👎 Bad at High-level Paradigms:** While paradigms like *MapReduce, task decomposition, and agents* are powerful, LLMs still struggle to design them elegantly. These high-level concepts should be emphasized in frameworks.

The ideal framework for LLMs should (1) **strip away low-level implementation details**, and (2) **keep high-level programming paradigms**. Hence, we provide this minimal (100-line) framework that allows LLMs to focus on what matters.  

Mini LLM Flow is also a *learning resource*, as current frameworks abstract too much away.

<div align="center">
  <img src="/assets/minillmflow.jpg" width="400"/>
</div>

## How Does it Work?

The [100 lines](minillmflow/__init__.py) capture what we see as the core abstraction of most LLM frameworks: a **nested directed graph** that breaks down tasks into multiple (LLM) steps, with branching and recursion for agent-like decision-making. From there, it’s easy to layer on more complex features.

- To learn more details, please check out documentation: https://minillmflow.github.io/miniLLMFlow/

- Beginner Tutorial: [Text summarization for Paul Graham Essay + QA agent](https://colab.research.google.com/github/zachary62/miniLLMFlow/blob/main/cookbook/demo.ipynb)

    - Have questions for this tutorial? Ask LLM assistants through [this prompt](https://chatgpt.com/share/676f16d2-7064-8000-b9d7-f6874346a6b5)
 
- More coming soon ... Let us know you’d love to see!
