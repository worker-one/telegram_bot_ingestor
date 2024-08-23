from omegaconf import OmegaConf
from telegram_bot_ingestor.service.fireworksai import FireworksLLM

config = OmegaConf.load("./tests/unit/conf/config.yaml")


def test_run():
	model_name = config.llm.model_name
	prompt_template = config.llm.prompt_template
	llm = FireworksLLM(model_name, prompt_template)
	product_name = "Saucony Kinvara 14 man 41 yellow/black"
	column_names = ["brand", "model", "sex", "color", "size", "price"]

	actual_prompt = llm.prompt_template.format(
		product_name=product_name,
        column_names=','.join(column_names)
	)

	assert product_name in actual_prompt
	assert column_names[0] in actual_prompt