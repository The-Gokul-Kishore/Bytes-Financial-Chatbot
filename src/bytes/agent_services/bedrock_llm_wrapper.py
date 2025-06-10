from langchain_core.language_models.llms import LLM
# from langchain_core.outputs import LLMResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

import boto3
import json
from typing import Optional, List
from pydantic import PrivateAttr

class BedrockLLM(LLM):
    model_id: str
    profile_name: str = "my-aws-profile"
    region_name: str = "us-west-2"

    # Private attribute (excluded from validation and serialization)
    _client: any = PrivateAttr()

    def model_post_init(self, __context) -> None:
        session = boto3.Session(
            profile_name=self.profile_name,
            region_name=self.region_name
        )
        self._client = session.client("bedrock-runtime")

    @property
    def _llm_type(self) -> str:
        return "bedrock-custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        body = {
            "prompt": prompt,
            "max_gen_len": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = self._client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        response_body = response['body'].read()
        output = json.loads(response_body)
        return output.get("generation", "[No output generated]")
