import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audio = formData.get("audio") as Blob | null;

    if (!audio) {
      return NextResponse.json(
        { error: "No audio file provided" },
        { status: 400 }
      );
    }
    const response = await fetch("https://localhost:8000", {
      method: "POST",
      headers: {
        "Content-Type": audio.type,
      },
      body: audio,
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to process audio" },
        { status: response.status }
      );
    }

    const processedAudio = await response.blob();

    return new NextResponse(processedAudio, {
      headers: {
        "Content-Type": audio.type,
      },
    });
  } catch (error) {
    console.error("Error processing audio:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
