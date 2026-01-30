from Agents import ObserverAgent, InterviewerAgent,SummaryAgent
from Logger import Logger
import langchain
langchain.debug = False
langchain.llm_cache = None
import argparse
import json

parser = argparse.ArgumentParser(description="Multi-Agent Interview CLI")
parser.add_argument("--input_json", type=str, required=True, help="Путь к JSON с данными кандидата")
parser.add_argument("--api_key", type=str, required=True, help="API ключ для GigaChat/OpenAI/LLM")
args = parser.parse_args()
api_key = args.api_key

with open(args.input_json, "r", encoding="utf-8") as f:
    data = json.load(f)

context = {
    "candidate_name": "Масленикова Полина Григорьевна",
    "position": data["position"],
    "grade": data["grade"],
    "experience": data["experience"],
    "history": [],
    "last_user_message": "",
    "last_agent_message": "",
    "finished": False
}

logger = Logger(context["candidate_name"])
observer = ObserverAgent(api_key)
interviewer = InterviewerAgent(api_key)
summary_agent = SummaryAgent(api_key)

turn_id = 1

while not context["finished"]:
    if turn_id == 1:
        observer_thoughts = "Начало интервью. Поздоровайся и попроси рассказать о себе"
        internal_combined = observer_thoughts

    agent_message = interviewer.ask_question(context, internal_combined)
    print(agent_message)

    user_message = input("> ")
    context["last_user_message"] = user_message
    context["history"].append({
        "agent": agent_message,
        "user": user_message
    })
    if user_message.lower().startswith("стоп"):
        context["finished"] = True
        break

    observer_thoughts = observer.analyze(context)
    interviewer_thoughts = interviewer.reflect(context, observer_thoughts)
    internal_combined = f"[Observer]: {observer_thoughts}+\n [Interviewer]: {interviewer_thoughts}+\n"

    logger.record_turn(
        turn_id=turn_id,
        agent_visible_message=agent_message,
        user_message=user_message,
        internal_thoughts=internal_combined
    )

    turn_id += 1

    if user_message.lower().startswith("стоп"):
        context["finished"] = True
        break

final_summary = summary_agent.summarize(context)
logger.set_final_feedback(final_summary)
logger.save_to_file()
print(final_summary)
logger.record_turn(
    turn_id=turn_id,
    agent_visible_message=agent_message,
    user_message=user_message,
    internal_thoughts=f'''['SummaryAgent']:{final_summary}\n''')
