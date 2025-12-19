from flask import Flask,request,jsonify
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Cassandra
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import cassio
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

TAVILY_API_KEY = os.environ.get("TRAVILY_API_KEY")
ASTERA_DB_APPLICATION_TOKEN = os.environ.get("ASTERA_DB_APPLICATION_TOKEN")
ASTERA_DB_ID = os.environ.get("ASTERA_DB_ID")
OPEN_API_KEY = os.environ.get("OPEN_API_KEY")

tool = TavilySearchResults(api_key=TAVILY_API_KEY)

chatllm = ChatOpenAI(openai_api_key=OPEN_API_KEY,temperature = 0,model="gpt-4o-2024-05-13" )
embedding = OpenAIEmbeddings(openai_api_key = OPEN_API_KEY)

cassio.init(token = ASTERA_DB_APPLICATION_TOKEN, database_id = ASTERA_DB_ID )

astra_vector_store = Cassandra(
    embedding = embedding,
    table_name = "Project_DB",
    session = None,
    keyspace = None
)

app = Flask(__name__)

@app.route("/food", methods=["POST"])
def get_food_recipe():
    payload = request.get_json(force=True)

    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    health = []
    food_name = ""
    for key,value in payload.items():
        if value==True and key!="Food Name":
            health.append(key)
        elif key=="Food Name":
            food_name = value
        else:
            continue

    ingredients = tool.invoke({"query": f"""provide me a detailed, expert level instructions and ingredients for {food_name},
                               ensuring that they are well detailed, the more complex the ingredients and instructions the better,
                               ingredients should be realistic, specific, detailed and quantities used explicitly mentioned,
                               also suggest optonal ingredients if any"""})

    query_text = f"find me all what people with {health} diseases can eat and people with {health} cannot eat"
    health_info = []
    for doc, score in astra_vector_store.similarity_search_with_score(query_text,k=9):
        health_info.append(doc.page_content)

    template = """
                  Generate safe and healthy alternative ingredients and cooking instructions for a specific food,
                  considering an individual suffering from {health} diseases.
                  You have the following information:
                  (1)Health Condition: The individual has {health}.
                  (2)Food: The queried food is {food_name}.
                  (3)Dietary Restrictions: Based on {health_info}, provide relevant dietary restrictions (what the individual can and cannot eat).
                  (4)Ingredients: Use the provided ingredients for {food_name}.
                  (5)Instructions:Generate detailed cooking instructions, emphasizing safety and accuracy.

                  Remember to explicitly use safer ingredients, state them clearly, and provide precise cooking times.
                  Focus only on diseases mentioned in {health_info}.Output format:
                  Ingredients: (List of ingredients),
                  Instructions: (Step-by-step cooking instructions),
                  
                  GIVE ANSWER IN FORMAT MENTIONED IN OUTPUT FORMAT ONLY
               """
    

    human_template = "{health},{ingredients},{health_info},{food_name}"

    chat_data = {
        "food_name":food_name,
        "health":health,
        "health_info":health_info,
        "ingredients":ingredients[0].get("content", "") if ingredients else ""
    }

    chatprompt = ChatPromptTemplate.from_messages([
        ("system",template),
        ("human",human_template)
    ])

    chains= chatprompt|chatllm
    chat_response = chains.invoke(chat_data)
    
    return jsonify({"response": chat_response.content})
    
if __name__=="__main__":
    app.run(debug=True)