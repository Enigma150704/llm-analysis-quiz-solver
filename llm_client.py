"""
LLM client for solving quiz questions using OpenAI API
"""
from openai import OpenAI, AsyncOpenAI
from typing import Optional, Dict, Any, List
import logging
import asyncio
from config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
    
    async def solve_question(
        self,
        question_text: str,
        context: Optional[Dict[str, Any]] = None,
        model: str = "gpt-4-turbo-preview"
    ) -> str:
        """
        Solve a quiz question using LLM
        
        Args:
            question_text: The question text to solve
            context: Additional context (data, files, etc.)
            model: Model to use for solving
            
        Returns:
            The answer as a string
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question_text, context)
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent answers
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer: {answer[:100]}...")
            return answer
        except Exception as e:
            logger.error(f"Error solving question with LLM: {e}")
            raise
    
    async def analyze_data(
        self,
        data_description: str,
        task_description: str,
        data_sample: Optional[str] = None,
        model: str = "gpt-4-turbo-preview"
    ) -> Any:
        """
        Analyze data based on task description
        
        Args:
            data_description: Description of the data
            task_description: What to do with the data
            data_sample: Sample of the data (if large, provide summary)
            model: Model to use
            
        Returns:
            Analysis result
        """
        prompt = f"""You are a data analyst. Given the following task:

Task: {task_description}

Data Description: {data_description}
"""
        if data_sample:
            prompt += f"\nData Sample:\n{data_sample}\n"
        
        prompt += "\nProvide a clear, concise answer. If the answer is a number, provide only the number. If it's text, provide the text directly."
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise data analyst. Provide accurate, concise answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            raise
    
    async def generate_visualization_code(
        self,
        data_description: str,
        visualization_requirements: str,
        model: str = "gpt-4-turbo-preview"
    ) -> str:
        """
        Generate Python code for data visualization
        
        Args:
            data_description: Description of the data
            visualization_requirements: What visualization is needed
            model: Model to use
            
        Returns:
            Python code for generating the visualization
        """
        prompt = f"""Generate Python code to create a visualization.

Data: {data_description}
Requirements: {visualization_requirements}

Return only the Python code, no explanations. Use matplotlib, seaborn, or plotly.
The code should save the plot as an image file."""
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Return only valid Python code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating visualization code: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt"""
        base_prompt = Config.SYSTEM_PROMPT or "You are a helpful assistant that solves data-related quiz questions accurately."
        return base_prompt
    
    def _build_user_prompt(self, question_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the user prompt with question and context"""
        prompt = f"Solve the following quiz question:\n\n{question_text}\n\n"
        
        if context:
            if 'data' in context:
                prompt += f"Data:\n{context['data']}\n\n"
            if 'instructions' in context:
                prompt += f"Additional instructions:\n{context['instructions']}\n\n"
        
        prompt += "Provide a clear, direct answer. If it's a number, provide only the number. If it's text, provide the text. Be precise and accurate."
        
        return prompt
    
    async def extract_answer_from_response(
        self,
        response: str,
        expected_type: Optional[str] = None
    ) -> Any:
        """
        Extract and format answer from LLM response
        
        Args:
            response: LLM response text
            expected_type: Expected type ('number', 'string', 'boolean', etc.)
            
        Returns:
            Formatted answer
        """
        response = response.strip()
        
        if expected_type == 'number':
            # Try to extract number
            import re
            numbers = re.findall(r'-?\d+\.?\d*', response)
            if numbers:
                try:
                    if '.' in numbers[0]:
                        return float(numbers[0])
                    return int(numbers[0])
                except ValueError:
                    pass
        
        if expected_type == 'boolean':
            response_lower = response.lower()
            if 'true' in response_lower or 'yes' in response_lower:
                return True
            elif 'false' in response_lower or 'no' in response_lower:
                return False
        
        return response

