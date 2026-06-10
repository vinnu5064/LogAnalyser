from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import re

parsed_logs = []
failed_recordsList = []
success_recordsList = []
contextualData = []
success_search_string = 'success'
failed_search_string = 'failed'

with open(r"C:\Users\vinod\Desktop\TestLogFile.log", "r", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        # Extract timestamp, log level and JSON
        match = re.match(
            r'^(\d{2}:\d{2}:\d{2}\.\d+)\s+(\w+)\s+({.*})$',
            line
        )

        if match:

            local_time = match.group(1)
            log_level = match.group(2)
            json_part = match.group(3)

            try:
                payload = json.loads(json_part)

                parsed_logs.append({
                    "local_time": local_time,
                    "level": log_level,
                    "message": payload.get("message"),
                    "process_name": payload.get("processName"),
                    "job_id": payload.get("jobId"),
                    "file_name": payload.get("fileName"),
                    "machine_name": payload.get("machineName"),
                    "robot_name": payload.get("robotName"),
                    "timestamp": payload.get("timeStamp")
                })
                
            except Exception as e:
                print(f"Failed: {e}")
    for i in parsed_logs:
                    #print (i)
                    successresult = {key: value for key, value in i.items() if success_search_string in value}
                    failedresult = {key: value for key, value in i.items() if failed_search_string in value}
                    if successresult:
                        #print (successresult)
                        success_recordsList.append(successresult['message'].split(" ")[1])
                        
                    failedresult = {key: value for key, value in i.items() if failed_search_string in value}
                    if failedresult:
                        #print (failedresult['message'])
                        failed_recordsList.append(failedresult['message'].split(" ")[1])
    #print(success_recordsList)
    #print(failed_recordsList)


    def create_context():
          contextualData.append("Sucessfully processed records/transactions are " + ",".join(success_recordsList))
          contextualData.append("Failed records/transactions are " + ",".join(failed_recordsList))
          contextualData.append("Total success records/transactions are " + str(len(success_recordsList)))
          contextualData.append("Total failed records/transactions are " + str(len(failed_recordsList)))
          contextualData.append("Total records/transactions are " + str(len(success_recordsList)+len(failed_recordsList)))
          return contextualData
    
    #print(create_context())

    model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = model.encode(create_context())
embeddings.shape

dimension = 384
index = faiss.IndexFlatL2(dimension)
vectors = np.array(embeddings).astype("float32")
index.add(vectors)

contexts = create_context()

metadata = {
    i: context
    for i, context in enumerate(contexts)
}

#### User Action ####
query_vector = model.encode(
    "How many transactions failed?"
)
D, I = index.search(
    np.array([query_vector]).astype("float32"),
    k=5
)
print(D, I)

results = []
for idx in I[0]:
    results.append(metadata[idx])
print(results)