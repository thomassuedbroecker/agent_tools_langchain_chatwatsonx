import argparse
import json
import requests

from langchain.globals import set_debug
from langchain_ibm import ChatWatsonx
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.globals import set_debug
from typing import List

from modules.load_env import load_watson_x_env_min, load_ibmcloud_env

# ******************************************
# Functions

@tool (response_format="content")
def current_temperature(cities: List[str]) -> List[str]:
     """provides the current temperature information for given cities. 
     Args:
                cities: The parameter cities is a list e.g. ["LA", "NY"].
     """
     base_weather_url="https://wttr.in/"
     cities_input = cities
     cities_output = []
     
     for city in cities_input:
          # Ensure to get the JSON format: '?format=j1'
          city_temp_url = base_weather_url + city + "?format=j1"
          response = requests.get(city_temp_url)
          if (response.status_code == 200):      
              # convert from byte to text
              byte_content = response.content
              text_content = byte_content.decode("utf-8")
              
              # load json
              content = json.loads(text_content)
              print(f"{content}")

              # extract temperature
              temperature = content['current_condition'][0]['temp_C']
              cities_output.append({"city": city, "temperature":temperature})
          else:
              cities_output.append({"city": f"{city} ERROR", "temperature":0})
                    
     return cities_output              

@tool (response_format="content")
def today_maximal_temperature(cities: List[str]) -> List[str]:
     """provides the maximal temperature for today information for the given cities. 
     Args:
                cities: The parameter cities is a list e.g. [ "LA", "NY"].
     """
     base_weather_url="https://wttr.in/"
     cities_input = cities
     cities_output = []
     
     for city in cities_input:
          # Ensure to get the JSON format: '?format=j1'
          city_temp_url = base_weather_url + city + "?format=j1"
          response = requests.get(city_temp_url)
          if (response.status_code == 200):      
              # convert from byte to text
              byte_content = response.content
              text_content = byte_content.decode("utf-8")
              
              # load json
              content = json.loads(text_content)

              # extract temperature
              temperature_max = content['weather'][0]['maxtempC']
              cities_output.append({"city": city, "temperature_max":temperature_max})
          else:
              cities_output.append({"city": f"{city} ERROR", "temperature_max":0}) 

     return cities_output
            
def load_env():
        
        ibmcloud_apikey , validation = load_ibmcloud_env()
        if( validation == False):
            return {  "apikey" : "ERROR",
                      "token" : "ERROR", 
                      "project_id" : "ERROR",
                      "url": "ERROR",
                      "model_id": "ERROR"
                    }
        else:
             apikey = ibmcloud_apikey['IBMCLOUD_APIKEY']
                   
        watson_x_env, validation = load_watson_x_env_min()
        
        if validation == False:
            return { "apikey" : "ERROR", 
                     "project_id" : "ERROR",
                     "url": "ERROR",
                     "model_id": "ERROR"
                    }
        else:
             project_id = watson_x_env['WATSONX_PROJECT_ID']
             url = watson_x_env['WATSONX_URL']
             model_id = watson_x_env['WATSONX_LLM_NAME']
                        
        return { "project_id" : project_id,
                 "url": url,
                 "model_id": model_id,
                 "apikey": apikey }

def agent_tools_calling():

     langchain_debug = False    
     set_debug(langchain_debug)
  
     environment = load_env()
     print(f"1. Load thhe environment variables\n{environment}\n\n")  

     tool = [current_temperature]
     print(f"2. Defined tools for langchain.tools.\n")
     print(f"- The type to the tools:\n{type(tool)}")
     print(f"- The tools list:\n{tool}\n")
        
     parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 400,
            "min_new_tokens": 1,
            "temperature": 1.0
     }
     print(f"3. Define the model parameters\n{parameters}\n")
        
     print(f"4. Create a ChatWatsonx instance for {environment['model_id']}, and not a WatsonxLLM, because to this instance a tool can't be bind.\n")
     watsonx_chat =  ChatWatsonx( model_id=environment['model_id'],
            url=environment['url'],
            project_id=environment['project_id'],
            apikey= environment['apikey'],
            params=parameters
     )

     print(f"5. Define a prompt using a ChatPromptTemplate.\n")            
     prompt_template = ChatPromptTemplate.from_messages(
       [
              ("system", system_prompt_load()),
              ("placeholder", "{chat_history}"),
              ("human", "{input}"),
              ("placeholder", "{agent_scratchpad}"),
       ]
     )
     print(f"-Prompt Template:\n{type(prompt_template)}\n\n{prompt_template}\n")
     print(f"6. Create a tool calling agent based on parameters: the watsonx_chat_with_tools, the tool, and the prompt.\n")  
     agent = create_tool_calling_agent(watsonx_chat, tool, prompt_template)

     print(f"7. Create an AgentExecutor.\n")  
     agent_executor = AgentExecutor(agent=agent, tools=tool, verbose=True)
     
     print(f"8. Execute the agent using the AgentExecutor by providing a question as input to invoke the model.\n")
     questions = ["Which city is hotter today: LA or NY?", 
                  "What is the temperature today in Berlin?",
                  "How to win a soccer game?",
                  "What is the official definition of the term weather?"]
     
     results = []
     for question in questions:
          response = agent_executor.invoke({"input": question,
                                            "include_run_info": True})
          text_json = response['output'].replace('```json\n', '').replace('```\n', '').replace('</endoftext>', '')
          content = json.loads(text_json)
          data = { "question": question, "answer":  content['type'] + ':' +content['function']['name'] }
          results.append(data)
     
     print(f"9. Results\n")
     print(f"|                 agent question                     |                  agent anwser                      |")
     print(f"|----------------------------------------------------|----------------------------------------------------|")
     for result in results:
          print(f"|{result['question'].ljust(52, '_')}|{result['answer'].ljust(52, '_')}|")
     
     return result

def system_prompt_load():
      system_prompt = """You are a weather expert. If the question is not about the weather, say: I don't know."""     
      return system_prompt

# ******************************************
# Execution
def main(args):
     city_list = ["Berlin", "NY", "Paris"]

     print(f"======== TOOL ONLY ========")
     print(f"1. Verify the tool schema definition")
     print(f"=============================")
     print(f"1. Tool name:\n{ today_maximal_temperature.name}")
     print(f"2. Tool description:\n{today_maximal_temperature.description}")
     print(f"3. Tool arguments:\n{today_maximal_temperature.args}")
     print(f"4. Tool arguments title:\n{today_maximal_temperature.args['cities']['title']}\n")
     
     print(f"\n=============================")
     print(f"\n\n2. Invoke the tool and print invocation result")
     print(f"=============================")
     argument = {"cities": city_list}
     result = today_maximal_temperature.invoke(argument)
     print(f"Result:\n{result}\n")
     
     print(f"======== AGENT ONLY========")
     debug_value = False
     print(f"Set LangChain Debug: {debug_value}\n")
     set_debug(debug_value) #Set global debug for LangChain
     agent_tools_calling()

if __name__ == "__main__":  
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)