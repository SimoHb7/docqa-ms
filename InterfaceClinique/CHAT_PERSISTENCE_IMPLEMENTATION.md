# Chat Persistence Implementation

## Overview
Implemented persistent chat history in the QA Chat page that survives page navigation and browser refreshes.

## Implementation Details

### Zustand Store Integration
The application already had a Zustand store (`src/store/index.ts`) with:
- **persist middleware**: Automatically saves state to localStorage
- **chatMessages**: Record of messages by session ID
- **currentChatSession**: Active session tracking
- **Helper functions**: addChatMessage, clearChatSession, setCurrentChatSession

### Changes Made to `src/pages/QAChat.tsx`

1. **Replaced Local State with Store**:
   ```typescript
   // Before: Local state (lost on unmount)
   const [messages, setMessages] = useState<ChatMessage[]>([]);
   const [sessionId, setSessionId] = useState<string | null>(null);
   
   // After: Zustand store (persisted automatically)
   const currentChatSession = useAppStore((state) => state.currentChatSession);
   const setCurrentChatSession = useAppStore((state) => state.setCurrentChatSession);
   const chatMessages = useAppStore((state) => state.chatMessages);
   const addChatMessage = useAppStore((state) => state.addChatMessage);
   const messages = currentChatSession ? (chatMessages[currentChatSession] || []) : [];
   ```

2. **Session Initialization**:
   ```typescript
   useEffect(() => {
     if (!currentChatSession) {
       const newSessionId = crypto.randomUUID();
       setCurrentChatSession(newSessionId);
     }
   }, [currentChatSession, setCurrentChatSession]);
   ```

3. **Updated Message Sending**:
   ```typescript
   const handleSendMessage = () => {
     // User message
     const userMessage: ChatMessage = { ... };
     addChatMessage(currentChatSession, userMessage);
     
     // Send to API
     askMutation.mutate({
       question: currentMessage,
       session_id: currentChatSession,
       ...
     });
   };
   ```

4. **Updated Mutation Success Handler**:
   ```typescript
   onSuccess: (data: QAResponse) => {
     const assistantMessage: ChatMessage = { ... };
     
     // Add to store (persisted automatically)
     if (currentChatSession) {
       addChatMessage(currentChatSession, assistantMessage);
     }
     
     // Update session ID if changed
     if (data.session_id && data.session_id !== currentChatSession) {
       setCurrentChatSession(data.session_id);
     }
   }
   ```

5. **Updated Clear Chat**:
   ```typescript
   const clearChat = () => {
     if (currentChatSession) {
       clearChatSession(currentChatSession);
     }
     // Create new session for next conversation
     const newSessionId = crypto.randomUUID();
     setCurrentChatSession(newSessionId);
     
     setShowSuggestions(true);
     setIsExpanded(false);
   };
   ```

## How It Works

1. **Session Creation**: On first visit, a UUID is generated for the session
2. **Message Storage**: Each message (user + assistant) is added to `chatMessages[sessionId]`
3. **Automatic Persistence**: Zustand's persist middleware saves to localStorage as `interface-clinique-storage`
4. **Restoration**: On page load, the store automatically restores from localStorage
5. **Session Continuity**: The same session ID continues across navigation

## User Experience

### Before
- Ask question → Get answer
- Navigate to Documents page
- Navigate back to QA Chat
- **Result**: Chat history lost ❌

### After
- Ask question → Get answer
- Navigate to Documents page
- Navigate back to QA Chat
- **Result**: Chat history still visible ✅

## Testing Steps

1. Open QA Chat page
2. Ask a question: "Quel est le diagnostic du patient ?"
3. Wait for response
4. Navigate to Documents page
5. Navigate back to QA Chat
6. **Verify**: Question and answer are still visible
7. Close browser and reopen
8. Navigate to QA Chat
9. **Verify**: Previous conversation is still there

## Additional Features

- **Clear History**: The "Nouvelle conversation" button clears current session and creates a new one
- **Multiple Sessions**: Could extend to show session history (not implemented yet)
- **Automatic Cleanup**: Could add expiry logic to clear old sessions (not implemented yet)

## localStorage Structure

```json
{
  "interface-clinique-storage": {
    "state": {
      "theme": "system",
      "sidebarOpen": true,
      "user": null,
      "notifications": [],
      "chatMessages": {
        "uuid-session-1": [
          {
            "id": "msg-uuid",
            "role": "user",
            "content": "Quel est le diagnostic du patient ?",
            "timestamp": "2025-01-08T...",
          },
          {
            "id": "msg-uuid",
            "role": "assistant",
            "content": "D'après les documents...",
            "timestamp": "2025-01-08T...",
            "sources": [...],
            "confidence": 0.92
          }
        ]
      },
      "currentChatSession": "uuid-session-1"
    },
    "version": 0
  }
}
```

## Benefits

1. **Better UX**: Users don't lose context when navigating
2. **No Backend Changes**: Pure frontend solution using existing store
3. **Automatic**: No manual save/restore logic needed
4. **Works Offline**: localStorage persists without server
5. **Resilient**: Survives browser refresh and tab close

## Future Enhancements

- Show list of previous chat sessions
- Export/import chat history
- Search through past conversations
- Auto-expire old sessions (e.g., after 7 days)
- Share chat session via URL
