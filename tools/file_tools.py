# file_tools.py
# agentic_ai_framework/tools/file_tools.py
import os
import asyncio
from tools import BaseTool
from utils.logger import setup_logger
from pydantic import BaseModel, Field

logger = setup_logger(__name__)

class ReadFileArgs(BaseModel):
    file_path: str = Field(..., description="The path to the file to read.")

async def read_file_func(file_path: str) -> str:
    """Reads the content of a text file."""
    try:
        await asyncio.sleep(0.5) # Simulate delay
        with open(file_path, 'r') as f:
            content = f.read()
        logger.info(f"Read content from file: {file_path}")
        return content
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return "Error: File not found."
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {e}"

ReadFileTool = BaseTool(
    name="read_file",
    description="Reads the content of a text file from the local file system.",
    func=read_file_func,
    schema=ReadFileArgs.model_json_schema()
)

class WriteFileArgs(BaseModel):
    file_path: str = Field(..., description="The path to the file to write to.")
    content: str = Field(..., description="The content to write into the file.")
    append: bool = Field(False, description="If true, content is appended; otherwise, file is overwritten.")

async def write_file_func(file_path: str, content: str, append: bool = False) -> str:
    """Writes content to a file. Overwrites by default, appends if `append` is True."""
    mode = 'a' if append else 'w'
    try:
        await asyncio.sleep(0.5) # Simulate delay
        with open(file_path, mode) as f:
            f.write(content)
        logger.info(f"Content {'appended to' if append else 'written to'} file: {file_path}")
        return "File written successfully."
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return f"Error writing file: {e}"

WriteFileTool = BaseTool(
    name="write_file",
    description="Writes or appends content to a file on the local file system.",
    func=write_file_func,
    schema=WriteFileArgs.model_json_schema()
)

class ListDirectoryArgs(BaseModel):
    path: str = Field(".", description="The path to the directory to list (defaults to current directory).")

async def list_directory_func(path: str = ".") -> str:
    """Lists files and directories in a given path."""
    try:
        await asyncio.sleep(0.5) # Simulate delay
        items = os.listdir(path)
        return "Contents of directory:\n" + "\n".join(items)
    except FileNotFoundError:
        logger.warning(f"Directory not found: {path}")
        return "Error: Directory not found."
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return f"Error listing directory: {e}"

ListDirectoryTool = BaseTool(
    name="list_directory",
    description="Lists the files and subdirectories within a specified directory.",
    func=list_directory_func,
    schema=ListDirectoryArgs.model_json_schema()
)