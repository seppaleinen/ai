
#### Installed llms
```
mistral:latest
nomic-embed-text:latest
qwen3:8b
hf.co/Triangle104/Qwen3-Esper3-Reasoning-CODER-Instruct-12B-Brainstorm20x-Q4_K_S-GGUF:Q4_K_S
hf.co/mradermacher/Llama3.3-70B-COT-GGUF:Q6_K
hf.co/mradermacher/Llama3.3-70B-COT-GGUF:Q4_K_M
gemma2:9b
gpt-oss:latest
granite-code:8b
granite4:latest
hir0rameel/qwen-claude:latest
gemma3:12b
deepseek-r1:8b
llama3:latest
vicuna:latest
phi3:latest
gemma2:latest
```



```
Enable your agent to search the web to answer your questions by connecting to a web-search (SERP) provider. Web search during agent sessions will not work until this is set up.
```


Old config using anything-llm
```
  anything-llm:
    image: mintplexlabs/anythingllm:latest
    container_name: anything-llm
    ports:
      - "3001:3001"
    volumes:
      - anything_llm_data:/app/server/storage
    environment:
      - STORAGE_DIR=/app/server/storage
      - STORAGE_KIND=chroma
      - CHROMA_ENDPOINT=http://chroma:8000 # Connects to the chroma service
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434 # Connects to the ollama service
      - LLM_MODEL_PREF=mistral # Specifies which model to use for generation
      - EMBEDDING_MODEL_PREF=nomic-embed-text # Specifies which model to use for vectorization
    depends_on:
      - ollama
      - chroma
```




```
| Target 				        | Model 							            | Parameters	| Size 		  | ~ELO 	 | Notes 							            |
| --------------------- | ------------------------------- | ----------- | --------- | ------ | ------------------------------ |
| deepseek-r1-qwen-14b 	| deepseek-r1-distill-qwen-14b 		| 14B 			  | 10.5 GB  	| 1375   | The best small thinking model 	|
| gemma-3-27b 			    | gemma-3-27b-it 					        | 27B 			  | 19.27 GB 	| 1361   | Google's best medium model 		|
| mistral-small-3		    | mistral-small-3.2-24b-instruct 	| 24B 			  | 16.76 GB 	| 1273	 | Mistral AI's best small model 	|
| llama-3-8b 			      | meta-llama-3.1-8b-instruct 		  | 8B  			  | 5.73 GB  	| 1193   | Meta's best small model 			  |
| phi-4-mini 			      | phi-4-mini-instruct				      | 4B  			  | 2.85 GB  	| 1088++ | Microsoft's best tiny model 		|
```