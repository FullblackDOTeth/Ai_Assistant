#!/usr/bin/env python3

import os
import json
import logging
import inspect
import ast
import re
from typing import Dict, List, Optional, Union
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader
import markdown
import mdx_math
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import openapi_spec_validator
from docstring_parser import parse as parse_docstring

class DocumentationGenerator:
    def __init__(self, config_path: str):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.template_env = self._setup_templates()
        self._setup_markdown()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for documentation generator."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('documentation.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DocumentationGenerator')

    def _load_config(self, config_path: str) -> Dict:
        """Load documentation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_templates(self) -> Environment:
        """Set up Jinja2 template environment."""
        return Environment(
            loader=FileSystemLoader('docs/templates'),
            autoescape=True
        )

    def _setup_markdown(self):
        """Configure markdown extensions."""
        self.markdown = markdown.Markdown(
            extensions=[
                'extra',
                'codehilite',
                'mdx_math',
                'toc',
                'meta',
                'tables',
                'fenced_code'
            ]
        )

    def generate_api_docs(self, api_dir: str) -> Dict:
        """Generate API documentation from source code."""
        try:
            api_docs = {
                'endpoints': [],
                'models': [],
                'services': []
            }
            
            # Walk through API directory
            for root, _, files in os.walk(api_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        
                        # Parse Python file
                        with open(file_path, 'r') as f:
                            tree = ast.parse(f.read())
                        
                        # Extract API information
                        api_info = self._extract_api_info(tree, file_path)
                        
                        # Categorize information
                        if 'endpoint' in file:
                            api_docs['endpoints'].extend(api_info)
                        elif 'model' in file:
                            api_docs['models'].extend(api_info)
                        elif 'service' in file:
                            api_docs['services'].extend(api_info)
            
            return api_docs
            
        except Exception as e:
            self.logger.error(f"Failed to generate API docs: {str(e)}")
            raise

    def generate_integration_guide(self, examples_dir: str) -> Dict:
        """Generate integration guide with code examples."""
        try:
            guide = {
                'sections': [],
                'examples': []
            }
            
            # Load integration sections
            sections_path = os.path.join(examples_dir, 'sections')
            for section_file in os.listdir(sections_path):
                if section_file.endswith('.md'):
                    with open(os.path.join(sections_path, section_file), 'r') as f:
                        content = f.read()
                        guide['sections'].append({
                            'title': section_file.replace('.md', '').title(),
                            'content': self.markdown.convert(content)
                        })
            
            # Load code examples
            examples_path = os.path.join(examples_dir, 'code')
            for example_file in os.listdir(examples_path):
                with open(os.path.join(examples_path, example_file), 'r') as f:
                    content = f.read()
                    language = example_file.split('.')[-1]
                    
                    guide['examples'].append({
                        'title': example_file.replace(f'.{language}', '').title(),
                        'language': language,
                        'content': self._highlight_code(content, language)
                    })
            
            return guide
            
        except Exception as e:
            self.logger.error(f"Failed to generate integration guide: {str(e)}")
            raise

    def generate_best_practices(self, practices_dir: str) -> Dict:
        """Generate best practices documentation."""
        try:
            practices = {
                'categories': []
            }
            
            # Load best practices by category
            for category_file in os.listdir(practices_dir):
                if category_file.endswith('.md'):
                    with open(os.path.join(practices_dir, category_file), 'r') as f:
                        content = f.read()
                        practices['categories'].append({
                            'name': category_file.replace('.md', '').title(),
                            'content': self.markdown.convert(content)
                        })
            
            return practices
            
        except Exception as e:
            self.logger.error(f"Failed to generate best practices: {str(e)}")
            raise

    def generate_troubleshooting_guide(self, issues_dir: str) -> Dict:
        """Generate troubleshooting guide."""
        try:
            guide = {
                'issues': []
            }
            
            # Load issue categories
            for category_dir in os.listdir(issues_dir):
                category_path = os.path.join(issues_dir, category_dir)
                if os.path.isdir(category_path):
                    category = {
                        'name': category_dir.title(),
                        'problems': []
                    }
                    
                    # Load problems in category
                    for problem_file in os.listdir(category_path):
                        if problem_file.endswith('.md'):
                            with open(os.path.join(category_path, problem_file), 'r') as f:
                                content = f.read()
                                category['problems'].append({
                                    'title': problem_file.replace('.md', '').title(),
                                    'content': self.markdown.convert(content)
                                })
                    
                    guide['issues'].append(category)
            
            return guide
            
        except Exception as e:
            self.logger.error(f"Failed to generate troubleshooting guide: {str(e)}")
            raise

    def generate_openapi_spec(self, api_docs: Dict) -> Dict:
        """Generate OpenAPI specification."""
        try:
            spec = {
                'openapi': '3.0.0',
                'info': {
                    'title': 'Head AI API',
                    'version': '1.0.0',
                    'description': 'API documentation for Head AI platform'
                },
                'paths': {},
                'components': {
                    'schemas': {},
                    'securitySchemes': {
                        'bearerAuth': {
                            'type': 'http',
                            'scheme': 'bearer',
                            'bearerFormat': 'JWT'
                        }
                    }
                }
            }
            
            # Add endpoints
            for endpoint in api_docs['endpoints']:
                path = endpoint['path']
                method = endpoint['method'].lower()
                
                if path not in spec['paths']:
                    spec['paths'][path] = {}
                
                spec['paths'][path][method] = {
                    'summary': endpoint['summary'],
                    'description': endpoint['description'],
                    'parameters': endpoint['parameters'],
                    'requestBody': endpoint.get('request_body'),
                    'responses': endpoint['responses'],
                    'security': [{'bearerAuth': []}]
                }
            
            # Add models
            for model in api_docs['models']:
                spec['components']['schemas'][model['name']] = {
                    'type': 'object',
                    'properties': model['properties'],
                    'required': model['required']
                }
            
            # Validate spec
            openapi_spec_validator.validate_spec(spec)
            
            return spec
            
        except Exception as e:
            self.logger.error(f"Failed to generate OpenAPI spec: {str(e)}")
            raise

    def _extract_api_info(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Extract API information from Python AST."""
        api_info = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract class information
                class_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': []
                }
                
                # Parse methods
                for method in [n for n in node.body if isinstance(n, ast.FunctionDef)]:
                    method_info = {
                        'name': method.name,
                        'docstring': parse_docstring(ast.get_docstring(method)),
                        'parameters': [arg.arg for arg in method.args.args],
                        'returns': self._get_return_type(method)
                    }
                    class_info['methods'].append(method_info)
                
                api_info.append(class_info)
            
            elif isinstance(node, ast.FunctionDef):
                # Extract function information
                func_info = {
                    'name': node.name,
                    'docstring': parse_docstring(ast.get_docstring(node)),
                    'parameters': [arg.arg for arg in node.args.args],
                    'returns': self._get_return_type(node)
                }
                api_info.append(func_info)
        
        return api_info

    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation from function."""
        if node.returns:
            return ast.unparse(node.returns)
        return 'Any'

    def _highlight_code(self, code: str, language: str) -> str:
        """Highlight code using Pygments."""
        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style='monokai')
        return pygments.highlight(code, lexer, formatter)

    def generate_documentation(self, output_dir: str):
        """Generate complete documentation."""
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate API documentation
            api_docs = self.generate_api_docs('api')
            spec = self.generate_openapi_spec(api_docs)
            
            with open(os.path.join(output_dir, 'openapi.json'), 'w') as f:
                json.dump(spec, f, indent=2)
            
            # Generate integration guide
            guide = self.generate_integration_guide('docs/examples')
            
            # Generate best practices
            practices = self.generate_best_practices('docs/best_practices')
            
            # Generate troubleshooting guide
            troubleshooting = self.generate_troubleshooting_guide('docs/issues')
            
            # Render documentation
            template = self.template_env.get_template('documentation.html')
            html = template.render(
                api_docs=api_docs,
                guide=guide,
                practices=practices,
                troubleshooting=troubleshooting
            )
            
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(html)
            
            self.logger.info(f"Documentation generated successfully in {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate documentation: {str(e)}")
            raise

def main():
    """Main entry point for documentation generator."""
    try:
        generator = DocumentationGenerator('config/documentation.yml')
        generator.generate_documentation('docs/build')
        
        print("Documentation generated successfully")
        
    except Exception as e:
        print(f"Documentation generation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
