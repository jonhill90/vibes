"""Text chunking service with semantic boundary respect.

This service implements semantic text chunking with ~500 token chunks, 50 token overlap,
and boundary respect (sentences, paragraphs). It uses tiktoken for accurate token counting
and runs CPU-intensive operations in a thread pool to avoid blocking the event loop.

Key features:
- Accurate token counting using tiktoken (text-embedding-3-small encoding)
- Semantic chunking: respects sentence and paragraph boundaries
- Configurable chunk size (default 500 tokens) and overlap (default 50 tokens)
- Chunk metadata: index, text, token count, character offsets
- Thread pool execution for CPU-bound operations (Gotcha #4)

Pattern: Semantic chunking + tiktoken + thread pool
Reference: prps/rag_service_implementation.md (Phase 4, Task 4.2, Gotcha #4)
"""

import asyncio
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a single text chunk with metadata.

    Attributes:
        chunk_index: Zero-based index of chunk in document
        text: Chunk content
        token_count: Number of tokens in chunk (tiktoken count)
        start_offset: Character offset where chunk starts in original text
        end_offset: Character offset where chunk ends in original text
    """

    chunk_index: int
    text: str
    token_count: int
    start_offset: int
    end_offset: int

    def to_dict(self) -> dict:
        """Convert chunk to dictionary for JSON serialization."""
        return {
            "chunk_index": self.chunk_index,
            "text": self.text,
            "token_count": self.token_count,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
        }


class TextChunker:
    """Semantic text chunker with token-aware boundary respect.

    This chunker creates overlapping chunks of approximately chunk_size tokens,
    respecting sentence and paragraph boundaries to maintain semantic coherence.
    It uses tiktoken for accurate token counting matching OpenAI's embedding models.

    CRITICAL PATTERNS:
    1. Tiktoken encoding: Matches text-embedding-3-small token counting
    2. Sentence boundaries: Splits on [.!?] followed by whitespace
    3. Paragraph boundaries: Falls back to \\n\\n for very long sentences
    4. Overlap: Maintains 50 token overlap for context continuity
    5. Thread pool: Runs CPU-intensive chunking in thread pool (Gotcha #4)

    Usage:
        chunker = TextChunker(chunk_size=500, overlap=50)

        # Async chunking (recommended)
        chunks = await chunker.chunk_text(long_text)

        # Sync chunking (for testing)
        chunks = chunker.chunk_text_sync(long_text)

        # Process chunks
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_index}: {chunk.token_count} tokens")

    Edge cases handled:
    - Empty text: Returns empty list
    - Very short text: Returns single chunk
    - Very long sentences: Falls back to paragraph boundaries
    - No sentence/paragraph boundaries: Character-based chunking

    Attributes:
        chunk_size: Target tokens per chunk (default 500)
        overlap: Tokens to overlap between chunks (default 50)
        encoding: tiktoken encoding for text-embedding-3-small
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """Initialize TextChunker.

        Args:
            chunk_size: Target number of tokens per chunk (default: 500)
            overlap: Number of tokens to overlap between chunks (default: 50)

        Raises:
            ValueError: If chunk_size <= overlap or either value is negative
        """
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap must be non-negative, got {overlap}")
        if overlap >= chunk_size:
            raise ValueError(
                f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

        # Initialize tiktoken encoding for text-embedding-3-small
        # This ensures token counts match OpenAI's embedding API
        try:
            self.encoding = tiktoken.encoding_for_model("text-embedding-3-small")
            logger.info(
                f"TextChunker initialized: chunk_size={chunk_size}, "
                f"overlap={overlap}, encoding={self.encoding.name}"
            )
        except Exception as e:
            logger.error(f"Failed to load tiktoken encoding: {e}")
            raise

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            int: Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences respecting common boundaries.

        Splits on:
        - Period followed by space and capital letter: ". A"
        - Question mark followed by space: "? "
        - Exclamation mark followed by space: "! "
        - Newline boundaries for paragraph breaks

        Args:
            text: Text to split

        Returns:
            list[str]: List of sentences (with trailing whitespace preserved)
        """
        # Split on sentence boundaries while preserving the delimiter
        # Pattern: (?<=[.!?]) means "preceded by .!?"
        #          \s+ means "followed by whitespace"
        #          (?=[A-Z]) means "followed by capital letter" (lookahead)
        # We also split on paragraph boundaries (\n\n+)
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?:\n\n+)", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs (fallback for very long sentences).

        Args:
            text: Text to split

        Returns:
            list[str]: List of paragraphs
        """
        paragraphs = re.split(r"\n\n+", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _create_chunk_with_overlap(
        self,
        sentences: list[str],
        start_idx: int,
        char_offset: int,
    ) -> tuple[list[str], int, int]:
        """Create a chunk from sentences starting at start_idx.

        Accumulates sentences until chunk_size is reached, then returns.
        Does not add overlap here (overlap is added when starting next chunk).

        Args:
            sentences: List of sentences to chunk from
            start_idx: Index to start accumulating from
            char_offset: Character offset in original text

        Returns:
            tuple: (selected_sentences, next_start_idx, char_offset_used)
        """
        chunk_sentences = []
        current_tokens = 0
        chars_used = 0

        for i in range(start_idx, len(sentences)):
            sentence = sentences[i]
            sentence_tokens = self._count_tokens(sentence)

            # Check if adding this sentence would exceed chunk_size
            if current_tokens + sentence_tokens > self.chunk_size and chunk_sentences:
                # Chunk is full, stop here
                break

            # Add sentence to chunk
            chunk_sentences.append(sentence)
            current_tokens += sentence_tokens
            chars_used += len(sentence) + 1  # +1 for space separator

            # If we've reached a good chunk size, stop
            if current_tokens >= self.chunk_size:
                break

        # Calculate next start index (with overlap)
        next_start_idx = i + 1 if i < len(sentences) else len(sentences)

        return chunk_sentences, next_start_idx, chars_used

    def _find_overlap_start_idx(
        self,
        sentences: list[str],
        end_idx: int,
    ) -> int:
        """Find the starting index for the next chunk with overlap.

        Works backwards from end_idx to find where overlap should start.

        Args:
            sentences: List of sentences
            end_idx: Index where previous chunk ended

        Returns:
            int: Starting index for next chunk (including overlap)
        """
        if end_idx <= 0 or self.overlap == 0:
            return end_idx

        overlap_tokens = 0
        overlap_start_idx = end_idx

        # Work backwards to accumulate overlap tokens
        for i in range(end_idx - 1, -1, -1):
            sentence_tokens = self._count_tokens(sentences[i])

            if overlap_tokens + sentence_tokens > self.overlap:
                # We have enough overlap
                break

            overlap_tokens += sentence_tokens
            overlap_start_idx = i

        return overlap_start_idx

    def chunk_text_sync(self, text: str) -> list[Chunk]:
        """Synchronously chunk text into semantic chunks.

        This is the CPU-intensive implementation that runs in a thread pool
        when called via chunk_text(). It implements the core chunking logic.

        Process:
        1. Handle edge cases (empty, very short text)
        2. Split into sentences
        3. Accumulate sentences into chunks of ~chunk_size tokens
        4. Add overlap between chunks (last 50 tokens of previous chunk)
        5. Fall back to paragraph splitting for very long sentences
        6. Return chunks with metadata

        Args:
            text: Text to chunk

        Returns:
            list[Chunk]: List of chunks with metadata

        Example:
            chunker = TextChunker(chunk_size=500, overlap=50)
            chunks = chunker.chunk_text_sync(document_text)
            print(f"Created {len(chunks)} chunks")
        """
        # Edge case: Empty or whitespace-only text
        if not text or not text.strip():
            logger.debug("Empty text provided, returning empty chunk list")
            return []

        text = text.strip()
        total_tokens = self._count_tokens(text)

        # Edge case: Very short text (less than chunk_size)
        if total_tokens <= self.chunk_size:
            logger.debug(
                f"Text is only {total_tokens} tokens, returning single chunk"
            )
            return [
                Chunk(
                    chunk_index=0,
                    text=text,
                    token_count=total_tokens,
                    start_offset=0,
                    end_offset=len(text),
                )
            ]

        # Split into sentences
        sentences = self._split_into_sentences(text)

        if not sentences:
            # Fallback: Split into paragraphs
            logger.warning("No sentence boundaries found, falling back to paragraphs")
            sentences = self._split_into_paragraphs(text)

        if not sentences:
            # Ultimate fallback: Treat entire text as one sentence
            logger.warning("No boundaries found, treating as single sentence")
            sentences = [text]

        # Create chunks with overlap
        chunks: list[Chunk] = []
        sentence_idx = 0
        char_offset = 0

        while sentence_idx < len(sentences):
            # If this is not the first chunk, add overlap
            if chunks:
                # Find where overlap should start
                overlap_start_idx = self._find_overlap_start_idx(
                    sentences, sentence_idx
                )

                # Adjust char_offset to account for overlap
                if overlap_start_idx < sentence_idx:
                    # Calculate character offset for overlap start
                    overlap_text = " ".join(sentences[overlap_start_idx:sentence_idx])
                    char_offset -= len(overlap_text) + 1

                sentence_idx = overlap_start_idx

            # Create chunk starting from sentence_idx
            chunk_sentences, next_idx, chars_used = self._create_chunk_with_overlap(
                sentences,
                sentence_idx,
                char_offset,
            )

            if not chunk_sentences:
                # Edge case: Single sentence too long, force split
                logger.warning(
                    f"Sentence at index {sentence_idx} exceeds chunk_size, "
                    f"forcing character-based split"
                )
                sentence = sentences[sentence_idx]
                # Take approximately chunk_size tokens worth of characters
                # Rough heuristic: 1 token ≈ 4 characters
                split_chars = self.chunk_size * 4
                chunk_text = sentence[:split_chars]
                chunk_token_count = self._count_tokens(chunk_text)

                chunks.append(
                    Chunk(
                        chunk_index=len(chunks),
                        text=chunk_text,
                        token_count=chunk_token_count,
                        start_offset=char_offset,
                        end_offset=char_offset + len(chunk_text),
                    )
                )

                # Update for next iteration
                sentence_idx += 1
                char_offset += len(chunk_text)
                continue

            # Build chunk text
            chunk_text = " ".join(chunk_sentences)
            chunk_token_count = self._count_tokens(chunk_text)

            chunks.append(
                Chunk(
                    chunk_index=len(chunks),
                    text=chunk_text,
                    token_count=chunk_token_count,
                    start_offset=char_offset,
                    end_offset=char_offset + chars_used,
                )
            )

            # Update for next iteration
            sentence_idx = next_idx
            char_offset += chars_used

        logger.info(
            f"Created {len(chunks)} chunks from {total_tokens} tokens "
            f"(avg {total_tokens / len(chunks):.1f} tokens/chunk)"
        )

        return chunks

    async def chunk_text(
        self,
        text: str,
        executor: Optional[ThreadPoolExecutor] = None,
    ) -> list[Chunk]:
        """Asynchronously chunk text into semantic chunks.

        This is a thin async wrapper around chunk_text_sync() that runs
        the CPU-intensive chunking in a thread pool to avoid blocking the
        event loop (Gotcha #4: CPU-intensive operations block event loop).

        Args:
            text: Text to chunk
            executor: Optional thread pool executor (uses default if None)

        Returns:
            list[Chunk]: List of chunks with metadata

        Example:
            chunker = TextChunker(chunk_size=500, overlap=50)
            chunks = await chunker.chunk_text(document_text)

            for chunk in chunks:
                print(f"Chunk {chunk.chunk_index}: {chunk.token_count} tokens")
                embedding = await embed_text(chunk.text)
        """
        loop = asyncio.get_event_loop()

        # Run CPU-intensive chunking in thread pool
        chunks = await loop.run_in_executor(
            executor,
            self.chunk_text_sync,
            text,
        )

        return chunks
