# utils/project_manager.py

from pathlib import Path
import shutil
import os
import logging
from datetime import datetime

def setup_logger(log_folder: Path) -> logging.Logger:
    """
    Sets up a logger that writes to a file in the specified log_folder.
    The log file is prefixed with the current date and hour (e.g., project_2024-12-03_04.log).
    If the log file for the current hour exists, logs are appended; otherwise, a new file is created.

    Args:
        log_folder (Path): The folder where the log file will be stored.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure the log directory exists
    log_folder.mkdir(parents=True, exist_ok=True)

    # Initialize the logger
    logger = logging.getLogger("ProjectLogger")
    logger.setLevel(logging.DEBUG)

    # Avoid adding multiple handlers if the logger is already configured
    if not logger.handlers:
        # Generate log file name with current date and hour
        current_time = datetime.now()
        log_filename = f"project_{current_time.strftime('%Y-%m-%d_%H')}.log"
        log_file_path = log_folder / log_filename

        # Create file handler which logs debug and higher level messages
        fh = logging.FileHandler(log_file_path, encoding='utf-8', mode='a')  # 'a' for append
        fh.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        logger.debug(f"Logger initialized. Logs are being written to {log_file_path}")
    else:
        # If handlers already exist, update the log file if the hour has changed
        existing_file_handler = next((h for h in logger.handlers if isinstance(h, logging.FileHandler)), None)
        if existing_file_handler:
            current_time = datetime.now()
            expected_filename = f"project_{current_time.strftime('%Y-%m-%d_%H')}.log"
            expected_file_path = log_folder / expected_filename

            # If the current log file is not the expected one, switch to the new file
            if Path(existing_file_handler.baseFilename).name != expected_filename:
                # Remove the old file handler
                logger.removeHandler(existing_file_handler)
                existing_file_handler.close()

                # Create a new file handler for the new hour
                new_fh = logging.FileHandler(expected_file_path, encoding='utf-8', mode='a')
                new_fh.setLevel(logging.DEBUG)
                new_fh.setFormatter(formatter)
                logger.addHandler(new_fh)

                logger.debug(f"Switched logger to new log file: {expected_file_path}")

    return logger

class ProjectManager:
    def __init__(
        self,
        project_path: Path,
        ignored_dirs: list = None,
        ignored_files: list = None,
        ignored_path_substrings: list = None
    ):
        """
        Initialize the ProjectManager with the given project path.

        Args:
            project_path (Path): The root path of the project to analyze.
        """
        self.project_path = project_path.resolve()
        self.workspace_folder = Path('./workspace').resolve()
        self.analysis_folder = self.workspace_folder / self.project_path.name
        self.code_summary_folder = self.analysis_folder / "code_summaries"
        # Remove logger initialization from here
        # self.logger = setup_logger(self.analysis_folder)
        # self.logger.info(f"ProjectManager initialized for project: {self.project_path}")

         # Initialize ignored patterns
        self.ignored_dirs = ignored_dirs if ignored_dirs else []
        self.ignored_files = ignored_files if ignored_files else []
        self.ignored_path_substrings = ignored_path_substrings if ignored_path_substrings else []


    def initialize_logger(self):
        """
        Initialize the logger after workspace setup.
        """
        self.logger = setup_logger(self.analysis_folder)
        self.logger.info(f"ProjectManager initialized for project: {self.project_path}")
    def close_logger(self):
        """
        Closes all handlers associated with the logger.
        """
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
    def setup_workspace(self, clean_existing: bool = False):
        """
        Create the workspace, analysis, and code_summaries folders.
        Optionally clean existing analysis and code_summary folders.

        Args:
            clean_existing (bool): If True, removes existing analysis and code_summary folders before creating new ones.
        """
        self.logger.info("Setting up workspace...")

        if self.workspace_folder.exists():
            self.logger.info(f"Workspace folder already exists at {self.workspace_folder}")
            if clean_existing:
                self.logger.info(f"Cleaning existing analysis folder at {self.analysis_folder}")
                # Close the logger before deleting
                self.close_logger()
                shutil.rmtree(self.analysis_folder)
                self.logger.info(f"Removed existing analysis folder at {self.analysis_folder}")
        else:
            self.logger.info(f"Creating workspace folder at {self.workspace_folder}")
            self.workspace_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created workspace folder at {self.workspace_folder}")

        # Create analysis_folder
        if not self.analysis_folder.exists():
            self.logger.info(f"Creating analysis folder at {self.analysis_folder}")
            self.analysis_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created analysis folder at {self.analysis_folder}")
        else:
            self.logger.info(f"Analysis folder already exists at {self.analysis_folder}")

        # Create code_summary_folder
        if not self.code_summary_folder.exists():
            self.logger.info(f"Creating code summaries folder at {self.code_summary_folder}")
            self.code_summary_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created code summaries folder at {self.code_summary_folder}")
        else:
            self.logger.info(f"Code summaries folder already exists at {self.code_summary_folder}")
    def get_all_python_files(
        self,
        ignored_dirs: list = None,
        ignored_files: list = None,
        ignored_path_substrings: list = None
    ) -> list:
        """
        Recursively retrieve all Python (.py) files in the project folder,
        excluding those in ignored directories, with ignored file names, or containing ignored substrings in their paths.

        Args:
            ignored_dirs (list, optional): List of directory names to ignore. Defaults to None.
            ignored_files (list, optional): List of file names to ignore. Defaults to None.
            ignored_path_substrings (list, optional): List of substrings in paths to ignore. Defaults to None.

        Returns:
            list: List of Path objects representing Python files.
        """
        ignored_dirs = ignored_dirs if ignored_dirs else self.ignored_dirs
        ignored_files = ignored_files if ignored_files else self.ignored_files
        ignored_path_substrings = ignored_path_substrings if ignored_path_substrings else self.ignored_path_substrings

        all_py_files = list(self.project_path.rglob('*.py'))
        filtered_py_files = []

        for py_file in all_py_files:
            relative_path = py_file.relative_to(self.project_path)

            # Check for ignored directories
            if any(part in ignored_dirs for part in py_file.parts):
                self.logger.debug(f"Ignoring {py_file} because it is in an ignored directory.")
                continue

            # Check for ignored file names
            if py_file.name in ignored_files:
                self.logger.debug(f"Ignoring {py_file} because it is an ignored file.")
                continue

            # Check for ignored path substrings
            if any(substring in str(relative_path) for substring in ignored_path_substrings):
                self.logger.debug(f"Ignoring {py_file} because its path contains an ignored substring.")
                continue

            filtered_py_files.append(py_file)

        # self.logger.info(f"Found {len(filtered_py_files)} Python files after applying ignore filters.")
        return filtered_py_files
    def get_project_folder(self) -> Path:
        """
        Return the path to the project folder.

        Returns:
            Path: Path to the project folder.
        """
        return self.project_path

    def get_analysis_folder(self) -> Path:
        """
        Return the path to the analysis folder.

        Returns:
            Path: Path to the analysis folder.
        """
        return self.analysis_folder

    def get_code_summary_folder(self) -> Path:
        """
        Return the path to the code summaries folder.

        Returns:
            Path: Path to the code summaries folder.
        """
        return self.code_summary_folder

    

    def get_code_summary_file_path(self, relative_path: Path) -> Path:
        """
        Given a file's relative path, return the corresponding code summary file path.

        Args:
            relative_path (Path): Relative path of the original Python file from the project root.

        Returns:
            Path: Path to the corresponding code summary JSON file.
        """
        summary_relative_path = relative_path.with_suffix('.json')
        summary_file_path = self.code_summary_folder / summary_relative_path
        return summary_file_path

    def ensure_code_summary_path(self, summary_file_path: Path):
        """
        Ensure that the parent directories for the summary file exist.

        Args:
            summary_file_path (Path): Path to the summary JSON file.
        """
        summary_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Ensured existence of directory: {summary_file_path.parent}")

    def clean_analysis_folder(self):
        """
        Remove the analysis and code summaries folders.

        **Use with caution:** This will delete all existing summaries.
        """
        if self.analysis_folder.exists():
            self.logger.info(f"Cleaning analysis folder at {self.analysis_folder}")
            shutil.rmtree(self.analysis_folder)
            self.logger.info(f"Removed analysis folder at {self.analysis_folder}")
        else:
            self.logger.info(f"No analysis folder found at {self.analysis_folder} to clean.")

    def get_relative_path(self, file_path: Path) -> Path:
        """
        Get the relative path of a file with respect to the project folder.

        Args:
            file_path (Path): Absolute path of the file.

        Returns:
            Path: Relative path from the project folder.
        """
        try:
            relative_path = file_path.relative_to(self.project_path)
            return relative_path
        except ValueError:
            self.logger.error(f"File path {file_path} is not within the project folder {self.project_path}")
            raise

    def get_all_code_summary_files(self) -> list:
        """
        Recursively retrieve all code summary JSON files in the code summaries folder.

        Returns:
            list: List of Path objects representing code summary JSON files.
        """
        summary_files = list(self.code_summary_folder.rglob('*.json'))
        self.logger.info(f"Found {len(summary_files)} code summary JSON files.")
        return summary_files
