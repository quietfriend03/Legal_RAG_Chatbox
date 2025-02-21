from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Use a more Mac-compatible model configuration
model_name = "kienhoang123/QR-llama3.2"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="mps" if torch.backends.mps.is_available() else "cpu",
    use_safetensors=True
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def generate_rewritten_queries(base_query, model, tokenizer, max_new_tokens=100):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = model.to(device)
    
    input_text = f"""
    ### Instruction:
    Rewrite the given query into three different variations.

    ### Input Query:
    {base_query}

    ### Rewritten Queries:
    """

    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)
    output_ids = model.generate(
        input_ids, 
        max_new_tokens=max_new_tokens, 
        do_sample=True,
        temperature=0.1,
        top_p=0.95,
        repetition_penalty=1.2
    )

    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    rewritten_part = generated_text.split("### Rewritten Queries:")[1].strip()
    
    # Extract only numbered queries
    queries = []
    for line in rewritten_part.split('\n'):
        line = line.strip()
        if line and any(line.startswith(f"{i}.") for i in range(1, 4)):
            # Remove the number and dot prefix
            query = line.split('.', 1)[1].strip()
            queries.append(query)
    return queries[:3]  # Ensure we only get 3 queries

# Example usage
# base_query = "Luật an ninh mạng là gì"
# rewritten_queries = generate_rewritten_queries(base_query, model, tokenizer)
# for i, query in enumerate(rewritten_queries, 1):
#     print(f"{i}. {query}")