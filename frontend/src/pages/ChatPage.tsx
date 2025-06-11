import React, { useState, useRef, useEffect } from 'react';
import {
  ChatContainer,
  Sidebar,
  ChatMain,
  ChatHeader,
  ChatMessages,
  MessageBubble,
  ChatInput,
  Input,
  SendButton,
  ChatItem,
  AnalysisPanel,
  GraphContainer,
} from '../components/chat/ChatStyles';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
}

const ChatPage: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([
    { id: '1', title: 'New Chat', messages: [] },
  ]);
  const [activeChat, setActiveChat] = useState<string>('1');
  const [message, setMessage] = useState('');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chats]);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date(),
    };

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChat
          ? {
              ...chat,
              messages: [...chat.messages, newMessage],
            }
          : chat
      )
    );

    setMessage('');

    // TODO: Implement API call to get AI response
    // Simulating AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: 'This is a simulated AI response. The actual API integration will be implemented here.',
        isUser: false,
        timestamp: new Date(),
      };

      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === activeChat
            ? {
                ...chat,
                messages: [...chat.messages, aiResponse],
              }
            : chat
        )
      );
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
    };
    setChats(prevChats => [...prevChats, newChat]);
    setActiveChat(newChat.id);
  };

  return (
    <ChatContainer>
      <Sidebar>
        <button
          onClick={createNewChat}
          style={{
            width: '100%',
            padding: '1rem',
            marginBottom: '1rem',
            background: 'linear-gradient(45deg, #00ff87, #60efff)',
            border: 'none',
            borderRadius: '0.5rem',
            color: '#1a1a2e',
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
        >
          New Chat
        </button>
        {chats.map(chat => (
          <ChatItem
            key={chat.id}
            isActive={chat.id === activeChat}
            onClick={() => setActiveChat(chat.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {chat.title}
          </ChatItem>
        ))}
      </Sidebar>

      <ChatMain>
        <ChatHeader>
          <h2>{chats.find(chat => chat.id === activeChat)?.title}</h2>
          <button
            onClick={() => setShowAnalysis(!showAnalysis)}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '0.5rem',
              color: 'white',
              cursor: 'pointer',
            }}
          >
            {showAnalysis ? 'Hide Analysis' : 'Show Analysis'}
          </button>
        </ChatHeader>

        <ChatMessages>
          {chats
            .find(chat => chat.id === activeChat)
            ?.messages.map(msg => (
              <MessageBubble
                key={msg.id}
                isUser={msg.isUser}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {msg.content}
              </MessageBubble>
            ))}
          <div ref={messagesEndRef} />
        </ChatMessages>

        <ChatInput>
          <Input
            value={message}
            onChange={e => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
          />
          <SendButton
            onClick={handleSendMessage}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Send
          </SendButton>
        </ChatInput>
      </ChatMain>

      {showAnalysis && (
        <AnalysisPanel>
          <h3>Analysis</h3>
          <GraphContainer>
            {/* TODO: Implement actual graph visualization */}
            <p>Graph visualization will appear here</p>
          </GraphContainer>
          <GraphContainer>
            <p>Additional analysis will appear here</p>
          </GraphContainer>
        </AnalysisPanel>
      )}
    </ChatContainer>
  );
};

export default ChatPage; 