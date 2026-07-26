from evaluation.evaluator import evaluate_run
import mlflow
print("hello")
mlflow.set_experiment("Enterprise AI Platform11")

with mlflow.start_run():
    mlflow.log_param("chunk_size",200)
    mlflow.log_param("top_k",10)
    mlflow.log_param("embedding_model","bge-small-en-v1.5")
    mlflow.log_param("temperature",0.1)
    mlflow.log_metric("faithfulness",0.83)
    mlflow.log_metric("latency",0.25)
    print("experiment logged successfully")

status= evaluate_run(0.4,1,.05)
print(status)

mlflow.log_param(
    "deployment_status",
    status
)