import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  AuthContainer,
  AuthBox,
  AuthTitle,
  AuthForm,
  AuthInput,
  AuthButton,
  AuthLink,
} from '../components/auth/AuthStyles';
import { useAuth } from '../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(formData.username, formData.password);
      navigate('/chat');
    } catch (err) {
      setError('Invalid username or password');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <AuthContainer>
      <AuthBox
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <AuthTitle>Welcome Back</AuthTitle>
        <AuthForm onSubmit={handleSubmit}>
          {error && (
            <div style={{ color: '#ff4444', marginBottom: '1rem', textAlign: 'center' }}>
              {error}
            </div>
          )}
          <AuthInput
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <AuthInput
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <AuthButton
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Login
          </AuthButton>
        </AuthForm>
        <AuthLink>
          Don't have an account?{' '}
          <Link to="/signup">Sign up</Link>
        </AuthLink>
      </AuthBox>
    </AuthContainer>
  );
};

export default LoginPage; 