'''
 function calling allows for:

More deterministic control: Transform natural text into a structured output through functions.
Structured data extraction: Using the resource to extract specific information from text.
Development of custom functions: Connect the model to external APIs, databases, and internal tools.

LLMs return unstructed data which is hard to use in applications other than chat. By invoking functions, 
you can make LLMs return structured data which can be used to interact with other systems. 
In practice, this means that the model will return a JSON instead of Natural Text, which can 
be parsed and passed as arguments to functions in your code.
'''
