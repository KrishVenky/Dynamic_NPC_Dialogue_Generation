# Refactoring Roadmap - Nick Valentine Dialogue System

## Current Status: ✅ Node.js/Express → 🔄 Python/Flask Migration

### Phase 1: Core Backend Migration (IN PROGRESS)
- [x] Create Flask server structure
- [x] Implement multi-agent system architecture
- [x] Port Gemini dialogue generator to Python
- [x] Create agent manager for seamless switching
- [ ] Add Hugging Face model integration
- [ ] Implement vector DB (ChromaDB) for context retrieval
- [ ] Create agent registry system

### Phase 2: Frontend Updates
- [x] Update API endpoints to match Flask
- [x] Add agent selection UI
- [x] Add model switching capability
- [ ] Add vector DB search visualization
- [ ] Add agentic pipeline visualization

### Phase 3: Advanced Features (FUTURE)
- [ ] Implement ChromaDB for semantic dialogue search
- [ ] Add Hugging Face models (facebook/opt-1.3b, gpt2-medium)
- [ ] Create multi-agent conversation pipeline
- [ ] Add RAG (Retrieval Augmented Generation) system
- [ ] Implement dialogue embeddings cache
- [ ] Add model performance metrics
- [ ] Create agent orchestration system

### Phase 4: Agentic Pipeline (FUTURE)
- [ ] Design agentic workflow system
- [ ] Implement agent-to-agent communication
- [ ] Create task delegation system
- [ ] Add context sharing between agents
- [ ] Implement agent memory system
- [ ] Create agent evaluation framework

### Phase 5: Optimization (FUTURE)
- [ ] Implement response caching
- [ ] Add model quantization for local HF models
- [ ] Optimize vector DB queries
- [ ] Add batch processing for embeddings
- [ ] Implement streaming responses

---

## Architecture Overview

### Multi-Agent System
```
┌─────────────────────────────────────────┐
│        Agent Manager                     │
│  ┌───────────────────────────────────┐  │
│  │  - Gemini Agent                   │  │
│  │  - HuggingFace Agent              │  │
│  │  - Local Model Agent              │  │
│  │  - Future: Custom Fine-tuned      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Context Retrieval (Vector DB)       │
│  - Semantic search                       │
│  - Dialogue embeddings                   │
│  - Contextual examples                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Prompt Engineering Module           │
│  - Character personality                 │
│  - Context injection                     │
│  - History management                    │
└─────────────────────────────────────────┘
```

### Agent Switching Flow
```
User selects Agent → Reset conversation → New agent takes over → Fresh context
```

---

## Tech Stack

### Backend (Python)
- **Flask**: Web server
- **google-generativeai**: Gemini API
- **transformers**: Hugging Face models
- **chromadb**: Vector database
- **sentence-transformers**: Embeddings
- **pandas**: CSV processing

### Frontend (JavaScript - No changes needed)
- Vanilla JS
- Fetch API for Flask endpoints
- Same UI/UX

---

## Notes
- Each agent maintains independent conversation history
- Agent switching = fresh start (as requested)
- Vector DB improves context retrieval across all agents
- Agentic pipeline allows future expansion for complex workflows
- All agents share the Nick Valentine personality profile

---

## Next Steps
1. ✅ Migrate to Flask
2. Test multi-agent switching
3. Integrate ChromaDB
4. Add HuggingFace models
5. Build agentic pipeline foundation
