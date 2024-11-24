"use client";

import { useState } from "react";
import AudioRecorder from "./components/AudioRecorder";
import AudioPlayer from "./components/AudioPlayer";

export default function AudioChat() {
  const [responseAudio, setResponseAudio] = useState<string | null>(null);

  const handleAudioRecorded = async (audioBlob: Blob) => {
    try {
      // Create a FormData object and append the audio blob
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      // Send the audio to the API
      const response = await fetch("/api/chat", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to send audio to API");
      }

      // Assume the API returns an audio blob
      const responseAudioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(responseAudioBlob);
      setResponseAudio(audioUrl);
    } catch (error) {
      console.error("Error sending audio to API:", error);
      alert("Failed to send audio. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Audio Chat
        </h1>
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="mb-6">
            <AudioRecorder onAudioRecorded={handleAudioRecorded} />
          </div>
          <div className="mb-6">
            <AudioPlayer audioUrl={responseAudio} />
          </div>
        </div>
      </div>
    </div>
  );
}
