import warnings
import argparse
import logging
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn
from pathlib import Path
import os

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

#get arguments from command
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.7)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.7)
args = parser.parse_args()

#evaluation function
def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # Read the wine-quality csv file from local
    data = pd.read_csv("red-wine-quality.csv")

    #os.mkdir("data/")
    ##data.to_csv("data/red-wine-quality.csv",index=False)

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)
    #train.to_csv("data/train.csv", index=False)
    #test.to_csv("data/test.csv", index=False)


    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = args.alpha
    l1_ratio = args.l1_ratio

    mlflow.set_tracking_uri(uri="")

    print("the set trucking uri is:", mlflow.get_tracking_uri())

    exp = mlflow.set_experiment(experiment_name="ex_6")

    #get_exp = mlflow.get_experiment(exp_id)

    print("Name: {}".format(exp.name))
    print("Experiment_id: {}".format(exp.experiment_id))
    print("Artifact Location: {}".format(exp.artifact_location))
    print("Tags: {}".format(exp.tags))
    print("Lifecycle_stage: {}".format(exp.lifecycle_stage))
    print("Creation timestamp: {}".format(exp.creation_time))

    #with mlflow.start_run(experiment_id=exp.experiment_id,run_name="run_1"):
    #with mlflow.start_run(run_id="71373a4e24b440dea4d9a50c61e5df5c"):
    #mlflow.start_run(run_id="71373a4e24b440dea4d9a50c61e5df5c")

    mlflow.start_run()

    # mlflow.set_tag("version","0.1")
    tags = {
        "engineering":"MLOps",
        "version":"0.2"

    }

    mlflow.set_tags(tags)

    lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
    lr.fit(train_x, train_y)

    predicted_qualities = lr.predict(test_x)

    (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

    print("Elasticnet model (alpha={:f}, l1_ratio={:f}):".format(alpha, l1_ratio))
    print("  RMSE: %s" % rmse)
    print("  MAE: %s" % mae)
    print("  R2: %s" % r2)
    params = {
        "alpha":alpha,
        "l1_ratio":l1_ratio
    }
    mlflow.log_params(params)

    metrics = {
        "rmse":rmse,
        "r2":r2,
        "mae":mae
    }
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(lr,"myNewModel_4")
    mlflow.log_artifact('red-wine-quality.csv')
    mlflow.log_artifacts("data/")

    run = mlflow.active_run()
    print("id is:",run.info.run_id," name is:",run.info.run_name)

    run = mlflow.last_active_run()
    print("for last active run    id is:", run.info.run_id, " name is:", run.info.run_name)

    mlflow.end_run()

    run = mlflow.last_active_run()
    print("for last active run    id is:", run.info.run_id, " name is:", run.info.run_name)
