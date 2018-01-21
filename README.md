# Practice

A module for creating retrieval practice tasks, to help you memorize anything. A few examples are included. You only need to define a generator, a task name, a few instructions and a prompt for each trial. The generator must yields tuples of the form (_question_, _answer_), where _question_ will be inserted within the prompt.

High scores are tracked, so you can check your progress over time. In-task prompts are written in French.
