"""
Data processing utilities for handling various data formats
"""
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Union
import logging
import re
import json
import base64
from pathlib import Path
import io
import pdfplumber
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class DataProcessor:
    """Utilities for processing various data formats"""
    
    @staticmethod
    def parse_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Parse PDF file and extract text and tables
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with 'text' and 'tables' keys
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            text_parts = []
            tables_list = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                    
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            tables_list.append({
                                'page': page_num,
                                'table': table
                            })
            
            return {
                'text': '\n\n'.join(text_parts),
                'tables': tables_list,
                'num_pages': len(text_parts)
            }
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    @staticmethod
    def extract_tables_from_html(html: str) -> list:
        """
        Extract tables from HTML content
        
        Args:
            html: HTML content as string
            
        Returns:
            List of pandas DataFrames
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            tables = soup.find_all('table')
            dataframes = []
            
            for table in tables:
                df = pd.read_html(str(table))[0]
                dataframes.append(df)
            
            return dataframes
        except Exception as e:
            logger.error(f"Error extracting tables from HTML: {e}")
            return []
    
    @staticmethod
    def parse_csv(csv_content: str) -> pd.DataFrame:
        """Parse CSV content into pandas DataFrame"""
        try:
            return pd.read_csv(io.StringIO(csv_content))
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise
    
    @staticmethod
    def parse_json(json_content: str) -> Any:
        """Parse JSON content"""
        try:
            return json.loads(json_content)
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    @staticmethod
    def download_file(url: str, headers: Optional[Dict] = None) -> bytes:
        """
        Download a file from URL
        
        Args:
            url: URL to download from
            headers: Optional HTTP headers
            
        Returns:
            File content as bytes
        """
        try:
            response = requests.get(url, headers=headers or {}, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            raise
    
    @staticmethod
    def fetch_api_data(url: str, method: str = 'GET', headers: Optional[Dict] = None, 
                       params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Any:
        """
        Fetch data from an API endpoint
        
        Args:
            url: API endpoint URL
            method: HTTP method
            headers: HTTP headers
            params: Query parameters
            json_data: JSON payload for POST/PUT
            
        Returns:
            API response (parsed JSON if possible, else raw text)
        """
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers or {}, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers or {}, json=json_data, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except:
                return response.text
        except Exception as e:
            logger.error(f"Error fetching API data from {url}: {e}")
            raise
    
    @staticmethod
    def analyze_dataframe(df: pd.DataFrame, operation: str, **kwargs) -> Any:
        """
        Perform operations on a DataFrame
        
        Args:
            df: pandas DataFrame
            operation: Operation to perform ('sum', 'mean', 'filter', 'groupby', etc.)
            **kwargs: Additional parameters for the operation
            
        Returns:
            Result of the operation
        """
        try:
            operation_lower = operation.lower()
            
            if operation_lower == 'sum':
                column = kwargs.get('column')
                if column:
                    return float(df[column].sum())
                return float(df.sum().sum())
            
            elif operation_lower == 'mean':
                column = kwargs.get('column')
                if column:
                    return float(df[column].mean())
                return float(df.mean().mean())
            
            elif operation_lower == 'filter':
                # kwargs should contain filter conditions
                filtered_df = df.copy()
                for key, value in kwargs.items():
                    if key != 'column':
                        filtered_df = filtered_df[filtered_df[key] == value]
                return filtered_df
            
            elif operation_lower == 'groupby':
                column = kwargs.get('column')
                agg_func = kwargs.get('agg', 'sum')
                groupby_col = kwargs.get('groupby')
                if groupby_col and column:
                    return df.groupby(groupby_col)[column].agg(agg_func).to_dict()
            
            elif operation_lower == 'sort':
                column = kwargs.get('column')
                ascending = kwargs.get('ascending', True)
                if column:
                    return df.sort_values(by=column, ascending=ascending)
            
            elif operation_lower == 'count':
                column = kwargs.get('column')
                if column:
                    return int(df[column].count())
                return len(df)
            
            elif operation_lower == 'max':
                column = kwargs.get('column')
                if column:
                    return df[column].max()
                return df.max().max()
            
            elif operation_lower == 'min':
                column = kwargs.get('column')
                if column:
                    return df[column].min()
                return df.min().min()
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error(f"Error performing operation {operation} on DataFrame: {e}")
            raise
    
    @staticmethod
    def encode_to_base64(data: bytes) -> str:
        """Encode bytes to base64 string"""
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def format_answer(answer: Any) -> Union[str, int, float, bool, Dict]:
        """
        Format answer according to expected type
        
        Args:
            answer: Answer to format
            
        Returns:
            Formatted answer
        """
        if isinstance(answer, (int, float, bool, str)):
            return answer
        elif isinstance(answer, pd.DataFrame):
            # Convert DataFrame to dict
            return answer.to_dict('records')
        elif isinstance(answer, np.ndarray):
            return answer.tolist()
        elif isinstance(answer, (list, dict)):
            return answer
        else:
            return str(answer)

