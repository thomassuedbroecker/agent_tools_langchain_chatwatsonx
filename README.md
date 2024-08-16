# Does it work to use WatsonxChat from langchain_ibm to implement an action that invokes functions?

This repository is an example using the langchain_ibm implementation for action function calling with ChatWatsonx class.

Related blog post: XXX

## 0. Clone the repository

```sh
git clone https://github.com/thomassuedbroecker/agent_tools_langchain_chatwatsonx.git
cd agent_tools_langchain_chatwatsonx
```

## 1. Environment Setup

### Step 1: Generate a virtual Python environment

```sh
cd code
python3 -m venv --upgrade-deps venv
source venv/bin/activate
```

### Step 2: Install the needed libraries

```sh 
python3 -m pip install -qU langchain-ibm
python3 -m pip install -qU langchain
```

### Step 3: Generate a `.env` file for the needed environment variables

```sh
cat env_example_template > .env
```

Insert the values for the two environment variables: 

* `WATSONX_PROJECT_ID=YOUR_WATSONX_PROJECT_ID`
* `IBMCLOUD_APIKEY=YOUR_KEY`

Content of the environment file.

```sh
export IBMCLOUD_APIKEY=YOUR_KEY
export IBMCLOUD_URL="https://iam.cloud.ibm.com/identity/token"

# Watsonx
export WATSONX_URL="https://eu-de.ml.cloud.ibm.com"
export WATSONX_VERSION=2023-05-29
export WATSONX_PROJECT_ID=YOUR_PROJECT_ID

export WATSONX_MIN_NEW_TOKENS=1
export WATSONX_MAX_NEW_TOKENS=300
export WATSONX_LLM_NAME=mistralai/mixtral-8x7b-instruct-v01
export WATSONX_INSTANCE_ID=YOUR_WATSONX_INSTANCE_ID
```

## 2. Execution

### Step 5: Run the example

```sh
cd code
bash example_agent_invocation.sh
```

* Output of the invocation:

```sg
======== TOOL ONLY ========
1. Verify the tool schema definition
=============================
1. Tool name:
today_maximal_temperature
2. Tool description:
provides the maximal temperature for today information for the given cities. 
     Args:
                cities: The parameter cities is a list e.g. [ "LA", "NY"].
3. Tool arguments:
{'cities': {'title': 'Cities', 'type': 'array', 'items': {'type': 'string'}}}
4. Tool arguments title:
Cities


=============================


2. Invoke the tool and print invocation result
=============================
Result:
[{'city': 'Berlin', 'temperature_max': '29'}, {'city': 'NY', 'temperature_max': '28'}, {'city': 'Paris', 'temperature_max': '26'}]

======== AGENT ONLY========
Set LangChain Debug: False

1. Load thhe environment variables
{'project_id': 'YOUR_PROJECT', 'url': 'https://eu-de.ml.cloud.ibm.com', 'model_id': 'mistralai/mixtral-8x7b-instruct-v01', 'apikey': 'YOUR_IBMCLOUD_KEY'}


2. Defined tools for langchain.tools.

- The type to the tools:
<class 'list'>
- The tools list:
[StructuredTool(name='current_temperature', description='provides the current temperature information for given cities. \n     Args:\n                cities: The parameter cities is a list e.g. ["LA", "NY"].', args_schema=<class 'pydantic.v1.main.current_temperatureSchema'>, func=<function current_temperature at 0x168614180>)]

3. Define the model parameters
{'decoding_method': 'greedy', 'max_new_tokens': 400, 'min_new_tokens': 1, 'temperature': 1.0}

4. Create a ChatWatsonx instance for mistralai/mixtral-8x7b-instruct-v01, and not a WatsonxLLM, because to this instance a tool can't be bind.

5. Define a prompt using a ChatPromptTemplate.

-Prompt Template:
<class 'langchain_core.prompts.chat.ChatPromptTemplate'>

input_variables=['input'] optional_variables=['agent_scratchpad', 'chat_history'] input_types={'chat_history': typing.List[typing.Union[langchain_core.messages.ai.AIMessage, langchain_core.messages.human.HumanMessage, langchain_core.messages.chat.ChatMessage, langchain_core.messages.system.SystemMessage, langchain_core.messages.function.FunctionMessage, langchain_core.messages.tool.ToolMessage]], 'agent_scratchpad': typing.List[typing.Union[langchain_core.messages.ai.AIMessage, langchain_core.messages.human.HumanMessage, langchain_core.messages.chat.ChatMessage, langchain_core.messages.system.SystemMessage, langchain_core.messages.function.FunctionMessage, langchain_core.messages.tool.ToolMessage]]} partial_variables={'chat_history': [], 'agent_scratchpad': []} messages=[SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template="You are a weather expert. If the question is not about the weather, say: I don't know.")), MessagesPlaceholder(variable_name='chat_history', optional=True), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')), MessagesPlaceholder(variable_name='agent_scratchpad', optional=True)]

6. Create a tool calling agent based on parameters: the watsonx_chat_with_tools, the tool, and the prompt.

7. Create an AgentExecutor.

8. Execute the agent using the AgentExecutor by providing a question as input to invoke the model.



> Entering new AgentExecutor chain...


```json
{
    "type": "function",
    "function": {
        "name": "current_temperature",
        "arguments": {
            "cities": ["LA", "NY"]
        }
    }
}
```

</endoftext>

> Finished chain.


> Entering new AgentExecutor chain...


```json
{
    "type": "function",
    "function": {
        "name": "current_temperature",
        "arguments": {
            "cities": ["Berlin"]
        }
    }
}
```
</endoftext>

> Finished chain.


> Entering new AgentExecutor chain...


```json
{
    "type": "function",
    "function": {
        "name": "Final Answer",
        "arguments": {
            "output": "I don't know."
        }
    }
}
</endoftext>

> Finished chain.


> Entering new AgentExecutor chain...


```json
{
    "type": "function",
    "function": {
        "name": "Final Answer",
        "arguments": {
            "output": "The term 'weather' refers to the state of the atmosphere at a particular place and time, with respect to temperature, humidity, cloudiness, wind, and atmospheric pressure."
        }
    }
}
```
</endoftext>

> Finished chain.
9. Results

|                 agent question                     |                  agent anwser                      |
|----------------------------------------------------|----------------------------------------------------|
|Which city is hotter today: LA or NY?_______________|function:current_temperature________________________|
|What is the temperature today in Berlin?____________|function:current_temperature________________________|
|How to win a soccer game?___________________________|function:Final Answer_______________________________|
|What is the official definition of the term weather?|function:Final Answer_______________________________|
```