import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import styled from '@emotion/styled';

const LandingContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 2rem;
  position: relative;
  overflow: hidden;
`;

const Stars = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, transparent 0%, #1a1a2e 100%);
  z-index: 1;
`;

const Content = styled.div`
  z-index: 2;
  text-align: center;
  max-width: 800px;
`;

const Title = styled(motion.h1)`
  font-size: 4rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #00ff87, #60efff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Subtitle = styled(motion.p)`
  font-size: 1.5rem;
  margin-bottom: 2rem;
  color: #a0a0a0;
`;

const Button = styled(motion.button)`
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border: none;
  border-radius: 50px;
  background: linear-gradient(45deg, #00ff87, #60efff);
  color: #1a1a2e;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <LandingContainer>
      <Stars />
      <Content>
        <Title
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          Welcome to the Future
        </Title>
        <Subtitle
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Explore the possibilities of AI-powered analysis and insights
        </Subtitle>
        <Button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          onClick={() => navigate('/login')}
        >
          Get Started
        </Button>
      </Content>
    </LandingContainer>
  );
};

export default LandingPage; 