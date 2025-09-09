"""
Base Agent class for TripSmith Multi-Agent Travel Planner
Provides common functionality for all specialized agents
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import json

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel

from schemas import AgentResponse, SearchRequest


class BaseAgent(ABC):
    """Base class for all specialized agents in the TripSmith system"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize the base agent
        
        Args:
            name: Agent name for identification
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.name = name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"OpenAI API key required for {self.name}")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        # Configure logging
        logger.add(
            f"logs/{self.name.lower()}_agent.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        logger.info(f"Initialized {self.name} agent")
    
    @abstractmethod
    async def process_request(self, request: SearchRequest) -> AgentResponse:
        """
        Process a search request and return a standardized response
        
        Args:
            request: Standardized search request
            
        Returns:
            AgentResponse with results and reasoning
        """
        pass
    
    def create_response(
        self,
        success: bool,
        data: Any = None,
        error_message: Optional[str] = None,
        reasoning: Optional[str] = None
    ) -> AgentResponse:
        """
        Create a standardized agent response
        
        Args:
            success: Whether the operation was successful
            data: Response data
            error_message: Error message if failed
            reasoning: Agent's reasoning for decisions
            
        Returns:
            Standardized AgentResponse
        """
        return AgentResponse(
            agent_name=self.name,
            success=success,
            data=data,
            error_message=error_message,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    async def call_llm(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI assistant.",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Make a call to the OpenAI API
        
        Args:
            prompt: User prompt
            system_message: System message
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            LLM response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            logger.debug(f"{self.name} LLM call successful")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"{self.name} LLM call failed: {str(e)}")
            raise
    
    def log_activity(self, message: str, level: str = "INFO"):
        """
        Log agent activity with standardized format
        
        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        log_message = f"[{self.name}] {message}"
        
        if level.upper() == "DEBUG":
            logger.debug(log_message)
        elif level.upper() == "INFO":
            logger.info(log_message)
        elif level.upper() == "WARNING":
            logger.warning(log_message)
        elif level.upper() == "ERROR":
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    def validate_request(self, request: SearchRequest) -> bool:
        """
        Validate incoming search request
        
        Args:
            request: Search request to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if not request.destination:
                self.log_activity("Invalid request: missing destination", "ERROR")
                return False
            
            if request.start_date >= request.end_date:
                self.log_activity("Invalid request: end_date must be after start_date", "ERROR")
                return False
            
            if request.travelers < 1:
                self.log_activity("Invalid request: travelers must be at least 1", "ERROR")
                return False
            
            self.log_activity(f"Request validated successfully: {request.destination}")
            return True
            
        except Exception as e:
            self.log_activity(f"Request validation failed: {str(e)}", "ERROR")
            return False
    
    def format_data_for_llm(self, data: Any) -> str:
        """
        Format data for LLM consumption
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        if isinstance(data, BaseModel):
            return data.model_dump_json(indent=2)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2, default=str)
        elif isinstance(data, list):
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)
    
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted JSON dict or None
        """
        try:
            # Look for JSON blocks in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
            return None
            
        except json.JSONDecodeError:
            self.log_activity("Failed to extract JSON from LLM response", "WARNING")
            return None
