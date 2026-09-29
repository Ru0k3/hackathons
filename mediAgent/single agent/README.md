# Multi-Agent Research System

A real-time multi-agent system with specialized agents for research and report writing using Gemini and Groq.

## 🎯 Features

- **Agent A (Researcher)**: Uses **Gemini Pro** to search the web via Tavily and analyze sources in real-time
- **Agent B (Writer)**: Uses **Groq (Mixtral 8x7B)** to format research into comprehensive, professional reports
- **Real-time Activity Monitor**: See exactly what each agent is doing as it happens
- **Live Progress Updates**: Track research phases, source analysis, and report generation
- **Source Attribution**: All research includes full source links and citations
- **Interactive UI**: Clean Streamlit interface with multiple views

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```powershell
.\setup.ps1
```

### Option 2: Manual Setup

1. Install UV (if not already installed):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

2. Create virtual environment and install dependencies:
```powershell
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get API keys from:
- **Gemini**: https://makersuite.google.com/app/apikey
- **Groq**: https://console.groq.com/
- **Tavily**: https://tavily.com/

4. Run the app:
```powershell
streamlit run app.py
```

## 📖 How It Works

1. **User Input**: Enter a research topic in the Streamlit interface
2. **Agent A (Researcher)**: 
   - Searches the web using Tavily API
   - Finds 5 high-quality sources
   - Uses Gemini Pro to analyze and extract key insights
3. **Agent B (Writer)**:
   - Takes the research analysis
   - Uses Groq's Mixtral model to generate a professional report
   - Structures information with sections, bullet points, and citations
4. **Real-time Updates**: Watch the activity monitor to see each step

## 🎨 Interface Features

- **Activity Monitor**: Real-time log of what agents are doing
- **Progress Bar**: Visual tracking of research phases
- **Multiple Views**: 
  - Final Report (formatted markdown)
  - Raw Research Data (detailed analysis)
  - Sources (all links and content previews)
- **Download**: Export reports as markdown files

## 📁 Project Structure

```
single agent/
├── app.py                  # Streamlit frontend
├── researcher_agent.py     # Agent A - Gemini-powered researcher
├── writer_agent.py         # Agent B - Groq-powered writer
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── setup.ps1              # Automated setup script
└── README.md              # Documentation
```

## 🔧 Technologies

- **LangChain**: Agent orchestration and LLM integration
- **Gemini Pro**: Research and analysis
- **Groq (Mixtral 8x7B)**: Fast report generation
- **Tavily**: Web search API
- **Streamlit**: Interactive UI
- **UV**: Fast Python package management
