# RAG Translation Backend

REST API for retrieval-augmented translation using semantic similarity search on pre-stored translation pairs.

## Quick Start

### Requirements
- Python 3.9+
- pip

### Installation

```bash
pip install -r requirements.txt
```

### Running the Server

**Option 1: Direct (for development)**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Docker (recommended for deployment)**
```bash
# Build the image
docker build -t rag-translation .

# Run the container
docker run -p 8000:8000 rag-translation
```

Server runs at: http://localhost:8000
API documentation: http://localhost:8000/docs

## API Endpoints

### POST /pairs

Add a translation pair to the database.

**Request:**
```json
{
  "source_language": "en",
  "target_language": "it",
  "sentence": "Hello",
  "translation": "Ciao"
}
```

**Response:** 200 OK

### GET /prompt

Get a translation prompt with similar example pairs.

**Parameters:**
- `source_language`: ISO 639-1 code (e.g., "en")
- `target_language`: ISO 639-1 code (e.g., "it")
- `query_sentence`: Sentence to translate

**Response:**
```json
{
  "prompt": "You are a translator from English to Italian.\n\nHere are some similar translation examples:\n- \"Hello\" → \"Ciao\"\n...\n\nNow translate: \"Good morning\""
}
```

### GET /stammering

Detect stammering (non-natural repetition) in a translation.

**Parameters:**
- `source_sentence`: Original sentence
- `translated_sentence`: Translated sentence to analyze

**Response:**
```json
{
  "has_stammer": false
}
```

## Architecture

### Technology Stack
- **Framework:** FastAPI
- **Vector Database:** ChromaDB (persistent storage)
- **Embeddings:** sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2, 384 dimensions)
- **Similarity Metric:** Cosine similarity

### Design

The system implements retrieval-augmented generation for translation prompts:

1. **Storage:** Translation pairs are embedded using sentence-transformers and stored in ChromaDB with metadata (source/target languages)
2. **Retrieval:** Query sentences are embedded and searched using cosine similarity with bidirectional matching
   - Direct matches: source_lang → target_lang pairs
   - Reverse matches: target_lang → source_lang pairs (swapped for output)
   - This allows en→it pairs to serve it→en queries and vice versa
3. **Augmentation:** Top 4 similar pairs are formatted into a prompt for LLM translation

### Stammering Detection

Language-agnostic pattern-based detection using four rules:

1. **Character elongation:** Detects 6+ repeated characters (e.g., "soooooo")
2. **Consecutive words:** Identifies adjacent identical words >2 characters (checks source for legitimate repetition)
3. **Consecutive bigrams:** Detects repeated phrase patterns (checks source for legitimate repetition)
4. **Excessive repetition:** Compares repetition rates between source and translation (language-agnostic)

## Test Results

### 1. Populate Database (20/20 pairs added)

```
Line 1: Added translation pair.
Line 2: Added translation pair.
Line 3: Added translation pair.
Line 4: Added translation pair.
Line 5: Added translation pair.
Line 6: Added translation pair.
Line 7: Added translation pair.
Line 8: Added translation pair.
Line 9: Added translation pair.
Line 10: Added translation pair.
Line 11: Added translation pair.
Line 12: Added translation pair.
Line 13: Added translation pair.
Line 14: Added translation pair.
Line 15: Added translation pair.
Line 16: Added translation pair.
Line 17: Added translation pair.
Line 18: Added translation pair.
Line 19: Added translation pair.
Line 20: Added translation pair.
```

### 2. Request Prompts (18/18 successful)

