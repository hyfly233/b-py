import logging

import click

from a2a_demo.agents.agent import TestOllamaAgent
from a2a_demo.agents.task_manager import AgentTaskManager
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
            id="test_skill",
            name="Test Skill",
            description="Test Skill",
            tags=["test"],
            examples=["Test echo Hello World"],
        )
        agent_card = AgentCard(
            name="Test Agent Card",
            description="Test Agent Card",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=TestOllamaAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TestOllamaAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        # 创建A2A服务器
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=TestOllamaAgent()),
            host=host,
            port=port,
        )

        logger.info("A2A服务器创建完成")

        server.start()
    except Exception as e:
        logger.error(f"服务器启动时发生错误: {e}")
        exit(1)


if __name__ == '__main__':
    main()
