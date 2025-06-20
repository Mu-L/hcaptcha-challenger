import asyncio
import json

from playwright.async_api import async_playwright, Page

from hcaptcha_challenger import AgentV, AgentConfig, CaptchaResponse
from hcaptcha_challenger import types
from hcaptcha_challenger.utils import SiteKey


async def challenge(page: Page) -> AgentV:
    """Automates the process of solving an hCaptcha challenge."""
    # [IMPORTANT] Initialize the Agent before triggering hCaptcha
    agent_config = AgentConfig(
        # Skip image drag-and-drop & image-label-area-select(single) challenge
        ignore_request_types=[
            types.RequestType.IMAGE_DRAG_DROP,
            types.ChallengeTypeEnum.IMAGE_LABEL_SINGLE_SELECT,
        ],
        # Disable special challenge
        ignore_request_questions=["Drag each segment to its position on the line"],
        # Change default models
        IMAGE_CLASSIFIER_MODEL='gemini-2.5-pro',
        SPATIAL_PATH_REASONER_MODEL='gemini-2.5-pro',
        SPATIAL_POINT_REASONER_MODEL='gemini-2.5-pro',
    )
    agent = AgentV(page=page, agent_config=agent_config)

    # In your real-world workflow, you may need to replace the `click_checkbox()`
    # It may be to click the Login button or the Submit button to trigger challenge
    await agent.robotic_arm.click_checkbox()

    # Wait for the challenge to appear and be ready for solving
    await agent.wait_for_challenge()

    return agent


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="tmp/.cache/user_data", headless=False, locale="en-US"
        )

        page = await context.new_page()

        await page.goto(SiteKey.as_site_link(SiteKey.discord))

        # --- When you encounter hCaptcha in your workflow ---
        agent: AgentV = await challenge(page)
        if agent.cr_list:
            cr: CaptchaResponse = agent.cr_list[-1]
            print(json.dumps(cr.model_dump(by_alias=True), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
