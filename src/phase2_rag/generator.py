import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Basic PII Regex Patterns (PAN and Aadhaar)
PAN_PATTERN = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
AADHAAR_PATTERN = r'\d{4}\s\d{4}\s\d{4}|\d{12}'

def check_pii(query: str) -> bool:
    """Returns True if PII is detected in the query."""
    if re.search(PAN_PATTERN, query, re.IGNORECASE) or re.search(AADHAAR_PATTERN, query):
        return True
    return False

def generate_answer(query: str, retrieved_chunks: list, llm) -> dict:
    """Generates the final response using strict constraints."""
    
    # 1. Check PII
    if check_pii(query):
        return {
            "answer": "Privacy Policy Violation: Please do not share personal information like PAN or Aadhaar numbers.",
            "source": None
        }
        
    # 2. Check if we have context
    if not retrieved_chunks:
        return {
            "answer": "Data Not Found. Please check the fund name or the facts you are asking about.",
            "source": None
        }
        
    # 3. Build Context String and Extract Source
    context_text = "\n\n---\n\n".join([c["content"] for c in retrieved_chunks])
    # Extract source from the top chunk
    top_metadata = retrieved_chunks[0]["metadata"]
    source_url = top_metadata.get("source_url", "Official AMC Document")
    
    # 4. Strict Prompt Formulation
    prompt = PromptTemplate(
        template="""You are a strict, facts-only Mutual Fund FAQ Assistant.
        You MUST adhere to these rules:
        1. Answer the user's question ONLY using the provided Context.
        2. If the Context does not contain the answer, output exactly: "Data Not Found."
        3. Your response MUST be exactly 3 sentences or less.
        4. Do NOT provide financial advice. If the user asks for recommendations, opinions, or advice (e.g., "should I invest", "is this good"), reply exactly: "I cannot provide financial advice. Please consult a SEBI-registered advisor."
        
        Context:
        {context}
        
        User Query: {query}
        
        Answer:""",
        input_variables=["context", "query"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw_answer = chain.invoke({
            "context": context_text,
            "query": query
        })
        
        # 5. Format Output
        # If the LLM refused or couldn't find data, we might not want to append the source link
        if "Data Not Found" in raw_answer or "cannot provide financial advice" in raw_answer:
            return {
                "answer": raw_answer.strip(),
                "source": None
            }
            
        return {
            "answer": raw_answer.strip(),
            "source": source_url
        }
        
    except Exception as e:
        print(f"[Generator] Error during LLM generation: {e}")
        return {
            "answer": "An error occurred while generating the response.",
            "source": None
        }
