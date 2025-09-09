import abc
import json
import time
from typing import Optional

# ...existing code...
import openai
# ...existing code...

from prompt.informer import load_few_shot as load_informer_few_shot
from prompt.planner import load_few_shot as load_agent_few_shot
from utils.enumeration import MODEL_TYPE, ROLE
from utils.exceptions import TokenLimitError
from utils.utils import get_model_token_limit, num_tokens_from_messages


class Assistant(abc.ABC):
    def __init__(self, sys_prompt, model_type: MODEL_TYPE, few_shot, api_config: dict) -> None:
        super().__init__()
        self.sys_prompt = sys_prompt
        self.model_type = model_type
        self.few_shot = few_shot
        self.msg_history = []

        if model_type.name.startswith("OLLAMA"):
            self.client = openai.OpenAI(api_key="ollama", base_url=api_config["api_base"], timeout=60)
        else:
            self.client = openai.OpenAI(api_key=api_config["api_key"], base_url=api_config["api_base"], timeout=60)

    @abc.abstractmethod
    def construct_few_shot_query(self, query: list):
        raise NotImplementedError()

    def ask(self, prompt: str) -> Optional[str]:
        self.msg_history.append({"role": ROLE.USER.value, "content": prompt})
        query = [{"role": ROLE.SYSTEM.value, "content": self.sys_prompt}]
        if self.few_shot:
            query = self.construct_few_shot_query(query)

        query.extend(self.msg_history)

        num_tokens = num_tokens_from_messages(query, self.model_type)
        token_limit = get_model_token_limit(self.model_type)
        if token_limit is None:
            # Per i modelli Ollama, potremmo non avere un limite predefinito,
            # quindi ne impostiamo uno generico alto per evitare l'errore.
            if self.model_type.name.startswith("OLLAMA"):
                token_limit = 8192  # Un valore di default ragionevole
            else:
                raise NotImplementedError(f"Model type {self.model_type} is not supported.")
        if num_tokens >= token_limit:
            raise TokenLimitError(num_tokens, token_limit)

        while True:
            try:
                if self.model_type in [MODEL_TYPE.GEMINI_PRO, MODEL_TYPE.GEMMA_7B_IT, MODEL_TYPE.GEMMA_3_12B, MODEL_TYPE.GEMMA_3_27B]:
                    # Gemini/Google uses a different format for messages; only 'user' and 'model' roles are allowed.
                    gemini_query = []
                    for msg in query:
                        # Force all non-assistant roles to 'user'
                        role = "model" if msg["role"] == "assistant" else "user"
                        gemini_query.append({"role": role, "parts": [msg["content"]]})

                    response = self.client.generate_content(gemini_query)
                    gpt_message_content = response.text
                    gpt_message_role = "assistant"  # Gemini API returns role as 'model'
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_type.value,
                        messages=query,  # type: ignore
                        # temperature=0.2,
                    )
                    gpt_message_content = response.choices[0].message.content
                    gpt_message_role = response.choices[0].message.role
                break
            except (
                openai.APIConnectionError,
                openai.APITimeoutError,
                openai.APIError,
                openai.RateLimitError,
                openai.InternalServerError,
                # ...existing code...
                Exception,
            ) as e:
                print(f"{e}\nRetrying...")
                time.sleep(5)

        self.msg_history.append({"role": gpt_message_role, "content": gpt_message_content})

        return gpt_message_content


class Planner(Assistant):
    def __init__(self, sys_prompt, model_type: MODEL_TYPE, few_shot, table_rep, with_informer, api_config) -> None:
        super().__init__(sys_prompt, model_type, few_shot, api_config)
        self.table_rep = table_rep
        self.with_informer = with_informer

    def construct_few_shot_query(self, query: list):
        few_shot_examples = load_agent_few_shot(self.with_informer)
        for shot in few_shot_examples:
            query.extend(shot)
        return query

    def save(self, save_dir):
        query = [{"role": ROLE.SYSTEM.value, "content": self.sys_prompt}]
        if self.few_shot:
            query = self.construct_few_shot_query(query)
        with open(save_dir / "history_agent.json", "w", encoding="utf-8") as f:
            json.dump(query + self.msg_history, f)


class Informer(Assistant):
    def __init__(self, sys_prompt, model_type: MODEL_TYPE, few_shot, api_config) -> None:
        super().__init__(sys_prompt, model_type, few_shot, api_config)

    def construct_few_shot_query(self, query: list):
        few_shot_examples = load_informer_few_shot()
        for shot in few_shot_examples:
            query.extend(shot)
        return query

    def save(self, save_dir):
        query = [{"role": ROLE.SYSTEM.value, "content": self.sys_prompt}]
        if self.few_shot:
            query = self.construct_few_shot_query(query)
        with open(save_dir / "history_informer.json", "w", encoding="utf-8") as f:
            json.dump(query + self.msg_history, f)
