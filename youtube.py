video_id = "pTFZFxd4hOI"

import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
from llama_index.core import Document
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
llm = Gemini(model="models/gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

def get_transcript(video_id: str) -> str:
    return " ".join([s["text"] for s in YouTubeTranscriptApi.get_transcript(video_id)])

transcript = get_transcript(video_id)
doc = Document(text=transcript)

def classify(transcript: str) -> str:
    res = llm.complete(
        f'''Classify the transcript strictly as one of the following:
    - educational
    - entertainment
        transcript:\n\n{transcript[:2000]}'''
    ).text.strip().lower()
    return res if res in ("educational", "entertainment") else "unknown"

classification = classify(doc.text)
# Define educational tools
tools_edu = [
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"Title for educational video:\n{txt}").text.strip(),
        name="GenerateTitle",
        description="Create a title for educational videos"
    ),
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"List key topics:\n{txt}").text.strip(),
        name="SummarizeTopics",
        description="Summarize topics covered"
    ),
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"List prerequisites:\n{txt}").text.strip(),
        name="FindPrerequisites",
        description="List prerequisites for understanding"
    ),
]

# Define entertainment tools
tools_ent = [
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"Identify genre:\n{txt}").text.strip(),
        name="IdentifyGenre",
        description="Identify the entertainment genre"
    ),
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"Suggest age group:\n{txt}").text.strip(),
        name="SuggestAgeGroup",
        description="Recommend suitable age group"
    ),
    FunctionTool.from_defaults(
        fn=lambda txt: llm.complete(f"150-word summary:\n{txt}").text.strip(),
        name="EntertainmentSummary",
        description="Provide a 150-word summary"
    ),
]

# Choose tools based on classification
if classification == "educational":
    agent_worker = FunctionCallingAgentWorker.from_tools(tools_edu, llm=llm, system_prompt="You are an educational assistant.")
elif classification == "entertainment":
    agent_worker = FunctionCallingAgentWorker.from_tools(tools_ent, llm=llm, system_prompt="You analyze entertainment videos.")
else:
    raise ValueError("Unknown video classification")

agent = AgentRunner(agent_worker)

# Execute each tool
print(f"Classification: {classification}\n")
tools_to_run = tools_edu if classification == "educational" else tools_ent

for tool in tools_to_run:
    print(f"\n {tool.metadata.name}:")
    result = tool(doc.text)
