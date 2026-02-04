"""
URL-based summarizer that works with document URLs directly.
Uses OpenRouter models that support document URLs (multimodal models).
"""
import requests
import json
from typing import List, Dict, Optional
from .config import Config


class URLSummarizer:
    """Summarize documents using direct URLs without downloading"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        # Use a model that supports documents/images
        # allenai/molmo-2-8b:free supports image_url
        # We can use it for documents by converting them to viewable format
        self.model = model or "google/gemini-flash-1.5:free"  # Supports file URLs
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
            'HTTP-Referer': 'https://github.com',
            'X-Title': 'Document Summarizer',
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
                timeout=120  # Longer timeout for document processing
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
    
    def summarize_document_url(self, file_url: str, filename: str = None) -> Dict:
        """
        Summarize a document from URL.
        
        Args:
            file_url: Public URL to the document
            filename: Optional filename for context
            
        Returns:
            Dict with summary information
        """
        context = f"Document: {filename}" if filename else "Document"
        
        # Create message with document URL
        messages = [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': f"""Please analyze this document and provide a clear, concise summary.
Focus on the main ideas, key points, and important details.

{context}

What are the main topics and key information in this document?"""
                    },
                    {
                        'type': 'image_url',  # Some models accept documents as image_url
                        'image_url': {
                            'url': file_url
                        }
                    }
                ]
            }
        ]
        
        try:
            summary = self._call_api(messages, max_tokens=1500)
            return {
                'filename': filename or 'unknown',
                'url': file_url,
                'summary': summary,
                'summary_status': 'success'
            }
        except Exception as e:
            return {
                'filename': filename or 'unknown',
                'url': file_url,
                'summary': f"Error: {str(e)}",
                'summary_status': 'error'
            }
    
    def summarize_text_content(self, text: str, context: str = "") -> str:
        """
        Summarize text content directly (fallback method).
        
        Args:
            text: Text to summarize
            context: Optional context
            
        Returns:
            Summary text
        """
        if not text or not text.strip():
            return "No content to summarize"
        
        # Truncate if too long
        max_chars = Config.MAX_TOKENS_PER_CHUNK * 4
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        prompt = f"""Please provide a clear and concise summary of the following content.
Focus on the main ideas, key points, and important details.

{f'Context: {context}' if context else ''}

Content:
{text}

Summary:"""
        
        messages = [
            {
                'role': 'user',
                'content': prompt
            }
        ]
        
        return self._call_api(messages, max_tokens=1000)
    
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
        
        # Prepare combined text
        combined_text = "# Individual Document Summaries\n\n"
        
        for i, doc in enumerate(summaries, 1):
            if doc.get('summary_status') == 'success':
                filename = doc.get('filename', f'Document {i}')
                combined_text += f"## {i}. {filename}\n"
                combined_text += f"{doc['summary']}\n\n"
        
        # Truncate if too long
        max_chars = Config.MAX_TOKENS_PER_CHUNK * 4
        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars] + "..."
        
        prompt = f"""You are analyzing a collection of documents. Below are summaries of individual documents from a folder.

Please create a comprehensive master summary that:
1. Identifies the main themes and topics across all documents
2. Highlights the most important information
3. Notes any connections or relationships between documents
4. Provides an overall synthesis of the content
5. Gives insights about what this collection of documents represents

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
        
        return {
            'master_summary': master_summary,
            'statistics': {
                'total_documents': total_docs,
                'successful_summaries': successful_summaries,
                'failed_summaries': failed_summaries,
            },
            'individual_summaries': summaries
        }
