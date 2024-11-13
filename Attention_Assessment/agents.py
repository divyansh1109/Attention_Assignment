from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class BaseAgent:
    def __init__(self, model_name="distilgpt2"):
        self.model = None
        self.tokenizer = None
        self.load_model(model_name)

    def load_model(self, model_name):
        if self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                device_map="cpu",
                low_cpu_mem_usage=True
            )

    def generate_response(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(
            inputs['input_ids'], 
            max_new_tokens=100,  
            do_sample=True, 
            top_p=0.9, 
            top_k=50,  
            temperature=0.7
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

class FutureWorksAgent(BaseAgent):
    def suggest_future_works(self, context):
        prompt = f"Based on the research contributions, suggest future research directions:\n{context}\nFuture Work Ideas:"
        return self.generate_response(prompt)

class QnAAgent(BaseAgent):
    def answer_question(self, question, context):
        prompt = f"Question: {question}\nContext: {context}"
        return self.generate_response(prompt)
