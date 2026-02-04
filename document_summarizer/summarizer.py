"""
Summarization module using OpenRouter API.
Handles text summarization with LLM models.
"""
import requests
import json
from typing import List, Dict, Optional
from .config import Config


class Summarizer:
    """Summarize text using OpenRouter API"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model or Config.DEFAULT_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
    
    def _call_api(self, messages: List[Dict], max_tokens: int = 2000) -> str:
        """
        Make API call to OpenRouter.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from the model
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com',  # Optional but recommended
            'X-Title': 'Document Summarizer',  # Optional but recommended
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.7,
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e}"
            if hasattr(e.response, 'text'):
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)
        
        except Exception as e:
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
    
    def summarize_text(self, text: str, context: str = "") -> str:
        """
        Summarize a single piece of text.
        
        Args:
            text: Text to summarize
            context: Optional context about the document
            
        Returns:
            Summary of the text
        """
        if not text or not text.strip():
            return "No content to summarize"
        
        # Truncate text if too long (rough estimate: 1 token ≈ 4 chars)
        max_chars = Config.MAX_TOKENS_PER_CHUNK * 4
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""Please provide a clear and concise summary of the following document.
Focus on the main ideas, key points, and important details.

{f'Context: {context}' if context else ''}

Document content:
{text}

Summary:"""
        
        messages = [
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        return self._call_api(messages, max_tokens=1000)
    
    def summarize_document(self, document: Dict) -> Dict:
        """
        Summarize a parsed document.
        
        Args:
            document: Dict with 'filename', 'type', 'content', 'size'
            
        Returns:
            Dict with original info plus 'summary'
        """
        context = f"Filename: {document['filename']} (Type: {document['type']})"
        
        try:
            summary = self.summarize_text(document['content'], context=context)
            document['summary'] = summary
            document['summary_status'] = 'success'
        except Exception as e:
            document['summary'] = f"Error generating summary: {str(e)}"
            document['summary_status'] = 'error'
        
        return document
    
    def create_master_summary(self, summaries: List[Dict]) -> str:
        """
        Create a master summary from individual document summaries.
        
        Args:
            summaries: List of document dicts with summaries
            
        Returns:
            Master summary text
        """
        if not summaries:
            return "No documents to summarize"
        
        # Prepare combined text with document summaries
        combined_text = "# Document Summaries\n\n"
        
        for i, doc in enumerate(summaries, 1):
            if doc.get('summary_status') == 'success':
                combined_text += f"## Document {i}: {doc['filename']}\n"
                combined_text += f"{doc['summary']}\n\n"
        
        # Truncate if too long
        max_chars = Config.MAX_TOKENS_PER_CHUNK * 4
        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars] + "..."
        
        prompt = f"""You are analyzing a collection of documents. Below are summaries of individual documents.

Please create a comprehensive master summary that:
1. Identifies the main themes and topics across all documents
2. Highlights the most important information
3. Notes any connections or relationships between documents
4. Provides an overall synthesis of the content

Individual document summaries:
{combined_text}

Master Summary:"""
        
        messages = [
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        try:
            master_summary = self._call_api(messages, max_tokens=2000)
            return master_summary
        except Exception as e:
            return f"Error creating master summary: {str(e)}"
    
    def generate_structured_summary(self, summaries: List[Dict]) -> Dict:
        """
        Generate a structured summary report.
        
        Returns:
            Dict with structured summary information
        """
        total_docs = len(summaries)
        successful_summaries = sum(1 for s in summaries if s.get('summary_status') == 'success')
        failed_summaries = total_docs - successful_summaries
        
        master_summary = self.create_master_summary(summaries)
        
        # Calculate total size
        total_size = sum(s.get('size', 0) for s in summaries)
        
        # Get file types
        file_types = {}
        for doc in summaries:
            ftype = doc.get('type', 'unknown')
            file_types[ftype] = file_types.get(ftype, 0) + 1
        
        return {
            'master_summary': master_summary,
            'statistics': {
                'total_documents': total_docs,
                'successful_summaries': successful_summaries,
                'failed_summaries': failed_summaries,
                'total_size_bytes': total_size,
                'file_types': file_types
            },
            'individual_summaries': summaries
        }
