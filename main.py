import argparse
from config import AgentConfig
from core.agent import MobileAgent


def main():
    parser = argparse.ArgumentParser(description='Mobile Agent - Automated mobile device control')
    
    parser.add_argument('--config', type=str, required=True, help='Path to config file (JSON or YAML)')
    parser.add_argument('--instruction', type=str, required=True, help='Task instruction')
    
    args = parser.parse_args()
    
    config = AgentConfig.from_file(args.config)
    
    message_builder = config.create_message_builder()
    model_client = config.create_model_client()
    response_parser = config.create_response_parser()
    
    agent = MobileAgent(
        config=config,
        message_builder=message_builder,
        model_client=model_client,
        response_parser=response_parser
    )
    
    history = agent.run(args.instruction)
    
    print(f"\nExecution summary:")
    print(f"Total steps: {len(history)}")
    for i, step in enumerate(history, 1):
        print(f"  Step {i}: {step['subtask']}")


if __name__ == "__main__":
    main()
