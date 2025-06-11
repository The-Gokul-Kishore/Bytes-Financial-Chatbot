import styled from '@emotion/styled';
import { motion } from 'framer-motion';

export const ChatContainer = styled.div`
  display: flex;
  height: 100vh;
  background: #1a1a2e;
  color: white;
`;

export const Sidebar = styled.div<{ width?: string }>`
  width: ${props => props.width || '280px'};
  background: rgba(255, 255, 255, 0.05);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem;
  overflow-y: auto;
`;

export const ChatMain = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #16213e;
`;

export const ChatHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

export const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

export const MessageBubble = styled(motion.div)<{ isUser?: boolean }>`
  max-width: 70%;
  padding: 1rem;
  border-radius: 1rem;
  background: ${props => props.isUser ? 'linear-gradient(45deg, #00ff87, #60efff)' : 'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.isUser ? '#1a1a2e' : 'white'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  word-wrap: break-word;
`;

export const ChatInput = styled.div`
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 1rem;
`;

export const Input = styled.textarea`
  flex: 1;
  padding: 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: white;
  resize: none;
  min-height: 50px;
  max-height: 150px;

  &:focus {
    outline: none;
    border-color: #00ff87;
  }
`;

export const SendButton = styled(motion.button)`
  padding: 0 1.5rem;
  border-radius: 1rem;
  border: none;
  background: linear-gradient(45deg, #00ff87, #60efff);
  color: #1a1a2e;
  cursor: pointer;
  font-weight: bold;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }
`;

export const ChatItem = styled(motion.div)<{ isActive?: boolean }>`
  padding: 1rem;
  border-radius: 0.5rem;
  background: ${props => props.isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent'};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

export const AnalysisPanel = styled.div`
  width: 400px;
  background: rgba(255, 255, 255, 0.05);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem;
  overflow-y: auto;
`;

export const GraphContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
`; 