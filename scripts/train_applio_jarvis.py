from gradio_client import Client

client = Client("http://127.0.0.1:6969/")

MODEL_NAME = "Jarvis"
DATASET_PATH = r"C:\AI\ProjectJarvis\voices\Jarvis"

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
    10,            # batch size
    True,          # save every epoch
    True,          # save only latest
    300,           # epochs
    "40000",       # sample rate
    4,             # save every N epochs
    "0",           # GPU id
    False,         # cache dataset in GPU
    50,            # overtraining detector
    True,          # pretrained
    False,         # custom pretrained
    "Auto",        # index algorithm
    False,         # vocoder fine-tuning?
    False,         # checkpointing?
    "",            # custom pretrained G, required dropdown may need UI value
    "",            # custom pretrained D, required dropdown may need UI value
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