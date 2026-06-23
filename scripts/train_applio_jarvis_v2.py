from gradio_client import Client

client = Client("http://127.0.0.1:6969/")

MODEL_NAME = "JarvisV2"
DATASET_PATH = r"C:\AI\ProjectJarvis\voices\JarvisV2"

print("1. Preprocessing dataset...")
print(client.predict(
    MODEL_NAME,
    DATASET_PATH,
    "40000",
    32,
    "Automatic",
    False,
    False,
    0.5,
    3.0,
    0.3,
    "post",
    api_name="/run_preprocess_script"
))

print("2. Extracting features...")
print(client.predict(
    MODEL_NAME,
    "rmvpe",
    32,
    "0",
    "40000",
    "contentvec",
    None,
    2,
    api_name="/run_extract_script"
))

print("3. Training model...")
print(client.predict(
    True,          # accept terms
    MODEL_NAME,    # model name
    8,             # batch size - slightly lower because dataset is tiny
    True,          # save every epoch
    True,          # save only latest
    200,           # epochs - 24 sec is tiny, don't go insane yet
    "40000",       # sample rate
    4,             # save every N epochs
    "0",           # GPU id
    False,         # cache dataset in GPU
    50,            # overtraining detector
    True,          # pretrained
    False,         # custom pretrained
    "Auto",        # index algorithm
    False,         # vocoder fine-tuning
    False,         # checkpointing
    "",            # custom pretrained G
    "",            # custom pretrained D
    "HiFi-GAN",    # vocoder
    False,
    api_name="/enforce_terms_1"
))

print("4. Training index...")
print(client.predict(
    MODEL_NAME,
    "Auto",
    api_name="/run_index_script"
))

print("Done.")