from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import stock_tool, search_tool, wiki_tool, sentiment_tool, StockData, get_live_market_movers_tool
from vector import store_research_response, retrieve_similar_docs
from typing import Optional, List, Dict, Any
import speech_recognition as sr
import os
import json

load_dotenv()

def validate_google_api_key():
    """Validates the presence and format of the Google API Key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found. Please add it to your .env file.")
    if not api_key.startswith('AI'):
        raise ValueError("❌ Invalid GOOGLE_API_KEY format. It should start with 'AI'.")
    print("✅ Google API Key validated successfully.")

def validate_fmp_api_key():
    """Validates the presence of the FMP API Key for live data."""
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("⚠️ FMP_API_KEY not found. The live market movers tool will be disabled. Add it to your .env file to enable.")
        return False
    print("✅ FMP API Key found. Live market movers tool enabled.")
    return True

try:
    validate_google_api_key()
    fmp_enabled = validate_fmp_api_key()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
except ValueError as e:
    print(f"Configuration Error: {e}")
    exit()


class ResearchResponse(BaseModel):
    """Defines the structured output for the financial research agent."""
    topic: str = Field(description="The main topic of the research, e.g., 'Apple Inc. Stock Data'.")
    summary: str = Field(description="A concise summary of the findings from the tools used.")
    sources: List[str] = Field(description="List of sources used, which can be filenames or URLs.")
    tools_used: List[str] = Field(description="The names of the tools that were invoked by the agent.")
    company_name: Optional[str] = Field(None, description="The full legal name of the company, e.g., 'Apple Inc.'.")
    ticker_symbol: Optional[str] = Field(None, description="The stock ticker symbol for the company, e.g., 'AAPL'.")
    recent_news_summary: str = Field(description="A summary of the top 1-2 most relevant recent news articles about the company or topic.")
    accuracy: float = Field(description="A self-assessed confidence score from 0.0 to 1.0 on the quality of the report.")
    stock_data: Optional[StockData] = Field(None, description="Detailed stock data if requested.")



parser = PydanticOutputParser(pydantic_object=ResearchResponse)

system_prompt = """You are an expert financial analyst AI powered by Google's Gemini.
Your mission is to provide accurate, data-driven financial insights by leveraging specialized tools.
All final output must be delivered in the structured format requested.

Execution Protocol:
1. **Analyze Request:** Carefully understand the user's financial query.
2. **Tool Selection Strategy:**
    - **Specific Company Focus:** If the query is about a SINGLE, CLEARLY IDENTIFIED company (e.g., 'Apple', 'MSFT'), you MUST use the `stock_tool` to fetch its key data, in addition to any other relevant tools. The final output must include the detailed stock data.
    - **Real-Time Market Movers:** For questions about top/worst performers (e.g., 'top gaining stocks today'), you MUST use the `get_live_market_movers_tool`.
        - **CRITICAL:** Your final summary MUST include the detailed list of stocks (names, tickers, change, percent change) returned by this tool. Do not just say you found the data; DISPLAY the data itself in a readable format.
    - **General/Broad Queries:** For historical, opinion-based, or broad questions (e.g., 'best stocks for beginners'), you MUST use the `search_tool` to find and summarize expert analysis.
3. **Process Data:** Analyze the tool outputs and synthesize the information into a comprehensive answer.
4. **Be Precise:** Ensure all financial data is accurate and properly attributed.
5. **Safety First:** You must not provide financial advice. Only provide factual information and analysis.

{format_instructions}"""


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [stock_tool, search_tool, wiki_tool, sentiment_tool]
if fmp_enabled:
    tools.append(get_live_market_movers_tool)

agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- Core Functions ---

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes audio from a file path to text using Google's speech recognition."""
    if not audio_file_path:
        return ""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[ERROR] Could not understand the audio."
    except sr.RequestError as e:
        return f"[ERROR] Google API error: {e}"
    except Exception as e:
        return f"[ERROR] Could not process audio file: {e}"


def process_query(query: str) -> Dict[str, Any]:
    """
    Processes a financial query using the AI agent and returns a structured dictionary.
    """
    if not query or not query.strip():
        return {"error": "Query cannot be empty."}

    try:
        raw_response = agent_executor.invoke({"query": query.strip()})
        response_str = raw_response.get("output", "")

        if not response_str:
            return {"error": "The AI agent did not return a valid response."}

        try:
            structured_response = parser.parse(response_str)
            store_research_response(structured_response)
            response_dict = structured_response.model_dump()
        except Exception as e:
            print(f"Pydantic Parsing Error: {e}")
            return {"error": "Failed to structure the AI response.", "raw_response": response_str}

        similar_text = ""
        try:
            similar_docs = retrieve_similar_docs(query)
            if similar_docs:
                for doc in similar_docs:
                    similar_text += f"- **{doc.metadata.get('topic', 'Untitled')}**: {doc.page_content[:200]}...\n"
            else:
                similar_text = "No similar past research found."
        except Exception as e:
            print(f"Error retrieving similar docs: {e}")
            similar_text = "⚠️ Could not retrieve similar research."

        extra_info = ""
        try:
            steps = raw_response.get("intermediate_steps", [])
            for action, observation in steps:
                if action.tool == "wiki_tool" and observation:
                    extra_info = f"🟡 Wikipedia Summary:\n{str(observation).strip()}"
                    break
        except Exception as e:
            print(f"Error processing intermediate steps: {e}")

        response_dict['similar_research'] = similar_text
        response_dict['extra_info'] = extra_info

        return response_dict

    except Exception as e:
        print(f"An unexpected error occurred in process_query: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
