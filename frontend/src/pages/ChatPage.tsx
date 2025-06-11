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
  FileUploadButton,
  FileInput,
} from '../components/chat/ChatStyles';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

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
  const { token } = useAuth();
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<string>('');
  const [message, setMessage] = useState('');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
useEffect(() => {
  if (token) fetchThreads();
}, [token]);

useEffect(() => {
  if (token && activeChat) {
    fetchChats(parseInt(activeChat));
  }
}, [token, activeChat]);
  useEffect(() => {
    scrollToBottom();
  }, [chats]);

const fetchThreads = async () => {
  if (!token) return; // 👈 important
  try {
    const response = await axios.get('http://localhost:8021/threads', {
      headers: { Authorization: `Bearer ${token}` }
    });
      const threads = response.data;
      setChats(threads.map((thread: any) => ({
        id: thread.thread_id.toString(),
        title: thread.thread_type,
        messages: []
      })));
      if (threads.length > 0) {
        setActiveChat(threads[0].thread_id.toString());
      }
    } catch (error) {
      console.error('Error fetching threads:', error);
    }
  };

const fetchChats = async (threadId: number) => {
  try {
    const response = await axios.get(`http://localhost:8021/chats?thread_id=${threadId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const chatData = Array.isArray(response.data) ? response.data : [];

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === threadId.toString()
          ? {
              ...chat,
              messages: chatData.map((msg: any) => ({
                id: msg.chat_id.toString(),
                content: msg.content,
                isUser: msg.username !== 'bot',
                timestamp: new Date(msg.created_at)
              }))
            }
          : chat
      )
    );
  } catch (error) {
    console.error('Error fetching chats:', error);
  }
};

const handleSendMessage = async () => {
  if (!message.trim() && !selectedFile) return;

  try {
    // If file is selected, upload first
    if (selectedFile) {
      const fileData = new FormData();
      fileData.append('file', selectedFile);

      await axios.post(
        `http://localhost:8021/upload-pdf?thread_id=${activeChat}`,
        fileData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );
    }

    // Now send the query message
    const response = await axios.post(
      'http://localhost:8021/query',
      {
        query: message,
        thread_id: parseInt(activeChat),
        thread_specific_call: true,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const { response: botResponse, chart, table } = response.data;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      isUser: true,
      timestamp: new Date(),
    };

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: botResponse,
      isUser: false,
      timestamp: new Date(),
    };

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChat
          ? {
              ...chat,
              messages: [...chat.messages, userMessage, botMessage],
            }
          : chat
      )
    );

    setMessage('');
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';

    if (chart || table) {
      setShowAnalysis(true);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
};
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const createNewChat = async () => {
    try {
const response = await axios.post(
  'http://localhost:8021/create-thread',
  {}, // empty body
  {
    headers: { Authorization: `Bearer ${token}` }
  }
);
      const newThread = response.data;
      const newChat: Chat = {
        id: newThread.thread_id.toString(),
        title: newThread.thread_type,
        messages: [],
      };
      setChats(prevChats => [...prevChats, newChat]);
      setActiveChat(newChat.id);
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
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
          <FileInput
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <FileUploadButton
            onClick={() => fileInputRef.current?.click()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            📎
          </FileUploadButton>
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
