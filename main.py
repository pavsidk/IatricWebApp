"""import os
import json
import base64
from groq import Groq
import websockets
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.websockets import WebSocketDisconnect
import asyncio
import tempfile
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import anthropic
import spacy
from typing import List
import google.generativeai as genai
from pymed import PubMed
from verify import get_results, get_verification_info, generate_validation
from opinion_query import get_doctors
from meeting_summary import summarize_transcript

TRANSCRIPTS=[]
nlp = spacy.load("en_core_web_sm")
pubmed = PubMed(tool="MyTool", email="disispavank@gmail.come")

def get_claims(transcript: str) -> List[str]:
    LINK_PHRASES = [
        "is a sign of", "is related to", "may indicate", "could suggest",
        "consistent with", "might be due to", "is due to", "is because of"
    ]
    doc = nlp(transcript.lower())
    claims = []

    for sent in doc.sents:
        for phrase in LINK_PHRASES:
            if phrase in sent.text:
                claims.append(sent.text.strip())
                break

    return claims


def transcribe_audio(audio_chunk: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        temp_audio.write(audio_chunk)
        temp_audio.flush()

        with open(temp_audio.name, "rb") as f:
            translation = client.audio.translations.create(
                file=(temp_audio.name, f),
                model="whisper-large-v3",
                prompt="use clinical terminology and correct spelling for conditions, medications, and procedures in a medical context",
                response_format="json",
                temperature=0.0 
            )

        print(translation.text)
        TRANSCRIPTS.append(translation.text)
        return translation.text
"""