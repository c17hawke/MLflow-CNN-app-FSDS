import argparse
import os
import shutil
from tqdm import tqdm
import logging
from src.utils.common import read_yaml, create_directories
import random
import tensorflow as tf

STAGE = "Training" ## <<< change stage name 

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )


def main(config_path):
    ## read config files
    config = read_yaml(config_path)

    ## get ready the data

    PARENT_DIR = os.path.join(
    config["data"]["unzip_data_dir"],
    config["data"]["parent_data_dir"])

    params = config["params"]

    logging.info(f"read the data from {PARENT_DIR}")
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        PARENT_DIR,
        validation_split=params["validation_split"],
        subset="training",
        seed=params["seed"],
        image_size=params["img_shape"][:-1],
        batch_size=params["batch_size"]
    )

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        PARENT_DIR,
        validation_split=params["validation_split"],
        subset="validation",
        seed=params["seed"],
        image_size=params["img_shape"][:-1],
        batch_size=params["batch_size"]
    )

    train_ds = train_ds.prefetch(buffer_size=params["buffer_size"])
    val_ds = val_ds.prefetch(buffer_size=params["buffer_size"])

    ## load the base model

    path_to_model = os.path.join(
        config["data"]["local_dir"],
        config["data"]["model_dir"], 
        config["data"]["init_model_file"])
    
    logging.info(f"load the base model from {path_to_model}")
    

    classifier = tf.keras.models.load_model(path_to_model)

    ## training
    logging.info(f"training started")

    classifier.fit(train_ds, epochs=params["epochs"], validation_data = val_ds)
    
    trained_model_file = os.path.join(
        config["data"]["local_dir"],
        config["data"]["model_dir"], 
        config["data"]["trained_model_file"])

    classifier.save(trained_model_file)
    logging.info(f"trained model is saved at : {trained_model_file}")

    

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main(config_path=parsed_args.config)
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e