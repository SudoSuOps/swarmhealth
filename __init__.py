"""
Diabetes Companion AI

Built by someone who lives it. For those who need it. FREE.

Usage:
    from diabetes_companion import DiabetesCompanion

    companion = DiabetesCompanion()
    response = companion.chat("I'm struggling today")
    print(response)
"""

from .diabetes_companion import DiabetesCompanion

__version__ = "1.0.0"
__author__ = "Diabetes Companion AI Contributors"
__all__ = ["DiabetesCompanion"]
