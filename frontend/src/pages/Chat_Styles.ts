// ChatStyles.ts
import styled from 'styled-components';
import { motion } from 'framer-motion';

export const ChatContainer = styled.div`
  display: flex;
  height: 100vh;
`;

export const Sidebar = styled.div`
  width: 250px;
  background: #1f1f2e;
  padding: 1rem;
  overflow-y: auto;
`;

export const ChatMain = styled.div`
  flex: 1;
  background: #12121f;
  display: flex;
  flex-direction: column;
`;

export const ChatHeader = styled.div`
  padding: 1rem;
  background: #222;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

export const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
`;

export const MessageBubble = styled(motion.div)<{ isUser: boolean }>`
  background: ${({ isUser }) => (isUser ? '#00ff87' : '#333')};
  color: ${({ isUser }) => (isUser ? '#000' : '#fff')};
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  margin: 0.5rem 0;
  max-width: 60%;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
`;

export const ChatInput = styled.div`
  display: flex;
  padding: 1rem;
  border-top: 1px solid #333;
`;

export const Input = styled.input`
  flex: 1;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: none;
  margin: 0 0.5rem;
`;

export const SendButton = styled(motion.button)`
  background: #00ff87;
  color: #000;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
`;

export const FileInput = styled.input``;

export const FileUploadButton = styled(motion.button)`
  background: #444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  padding: 0.75rem;
`;

export const ChatItem = styled(motion.div)<{ isActive: boolean }>`
  background: ${({ isActive }) => (isActive ? '#444' : 'transparent')};
  padding: 0.75rem;
  border-radius: 0.5rem;
  color: white;
  cursor: pointer;
  margin-bottom: 0.5rem;
`;

export const AnalysisPanel = styled.div`
  width: 300px;
  background: #1a1a2e;
  padding: 1rem;
  color: white;
`;

export const GraphContainer = styled.div`
  background: #333;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
`;
