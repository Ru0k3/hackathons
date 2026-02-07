"""
Researcher Agent - Uses Gemini to search the web and gather raw data
"""
import os
from typing import List, Dict, Callable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

class ResearcherAgent:
    def __init__(self, gemini_api_key: str, tavily_api_key: str, status_callback: Callable[[str], None] = None):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_api_key,
            temperature=0.7
        )
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.status_callback = status_callback
        
    def search_web(self, query: str, status_callback=None) -> List[Dict]:
        """Search the web using Tavily API"""
        if status_callback:
            status_callback(f"🔍 Searching web for: {query}")
        
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            results = response.get('results', [])
            if status_callback:
                status_callback(f"✅ Found {len(results)} relevant sources")
            
            return results
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Search error: {str(e)}")
            return []
    
    def analyze_sources(self, sources: List[Dict], topic: str, status_callback=None) -> str:
        """Analyze search results and extract key information using Gemini"""
        if status_callback:
            status_callback(f"🧠 Analyzing {len(sources)} sources with Gemini...")
        
        # Prepare context from sources
        context = ""
        for idx, source in enumerate(sources, 1):
            context += f"\n\nSource {idx}:\n"
            context += f"Title: {source.get('title', 'N/A')}\n"
            context += f"URL: {source.get('url', 'N/A')}\n"
            context += f"Content: {source.get('content', 'N/A')}\n"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst. Analyze the provided web sources and extract:
            1. Key facts and data points
            2. Important insights and trends
            3. Relevant statistics or findings
            4. Main themes and concepts
            
            Organize the information clearly and cite which source each piece of information comes from."""),
            ("user", f"""Analyze these sources about: {topic}

{context}

Provide a comprehensive analysis of the key information found:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            
            if status_callback:
                status_callback("✅ Analysis complete")
            
            return response.content
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Analysis error: {str(e)}")
            return f"Error during analysis: {str(e)}"
    
    def research(self, topic: str, status_callback=None) -> Dict:
        """Main research method - coordinates web search and analysis"""
        if status_callback:
            status_callback(f"🚀 Starting research on: {topic}")
        
        # Step 1: Search the web
        sources = self.search_web(topic, status_callback)
        
        if not sources:
            return {
                'topic': topic,
                'sources': [],
                'analysis': 'No sources found for this topic.',
                'success': False
            }
        
        # Step 2: Analyze the sources
        analysis = self.analyze_sources(sources, topic, status_callback)
        
        if status_callback:
            status_callback("✅ Research complete!")
        
        return {
            'topic': topic,
            'sources': sources,
            'analysis': analysis,
            'success': True
        }

