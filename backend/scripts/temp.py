import kagglehub

# Download latest version
path = kagglehub.dataset_download("jithinanievarghese/drugs-related-to-common-treatments")

print("Path to dataset files:", path)