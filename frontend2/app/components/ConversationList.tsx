interface ConversationListProps {
  conversation: string[];
  onAudioSelect: (audioUrl: string) => void;
}

export default function ConversationList({
  conversation,
  onAudioSelect,
}: ConversationListProps) {
  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-4">Conversation History</h2>
      <div className="space-y-2">
        {conversation.map((audioUrl, index) => (
          <button
            key={index}
            onClick={() => onAudioSelect(audioUrl)}
            className="w-full px-4 py-2 text-left border border-gray-300 rounded-md hover:bg-gray-100"
          >
            Audio Message {index + 1}
          </button>
        ))}
      </div>
    </div>
  );
}
