"""
Export utilities for different tablature formats.
"""

from typing import List
from .tab_generator import Tablature, Note


class TabExporter:
    """
    Handles exporting tablature to various formats.
    """
    
    @staticmethod
    def to_ascii(tab: Tablature, width: int = 80) -> str:
        """
        Export tablature as ASCII text.
        
        Args:
            tab: Tablature object
            width: Character width of output
            
        Returns:
            ASCII formatted tablature
        """
        lines = [
            "=" * width,
            f"Title: {tab.title}".center(width),
            f"Tuning: {'-'.join(tab.tuning)}".center(width),
            "=" * width,
            ""
        ]
        
        # Generate tab lines
        tab_content = tab._generate_ascii_tab()
        lines.extend(tab_content)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(tab: Tablature) -> dict:
        """
        Export tablature as JSON-compatible dictionary.
        
        Args:
            tab: Tablature object
            
        Returns:
            Dictionary representation
        """
        return {
            "title": tab.title,
            "tuning": tab.tuning,
            "notes": [
                {
                    "string": note.string,
                    "fret": note.fret,
                    "start_time": note.start_time,
                    "duration": note.duration
                }
                for note in tab.notes
            ]
        }
    
    @staticmethod
    def to_markdown(tab: Tablature) -> str:
        """
        Export tablature as Markdown.
        
        Args:
            tab: Tablature object
            
        Returns:
            Markdown formatted tablature
        """
        lines = [
            f"# {tab.title}",
            "",
            f"**Tuning:** {'-'.join(tab.tuning)}",
            "",
            "```",
        ]
        
        tab_content = tab._generate_ascii_tab()
        lines.extend(tab_content)
        lines.append("```")
        
        return "\n".join(lines)
