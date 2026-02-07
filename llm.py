"""
LLM integration using Groq for fast, efficient inference.
"""

import os
from typing import Optional
from groq import Groq


class GroqLLM:
    """Wrapper for Groq LLM API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"):
        """
        Initialize Groq LLM client.
        
        Args:
            api_key: Groq API key (if None, reads from GROQ_API_KEY env var)
            model: Model to use (default: mixtral-8x7b-32768)
        """
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not provided and not found in environment. "
                "Set it via parameter or GROQ_API_KEY environment variable."
            )
        
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using Groq.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in the response
            temperature: Temperature for sampling (0.0 - 2.0)
        
        Returns:
            Generated text response
        """
        message = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return message.choices[0].message.content
    
    def generate_answer(
        self,
        question: str,
        context: str,
        max_tokens: int = 400,
    ) -> str:
        """
        Generate an answer based on question and context from podcast.
        
        Args:
            question: The user's question
            context: Relevant transcript segments for context
            max_tokens: Maximum tokens in the response
        
        Returns:
            Generated answer
        """
        prompt = f"""You are a helpful podcast assistant. Based on the provided transcript segments, 
answer the user's question concisely and accurately. Keep your answer brief (2-3 sentences max).

Question: {question}

Relevant transcript excerpts:
{context}

Answer:"""
        
        return self.generate(prompt, max_tokens=max_tokens)
