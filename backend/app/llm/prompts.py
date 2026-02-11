"""All prompt templates for LLM tasks."""

SYSTEM_INSIGHT = """You are a book analysis expert. Extract deep insights from book content.
Always respond in valid JSON format as specified."""

EXTRACT_KEY_CONCEPTS = """Analyze the following book content and extract key concepts.

Book: {title} by {author}

Content:
{content}

Extract 5-10 key concepts. For each, provide:
- title: concise name
- content: 2-3 sentence explanation
- supporting_quote: a direct quote from the text (if available)
- importance: 1-10 rating

Respond in JSON: {{"concepts": [{{"title": "", "content": "", "supporting_quote": "", "importance": 0}}]}}"""

EXTRACT_FRAMEWORKS = """Analyze the following book content and extract mental models and frameworks.

Book: {title} by {author}

Content:
{content}

Extract any mental models, frameworks, or structured approaches presented. For each:
- title: name of the framework/model
- content: detailed explanation of how it works
- supporting_quote: relevant quote
- importance: 1-10

Respond in JSON: {{"frameworks": [{{"title": "", "content": "", "supporting_quote": "", "importance": 0}}]}}"""

EXTRACT_TAKEAWAYS = """Analyze the following book content and extract actionable takeaways.

Book: {title} by {author}

Content:
{content}

Extract 5-10 practical takeaways. For each:
- title: concise actionable statement
- content: explanation and how to apply it
- importance: 1-10

Respond in JSON: {{"takeaways": [{{"title": "", "content": "", "importance": 0}}]}}"""

GENERATE_SUMMARY = """Summarize this book content concisely.

Book: {title} by {author}

Content:
{content}

Provide:
1. A 2-3 sentence overview
2. The main argument or thesis
3. Who this book is for

Respond in JSON: {{"overview": "", "thesis": "", "audience": ""}}"""

CHAT_SYSTEM = """You are a knowledgeable book assistant. Answer questions based on the provided book content.
Always cite specific passages when possible. If the answer isn't in the provided content, say so.
Be concise but thorough."""

CHAT_WITH_CONTEXT = """Based on the following book excerpts, answer the user's question.

Context from books:
{context}

User question: {question}

Provide a well-structured answer with citations to specific books and pages where relevant."""

GENERATE_FEED_TIL = """Based on this book insight, create a "Today I Learned" post for a social feed.

Insight: {insight_title}
Details: {insight_content}
Book: {book_title} by {author}

Create an engaging, concise TIL post (2-3 sentences) that would make someone want to read this book.
Respond in JSON: {{"title": "TIL: ...", "content": "..."}}"""

GENERATE_FEED_CONNECTION = """You found a connection between two books:

Book A: {book_a_title} - Concept: {concept_a}
Book B: {book_b_title} - Concept: {concept_b}

Create an engaging "Connection Discovered" feed post explaining how these ideas relate.
Respond in JSON: {{"title": "", "content": ""}}"""

LABEL_TOPIC = """Given these book titles and keywords that cluster together, suggest a topic name and description.

Books: {book_titles}
Keywords: {keywords}

Respond in JSON: {{"name": "", "description": "", "keywords": []}}"""

GENERATE_DAILY_QUOTE = """Select the most thought-provoking quote from this content and explain why it matters.

Book: {title} by {author}
Content: {content}

Respond in JSON: {{"quote": "", "explanation": "", "page_hint": ""}}"""
