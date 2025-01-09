from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

class MemeNarrator:
    def __init__(self):
        model_name = "gpt2"
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate_narrative(self, meme_data):
        prompt = f"Create a narrative for a memecoin named {meme_data['name']} with the symbol {meme_data['symbol']}. It's known for {meme_data['description']}."
        results = self.generator(prompt, max_length=300, num_return_sequences=1, do_sample=True, temperature=0.7)
        return results[0]['generated_text']
