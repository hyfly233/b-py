import logging

import click

from a2a_demo.common.server import A2AServer
from a2a_demo.common.types import AgentCapabilities, AgentSkill, AgentCard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="process_reimbursement",
            name="Process Reimbursement Tool",
            description="Helps with the reimbursement process for users given the amount and purpose of the reimbursement.",
            tags=["reimbursement"],
            examples=["Can you reimburse me $20 for my lunch with the clients?"],
        )
        agent_card = AgentCard(
            name="Reimbursement Agent",
            description="This agent handles the reimbursement process for the employees given the amount and purpose of the reimbursement.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=ReimbursementAgent()),
            host=host,
            port=port,
        )
        server.start()
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == '__main__':
    main()
