from typing import Dict

import yaml

from src.common.logging import logger


class TemplateManager:
    """
    Simple template manager for loading and filling text templates.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initialize the TemplateManager with a configuration file.
        """
        self.config = self._load_yaml(config_path)

    def _load_yaml(self, filename: str) -> Dict:
        """
        Load a YAML configuration file.
        """
        try:
            with open(filename, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {filename}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file '{filename}': {e}")
            raise

    def create_template(self, role: str, action: str) -> Dict[str, str]:
        """
        Load system and user templates for a given role and action.

        Args:
            role: Template role (e.g., 'coordinator', 'delegate')
            action: Template action (e.g., 'route', 'consolidate')

        Returns:
            Dictionary with 'system' and 'user' template content
        """
        try:
            template_config = self.config[role][action]

            return {
                "system": self._load_template_file(template_config["system_instructions"]),
                "user": self._load_template_file(template_config["user_instructions"]),
            }
        except KeyError as e:
            logger.error(f"Template configuration not found: {role}.{action} - {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating template for {role}.{action}: {e}")
            raise

    def _load_template_file(self, template_path: str) -> str:
        """
        Load template content from a file.
        """
        try:
            with open(template_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading template file {template_path}: {e}")
            raise

    @staticmethod
    def fill_template(template_content: str, **kwargs: str) -> str:
        """
        Fill template placeholders with provided values.

        Args:
            template_content: Template string with {placeholder} markers
            **kwargs: Values to substitute for placeholders

        Returns:
            Template with placeholders replaced
        """
        try:
            filled_template = template_content
            for key, value in kwargs.items():
                placeholder = f"{{{key}}}"
                filled_template = filled_template.replace(placeholder, str(value))
            return filled_template
        except Exception as e:
            logger.error(f"Error filling template: {e}")
            raise
