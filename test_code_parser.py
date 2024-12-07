# # test_code_parser.py

# import os
# from pathlib import Path
# from utils.code_parser import CodeParser

# def create_sample_project(project_path: Path):
#     """
#     Creates a sample Python project structure for testing.
#     """
#     # Create directories
#     (project_path / "module").mkdir(parents=True, exist_ok=True)
#     (project_path / "utils").mkdir(parents=True, exist_ok=True)

#     # Create sample Python files
#     main_py = project_path / "main.py"
#     module_py = project_path / "module" / "module.py"
#     utils_py = project_path / "utils" / "utils.py"

#     main_py.write_text("""
# def main_function():
#     pass

# class MainClass:
#     def method_one(self):
#         pass

#     def method_two(self):
#         pass
# """, encoding="utf-8")

#     module_py.write_text("""
# def module_function():
#     pass

# class ModuleClass:
#     def module_method(self):
#         pass
# """, encoding="utf-8")

#     utils_py.write_text("""
# def util_function():
#     pass
# """, encoding="utf-8")

# def main():
#     # Define the path for the sample project
#     sample_project_path = Path("./sample_project")
#     print(f"sample_project_path: {sample_project_path} ")
#     print(f"Sample project created at {sample_project_path.resolve()}")


#     # Initialize the CodeParser
#     parser = CodeParser(project_path=sample_project_path)
    
#     # Extract symbols
#     symbols = parser.extract_symbols()
#     print(f"symbols {symbols}")
#     # Define the output file path
#     output_file = Path("parsed_symbols.txt")
    
#     # Write symbols to the output file
#     parser.write_symbols_to_file(symbols, output_file)
#     print(f"Symbols written to {output_file.resolve()}")

#     # Optionally, display the output file content
#     print("\n--- Parsed Symbols ---")
#     with open(output_file, "r", encoding="utf-8") as f:
#         print(f.read())

# if __name__ == "__main__":
#     main()
