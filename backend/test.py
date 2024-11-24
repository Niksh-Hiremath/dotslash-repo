import numpy as np
import matplotlib.pyplot as plt
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import ShortTermFeatures

# Load the audio file
audio_path = "test.wav"
[Fs, x] = audioBasicIO.read_audio_file(audio_path)  # Fs: Sampling rate, x: Audio signal

# Convert to mono if the audio is stereo
if x.ndim > 1:
    x = x.mean(axis=1)

# Step size (25ms) and window size (50ms)
step_size = int(0.025 * Fs)  # Convert from seconds to samples
window_size = int(0.05 * Fs)  # Convert from seconds to samples

# Extract short-term features
F, feature_names = ShortTermFeatures.feature_extraction(x, Fs, window_size, step_size)

# Print feature names and their mean values
print("Feature Summary:")
for i, name in enumerate(feature_names):
    print(f"{name}: {np.mean(F[i]):.4f}")

# Extract specific features for further analysis
energy = F[1]  # Short-term Energy
zcr = F[0]     # Zero-Crossing Rate

# Set a silence threshold based on energy
silence_threshold = 0.05 * np.max(energy)  # 10% of max energy

# Detect pauses (regions where energy is below the threshold)
pauses = np.where(energy < silence_threshold, 1, 0)

# Calculate the total pause duration
total_pause_duration = np.sum(pauses) * (step_size / Fs)
print(f"\nTotal Pause Duration: {total_pause_duration:.2f} seconds")

# Calculate average ZCR for voiced regions (where energy > silence threshold)
voiced_regions = energy > silence_threshold
average_zcr = np.mean(zcr[voiced_regions])
print(f"Average ZCR for Voiced Speech: {average_zcr:.4f}")

# Create a time axis for plotting
time = np.arange(F.shape[1]) * (step_size / Fs)

# Define the ideal range for ZCR
zcr_ideal_min = 0.01
zcr_ideal_max = 0.1

# Score calculation for ZCR
if average_zcr < zcr_ideal_min:
    zcr_score = 100  # Perfect score for low ZCR
elif average_zcr > zcr_ideal_max:
    zcr_score = 0  # Poor score for high ZCR
else:
    zcr_score = 100 * (1 - (average_zcr - zcr_ideal_min) / (zcr_ideal_max - zcr_ideal_min))

print(f"ZCR Score: {zcr_score:.2f}/100")

total_speech_duration = len(x) / Fs  # Length of audio signal divided by sampling rate

# Define the ideal range for pause percentage
pause_ideal_min = 0  # No pauses
pause_ideal_max = 100  # shit speech
pause_time_percentage = (1 - total_pause_duration / total_speech_duration) * 100

# Score calculation for pause percentage
if pause_time_percentage < pause_ideal_min:
    pause_score = 100  # Perfect score for no pauses
elif pause_time_percentage > pause_ideal_max:
    pause_score = 0  # Poor score for too many pauses
else:
    pause_score = 100 * (1 - (pause_time_percentage - pause_ideal_min) / (pause_ideal_max - pause_ideal_min))

print(f"Pause Time Percentage Score: {pause_score:.2f}/100")

# Plot Energy and ZCR over time
plt.figure(figsize=(10, 6))
plt.plot(time, energy, label="Energy", color="blue")
plt.plot(time, zcr, label="ZCR", color="orange")
plt.axhline(y=silence_threshold, color='red', linestyle='--', label="Silence Threshold")
plt.xlabel("Time (s)")
plt.ylabel("Feature Value")
plt.title("Energy and ZCR over Time")
plt.legend()
plt.show()
