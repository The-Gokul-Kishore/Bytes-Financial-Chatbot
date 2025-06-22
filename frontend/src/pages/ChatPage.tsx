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
import Plot from 'react-plotly.js';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  chartData?: any; // 🧠 New optional chart
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
    if (!token) return;
    try {
      const response = await axios.get('http://localhost:8021/threads', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const threads = response.data;
      setChats(threads.map((thread: any) => ({
        id: thread.thread_id.toString(),
        title: thread.thread_name,
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
              messages: chatData.map((msg: any) => {
                let content = msg.content;
                let chartData = null;

                // Try to parse JSON content for bot messages
                if (msg.username === 'bot') {
                  try {
                    const parsed = JSON.parse(msg.content);
                    if (parsed.response) content = parsed.response;
                    if (parsed.chart) chartData = parsed.chart;
                  } catch (e) {
                    console.warn('Failed to parse bot message as JSON:', e);
                  }
                }

                return {
                  id: msg.chat_id.toString(),
                  content,
                  isUser: msg.username !== 'bot',
                  timestamp: new Date(msg.created_at),
                  chartData,
                };
              }),
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

  const userMessage: Message = {
    id: Date.now().toString(),
    content: message,
    isUser: true,
    timestamp: new Date(),
  };

  const loadingBotMessage: Message = {
    id: 'loading-' + Date.now(),
    content: 'Thinking...',
    isUser: false,
    timestamp: new Date(),
  };

  setChats(prevChats =>
    prevChats.map(chat =>
      chat.id === activeChat
        ? {
            ...chat,
            messages: [...chat.messages, userMessage, loadingBotMessage],
          }
        : chat
    )
  );

  setMessage('');
  setSelectedFile(null);
  if (fileInputRef.current) fileInputRef.current.value = '';

  try {
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

    const response = await axios.post(
      'http://localhost:8021/query',
      {
        query: message,
        thread_id: parseInt(activeChat),
        thread_specific_call: false,
      },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    const { response: botResponse, chart } = response.data;

    const finalBotMessage: Message = {
      id: Date.now().toString() + '-bot',
      content: botResponse,
      isUser: false,
      timestamp: new Date(),
      chartData: chart || null,
    };

    // Replace the placeholder loading message with actual bot message
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChat
          ? {
              ...chat,
              messages: chat.messages.map(msg =>
                msg.id === loadingBotMessage.id ? finalBotMessage : msg
              ),
            }
          : chat
      )
    );
  } catch (error) {
    console.error('Error sending message:', error);

    // Optionally update bot message to show error
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChat
          ? {
              ...chat,
              messages: chat.messages.map(msg =>
                msg.id === loadingBotMessage.id
                  ? { ...msg, content: '❌ Error occurred. Please try again.' }
                  : msg
              ),
            }
          : chat
      )
    );
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
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      const newThread = response.data;
      const newChat: Chat = {
        id: newThread.thread_id.toString(),
        title: newThread.thread_name,
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
            onClick={() => window.location.href = 'http://localhost:5100/'}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '0.5rem',
              color: 'white',
              cursor: 'pointer',
            }}
          >
            Risk Report
          </button>
        </ChatHeader>

        <ChatMessages>
          {chats
            .find(chat => chat.id === activeChat)
            ?.messages.map(msg => (
              <div key={msg.id}>
<div
  key={msg.id}
  style={{
    display: 'flex',
    justifyContent: msg.isUser ? 'flex-end' : 'flex-start',
    padding: '0.25rem',
  }}
>
  <div
    style={{
      maxWidth: '60%',
      backgroundColor: msg.isUser ? '#007aff' : '#2f3542',
      color: 'white',
      padding: '1rem',
      borderRadius: '1rem',
      borderBottomRightRadius: msg.isUser ? '0' : '1rem',
      borderBottomLeftRadius: msg.isUser ? '1rem' : '0',
      textAlign: msg.isUser ? 'right' : 'left',
    }}
  >
    {msg.content}
  </div>
</div>
{(() => {
  console.log('ChartData:', msg.chartData);
  if(msg.chartData === null) return null;
  const parsedChartData = JSON.parse(msg.chartData);
  const data = parsedChartData.data;
  const layout = parsedChartData.layout;
  return (
    msg.chartData && (
      <div style={{ padding: '1rem', width: '100%' }}>
        <Plot
          data={data}
layout={{
  ...(layout ),
  autosize: true,
}}
          useResizeHandler
          style={{ width: '100%', height: '400px' }}
        />
      </div>
    )
  );
})()}

              </div>
              
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
    </ChatContainer>
  );
};

export default ChatPage;
