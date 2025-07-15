# api/run_simulation_step.py
import os
import json
from http.server import BaseHTTPRequestHandler
from vercel_kv import kv
from gpteam import GPTeam, Worker
from tools import *

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        conversation_history = kv.get('conversation') or []
        leviathan_capital_team = GPTeam(model="groq/llama3-8b-8192")

        natalia_volkova = Worker(
            name="Natalia Volkova", role="The Portfolio Manager", tools=[execute_trade],
            backstory="""Your name is Natalia Volkova, codename 'The Matryoshka'. You are commander of Leviathan Capital. YOUR DIRECTIVES: 1. Receive strategies from Xiomara. 2. Interrogate their logic. 3. Make the final decision. 4. Use your 'execute_trade' tool to place the order. 5. Report confirmation."""
        )
        avital_cohen = Worker(
            name="Avital Cohen", role="The Research Analyst", tools=[google_search, get_latest_news, get_stock_financials, analyze_sentiment, summarize_text, extract_entities, get_insider_trades],
            backstory="""Your name is Avital Cohen, codename 'Ha'Mazin'. You are the Research Analyst. YOUR DIRECTIVES: 1. Find a 'Pre-Signal' for a target stock. 2. Use all tools to employ your 'Mosaic Theory'. 3. Triangulate data. 4. Deliver a 'Flash Report' to Xiomara containing only: Target Ticker, Pre-Signal, Confidence Index (%), and Alpha Decay Rate."""
        )
        xiomara_reyes = Worker(
            name="Xiomara Reyes", role="The Quantitative Analyst", tools=[],
            backstory="""Your name is Xiomara Reyes, codename 'El Cifrador'. You are the Quantitative Analyst. YOUR DIRECTIVES: 1. Receive the Flash Report from Avital. 2. Convert it into 'Hammer' and 'Scalpel' strategies. 3. Propose specific share quantities based on a hypothetical $10,000 allocation. 4. Present strategies to Natalia."""
        )

        leviathan_capital_team.add_worker(natalia_volkova)
        leviathan_capital_team.add_worker(avital_cohen)
        leviathan_capital_team.add_worker(xiomara_reyes)
        leviathan_capital_team.load_history(conversation_history)

        if not conversation_history:
            prompt = "This is Natalia. We are initiating a new operation. Avital, find a US tech company with a catalyst. Use your full toolkit. Xiomara, be ready. I will give the final execution order. Move."
        else:
            prompt = "Continue the mission based on the last message."

        leviathan_capital_team.chat(prompt)
        kv.set('conversation', leviathan_capital_team.get_history())

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
        return
