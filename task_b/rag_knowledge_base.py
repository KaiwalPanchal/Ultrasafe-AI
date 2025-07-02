"""
RAG Knowledge Base for Content Transformation System
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
import requests

USF_EMBEDDING_URL = "https://api.us.inc/usf/v1/embed/embeddings"
USF_EMBEDDING_MODEL = "usf1-embed"
USF_RERANK_URL = "https://api.us.inc/usf/v1/embed/reranker"
USF_RERANK_MODEL = "usf1-rerank"
USF_API_KEY = os.getenv("ULTRASAFE_API_KEY")

def get_usf_embedding(text: str) -> list:
    headers = {"Authorization": f"Bearer {USF_API_KEY}"} if USF_API_KEY else {}
    payload = {
        "model": USF_EMBEDDING_MODEL,
        "input": text
    }
    try:
        response = requests.post(USF_EMBEDDING_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        embedding = response.json()["result"]["data"][0]["embedding"]
        return embedding
    except requests.Timeout:
        print("[ERROR] USF embedding API timed out.")
        return [0.0] * 1536  # Return dummy embedding of expected size
    except Exception as e:
        print(f"[ERROR] USF embedding API failed: {e}")
        return [0.0] * 1536

def rerank_usf(query: str, texts: list) -> list:
    headers = {"Authorization": f"Bearer {USF_API_KEY}"} if USF_API_KEY else {}
    payload = {
        "model": USF_RERANK_MODEL,
        "query": query,
        "texts": texts
    }
    response = requests.post(USF_RERANK_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["result"]["data"]

class RAGKnowledgeBase:
    """RAG system for style guides and examples"""
    
    def __init__(self, embeddings: OpenAIEmbeddings):
        self.style_guides_dir = Path(__file__).parent / "style_guides"
        self.examples_dir = Path(__file__).parent / "generated_stylized_content"
        self.vectorstore = None
        self.knowledge_base = {}
        self.embeddings = embeddings
        self.expected_embedding_size = None
        
    def build_knowledge_base(self):
        """Build the knowledge base from style guides and examples using USF embeddings API"""
        # Check directories exist
        if not self.style_guides_dir.exists():
            print(f"[ERROR] Style guides directory not found: {self.style_guides_dir}")
            return
        if not self.examples_dir.exists():
            print(f"[ERROR] Examples directory not found: {self.examples_dir}")
            return
        print("Building RAG knowledge base...")
        style_guides = self._load_style_guides()
        examples = self._load_examples()
        print(f"Found {len(style_guides)} style guides and {len(examples)} examples ({len(style_guides) + len(examples)} total)")
        # Test with one style guide and one example first
        test_style_guides = style_guides[:1] if style_guides else []
        test_examples = examples[:1] if examples else []
        test_documents = []
        test_embeddings = []
        idx = 0
        for guide in test_style_guides:
            idx += 1
            print(f"[TEST] Embedding style guide {idx}: {guide['filename']}")
            doc = Document(
                page_content=guide['content'],
                metadata={
                    'type': 'style_guide',
                    'format': guide['format'],
                    'style': guide['style'],
                    'complexity': guide['complexity'],
                    'filename': guide['filename']
                }
            )
            test_documents.append(doc)
            emb = get_usf_embedding(guide['content'])
            if self.expected_embedding_size is None:
                self.expected_embedding_size = len(emb)
                print(f"[INFO] Detected embedding size: {self.expected_embedding_size}")
            print(f"[DEBUG] Style guide embedding type: {type(emb)}, len: {len(emb) if isinstance(emb, list) else 'N/A'}, preview: {emb[:10] if isinstance(emb, list) else emb}")
            if not isinstance(emb, list) or len(emb) != self.expected_embedding_size or any(isinstance(x, list) for x in emb) or not all(isinstance(x, (float, int)) for x in emb):
                print(f"[WARNING] Invalid embedding for {guide['filename']}, using dummy embedding.")
                emb = [0.0] * (self.expected_embedding_size or 1024)
            test_embeddings.append(emb)
        for example in test_examples:
            idx += 1
            print(f"[TEST] Embedding example {idx}: {example['filename']} (topic: {example['topic']})")
            doc = Document(
                page_content=example['content'],
                metadata={
                    'type': 'example',
                    'format': example['format'],
                    'style': example['style'],
                    'complexity': example['complexity'],
                    'topic': example['topic'],
                    'filename': example['filename']
                }
            )
            test_documents.append(doc)
            emb = get_usf_embedding(example['content'])
            if self.expected_embedding_size is None:
                self.expected_embedding_size = len(emb)
                print(f"[INFO] Detected embedding size: {self.expected_embedding_size}")
            print(f"[DEBUG] Example embedding type: {type(emb)}, len: {len(emb) if isinstance(emb, list) else 'N/A'}, preview: {emb[:10] if isinstance(emb, list) else emb}")
            if not isinstance(emb, list) or len(emb) != self.expected_embedding_size or any(isinstance(x, list) for x in emb) or not all(isinstance(x, (float, int)) for x in emb):
                print(f"[WARNING] Invalid embedding for {example['filename']}, using dummy embedding.")
                emb = [0.0] * (self.expected_embedding_size or 1024)
            test_embeddings.append(emb)
        if test_documents:
            try:
                text_embedding_pairs = [
                    (doc.page_content, emb) for doc, emb in zip(test_documents, test_embeddings)
                ]
                self.vectorstore = FAISS.from_embeddings(
                    text_embedding_pairs, self.embeddings
                )
                print(f"[TEST] Built knowledge base with {len(test_documents)} documents (1 style guide, 1 example)")
            except Exception as e:
                print(f"[ERROR] Test FAISS build failed: {e}")
                return
        else:
            print("[TEST] No documents found for knowledge base")
            return
        # Proceed to full build if test succeeded
        documents = []
        embeddings = []
        idx = 0
        for guide in style_guides:
            idx += 1
            print(f"Embedding style guide {idx}/{len(style_guides) + len(examples)}: {guide['filename']}")
            doc = Document(
                page_content=guide['content'],
                metadata={
                    'type': 'style_guide',
                    'format': guide['format'],
                    'style': guide['style'],
                    'complexity': guide['complexity'],
                    'filename': guide['filename']
                }
            )
            documents.append(doc)
            emb = get_usf_embedding(guide['content'])
            if self.expected_embedding_size is None:
                self.expected_embedding_size = len(emb)
                print(f"[INFO] Detected embedding size: {self.expected_embedding_size}")
            print(f"[DEBUG] Style guide embedding type: {type(emb)}, len: {len(emb) if isinstance(emb, list) else 'N/A'}, preview: {emb[:10] if isinstance(emb, list) else emb}")
            if not isinstance(emb, list) or len(emb) != self.expected_embedding_size or any(isinstance(x, list) for x in emb) or not all(isinstance(x, (float, int)) for x in emb):
                print(f"[WARNING] Invalid embedding for {guide['filename']}, using dummy embedding.")
                emb = [0.0] * (self.expected_embedding_size or 1024)
            embeddings.append(emb)
        for example in examples:
            idx += 1
            print(f"Embedding example {idx}/{len(style_guides) + len(examples)}: {example['filename']} (topic: {example['topic']})")
            doc = Document(
                page_content=example['content'],
                metadata={
                    'type': 'example',
                    'format': example['format'],
                    'style': example['style'],
                    'complexity': example['complexity'],
                    'topic': example['topic'],
                    'filename': example['filename']
                }
            )
            documents.append(doc)
            emb = get_usf_embedding(example['content'])
            if self.expected_embedding_size is None:
                self.expected_embedding_size = len(emb)
                print(f"[INFO] Detected embedding size: {self.expected_embedding_size}")
            print(f"[DEBUG] Example embedding type: {type(emb)}, len: {len(emb) if isinstance(emb, list) else 'N/A'}, preview: {emb[:10] if isinstance(emb, list) else emb}")
            if not isinstance(emb, list) or len(emb) != self.expected_embedding_size or any(isinstance(x, list) for x in emb) or not all(isinstance(x, (float, int)) for x in emb):
                print(f"[WARNING] Invalid embedding for {example['filename']}, using dummy embedding.")
                emb = [0.0] * (self.expected_embedding_size or 1024)
            embeddings.append(emb)
        if documents:
            try:
                text_embedding_pairs = [
                    (doc.page_content, emb) for doc, emb in zip(documents, embeddings)
                ]
                self.vectorstore = FAISS.from_embeddings(
                    text_embedding_pairs, self.embeddings
                )
                print(f"Built knowledge base with {len(documents)} documents")
            except Exception as e:
                print(f"[ERROR] Full FAISS build failed: {e}")
        else:
            print("No documents found for knowledge base")
    
    def _load_style_guides(self) -> List[Dict[str, Any]]:
        """Load all style guide files"""
        guides = []
        
        if not self.style_guides_dir.exists():
            print(f"Style guides directory not found: {self.style_guides_dir}")
            return guides
        
        for file_path in self.style_guides_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Parse filename
                filename = file_path.stem
                parts = self._parse_style_filename(filename)
                
                if parts:
                    guides.append({
                        'filename': filename,
                        'format': parts['format'],
                        'style': parts['style'],
                        'complexity': parts['complexity'],
                        'content': content,
                        'file_path': str(file_path)
                    })
                    
            except Exception as e:
                print(f"Error loading style guide {file_path}: {str(e)}")
                continue
        
        return guides
    
    def _load_examples(self) -> List[Dict[str, Any]]:
        """Load example content from generated_stylized_content (recursively)"""
        examples = []
        if not self.examples_dir.exists():
            print(f"Examples directory not found: {self.examples_dir}")
            return examples
        # Recursively walk through all subdirectories and collect .txt files
        for file_path in self.examples_dir.rglob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                # Parse filename
                filename = file_path.stem
                parts = self._parse_style_filename(filename)
                # Topic is the first-level subdirectory under generated_stylized_content
                try:
                    topic_name = file_path.relative_to(self.examples_dir).parts[0]
                except Exception:
                    topic_name = None
                if parts and topic_name:
                    examples.append({
                        'filename': filename,
                        'topic': topic_name,
                        'format': parts['format'],
                        'style': parts['style'],
                        'complexity': parts['complexity'],
                        'content': content,
                        'file_path': str(file_path)
                    })
            except Exception as e:
                print(f"Error loading example {file_path}: {str(e)}")
                continue
        return examples
    
    def _parse_style_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """Parse style guide/example filename to extract components"""
        filename_lower = filename.lower()
        
        # Define mappings
        formats = {
            'blog_post': 'blog_post',
            'linkedin_post': 'linkedin_post', 
            'twitter_thread': 'twitter_thread',
            'email_newsletter': 'email_newsletter',
            'podcast_script': 'podcast_script'
        }
        
        styles = {
            'gen_z': 'gen_z',
            'millennial': 'millennial',
            'enthusiastic_and_motivational': 'enthusiastic_and_motivational',
            'formal_professional': 'formal_professional',
            'casual_conversational': 'casual_conversational',
            'yoda_star_wars': 'yoda_star_wars',
            'sherlock_holmes': 'sherlock_holmes',
            'tony_stark_iron_man': 'tony_stark_iron_man'
        }
        
        complexities = {
            'newbie': 'newbie',
            'knows_a_little': 'knows_a_little',
            'expert': 'expert'
        }
        
        # Find format
        format_found = None
        for key, value in formats.items():
            if filename_lower.startswith(key):
                format_found = value
                filename_lower = filename_lower[len(key):].lstrip('_')
                break
        
        if not format_found:
            return None
        
        # Find complexity (from the end)
        complexity_found = None
        for key, value in complexities.items():
            if filename_lower.endswith(key):
                complexity_found = value
                filename_lower = filename_lower[:-len(key)].rstrip('_')
                break
        
        if not complexity_found:
            return None
        
        # Remaining should be style
        style_found = None
        for key, value in styles.items():
            if key in filename_lower:
                style_found = value
                break
        
        if not style_found:
            return None
        
        return {
            'format': format_found,
            'style': style_found,
            'complexity': complexity_found
        }
    
    def retrieve_relevant_context(self, query: str, target_format: str = None, 
                                target_style: str = None, target_complexity: str = None, target_topic: str = None, use_reranker: bool = True) -> Dict[str, Any]:
        """Retrieve relevant style guides and examples for transformation, guaranteeing inclusion of exact style guide and topic example if available. Optionally rerank results."""
        if not self.vectorstore:
            return {'style_guides': [], 'examples': []}
        search_terms = [query]
        if target_format:
            search_terms.append(f"format: {target_format}")
        if target_style:
            search_terms.append(f"style: {target_style}")
        if target_complexity:
            search_terms.append(f"complexity: {target_complexity}")
        if target_topic:
            search_terms.append(f"topic: {target_topic}")
        search_query = " ".join(search_terms)
        # Embed the query using the USF API
        query_embedding = get_usf_embedding(search_query)
        # Search for relevant documents
        docs = self.vectorstore.similarity_search_by_vector(query_embedding, k=7)
        # Optionally rerank the results
        if use_reranker and docs:
            reranked = rerank_usf(search_query, [doc.page_content for doc in docs])
            # Sort docs by reranker score (descending)
            reranked_indices = [r['index'] for r in sorted(reranked, key=lambda x: -x['score'])]
            docs = [docs[i] for i in reranked_indices]
        # Separate style guides and examples
        style_guides = []
        examples = []
        style_guide_keys = set()
        example_keys = set()
        for doc in docs:
            if doc.metadata.get('type') == 'style_guide':
                style_guides.append({'content': doc.page_content, 'metadata': doc.metadata})
                style_guide_keys.add((doc.metadata.get('format'), doc.metadata.get('style'), doc.metadata.get('complexity')))
            elif doc.metadata.get('type') == 'example':
                examples.append({'content': doc.page_content, 'metadata': doc.metadata})
                example_keys.add((doc.metadata.get('format'), doc.metadata.get('style'), doc.metadata.get('complexity'), doc.metadata.get('topic')))
        
        # Guarantee inclusion of the exact style guide
        if target_format and target_style and target_complexity:
            key = (target_format, target_style, target_complexity)
            if key not in style_guide_keys:
                filename = f"{target_format}_{target_style}_{target_complexity}.txt"
                file_path = self.style_guides_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    style_guides.insert(0, {
                        'content': content,
                        'metadata': {
                            'type': 'style_guide',
                            'format': target_format,
                            'style': target_style,
                            'complexity': target_complexity,
                            'filename': filename
                        }
                    })
        # Guarantee inclusion of at least one topic example
        if target_format and target_style and target_complexity and target_topic:
            key = (target_format, target_style, target_complexity, target_topic)
            if key not in example_keys:
                topic_dir = self.examples_dir / target_topic
                if topic_dir.exists():
                    for file_path in topic_dir.glob("*.txt"):
                        fname = file_path.stem
                        parts = self._parse_style_filename(fname)
                        if parts and parts['format'] == target_format and parts['style'] == target_style and parts['complexity'] == target_complexity:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            examples.insert(0, {
                                'content': content,
                                'metadata': {
                                    'type': 'example',
                                    'format': target_format,
                                    'style': target_style,
                                    'complexity': target_complexity,
                                    'topic': target_topic,
                                    'filename': file_path.name
                                }
                            })
                            break
        return {
            'style_guides': style_guides,
            'examples': examples,
            'search_query': search_query
        }

    def save_index(self, path: str = "rag_faiss_index"):
        """Save the FAISS index to disk."""
        if self.vectorstore:
            self.vectorstore.save_local(path)
            print(f"FAISS index saved to {path}")
        else:
            print("No FAISS index to save.")

    def load_index(self, path: str = "rag_faiss_index"):
        """Load the FAISS index from disk."""
        if Path(path).exists():
            self.vectorstore = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            print(f"FAISS index loaded from {path}")
        else:
            print(f"No FAISS index found at {path}")

    def incremental_update(self, path: str = "rag_faiss_index"):
        """Incrementally add new/changed style guides/examples to the index."""
        print("Performing incremental update of RAG knowledge base...")
        # Load existing index if present
        if Path(path).exists():
            self.load_index(path)
            existing_filenames = set()
            for doc in self.vectorstore.docstore._dict.values():
                existing_filenames.add(doc.metadata.get('filename'))
        else:
            self.vectorstore = None
            existing_filenames = set()
        # Load all style guides and examples
        style_guides = self._load_style_guides()
        examples = self._load_examples()
        new_documents = []
        new_embeddings = []
        for guide in style_guides:
            if guide['filename'] not in existing_filenames:
                doc = Document(
                    page_content=guide['content'],
                    metadata={
                        'type': 'style_guide',
                        'format': guide['format'],
                        'style': guide['style'],
                        'complexity': guide['complexity'],
                        'filename': guide['filename']
                    }
                )
                new_documents.append(doc)
                emb = get_usf_embedding(guide['content'])
                # Validate embedding
                if not (isinstance(emb, list) and len(emb) == self.expected_embedding_size and all(isinstance(x, (float, int)) for x in emb)):
                    print(f"[WARNING] Invalid embedding for {guide['filename']}, using dummy embedding.")
                    emb = [0.0] * (self.expected_embedding_size or 1024)
                new_embeddings.append(emb)
        for example in examples:
            if example['filename'] not in existing_filenames:
                doc = Document(
                    page_content=example['content'],
                    metadata={
                        'type': 'example',
                        'format': example['format'],
                        'style': example['style'],
                        'complexity': example['complexity'],
                        'topic': example['topic'],
                        'filename': example['filename']
                    }
                )
                new_documents.append(doc)
                emb = get_usf_embedding(example['content'])
                # Validate embedding
                if not (isinstance(emb, list) and len(emb) == self.expected_embedding_size and all(isinstance(x, (float, int)) for x in emb)):
                    print(f"[WARNING] Invalid embedding for {example['filename']}, using dummy embedding.")
                    emb = [0.0] * (self.expected_embedding_size or 1024)
                new_embeddings.append(emb)
        if new_documents:
            if self.vectorstore:
                self.vectorstore.add_embeddings(new_embeddings, new_documents)
                print(f"Added {len(new_documents)} new documents to the index.")
            else:
                self.vectorstore = FAISS.from_embeddings(new_embeddings, new_documents, self.embeddings)
                print(f"Created new index with {len(new_documents)} documents.")
            self.save_index(path)
        else:
            print("No new documents to add.") 