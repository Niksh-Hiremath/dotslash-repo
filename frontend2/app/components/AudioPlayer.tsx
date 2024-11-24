"use client";

import { useRef, useEffect, useState } from "react";

interface AudioPlayerProps {
  audioUrl: string | null;
}

export default function AudioPlayer({ audioUrl }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.src = audioUrl || "";
      setIsPlaying(false);
    }
  }, [audioUrl]);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="flex justify-center items-center">
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />
      <button
        onClick={togglePlayPause}
        disabled={!audioUrl}
        className={`px-4 py-2 rounded-md ${
          audioUrl
            ? "bg-green-500 hover:bg-green-600 text-white"
            : "bg-gray-300 text-gray-500 cursor-not-allowed"
        }`}
      >
        {isPlaying ? "Pause" : "Play Response"}
      </button>
    </div>
  );
}
