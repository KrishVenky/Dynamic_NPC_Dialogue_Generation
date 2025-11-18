"""
Flask Server for Nick Valentine Dialogue Generator
Multi-agent dialogue system with seamless agent switching
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

from agents.agent_manager import AgentManager
from agents.gemini_agent import GeminiAgent
from agents.huggingface_agent import HuggingFaceAgent

# Load environment variables
load_dotenv()

# Try to import vector store (optional dependency)
try:
    from vector_store import get_vector_store
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    print("⚠️ Vector store not available (sentence-transformers not installed)")

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Initialize Agent Manager
agent_manager = AgentManager()

# Initialize vector store (optional)
vector_store = None

# Initialize agents
def initialize_agents():
    """Initialize all available agents"""
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'nick_valentine_dialogue.csv')
    
    # Initialize Vector Store (if available)
    global vector_store
    if VECTOR_STORE_AVAILABLE:
        try:
            print("🔄 Loading ChromaDB...")
            db_path = os.path.join(os.path.dirname(__file__), 'chroma_db_nick_valentine')
            vector_store = get_vector_store(db_path)
            print("✅ ChromaDB ready!")
        except Exception as e:
            print(f"⚠️ ChromaDB failed: {e}")
    
    # Gemini Agent - Simple workflow, no vector DB
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            gemini_agent = GeminiAgent(
                api_key=gemini_api_key,
                model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            )
            gemini_agent.initialize()
            agent_manager.register_agent('gemini', gemini_agent)
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini agent: {e}")
    else:
        print("⚠️  GEMINI_API_KEY not found in .env")
    
    # HuggingFace Agent - Uses vector DB for better context
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        try:
            print("🔄 Initializing HuggingFace agent (TinyLlama with vector DB)...")
            hf_agent = HuggingFaceAgent(
                csv_path=csv_path,
                model_name=os.getenv('HF_MODEL', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0')
            )
            if hf_agent.initialize():
                agent_manager.register_agent('huggingface', hf_agent)
        except Exception as e:
            print(f"⚠️  Failed to initialize HuggingFace agent: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  HF_TOKEN not found in .env")


# Routes

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('public', 'index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate dialogue response using active agent"""
    data = request.json
    
    user_input = data.get('userInput', '').strip()
    if not user_input:
        return jsonify({'error': 'userInput is required'}), 400
    
    context = data.get('context', 'casual')
    emotion = data.get('emotion')
    include_examples = data.get('includeExamples', True)
    
    try:
        response = agent_manager.generate_response(
            user_input=user_input,
            context=context,
            emotion=emotion,
            include_examples=include_examples
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all available agents"""
    agents = agent_manager.list_agents()
    return jsonify({'agents': agents})


@app.route('/api/agents/switch', methods=['POST'])
def switch_agent():
    """Switch to a different agent"""
    data = request.json
    agent_id = data.get('agentId')
    
    if not agent_id:
        return jsonify({'error': 'agentId is required'}), 400
    
    result = agent_manager.switch_agent(agent_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404


@app.route('/api/agents/active', methods=['GET'])
def get_active_agent():
    """Get information about the active agent"""
    info = agent_manager.get_agent_info()
    return jsonify(info)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history from active agent"""
    history = agent_manager.get_conversation_history()
    return jsonify({'history': history})


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation for active agent"""
    result = agent_manager.reset_conversation()
    return jsonify(result)


@app.route('/api/export', methods=['GET'])
def export():
    """Export conversation history"""
    history = agent_manager.get_conversation_history()
    agent = agent_manager.get_active_agent()
    
    export_data = {
        'agent': agent.name if agent else 'Unknown',
        'model': agent.model_name if agent else 'Unknown',
        'conversation': history
    }
    
    return jsonify(export_data)


@app.route('/api/cost-estimate', methods=['GET'])
def cost_estimate():
    """Get cost estimate for number of exchanges"""
    exchanges = int(request.args.get('exchanges', 100))
    
    # Rough estimates for Gemini 1.5 Flash
    avg_input_tokens = 500
    avg_output_tokens = 100
    
    total_input_tokens = exchanges * avg_input_tokens
    total_output_tokens = exchanges * avg_output_tokens
    
    # Gemini 1.5 Flash pricing (FREE tier has generous limits)
    input_cost = (total_input_tokens / 1_000_000) * 0.075
    output_cost = (total_output_tokens / 1_000_000) * 0.30
    total_cost = input_cost + output_cost
    
    return jsonify({
        'exchanges': exchanges,
        'estimatedInputTokens': total_input_tokens,
        'estimatedOutputTokens': total_output_tokens,
        'estimatedCost': f'${total_cost:.4f}',
        'note': 'Gemini 1.5 Flash has a FREE tier with generous limits!'
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'agents_count': len(agent_manager.agents),
        'active_agent': agent_manager.active_agent,
    })


if __name__ == '__main__':
    print("\n🎮 Nick Valentine Dialogue Generator (Python/Flask)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Initialize agents
    initialize_agents()
    
    if not agent_manager.agents:
        print("⚠️  No agents initialized! Please configure API keys in .env")
        exit(1)
    
    print(f"✓ Active agent: {agent_manager.active_agent}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    port = int(os.getenv('PORT', 3000))
    print(f"🌐 Server running at http://localhost:{port}")
    print(f"📊 API endpoints:")
    print(f"   POST   /api/generate        - Generate dialogue")
    print(f"   GET    /api/agents          - List all agents")
    print(f"   POST   /api/agents/switch   - Switch active agent")
    print(f"   GET    /api/agents/active   - Get active agent info")
    print(f"   GET    /api/history         - Get conversation history")
    print(f"   POST   /api/reset           - Reset conversation")
    print(f"   GET    /api/export          - Export conversation")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
