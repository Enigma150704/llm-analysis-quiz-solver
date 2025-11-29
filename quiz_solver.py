"""
Core quiz solving logic that orchestrates browser, LLM, and data processing
"""
import asyncio
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import base64
import pandas as pd

from browser import BrowserManager
from llm_client import LLMClient
from data_processor import DataProcessor
from config import Config

logger = logging.getLogger(__name__)


class QuizSolver:
    """Main quiz solver that handles the complete quiz-solving workflow"""
    
    def __init__(self, email: str, secret: str):
        self.email = email
        self.secret = secret
        self.browser = BrowserManager()
        self.llm = LLMClient()
        self.data_processor = DataProcessor()
        self.start_time: Optional[datetime] = None
        self.max_time = timedelta(seconds=Config.MAX_QUIZ_TIME_SECONDS)
    
    async def solve_quiz(self, initial_url: str) -> Dict[str, Any]:
        """
        Solve a quiz starting from the initial URL
        
        Args:
            initial_url: Starting quiz URL
            
        Returns:
            Dictionary with solution results
        """
        self.start_time = datetime.now()
        current_url = initial_url
        results = []
        
        try:
            await self.browser.start()
            
            while current_url:
                # Check time limit
                if datetime.now() - self.start_time > self.max_time:
                    logger.warning("Time limit exceeded")
                    break
                
                logger.info(f"Solving quiz at: {current_url}")
                
                # Solve current quiz
                result = await self._solve_single_quiz(current_url)
                results.append(result)
                
                if result.get('correct'):
                    # Get next URL if available
                    current_url = result.get('next_url')
                    if not current_url:
                        logger.info("Quiz completed - no more URLs")
                        break
                else:
                    # If wrong, we can retry (handled in _solve_single_quiz)
                    # Or move to next URL if provided
                    next_url = result.get('next_url')
                    if next_url:
                        current_url = next_url
                    else:
                        # Retry current quiz
                        break
            
            return {
                'success': True,
                'results': results,
                'total_time': (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'results': results
            }
        finally:
            await self.browser.close()
    
    async def _solve_single_quiz(self, url: str) -> Dict[str, Any]:
        """
        Solve a single quiz question
        
        Args:
            url: Quiz URL
            
        Returns:
            Result dictionary with answer and correctness
        """
        try:
            # Navigate to quiz page
            html_content = await self.browser.navigate(url)
            text_content = await self.browser.extract_text(url)
            
            # Extract quiz question and instructions
            question_info = self._extract_question_info(text_content, html_content)
            logger.info(f"Question type: {question_info.get('type', 'unknown')}")
            
            # Solve the question
            answer = await self._solve_question(question_info)
            
            # Submit answer
            submit_url = question_info.get('submit_url')
            if not submit_url:
                # Try to extract from HTML
                submit_url = self._extract_submit_url(html_content)
            
            if submit_url:
                result = await self._submit_answer(submit_url, url, answer)
                return result
            else:
                logger.warning("No submit URL found")
                return {
                    'url': url,
                    'answer': answer,
                    'correct': None,
                    'error': 'No submit URL found'
                }
        except Exception as e:
            logger.error(f"Error solving single quiz: {e}", exc_info=True)
            return {
                'url': url,
                'error': str(e),
                'correct': False
            }
    
    def _extract_question_info(self, text_content: str, html_content: str) -> Dict[str, Any]:
        """
        Extract question information from quiz page
        
        Args:
            text_content: Visible text from page
            html_content: Full HTML content
            
        Returns:
            Dictionary with question details
        """
        info = {
            'text': text_content,
            'html': html_content,
            'type': 'general',
            'submit_url': None,
            'data_urls': []
        }
        
        # Extract submit URL from text/HTML
        submit_url = self._extract_submit_url(html_content)
        if submit_url:
            info['submit_url'] = submit_url
        
        # Extract data URLs (files, APIs, etc.)
        url_pattern = r'https?://[^\s<>"\'\)]+'
        urls = re.findall(url_pattern, text_content)
        info['data_urls'] = urls
        
        # Determine question type
        text_lower = text_content.lower()
        
        if 'download' in text_lower or 'file' in text_lower:
            info['type'] = 'file_download'
        elif 'api' in text_lower or 'endpoint' in text_lower:
            info['type'] = 'api_fetch'
        elif 'sum' in text_lower or 'calculate' in text_lower or 'table' in text_lower:
            info['type'] = 'data_analysis'
        elif 'visualize' in text_lower or 'chart' in text_lower or 'plot' in text_lower:
            info['type'] = 'visualization'
        elif 'pdf' in text_lower:
            info['type'] = 'pdf_analysis'
        
        return info
    
    def _extract_submit_url(self, html_content: str) -> Optional[str]:
        """Extract submit URL from HTML content"""
        # Look for URLs in the content
        url_pattern = r'https?://[^\s<>"\'\)]+/submit[^\s<>"\'\)]*'
        matches = re.findall(url_pattern, html_content)
        if matches:
            return matches[0]
        
        # Also check for submit endpoints in text
        submit_pattern = r'https?://[^\s<>"\'\)]+/submit[^\s<>"\'\)]*'
        matches = re.findall(submit_pattern, html_content)
        if matches:
            return matches[0]
        
        return None
    
    async def _solve_question(self, question_info: Dict[str, Any]) -> Any:
        """
        Solve a question based on its type
        
        Args:
            question_info: Question information dictionary
            
        Returns:
            Answer to the question
        """
        question_type = question_info.get('type', 'general')
        text = question_info.get('text', '')
        
        try:
            if question_type == 'file_download':
                return await self._solve_file_question(question_info)
            elif question_type == 'api_fetch':
                return await self._solve_api_question(question_info)
            elif question_type == 'pdf_analysis':
                return await self._solve_pdf_question(question_info)
            elif question_type == 'data_analysis':
                return await self._solve_data_analysis_question(question_info)
            elif question_type == 'visualization':
                return await self._solve_visualization_question(question_info)
            else:
                return await self._solve_general_question(question_info)
        except Exception as e:
            logger.error(f"Error solving {question_type} question: {e}")
            # Fallback to general LLM solving
            return await self._solve_general_question(question_info)
    
    async def _solve_file_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a question involving file download"""
        text = question_info['text']
        urls = question_info['data_urls']
        
        # Extract file URL from question
        file_url = None
        for url in urls:
            if any(ext in url.lower() for ext in ['.pdf', '.csv', '.json', '.xlsx', '.xls']):
                file_url = url
                break
        
        if not file_url:
            # Try to find URL in text
            url_pattern = r'https?://[^\s<>"\'\)]+\.(pdf|csv|json|xlsx|xls)[^\s<>"\'\)]*'
            matches = re.findall(url_pattern, text, re.IGNORECASE)
            if matches:
                file_url = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        if file_url:
            # Download file
            file_bytes = self.data_processor.download_file(file_url)
            
            # Process based on file type
            if file_url.endswith('.pdf'):
                pdf_data = self.data_processor.parse_pdf(file_bytes)
                # Use LLM to analyze PDF and answer question
                context = {
                    'data': pdf_data['text'],
                    'tables': pdf_data['tables']
                }
                answer = await self.llm.solve_question(text, context)
                return self._extract_answer(answer, text)
            
            elif file_url.endswith('.csv'):
                csv_text = file_bytes.decode('utf-8')
                df = self.data_processor.parse_csv(csv_text)
                # Analyze data
                answer = await self._analyze_dataframe_question(df, text)
                return answer
            
            elif file_url.endswith('.json'):
                json_text = file_bytes.decode('utf-8')
                json_data = self.data_processor.parse_json(json_text)
                context = {'data': json.dumps(json_data, indent=2)}
                answer = await self.llm.solve_question(text, context)
                return self._extract_answer(answer, text)
        
        # Fallback
        return await self._solve_general_question(question_info)
    
    async def _solve_api_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a question involving API data fetching"""
        text = question_info['text']
        urls = question_info['data_urls']
        
        # Find API URL
        api_url = None
        for url in urls:
            if 'api' in url.lower() or 'endpoint' in url.lower():
                api_url = url
                break
        
        if api_url:
            # Fetch API data
            api_data = self.data_processor.fetch_api_data(api_url)
            context = {'data': json.dumps(api_data, indent=2) if isinstance(api_data, dict) else str(api_data)}
            answer = await self.llm.solve_question(text, context)
            return self._extract_answer(answer, text)
        
        return await self._solve_general_question(question_info)
    
    async def _solve_pdf_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a PDF-related question"""
        return await self._solve_file_question(question_info)
    
    async def _solve_data_analysis_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a data analysis question"""
        text = question_info['text']
        
        # Try to extract tables from HTML
        tables = self.data_processor.extract_tables_from_html(question_info['html'])
        
        if tables:
            # Use the first table or combine them
            df = tables[0] if len(tables) == 1 else pd.concat(tables, ignore_index=True)
            return await self._analyze_dataframe_question(df, text)
        
        # Fallback to general solving
        return await self._solve_general_question(question_info)
    
    async def _solve_visualization_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a visualization question"""
        # This would require generating visualization code
        # For now, use LLM to understand requirements
        answer = await self._solve_general_question(question_info)
        return answer
    
    async def _solve_general_question(self, question_info: Dict[str, Any]) -> Any:
        """Solve a general question using LLM"""
        text = question_info.get('text', '')
        answer = await self.llm.solve_question(text)
        return self._extract_answer(answer, text)
    
    async def _analyze_dataframe_question(self, df, question_text: str) -> Any:
        """Analyze a DataFrame to answer a question"""
        import pandas as pd
        
        # Try to extract operation from question
        question_lower = question_text.lower()
        
        # Check for common operations
        if 'sum' in question_lower:
            # Extract column name if mentioned
            column_match = re.search(r'"([^"]+)"', question_text)
            if column_match:
                column = column_match.group(1)
                if column in df.columns:
                    return float(df[column].sum())
            return float(df.sum().sum())
        
        elif 'mean' in question_lower or 'average' in question_lower:
            column_match = re.search(r'"([^"]+)"', question_text)
            if column_match:
                column = column_match.group(1)
                if column in df.columns:
                    return float(df[column].mean())
            return float(df.mean().mean())
        
        elif 'count' in question_lower:
            return len(df)
        
        elif 'max' in question_lower:
            column_match = re.search(r'"([^"]+)"', question_text)
            if column_match:
                column = column_match.group(1)
                if column in df.columns:
                    return df[column].max()
        
        # Use LLM for complex analysis
        context = {
            'data': f"DataFrame shape: {df.shape}\nColumns: {list(df.columns)}\nFirst few rows:\n{df.head().to_string()}"
        }
        answer = await self.llm.solve_question(question_text, context)
        return self._extract_answer(answer, question_text)
    
    def _extract_answer(self, llm_response: str, question_text: str) -> Any:
        """Extract and format answer from LLM response"""
        # Try to extract number
        number_pattern = r'-?\d+\.?\d*'
        numbers = re.findall(number_pattern, llm_response)
        if numbers:
            try:
                num_str = numbers[0]
                if '.' in num_str:
                    return float(num_str)
                return int(num_str)
            except:
                pass
        
        # Return as string
        return llm_response.strip()
    
    async def _submit_answer(
        self,
        submit_url: str,
        quiz_url: str,
        answer: Any,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Submit answer to the quiz endpoint
        
        Args:
            submit_url: URL to submit answer to
            quiz_url: Original quiz URL
            answer: Answer to submit
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result dictionary
        """
        import httpx
        
        payload = {
            "email": self.email,
            "secret": self.secret,
            "url": quiz_url,
            "answer": answer
        }
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(submit_url, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Answer submitted successfully. Correct: {result.get('correct')}")
                        return {
                            'url': quiz_url,
                            'answer': answer,
                            'correct': result.get('correct', False),
                            'next_url': result.get('url'),
                            'reason': result.get('reason'),
                            'attempt': attempt + 1
                        }
                    else:
                        logger.warning(f"Submit failed with status {response.status_code}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)  # Wait before retry
            
            except Exception as e:
                logger.error(f"Error submitting answer (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        return {
            'url': quiz_url,
            'answer': answer,
            'correct': False,
            'error': 'Failed to submit after retries'
        }

