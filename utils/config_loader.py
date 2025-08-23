import yaml
import os


def load_config(config_path: str = os.path.join("config", "config.yaml")) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration data as a dictionary.
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
        
    print(config)
    return config

if __name__ == "__main__":
    load_config(str(os.path.join("config", "config.yaml")))