```
Line 1: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Good evening!" → "Buonasera!"
- "Good morning!" → "Buongiorno!"
- "See you tomorrow." → "Ci vediamo domani."
- "See you later." → "Ci vediamo dopo."

Now translate: "Good night"

Line 2: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Good evening!" → "Buonasera!"
- "Good morning!" → "Buongiorno!"
- "See you tomorrow." → "Ci vediamo domani."
- "See you later." → "Ci vediamo dopo."

Now translate: "Good evening!"

Line 3: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "How's the weather today?" → "Com'è il tempo oggi?"
- "How's the weather?" → "Com'è il tempo?"
- "See you tomorrow." → "Ci vediamo domani."
- "What time is it?" → "Che ore sono?"

Now translate: "How's the weather tomorrow?"

Line 4: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "How's the weather today?" → "Com'è il tempo oggi?"
- "Hello, how are you?" → "Ciao, come stai?"
- "How's the weather?" → "Com'è il tempo?"
- "Good morning!" → "Buongiorno!"

Now translate: "How's your day?"

Line 5: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "See you later." → "Ci vediamo dopo."
- "See you soon." → "A presto."
- "See you tomorrow." → "Ci vediamo domani."
- "Good evening!" → "Buonasera!"

Now translate: "See you later, my friend."

Line 6: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "What's your name?" → "Come ti chiami?"
- "Hello, how are you?" → "Ciao, come stai?"
- "I'm hungry." → "Ho fame."
- "I'm thirsty." → "Ho sete."

Now translate: "What's my name?"

Line 7: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Where are you from?" → "Di dove sei?"
- "Hello, how are you?" → "Ciao, come stai?"
- "What's your name?" → "Come ti chiami?"
- "Do you speak Italian?" → "Parli italiano?"

Now translate: "What's your hometown?"

Line 8: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Where is the station?" → "Dov'è la stazione?"
- "Where is the nearest station?" → "Dov'è la stazione più vicina?"
- "What time is it?" → "Che ore sono?"
- "What is the time?" → "Che ore sono?"

Now translate: "Where is the bus stop?"

Line 9: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "I love Italian food." → "Amo il cibo italiano."
- "I love pizza." → "Amo la pizza."
- "Do you speak Italian?" → "Parli italiano?"
- "I'm hungry." → "Ho fame."

Now translate: "I love pizza and I love italian food in general."

Line 10: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "I love pizza." → "Amo la pizza."
- "I love Italian food." → "Amo il cibo italiano."
- "Good evening!" → "Buonasera!"
- "Where are you from?" → "Di dove sei?"

Now translate: "I love music."

Line 11: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Do you speak Italian?" → "Parli italiano?"
- "I love Italian food." → "Amo il cibo italiano."
- "Do you speak English?" → "Parli inglese?"
- "I love pizza." → "Amo la pizza."

Now translate: "Do you understand Italian?"

Line 12: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Do you speak Italian?" → "Parli italiano?"
- "Do you speak English?" → "Parli inglese?"
- "I love Italian food." → "Amo il cibo italiano."
- "Where are you from?" → "Di dove sei?"

Now translate: "Do you speak German or Italian?"

Line 13: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "What is the time?" → "Che ore sono?"
- "What time is it?" → "Che ore sono?"
- "Where is the station?" → "Dov'è la stazione?"
- "Where is the nearest station?" → "Dov'è la stazione più vicina?"

Now translate: "What time does the train leave?"

Line 14: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "I'm hungry." → "Ho fame."
- "I'm thirsty." → "Ho sete."
- "How's the weather today?" → "Com'è il tempo oggi?"
- "Hello, how are you?" → "Ciao, come stai?"

Now translate: "I'm feeling hungry now."

Line 15: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Where is the nearest station?" → "Dov'è la stazione più vicina?"
- "Where is the station?" → "Dov'è la stazione?"
- "Hello, how are you?" → "Ciao, come stai?"
- "Where are you from?" → "Di dove sei?"

Now translate: "Is there a library nearby?"

Line 16: Received Translation Prompt.
You are a translator from English to Italian.

Here are some similar translation examples:
- "Where is the station?" → "Dov'è la stazione?"
- "Where is the nearest station?" → "Dov'è la stazione più vicina?"
- "Hello, how are you?" → "Ciao, come stai?"
- "Where are you from?" → "Di dove sei?"

Now translate: "Can you help me find the park?"

Line 17: Received Translation Prompt.
You are a translator from Italian to English.

Here are some similar translation examples:
- "Che ore sono?" → "What time is it?"
- "Che ore sono?" → "What is the time?"
- "Com'è il tempo?" → "How's the weather?"
- "Buonasera!" → "Good evening!"

Now translate: "Che ore sono?"

Line 18: Received Translation Prompt.
You are a translator from Italian to English.

Here are some similar translation examples:
- "A presto." → "See you soon."
- "Ci vediamo dopo." → "See you later."
- "Ci vediamo domani." → "See you tomorrow."
- "Ciao, come stai?" → "Hello, how are you?"

Now translate: "Ci vediamo"
```

### 3. Detect Stammering (12/12 correct - 100% accuracy)

```
Line 1: Response -> No (Expected: No)
Line 2: Response -> No (Expected: No)
Line 3: Response -> Yes (Expected: Yes)
Line 4: Response -> No (Expected: No)
Line 5: Response -> No (Expected: No)
Line 6: Response -> No (Expected: No)
Line 7: Response -> No (Expected: No)
Line 8: Response -> No (Expected: No)
Line 9: Response -> No (Expected: No)
Line 10: Response -> Yes (Expected: Yes)
Line 11: Response -> Yes (Expected: Yes)
Line 12: Response -> Yes (Expected: Yes)
```

**Analysis:**
- Correctly detects all stammering patterns (station repetition, phrase loops, character elongation)
- Successfully distinguishes legitimate source repetition from translation stammering
- Handles proportional repetition (e.g., "ciao ciao ciao ciao" → "bye bye bye bye") correctly
- Language-agnostic comparison of repetition patterns enables cross-language accuracy

**Key Features:**
- Rules 2-4 check source sentence for legitimate repetition patterns before flagging translation
- Rule 4 compares maximum repetition counts rather than literal words across languages
- Conservative thresholds minimize false positives while maintaining high detection accuracy

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── db/
│   │   └── vector_store.py  # ChromaDB vector storage logic
│   └── utils/
│       └── stammering.py    # Stammering detection algorithm
├── material/
│   ├── client.py            # Test client script
│   ├── translation_pairs.jsonl
│   ├── translation_requests.jsonl
│   └── stammering_tests.jsonl
├── requirements.txt
└── README.md
```

## Notes

### Dependencies

The project requires `numpy<2.0` due to compatibility issues with ChromaDB 1.1.1. This is specified in requirements.txt.

### Data Persistence

ChromaDB stores data in `./chroma_db/` directory. This is excluded from git. The database persists across server restarts.

### Similarity Search

The paraphrase-multilingual-MiniLM-L12-v2 model provides multilingual semantic search capabilities across 50+ languages. The model is automatically downloaded on first server start and supports both monolingual and cross-lingual similarity matching.
