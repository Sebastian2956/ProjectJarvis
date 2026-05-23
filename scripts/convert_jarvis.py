from gradio_client import Client, handle_file
import shutil

client = Client("http://127.0.0.1:6969/")

input_audio = r"C:\AI\ProjectJarvis\audio\output.wav"

select_audio, output_path = client.predict(
    handle_file(input_audio),
    api_name="/save_to_wav2"
)

print("Cached audio:", select_audio)
print("Output path:", output_path)

result = client.predict(
    True,
    0,
    0.75,
    1,
    0.5,
    "rmvpe",
    select_audio,
    output_path,
    r"C:\AI\Tools\ApplioV3.6.2\logs\Jarvis\Jarvis_300e_1800s.pth",
    r"C:\AI\Tools\ApplioV3.6.2\logs\Jarvis\Jarvis.index",
    False, False, 1, False, 155.0, False, 0.5,
    "WAV",
    "contentvec",
    None,
    False, 1.0, 1.0,
    False, False, False, False, False, False, False, False, False, False, False,
    0.5, 0.5, 0.33, 0.4, 1.0, 0.0, 0, -6, 0.05, 0, 25,
    1.0, 0.25, 7, 0.0, 0.5, 8, -6, 0, 1, 1.0, 100, 0.5, 0.0, 0.5,
    0,
    api_name="/enforce_terms"
)

print("RESULT:")
print(result)

# result[1] is the temp converted wav
temp_output = result[1]

final_output = r"C:\AI\ProjectJarvis\audio\jarvis_final.wav"

shutil.copy(temp_output, final_output)

print(f"\nSaved final file to:\n{final_output}")