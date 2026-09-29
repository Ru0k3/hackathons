"""
Writer Agent - Uses Groq to format research into comprehensive reports
"""
import os
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class WriterAgent:
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.6
        )
    
    def create_report(self, research_data: Dict, status_callback=None) -> str:
        """Generate a formatted report from research data"""
        topic = research_data.get('topic', 'Unknown Topic')
        analysis = research_data.get('analysis', '')
        sources = research_data.get('sources', [])
        
        if status_callback:
            status_callback(f"📝 Writing report on: {topic}")
        
        # Prepare sources list
        sources_text = ""
        for idx, source in enumerate(sources, 1):
            sources_text += f"{idx}. {source.get('title', 'N/A')} - {source.get('url', 'N/A')}\n"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional report writer. Create a comprehensive, well-structured report that:
            1. Has a clear executive summary
            2. Organizes information logically with sections and subsections
            3. Presents data clearly with bullet points where appropriate
            4. Includes key findings and insights
            5. Has a conclusion section
            6. Lists all sources
            
            Use proper markdown formatting. Be professional and thorough."""),
            ("user", """Create a detailed report on: {topic}

Research Analysis:
{analysis}

Available Sources:
{sources_text}

Generate a complete, professional report:""")
        ])
        
        try:
            if status_callback:
                status_callback("🤖 Groq is generating the report...")
            
            chain = prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "analysis": analysis,
                "sources_text": sources_text
            })
            
            # Add sources section at the end
            report = response.content
            report += f"\n\n## References\n\n"
            for idx, source in enumerate(sources, 1):
                report += f"{idx}. [{source.get('title', 'N/A')}]({source.get('url', 'N/A')})\n"
            
            if status_callback:
                status_callback("✅ Report generation complete!")
            
            return report
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Report generation error: {str(e)}")
            return f"# Error Generating Report\n\n{str(e)}"
        

    
    def refine_report(self, report: str, feedback: str, status_callback=None) -> str:
        """Refine the report based on feedback"""
        if status_callback:
            status_callback(f"🔄 Refining report based on feedback...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional editor. Refine the report based on the feedback provided."),
            ("user", f"Original Report:\n{report}\n\nFeedback:\n{feedback}\n\nProvide the refined report:")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            
            if status_callback:
                status_callback(f"✅ Report refined successfully")
            
            return response.content
        except Exception as e:
            if status_callback:
                status_callback(f"❌ Refinement error: {str(e)}")
            return f"Error refining report: {str(e)}"
